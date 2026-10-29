import unittest
import slop_scan
import _markdown

class ObservationTest(unittest.TestCase):
    def obs(self, text, lang="ru"):
        return slop_scan.scan(text, lang)["observations"]

    def test_code_offsets_and_real_trace(self):
        text = 'Документация: ' + chr(96) + '</think>' + chr(96) + '\n</think> Текст.'
        r = slop_scan.scan(text, "ru")
        found = [f for f in r["findings"] if f["id"] == "c-think-tag"]
        self.assertEqual([(f["line"],f["column"]) for f in found], [(2,1)])
        self.assertEqual(len(_markdown.mask_code(text)),len(text))
        self.assertIn("·",_markdown.mask_code(text))

    def test_fences_and_nested_inline(self):
        tick = chr(96)
        for text in (tick*3+'\n</think>\n'+tick*4, tick*2+'a'+tick+'</think>'+tick*2):
            self.assertNotIn("c-think-tag", {f["id"] for f in slop_scan.scan(text,"ru")["findings"]})
        self.assertIn("c-think-tag", {f["id"] for f in slop_scan.scan(tick*3+'\n</think>',"ru")["findings"]})

    def test_quotes_and_urls_stay_visible(self):
        r=slop_scan.scan('«Это не просто сервис. Это экосистема». https://x.ru/?utm_source=chatgpt.com',"ru")
        by={f["id"]:f for f in r["findings"]}
        self.assertEqual(by["ru-eto-ne-prosto"]["severity"],"soft")
        self.assertIn("c-utm-ai",by)

    def test_new_word_form(self):
        self.assertIn("ru-chatbot-closing",{f["id"] for f in slop_scan.scan("Надеюсь, это было полезно.","ru")["findings"]})

    def test_escaped_backtick_opener(self):
        for count in (1, 2, 3, 4):
            text = 'Знак ' + '\\' * count + chr(96) + ' </think> ' + chr(96) + ' конец.'
            found = {f['id'] for f in slop_scan.scan(text, 'ru')['findings']}
            self.assertEqual('c-think-tag' in found, bool(count % 2))

    def test_newline_boundary_and_rhythm_ignore(self):
        self.assertIn('obs-hedge-stack', {o['id'] for o in self.obs('Возможно, в некоторых случаях это, скорее всего, сработает\nНовый абзац.')})
        r = slop_scan.scan('Мы отправили документы вчера. ' * 8, 'ru', ['obs-rhythm'])
        self.assertNotIn('obs-rhythm', {o['id'] for o in r['observations']})

    def test_hedge_stack_not_single_uncertainty(self):
        self.assertIn("obs-hedge-stack",{o["id"] for o in self.obs("Возможно, в некоторых случаях это, скорее всего, сработает.")})
        self.assertNotIn("obs-hedge-stack",{o["id"] for o in self.obs("Возможно, поставщик ответит завтра.")})

    def test_repeats_bilingual(self):
        for lang,text in [
            ("ru","Мы сверяем адрес доставки перед отправкой заказа.\nМы сверяем адрес доставки перед отправкой заказа."),
            ("en","We check the delivery address before sending the order.\nWe check the delivery address before sending the order.")]:
            found=[o for o in self.obs(text,lang) if o["id"]=="obs-repeated-phrase"]
            self.assertTrue(found,lang)
            self.assertEqual([p["line"] for p in found[0]["places"]],[1,2])

    def test_cluster_not_isolated_term(self):
        self.assertNotIn("obs-en-vocab-cluster",{o["id"] for o in self.obs("The robust regression model handles outliers.","en")})
        self.assertIn("obs-en-vocab-cluster",{o["id"] for o in self.obs("Robust tools foster growth and enhance collaboration.","en")})

    def test_structure_not_required_triad(self):
        self.assertIn("obs-heading-echo",{o["id"] for o in self.obs("## Performance\nPerformance matters.","en")})
        self.assertFalse(self.obs("Три темы:\n1. Рынок\n2. Решения\n3. Планы","ru"))
        self.assertIn("obs-short-chain",{o["id"] for o in self.obs("Стоп. Вдох. Новый старт.","ru")})

    def test_hints_preserve_authority(self):
        for text,lang,ident,word in [
            ("Если нужно, могу подготовить версию договора.","ru","ru-offer-more","authorized"),
            ("Точность равна 0,123.","ru","ru-number-format","decimal"),
            ("Approximately 12 people attended.","en","en-approx-number","uncertainty")]:
            found=[f for f in slop_scan.scan(text,lang)["findings"] if f["id"]==ident]
            self.assertTrue(found)
            self.assertEqual(found[0]["severity"],"soft")
            self.assertIn(word,found[0]["hint"])

    def test_observations_separate_ignore_and_no_verdict(self):
        r=slop_scan.scan("Отчёт демонстрирует различия.","ru")
        self.assertTrue(r["observations"])
        self.assertEqual(r["findings"],[])
        self.assertNotIn("score",r)
        self.assertFalse(slop_scan.scan("Отчёт демонстрирует различия.","ru",["obs-ru-evidence"])["observations"])
