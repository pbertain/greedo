import os
import unittest
from datetime import datetime, timezone

import holonet_stamp
from holonet_stamp import build_payload, render_one_line


class DummyArgs:
    # minimal shim for _final_request_id tests
    def __init__(
        self,
        json=False,
        quiet=False,
        one_line=False,
        request_id=None,
        request_id_mode="uuid",
        rid_prefix=None,
    ):
        self.json = json
        self.quiet = quiet
        self.one_line = one_line
        self.request_id = request_id
        self.request_id_mode = request_id_mode
        self.rid_prefix = rid_prefix


class TestHolonetStamp(unittest.TestCase):
    def test_payload_fact_always_present(self):
        fixed = datetime(2025, 12, 31, 22, 18, 23, tzinfo=timezone.utc)
        payload = build_payload(
            now_utc=fixed,
            tz_name="America/Los_Angeles",
            include_sw=False,
            epoch_mode="current",
            request_id="web-req-1",
        )
        self.assertEqual(payload["fact"], "Han shot first.")
        self.assertEqual(payload["request_id"], "web-req-1")
        self.assertEqual(payload["x_request_id"], "web-req-1")

    def test_one_line_contains_rid_and_fact(self):
        fixed = datetime(2025, 12, 31, 22, 18, 23, tzinfo=timezone.utc)
        payload = build_payload(
            now_utc=fixed,
            tz_name="America/Los_Angeles",
            include_sw=True,
            epoch_mode="current",
            request_id="api-123",
        )
        line = render_one_line(payload)
        self.assertIn("rid=api-123", line)
        self.assertIn('fact="Han shot first."', line)
        self.assertIn("swet=", line)
        self.assertIn('cgt="CGT', line)

    def test_sw_block_only_when_enabled(self):
        fixed = datetime(2025, 12, 31, 22, 18, 23, tzinfo=timezone.utc)
        p1 = build_payload(fixed, "America/Los_Angeles", include_sw=False, epoch_mode="current", request_id="x")
        p2 = build_payload(fixed, "America/Los_Angeles", include_sw=True, epoch_mode="current", request_id="x")
        self.assertNotIn("sw", p1)
        self.assertIn("sw", p2)

    def test_auto_prefix_api_when_json(self):
        args = DummyArgs(json=True, quiet=False, one_line=False, request_id=None, rid_prefix=None)
        rid = holonet_stamp._final_request_id(args)
        self.assertTrue(rid.startswith("api-"))

    def test_auto_prefix_curl_when_one_line(self):
        args = DummyArgs(json=False, quiet=False, one_line=True, request_id=None, rid_prefix=None)
        rid = holonet_stamp._final_request_id(args)
        self.assertTrue(rid.startswith("curl-"))

    def test_auto_prefix_web_for_pretty(self):
        args = DummyArgs(json=False, quiet=False, one_line=False, request_id=None, rid_prefix=None)
        rid = holonet_stamp._final_request_id(args)
        self.assertTrue(rid.startswith("web-"))

    def test_inbound_x_request_id_env_used(self):
        old = os.environ.get("HTTP_X_REQUEST_ID")
        try:
            os.environ["HTTP_X_REQUEST_ID"] = "curl-abc"
            args = DummyArgs(json=False, quiet=True, one_line=True, request_id=None, rid_prefix=None)
            rid = holonet_stamp._final_request_id(args)
            # if already prefixed, should keep it (and not double-prefix)
            self.assertEqual(rid, "curl-abc")
        finally:
            if old is None:
                os.environ.pop("HTTP_X_REQUEST_ID", None)
            else:
                os.environ["HTTP_X_REQUEST_ID"] = old

    def test_cli_request_id_gets_prefixed_if_missing_prefix(self):
        args = DummyArgs(json=True, request_id="123", rid_prefix="api-")
        rid = holonet_stamp._final_request_id(args)
        self.assertEqual(rid, "api-123")


if __name__ == "__main__":
    unittest.main(verbosity=2)

