import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.helpers import SCRIPTS, run
import draft

HOOK = Path(SCRIPTS).parents[2] / "hooks/hook.py"
spec = importlib.util.spec_from_file_location("writer_hook", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class DraftHooksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.cwd = Path.cwd()
        self.env = patch.dict(os.environ, {"WRITER_DRAFT_ROOT": str(self.base / "private"),
                                           "WRITER_SESSION_ID": "one"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def event(self, kind, receipt=None, sid="one", cwd=None):
        data = {"hook_event_name": kind, "session_id": sid, "cwd": str(cwd or self.cwd)}
        if receipt:
            data["tool_response"] = {"stdout": json.dumps(receipt)}
            data["tool_input"] = {"command": "python3 /plugin/scripts/draft.py put --text -"}
        return hook.process(data)

    def test_post_tool_analyzes_before_accept(self):
        staged = draft.stage("Пришлите файл до пятницы.")
        with self.assertRaises(OSError):
            draft.accept(staged["id"], staged["revision"], {})
        feedback = self.event("PostToolUse", staged)
        self.assertIn(staged["revision"], feedback["hookSpecificOutput"]["additionalContext"])
        report = draft.analyze(staged["id"])
        keep = {key: "Needed in this context" for key in report["finding_keys"]}
        text = draft.accept(staged["id"], staged["revision"], keep)
        self.assertEqual(text, "Пришлите файл до пятницы.")
        self.assertIsNone(self.event("Stop"))

    def test_stale_accept_rejected_after_direct_edit(self):
        staged = draft.stage("Отправьте файл.")
        self.event("PostToolUse", staged)
        draft.accept(staged["id"], staged["revision"], {})
        path = draft.directory(staged["id"])
        (path / "text.txt").write_text("Отправьте другой файл.")
        with self.assertRaises(draft.DraftError):
            draft.accepted(staged["id"])
        self.assertIn("additionalContext", self.event("PostToolUse")["hookSpecificOutput"])
        self.assertEqual(self.event("Stop")["decision"], "block")

    def test_update_keeps_limits_and_invalidates_old_analysis(self):
        staged = draft.stage("Файл.", max_chars=10)
        draft.analyze(staged["id"])
        changed = draft.stage("Слишком длинный текст.", staged["id"])
        with self.assertRaises(draft.DraftError):
            draft.accept(staged["id"], staged["revision"], {})
        report = draft.analyze(staged["id"])
        self.assertNotEqual(changed["revision"], staged["revision"])
        self.assertEqual(report["exceeded_limits"][0]["maximum"], 10)
        with self.assertRaises(draft.DraftError):
            draft.accept(staged["id"], changed["revision"], {})

    def test_findings_can_be_kept_with_reasons_without_zero_score(self):
        staged = draft.stage("Уважаемые коллеги! В современном мире мы раскрываем невероятный потенциал.")
        report = draft.analyze(staged["id"])
        self.assertTrue(report["finding_keys"])
        with self.assertRaises(draft.DraftError):
            draft.accept(staged["id"], staged["revision"], {})
        with self.assertRaises(draft.DraftError):
            draft.accept(staged["id"], staged["revision"], {k: "" for k in report["finding_keys"]})
        text = draft.accept(staged["id"], staged["revision"], {k: "Quoted wording is required" for k in report["finding_keys"]})
        self.assertIn("невероятный", text)

    def test_authorized_help_can_still_be_accepted(self):
        staged = draft.stage("I'm happy to help. We can arrange a quick session.")
        report = draft.analyze(staged["id"])
        self.assertTrue(report["finding_keys"])
        decisions = {key: "The person explicitly authorized help and a session" for key in report["finding_keys"]}
        self.assertEqual(draft.accept(staged["id"], staged["revision"], decisions),
                         "I'm happy to help. We can arrange a quick session.")

    def test_source_must_be_analyzed_before_rewrite(self):
        source = draft.stage("В апреле пройдут 3 встречи по 40 минут.", kind="source")
        with self.assertRaises(OSError):
            draft.stage("В апреле — 3 встречи по 40 минут.", source["id"])
        self.event("PostToolUse", source)
        changed = draft.stage("В апреле — 3 встречи по 40 минут.", source["id"])
        report = draft.analyze(source["id"])
        self.assertIn("source_sha256", report)
        draft.accept(source["id"], changed["revision"], {})

    def test_source_change_invalidates_revision(self):
        staged = draft.stage("3 встречи.", source="3 встречи.")
        draft.analyze(staged["id"])
        path = draft.directory(staged["id"])
        (path / "source.txt").write_text("4 встречи.")
        with self.assertRaises(draft.DraftError):
            draft.accept(staged["id"], staged["revision"], {})

    def test_failed_scan_creates_no_success_receipt(self):
        staged = draft.stage("Пришлите файл.")
        with patch.object(draft.slop_scan, "scan", side_effect=ValueError("catalog broken")):
            with self.assertRaises(ValueError):
                draft.analyze(staged["id"])
        self.assertFalse((draft.directory(staged["id"]) / "analysis.json").exists())
        with self.assertRaises(OSError):
            draft.accept(staged["id"], staged["revision"], {})

    def test_other_session_and_other_cwd_are_not_touched(self):
        staged = draft.stage("Пришлите файл.")
        self.event("PostToolUse", staged)
        self.assertIsNone(self.event("Stop", sid="two"))
        with self.assertRaises(draft.DraftError):
            self.event("PostToolUse", staged, cwd=self.base)
        self.assertTrue(draft.directory(staged["id"]).is_dir())

    def test_new_prompt_releases_previous_active_draft(self):
        staged = draft.stage("Пришлите файл.")
        self.event("PostToolUse", staged)
        self.assertEqual(self.event("Stop")["decision"], "block")
        self.event("UserPromptSubmit")
        self.assertIsNone(self.event("Stop"))

    def test_session_end_removes_only_its_private_drafts(self):
        first = draft.stage("Первый текст.")
        second = draft.stage("Другой текст.", owner="two")
        self.event("PostToolUse", first)
        self.event("PostToolUse", second, sid="two")
        self.event("SessionEnd")
        self.assertFalse((draft.root() / first["id"]).exists())
        self.assertTrue(draft.directory(second["id"]).exists())

    def test_symlink_draft_is_rejected(self):
        staged = draft.stage("Пришлите файл.")
        path = draft.directory(staged["id"]) / "text.txt"
        path.unlink()
        path.symlink_to(self.base / "unrelated")
        with self.assertRaises(draft.DraftError):
            draft.analyze(staged["id"])

    def test_standalone_cli_runs_same_analysis(self):
        proc = run("draft.py", "put", "--standalone", stdin="Пришлите файл.")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        staged = json.loads(proc.stdout)
        self.assertEqual(staged["analysis"]["revision"], staged["revision"])
        accepted = run("draft.py", "accept", staged["id"], "--revision", staged["revision"])
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual(accepted.stdout.decode(), "Пришлите файл.")

    def test_hook_wire_shapes_both_hosts(self):
        staged = draft.stage("Пришлите файл.", owner="wire")
        for response in ({"stdout": json.dumps(staged)}, json.dumps(staged),
                         {"output": "exit 0\n" + json.dumps(staged)}):
            feedback = hook.process({"session_id": "wire", "cwd": str(self.cwd),
                                     "tool_input": {"command": "python3 draft.py put --text -"},
                                     "hook_event_name": "PostToolUse", "tool_response": response})
            self.assertEqual(feedback["hookSpecificOutput"]["hookEventName"], "PostToolUse")

    def test_negative_limit_is_rejected(self):
        with self.assertRaises(draft.DraftError):
            draft.stage("Файл.", max_chars=-1)

    def test_reading_foreign_receipt_does_not_claim_or_remove_draft(self):
        staged = draft.stage("Private text from another session.", owner="owner")
        self.event("PostToolUse", staged, sid="owner")
        result = hook.process({"session_id": "reader", "cwd": str(self.cwd),
                               "hook_event_name": "PostToolUse",
                               "tool_input": {"command": "cat old-log.json"},
                               "tool_response": json.dumps(staged)})
        self.assertIsNone(result)
        self.event("SessionEnd", sid="reader")
        self.assertTrue(draft.directory(staged["id"]).exists())
        self.assertIsNone(self.event("PostToolUse", staged, sid="reader"))

    def test_standalone_log_is_not_claimed_even_with_staging_words(self):
        staged = draft.stage("Private standalone text.", owner="standalone")
        result = hook.process({"session_id": "reader", "cwd": str(self.cwd),
                               "hook_event_name": "PostToolUse",
                               "tool_input": {"command": 'rg -A5 "draft.py put" run.log'},
                               "tool_response": json.dumps(staged)})
        self.assertIsNone(result)
        self.event("SessionEnd", sid="reader")
        self.assertTrue(draft.directory(staged["id"]).exists())

    def test_every_draft_in_a_set_needs_acceptance(self):
        first = draft.stage("First subject", max_chars=40)
        second = draft.stage("Second subject", max_chars=40)
        self.event("PostToolUse", first)
        self.event("PostToolUse", second)
        draft.accept(second["id"], second["revision"], {})
        self.assertEqual(self.event("Stop")["decision"], "block")
        draft.accept(first["id"], first["revision"], {})
        self.assertIsNone(self.event("Stop"))


if __name__ == "__main__":
    unittest.main()
