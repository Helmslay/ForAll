import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from check_stac import Provider, check_provider, main


class Handler(BaseHTTPRequestHandler):
    mode = "ok"

    def do_GET(self):
        if self.path.endswith("/collections"):
            if self.mode == "timeout":
                import time
                time.sleep(0.25)
            body = b"{invalid" if self.mode == "invalid" else json.dumps({"collections": []}).encode()
        else:
            body = b"{invalid" if self.mode == "invalid" else json.dumps({"stac_version": "1.0.0", "links": []}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            pass

    def log_message(self, *_args):
        pass


class StacCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.provider = Provider("mock", f"http://127.0.0.1:{cls.server.server_port}/v1/", "127.0.0.1")

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=1)

    def network_ok(self, _host, _timeout):
        return {"dns": "PASS", "tcp": "PASS", "tls": "PASS"}

    def test_http_200_root_and_collections(self):
        Handler.mode = "ok"
        report = check_provider(self.provider, network_probe=self.network_ok)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["root"], "PASS")
        self.assertEqual(report["collections"], "PASS")

    def test_timeout(self):
        Handler.mode = "timeout"
        report = check_provider(self.provider, timeout=0.05, network_probe=self.network_ok)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["error_stage"], "HTTP")

    def test_dns_error(self):
        report = check_provider(
            self.provider,
            network_probe=lambda _host, _timeout: {"dns": "FAIL", "tcp": "UNKNOWN", "tls": "UNKNOWN", "error_class": "DNSResolutionError"},
        )
        self.assertEqual(report["error_class"], "DNSResolutionError")
        self.assertEqual(report["root"], "UNKNOWN")

    def test_tls_error(self):
        report = check_provider(
            self.provider,
            network_probe=lambda _host, _timeout: {"dns": "PASS", "tcp": "PASS", "tls": "FAIL", "error_class": "SSLError"},
        )
        self.assertEqual(report["error_class"], "SSLError")
        self.assertEqual(report["root"], "UNKNOWN")

    def test_invalid_json(self):
        Handler.mode = "invalid"
        report = check_provider(self.provider, network_probe=self.network_ok)
        self.assertEqual(report["error_stage"], "JSON")
        self.assertEqual(report["error_class"], "InvalidJSON")

    def test_cli_exit_code_success_and_failure(self):
        with patch("check_stac.check_provider", return_value={"status": "PASS"}):
            with redirect_stdout(StringIO()):
                self.assertEqual(main(["--provider", "cdse"]), 0)
        with patch("check_stac.check_provider", return_value={"status": "FAIL"}):
            with redirect_stdout(StringIO()):
                self.assertEqual(main(["--provider", "cdse"]), 1)

    def test_cli_rejects_unknown_provider(self):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as raised:
                main(["--provider", "unknown-provider"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
