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
