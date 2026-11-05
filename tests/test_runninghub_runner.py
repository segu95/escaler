import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "runner", Path(__file__).parents[1] / "tools" / "test_runninghub.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class FakeAPI:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def post(self, path, value):
        self.calls.append((path, value))
        return next(self.responses)


class RunnerTests(unittest.TestCase):
    def test_presets_map_to_known_nodes(self):
        for quality, scale in (("4k", "4"), ("6k", "6"), ("8k", "8")):
            body = runner.payload("uploaded.png", quality)
            nodes = {n["nodeId"]: n for n in body["nodeInfoList"]}
            self.assertEqual(nodes["142"]["fieldValue"], scale)
            self.assertEqual(nodes["172"]["fieldValue"], "always")
            self.assertEqual(nodes["123"]["fieldValue"], "uploaded.png")

    def test_resume_only_queries_existing_task(self):
        api = FakeAPI([{"taskId": "42", "status": "RUNNING"},
                       {"taskId": "42", "status": "SUCCESS", "results": []}])
        with tempfile.TemporaryDirectory() as directory:
            response = runner.wait_for_result(api, "42", Path(directory), pause=lambda _: None)
            self.assertEqual(response["status"], "SUCCESS")
            saved = json.loads((Path(directory) / "provider-response.private.json").read_text())
            self.assertEqual(saved["status"], "SUCCESS")
        self.assertEqual(api.calls, [("/query", {"taskId": "42"})] * 2)

    def test_other_task_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                runner.wait_for_result(FakeAPI([{"taskId": "other", "status": "SUCCESS"}]),
                                       "42", Path(directory))

    def test_failure_is_terminal(self):
        api = FakeAPI([{"taskId": "42", "status": "FAILED"}])
        with tempfile.TemporaryDirectory() as directory:
            result = runner.wait_for_result(api, "42", Path(directory))
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(len(api.calls), 1)

    def test_headers_without_pixel_allocation(self):
        png = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 8192, 6144)
        jpeg = b"\xff\xd8\xff\xe1\x00\x04xx\xff\xc0\x00\x11\x08" + struct.pack(">HH", 3072, 4096)
        webp = b"RIFF" + bytes(4) + b"WEBPVP8X" + bytes(8) + (4095).to_bytes(3, "little") + (2047).to_bytes(3, "little")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "header"
            for data, expected in [(png, (8192, 6144)), (jpeg, (4096, 3072)), (webp, (4096, 2048))]:
                path.write_bytes(data)
                self.assertEqual(runner.dimensions(path), expected)
            path.write_bytes(b"not an image")
            self.assertIsNone(runner.dimensions(path))

    def test_unknown_submit_response_not_retried(self):
        api = runner.API("test-key")
        with patch.object(api.opener, "open", side_effect=TimeoutError) as request:
            with self.assertRaises(RuntimeError):
                api.post("/run/workflow/42", {})
            self.assertEqual(request.call_count, 1)

    def test_authentication_redirect_blocked(self):
        with self.assertRaises(RuntimeError):
            runner.NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.example")


if __name__ == "__main__":
    unittest.main()
