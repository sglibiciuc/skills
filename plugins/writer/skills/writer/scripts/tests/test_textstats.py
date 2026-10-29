import json
import unittest

from tests.helpers import run
import textstats


class TextstatsTest(unittest.TestCase):
    def test_counts_cyrillic_and_latin(self):
        r = textstats.measure("  Привет, мир! Hello world.  \n")
        self.assertEqual(r["characters"], len("Привет, мир! Hello world."))
        self.assertEqual(r["characters_no_spaces"], len("Привет,мир!Helloworld."))
        self.assertEqual(r["words"], 4)
        self.assertEqual(r["limits"], {})

    def test_limits_report_distance_both_ways(self):
        r = textstats.measure("один два три четыре", max_chars=10, max_words=5)
        self.assertEqual(r["limits"]["characters"]["over_by"], len("один два три четыре") - 10)
        self.assertEqual(r["limits"]["words"]["over_by"], -1)

    def test_cli(self):
        p = run("textstats.py", "-", "--max-chars", "5", "--format", "text", stdin="Слово слово")
        self.assertEqual(p.returncode, 0, p.stderr)
        out = p.stdout.decode("utf-8")
        self.assertIn("characters: 11", out)
        self.assertIn("over by 6", out)
        p = run("textstats.py", "-", "--max-words", "3", stdin="раз два")
        self.assertEqual(json.loads(p.stdout.decode("utf-8"))["limits"]["words"]["over_by"], -1)

    def test_bad_input(self):
        self.assertEqual(run("textstats.py", "/no/such/file").returncode, 2)
        self.assertEqual(run("textstats.py", "-", "--max-chars", "0", stdin="x").returncode, 2)


if __name__ == "__main__":
    unittest.main()
