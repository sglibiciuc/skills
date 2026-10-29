import json
import os
import unittest

from tests.helpers import fixture, read_fixture, run
import slop_scan
import _text

REQUIRED = {"id", "category", "severity", "hint", "example_bad"}


def catalog(name):
    return _text.load_json(os.path.join(slop_scan.SLOP_DIR, name + ".json"))["patterns"]


class CatalogTest(unittest.TestCase):
    def test_schema_counts_and_self_match(self):
        minimum = {"common": 10, "ru": 40, "en": 40}
        seen = set()
        for name, low in minimum.items():
            pats = catalog(name)
            self.assertGreaterEqual(len(pats), low, name)
            for p in pats:
                self.assertTrue(REQUIRED <= set(p), p.get("id"))
                self.assertIn(p["severity"], ("hard", "soft"))
                self.assertTrue(("regex" in p) != ("words" in p), p["id"])
                self.assertNotIn(p["id"], seen)
                seen.add(p["id"])
                if "regex" in p:
                    self.assertNotIn(r"\b", p["regex"], "use explicit boundaries: " + p["id"])
                rx = slop_scan.compile_pattern(p)
                self.assertTrue(rx.search(p["example_bad"]), "example does not trigger " + p["id"])

    def test_no_source_field(self):
        for name in ("common", "ru", "en"):
            for p in catalog(name):
                self.assertNotIn("source", p, p["id"])

    def test_hard_is_rare(self):
        for name in ("common", "ru", "en"):
            pats = catalog(name)
            hard = [p for p in pats if p["severity"] == "hard"]
            self.assertLess(len(hard), len(pats) / 3.0, name)


class ScanTest(unittest.TestCase):
    def test_service_offer_coverage_for_author_commitments(self):
        examples = [
            ("I'm happy to help you work through this.", "en", "en-offer-help"),
            ("I’m happy to help. Let me know a few times that work for you.", "en", "en-offer-help"),
            ("If you still need help, we can arrange a quick session.", "en", "en-offer-help"),
            ("We can set up a short call.", "en", "en-offer-help"),
            ("Я готов помочь с настройками.", "ru", "ru-offer-help"),
            ("Созвонимся в четверг.", "ru", "ru-offer-help"),
            ("Можем созвониться и посмотреть настройки.", "ru", "ru-offer-help"),
        ]
        for text, lang, ident in examples:
            findings = [f for f in slop_scan.scan(text, lang)["findings"] if f["id"] == ident]
            self.assertTrue(findings, text)
            self.assertTrue(all(f["severity"] == "soft" for f in findings))
            self.assertTrue(all("authorized offer can stay" in f["hint"] for f in findings))

    def test_service_offer_negation_and_reported_request(self):
        examples = [("Я не готов помочь с настройками.", "ru", "ru-offer-help"),
                    ("Не можем созвониться.", "ru", "ru-offer-help"),
                    ("I'm not available to help.", "en", "en-offer-help"),
                    ("The team asked for a call.", "en", "en-offer-help")]
        for text, lang, ident in examples:
            self.assertNotIn(ident, {f["id"] for f in slop_scan.scan(text, lang)["findings"]}, text)

    def test_todo_marker_catches_both_gap_markers(self):
        for text, lang, pid in (("Запуск [нужно: дата запуска].", "ru", "ru-todo-marker"),
                                ("Launch is on [needed: launch date].", "en", "c-todo-marker"),
                                ("Start am [needed: Datum des Starts].", "de", "c-todo-marker")):
            ids = {f["id"] for f in slop_scan.scan(text, lang=lang)["findings"]}
            self.assertIn(pid, ids, text)

    def test_common_catalog_has_no_cyrillic(self):
        with open(os.path.join(slop_scan.SLOP_DIR, "common.json"), encoding="utf-8") as fh:
            self.assertIsNone(_text.CYR_RE.search(fh.read()))

    def test_russian_parts_of_common_patterns_live_in_ru(self):
        cases = (("С уважением, [Ваше имя]", "ru-placeholder"), ("Здравствуйте, {имя}!", "ru-merge-field"),
                 ("Отправлено с моего iPhone", "ru-mail-clutter"), ("Смотрите [здесь](https://x.ru).", "ru-link-anchor"),
                 ("Быстро, надёжно и инновационно.", "ru-triple-list"))
        for text, pid in cases:
            self.assertIn(pid, {f["id"] for f in slop_scan.scan(text, lang="ru")["findings"]}, text)
            self.assertEqual(slop_scan.scan(text, lang="de")["findings"], [], text)

    def test_en_intensifier(self):
        ids = {f["id"] for f in slop_scan.scan("This is a really important step.", lang="en")["findings"]}
        self.assertIn("en-intensifier", ids)
        ids = {f["id"] for f in slop_scan.scan("Everybody reads it.", lang="en")["findings"]}
        self.assertNotIn("en-intensifier", ids)

    def test_no_score_in_output(self):
        r = slop_scan.scan("It is really good. " + "Plain words here. " * 33, lang="en")
        self.assertNotIn("density", r["summary"])
        self.assertTrue(all(f["hint"] for f in r["findings"]))

    def test_clean_texts_have_no_findings(self):
        for f in ("ru_clean.md", "en_clean.md"):
            r = slop_scan.scan(read_fixture(f))
            self.assertEqual(r["summary"]["findings"], 0, (f, r["findings"]))

    def test_ru_slop(self):
        r = slop_scan.scan(read_fixture("ru_slop.md"))
        ids = {f["id"] for f in r["findings"]}
        self.assertEqual(r["language"], "ru")
        for i in ("ru-ne-prosto-a", "ru-sovremennyi-mir", "ru-vazhno-otmetit", "ru-weasel",
                  "ru-klyuchevaya-rol", "ru-podvodya-itog", "ru-chatbot-closing"):
            self.assertIn(i, ids)
        # A contrast can be intentional; only the explicit chat residue here is hard.
        self.assertEqual(next(f for f in r["findings"] if f["id"] == "ru-chatbot-closing")["severity"], "hard")

    def test_en_slop_and_positions(self):
        r = slop_scan.scan(read_fixture("en_slop.md"))
        by_id = {f["id"]: f for f in r["findings"]}
        for i in ("en-todays-world", "en-not-just-its", "en-chatbot-residue", "en-title-case-heading", "en-pivotal-role"):
            self.assertIn(i, by_id)
        self.assertEqual((by_id["en-todays-world"]["line"], by_id["en-todays-world"]["column"]), (3, 1))
        self.assertEqual(by_id["en-chatbot-residue"]["severity"], "hard")

    def test_cyrillic_boundaries(self):
        # «данные» (data) must not hit the «данный» (this) rule; «оченьь» is not «очень»
        r = slop_scan.scan("Данные за квартал готовы. Оченьважно.", lang="ru")
        ids = {f["id"] for f in r["findings"]}
        self.assertNotIn("ru-dannyi", ids)
        self.assertNotIn("ru-usiliteli", ids)
        r = slop_scan.scan("Данный отчёт очень длинный.", lang="ru")
        ids = {f["id"] for f in r["findings"]}
        self.assertIn("ru-dannyi", ids)
        self.assertIn("ru-usiliteli", ids)

    def test_ignore(self):
        r = slop_scan.scan(read_fixture("ru_slop.md"), ignore=["ru-ne-prosto-a", "ru-weasel"])
        ids = {f["id"] for f in r["findings"]}
        self.assertNotIn("ru-ne-prosto-a", ids)
        self.assertNotIn("ru-weasel", ids)
        self.assertEqual(r["ignored"], ["ru-ne-prosto-a", "ru-weasel"])

    def test_unknown_language_uses_common_only(self):
        r = slop_scan.scan("Wir liefern — schnell — günstig — und sicher. Mehr unter https://x.de/?utm_source=chatgpt.com", lang="de")
        self.assertEqual(r["catalogs"], ["slop/common.json"])
        self.assertIsNotNone(r["note"])
        ids = {f["id"] for f in r["findings"]}
        self.assertIn("c-utm-ai", ids)
        self.assertIn("c-emdash-cluster", ids)

    def test_summary_by_category(self):
        r = slop_scan.scan(read_fixture("en_slop.md"))
        total = sum(c["hard"] + c["soft"] for c in r["summary"]["by_category"].values())
        self.assertEqual(total, r["summary"]["findings"])


class CliTest(unittest.TestCase):
    def test_cli_json_text_and_never_rewrites(self):
        before = read_fixture("ru_slop.md")
        p = run("slop_scan.py", fixture("ru_slop.md"))
        self.assertEqual(p.returncode, 0)
        self.assertIn("findings", json.loads(p.stdout.decode("utf-8")))
        p = run("slop_scan.py", "-", "--format", "text", "--lang", "en", stdin="I hope this helps!")
        self.assertEqual(p.returncode, 0)
        self.assertIn("en-chatbot-residue", p.stdout.decode("utf-8"))
        self.assertEqual(read_fixture("ru_slop.md"), before)

    def test_bad_input(self):
        self.assertEqual(run("slop_scan.py", fixture("missing.md")).returncode, 2)
        self.assertEqual(run("slop_scan.py", fixture("ru_slop.md"), "--lang", "русский").returncode, 2)


if __name__ == "__main__":
    unittest.main()


class HumanizerPatternsTest(unittest.TestCase):
    """Patterns added with the humanizer: each catches its form and leaves ordinary sentences alone."""

    def ids(self, text, lang):
        return {f["id"] for f in slop_scan.scan(text, lang=lang)["findings"]}

    def test_catches(self):
        cases = (("Revenue grew 12% [cite: 4] last year.", "en", "c-chat-citation-token"),
                 ("Пpивет, коллеги.", "ru", "ru-latin-homoglyph"),
                 ("Если нужно, могу подготовить версию для сайта.", "ru", "ru-offer-more"),
                 ("В связи с этим мы меняем график.", "ru", "ru-v-svyazi-s-etim"),
                 ("Отчёт без воды, без догадок, без пафоса.", "ru", "ru-tail-negations"),
                 ("Want me to add a section on pricing?", "en", "en-chatbot-offer"),
                 ("A full report, no guesswork, no surprises, no fees.", "en", "en-tail-negations"),
                 ("That distinction matters.", "en", "en-interpretive-aside"))
        for text, lang, pid in cases:
            self.assertIn(pid, self.ids(text, lang), text)

    def test_leaves_ordinary_sentences(self):
        cases = (("Цена 12 400 рублей.", "ru", "c-invisible-char"),
                 ("В связи с этим письмом прошу продлить договор.", "ru", "ru-v-svyazi-s-etim"),
                 ("Чай без сахара, без молока.", "ru", "ru-tail-negations"),
                 ("Меня вдохновляет эта работа.", "ru", "ru-model-handwriting"),
                 ("Это может повлиять на сроки.", "ru", "ru-modal-fog"),
                 ("Tea, no sugar, no milk.", "en", "en-tail-negations"),
                 ("That detail matters for the auditor because the totals differ.", "en", "en-interpretive-aside"),
                 ("The source code is not publicly available.", "en", "en-profile-filler"),
                 ("Great! See you Monday.", "en", "en-chatbot-residue"))
        for text, lang, pid in cases:
            self.assertNotIn(pid, self.ids(text, lang), text)
