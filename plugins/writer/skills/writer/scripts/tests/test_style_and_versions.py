import json
import os
import tempfile
import unittest

from tests.helpers import run
import save_version
import style


class StyleTest(unittest.TestCase):
    """Every test points WRITER_HOME at a temp dir: the real ~/.writer is never touched."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = os.path.join(self.tmp.name, "home")
        self.project = os.path.join(self.tmp.name, "project", "sub")
        os.makedirs(self.project)
        self.env = {"WRITER_HOME": self.home}
        self.old = os.environ.get("WRITER_HOME")
        os.environ["WRITER_HOME"] = self.home

    def tearDown(self):
        if self.old is None:
            os.environ.pop("WRITER_HOME", None)
        else:
            os.environ["WRITER_HOME"] = self.old
        self.tmp.cleanup()

    def test_show_empty_writes_nothing(self):
        self.assertEqual(style.global_path(), os.path.join(self.home, "style.md"))
        r = style.effective(self.project)
        self.assertEqual(r["used"], [])
        self.assertEqual(r["writes_to"], style.global_path())
        self.assertEqual(style.effective(self.project, project=True)["writes_to"],
                         os.path.join(self.project, ".writer", "style.md"))
        self.assertFalse(os.path.exists(self.home), "show must not create anything")

    def test_write_backup_and_merge_with_project_layer(self):
        style.write_profile("Global v1\n")
        r = style.write_profile("Global v2\n")
        self.assertTrue(r["backup"].endswith("style.md.bak"))
        with open(r["backup"], encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "Global v1\n")
        layer = os.path.join(self.tmp.name, "project", ".writer")
        os.makedirs(layer)
        with open(os.path.join(layer, "style.md"), "w", encoding="utf-8") as fh:
            fh.write("Project: no emoji\n")
        r = style.effective(self.project)
        self.assertEqual(len(r["used"]), 2)
        self.assertLess(r["profile"].index("Global v2"), r["profile"].index("Project: no emoji"))
        self.assertEqual(sorted(os.listdir(self.home)), ["style.md", "style.md.bak"])

    def test_remember_appends_rule_with_scope_and_origin(self):
        r = style.remember("не называть сумму вознаграждения", "письма партнёрам до подписания договора",
                           "письмо поставщику", date="2026-10-07")
        self.assertEqual(r["line"], "- [письма партнёрам до подписания договора] не называть сумму "
                                    "вознаграждения (письмо поставщику, 2026-10-07)")
        self.assertIsNone(r["backup"])
        style.remember("подпись: Саша", "все письма", "письмо Марте", date="2026-10-08")
        with open(style.global_path(), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[1].startswith("- [все письма] подпись: Саша"))
        for bad in (("x", "", "y"), ("x", "y", "  "), ("a\nb", "y", "z")):
            with self.assertRaises(style._text.BadInput):
                style.remember(*bad)

    def test_cli(self):
        p = run("style.py", "show", env=self.env)
        self.assertEqual(json.loads(p.stdout.decode("utf-8"))["global"]["path"], os.path.join(self.home, "style.md"))
        self.assertFalse(os.path.exists(self.home), "show must not write")
        p = run("style.py", "write", "--from", "-", stdin="Пишу коротко.\n", env=self.env)
        self.assertEqual(p.returncode, 0, p.stderr)
        p = run("style.py", "remember", "--rule", "без «коллеги»", "--when", "посты в канал",
                "--origin", "пост про бота", "--format", "text", env=self.env)
        self.assertEqual(p.returncode, 0, p.stderr)
        p = run("style.py", "show", "--format", "text", env=self.env, cwd=self.project)
        out = p.stdout.decode("utf-8")
        self.assertIn("Пишу коротко.", out)
        self.assertIn("- [посты в канал] без «коллеги» (пост про бота, ", out)
        self.assertEqual(run("style.py", "write", "--from", "-", stdin="  \n", env=self.env).returncode, 2)
        self.assertEqual(run("style.py", "remember", "--rule", "x", "--when", "", "--origin", "y",
                             env=self.env).returncode, 2)
        self.assertEqual(run("style.py", env=self.env).returncode, 2)

    def block_home(self):
        """A regular file where the WRITER_HOME folder should be: the global profile cannot be written."""
        os.makedirs(os.path.dirname(self.home), exist_ok=True)
        with open(self.home, "w", encoding="utf-8") as fh:
            fh.write("not a folder\n")

    def test_write_falls_back_to_project_layer(self):
        self.block_home()
        r = style.write_profile("Fallback v1\n", start=self.project)
        target = os.path.join(self.project, ".writer", "style.md")
        self.assertEqual((r["path"], r["layer"]), (target, "project"))
        self.assertEqual(r["fallback_from"], style.global_path())
        self.assertTrue(r["error"])
        self.assertTrue(os.path.isfile(self.home), "the blocked global folder stays as it was")
        r = style.write_profile("Fallback v2\n", start=self.project)
        with open(r["backup"], encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "Fallback v1\n")
        e = style.effective(self.project)
        self.assertEqual(e["used"], [target])
        self.assertEqual(e["project"], target)
        self.assertIn("Fallback v2", e["profile"])

    def test_write_project_flag_uses_nearest_layer(self):
        layer = os.path.join(self.tmp.name, "project", ".writer")
        os.makedirs(layer)
        with open(os.path.join(layer, "style.md"), "w", encoding="utf-8") as fh:
            fh.write("Old project\n")
        r = style.write_profile("New project\n", project=True, start=self.project)
        self.assertEqual(r["path"], os.path.join(layer, "style.md"))
        self.assertIsNone(r["fallback_from"])
        self.assertTrue(r["backup"].endswith("style.md.bak"))
        self.assertFalse(os.path.exists(self.home), "--project never touches the global profile")

    def test_cli_fallback_and_project_flag(self):
        self.block_home()
        p = run("style.py", "write", "--from", "-", "--format", "text", stdin="Пишу коротко.\n",
                env=self.env, cwd=self.project)
        self.assertEqual(p.returncode, 0, p.stderr)
        out = p.stdout.decode("utf-8")
        target = os.path.join(os.path.realpath(self.project), ".writer", "style.md")
        self.assertIn("project layer", out)
        self.assertIn("could not write the global profile", out)
        with open(target, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "Пишу коротко.\n")
        p = run("style.py", "show", "--format", "text", env=self.env, cwd=self.project)
        self.assertIn("Пишу коротко.", p.stdout.decode("utf-8"))
        p = run("style.py", "write", "--from", "-", "--project", stdin="Проект.\n", env=self.env, cwd=self.project)
        r = json.loads(p.stdout.decode("utf-8"))
        self.assertEqual((r["layer"], r["fallback_from"]), ("project", None))
        self.assertTrue(r["backup"].endswith("style.md.bak"))

    def test_cli_both_unwritable_fails_cleanly(self):
        self.block_home()
        blocked = os.path.join(self.tmp.name, "blocked")
        os.makedirs(blocked)
        with open(os.path.join(blocked, ".writer"), "w", encoding="utf-8") as fh:
            fh.write("a file, not a folder\n")
        p = run("style.py", "write", "--from", "-", stdin="x\n", env=self.env, cwd=blocked)
        self.assertEqual(p.returncode, 2)
        self.assertIn("could not write the profile", p.stderr.decode("utf-8"))


    def write_layer(self, folder, name, text):
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_show_summary(self):
        s = style.effective(self.project)["summary"]
        self.assertEqual(dict(s), {"rules": 0, "updated": None, "declined": 0})
        p = run("style.py", "show", "--format", "text", env=self.env, cwd=self.project)
        self.assertEqual(p.stdout.decode("utf-8").splitlines()[0], "no profile yet")
        style.write_profile("Пишу коротко.\n- подпись: Саша\n- без эмодзи\n")
        layer = os.path.join(self.tmp.name, "project", ".writer")
        self.write_layer(layer, "style.md", "- на «вы»\n")
        self.write_layer(layer, "declined.md", "- [посты] без восклицаний (2026-11-01)\n")
        self.write_layer(self.home, "declined.md", "- [письма] без подписи (2026-11-02)\n")
        os.utime(style.global_path(), (0, 0))
        s = style.effective(self.project)["summary"]
        self.assertEqual((s["rules"], s["declined"]), (3, 2))
        today = __import__("datetime").date.today().isoformat()
        self.assertEqual(s["updated"], today, "the newest used file decides the date")
        p = run("style.py", "show", "--format", "text", env=self.env, cwd=self.project)
        self.assertEqual(p.stdout.decode("utf-8").splitlines()[0], "profile: 3 rules, updated " + today)

    def candidates(self, *rules):
        return [{"rule": r, "when": "письма клиентам", "origin": "ответ Марте"} for r in rules]

    def test_review_filters_profile_declined_and_limit(self):
        style.remember("Подпись: Саша", "все письма", "письмо Марте", date="2026-10-08")
        style.remember("цены (с НДС) цифрами", "письма", "ответ Марте (упаковка)", date="2026-10-09")
        style.write_profile(style.read(style.global_path()) + "- без эмодзи\n")
        self.write_layer(self.home, "declined.md", "- [письма] без подписи (2026-11-02)\n")
        layer = os.path.join(self.tmp.name, "project", ".writer")
        self.write_layer(layer, "declined.md", "- [посты] без восклицаний (2026-11-01)\n")
        before = sorted(os.listdir(self.home)), sorted(os.listdir(layer))
        r = style.review(self.candidates("  подпись:   саша. ", "Без эмодзи", "цены (с НДС) цифрами", "без подписи", "Без восклицаний.",
                                         "один", "два", "три", "четыре"), start=self.project)
        self.assertEqual([c["rule"] for c in r["propose"]], ["один", "два", "три"])
        self.assertEqual(r["propose"][0], {"rule": "один", "when": "письма клиентам", "origin": "ответ Марте"})
        self.assertEqual([(d["rule"].strip(), d["reason"]) for d in r["dropped"]],
                         [("подпись:   саша.", "in_profile"), ("Без эмодзи", "in_profile"), ("цены (с НДС) цифрами", "in_profile"),
                          ("без подписи", "declined"), ("Без восклицаний.", "declined"), ("четыре", "limit")])
        self.assertEqual(r["writes_to"], style.global_path())
        self.assertEqual(r["declined"], ["без подписи", "без восклицаний"])
        self.assertEqual(style.review([], start=self.project, project=True)["writes_to"],
                         os.path.join(self.project, ".writer", "style.md"), "declined.md alone is no profile layer")
        self.assertEqual((sorted(os.listdir(self.home)), sorted(os.listdir(layer))), before, "review writes nothing")
        with self.assertRaises(style._text.BadInput):
            style.review([{"rule": "x", "when": ""}])

    def test_review_cli_empty_and_bad_input(self):
        p = run("style.py", "review", "--candidates", "-", stdin="[]", env=self.env, cwd=self.project)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = json.loads(p.stdout.decode("utf-8"))
        self.assertEqual((r["propose"], r["dropped"]), ([], []))
        self.assertEqual(run("style.py", "review", stdin="", env=self.env, cwd=self.project).returncode, 0)
        self.assertEqual(run("style.py", "review", stdin="{", env=self.env, cwd=self.project).returncode, 2)
        p = run("style.py", "review", "--project", stdin=json.dumps(self.candidates("один")), env=self.env,
                cwd=self.project)
        r = json.loads(p.stdout.decode("utf-8"))
        self.assertEqual(r["writes_to"], os.path.join(os.path.realpath(self.project), ".writer", "style.md"))
        self.assertEqual(len(r["propose"]), 1)
        self.assertFalse(os.path.exists(self.home), "review must not write")
        self.assertFalse(os.path.exists(os.path.join(self.project, ".writer")))

    def test_decline_writes_declined_with_backup(self):
        r = style.decline("без подписи", "письма", date="2026-11-02")
        self.assertEqual(r["path"], os.path.join(self.home, "declined.md"))
        self.assertEqual(r["line"], "- [письма] без подписи (2026-11-02)")
        self.assertIsNone(r["backup"])
        r = style.decline("без эмодзи", "посты", date="2026-11-03")
        self.assertTrue(r["backup"].endswith("declined.md.bak"))
        self.assertFalse(os.path.exists(style.global_path()), "decline leaves style.md alone")
        self.assertEqual(style.effective(self.project)["summary"]["declined"], 2)
        self.assertEqual(style.review(self.candidates("Без подписи."))["dropped"][0]["reason"], "declined")
        with self.assertRaises(style._text.BadInput):
            style.decline("x", " ")

    def test_decline_project_flag_and_fallback(self):
        layer = os.path.join(self.tmp.name, "project", ".writer")
        self.write_layer(layer, "style.md", "- на «вы»\n")
        r = style.decline("без эмодзи", "посты", project=True, start=self.project)
        self.assertEqual((r["path"], r["layer"]), (os.path.join(layer, "declined.md"), "project"))
        self.assertFalse(os.path.exists(self.home))
        self.block_home()
        other = os.path.join(self.tmp.name, "other")
        os.makedirs(other)
        p = run("style.py", "decline", "--rule", "без подписи", "--when", "письма", env=self.env, cwd=other)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = json.loads(p.stdout.decode("utf-8"))
        self.assertEqual((r["layer"], r["fallback_from"]), ("project", style.global_path("declined.md")))
        self.assertEqual(r["path"], os.path.join(os.path.realpath(other), ".writer", "declined.md"))
        p = run("style.py", "decline", "--rule", "ещё", "--when", "письма", env=self.env, cwd=other)
        self.assertTrue(json.loads(p.stdout.decode("utf-8"))["backup"].endswith("declined.md.bak"))
        p = run("style.py", "review", stdin=json.dumps(self.candidates("без подписи")), env=self.env, cwd=other)
        self.assertEqual(json.loads(p.stdout.decode("utf-8"))["dropped"][0]["reason"], "declined")


class SaveVersionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.orig = os.path.join(self.tmp.name, "text.md")
        with open(self.orig, "w", encoding="utf-8") as fh:
            fh.write("original\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_next_paths(self):
        self.assertEqual(save_version.next_version(self.orig), (os.path.join(self.tmp.name, "text.v2.md"), 2))
        open(os.path.join(self.tmp.name, "text.v2.md"), "w").close()
        open(os.path.join(self.tmp.name, "text.v4.md"), "w").close()
        self.assertEqual(save_version.next_version(self.orig)[1], 5)
        self.assertEqual(save_version.next_version(os.path.join(self.tmp.name, "text.v2.md"))[1], 5)

    def test_cli_writes_new_file_and_keeps_original(self):
        p = run("save_version.py", self.orig)
        r = json.loads(p.stdout.decode("utf-8"))
        self.assertFalse(r["written"])
        self.assertFalse(os.path.exists(r["path"]))
        p = run("save_version.py", self.orig, "--content", "-", stdin="правка\n")
        self.assertEqual(p.returncode, 0, p.stderr)
        r = json.loads(p.stdout.decode("utf-8"))
        with open(r["path"], encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "правка\n")
        with open(self.orig, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "original\n")
        p = run("save_version.py", self.orig, "--content", "-", stdin="ещё\n")
        self.assertTrue(json.loads(p.stdout.decode("utf-8"))["path"].endswith("text.v3.md"))

    def test_bad_input(self):
        self.assertEqual(run("save_version.py", os.path.join(self.tmp.name, "none.md")).returncode, 2)
        self.assertEqual(run("save_version.py", self.orig, "--content", os.path.join(self.tmp.name, "x")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
