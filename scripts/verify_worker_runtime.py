"""Validate the worker on Python 3.11 without credentials or external connections."""

import contextlib
import importlib.metadata
import io
import ipaddress
import json
import os
from pathlib import Path
import platform
import socket
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def block_external_connections():
    # Windows asyncio needs a loopback socket pair. Only that traffic is allowed.
    def local(address):
        if not isinstance(address, tuple):
            return False
        try:
            return ipaddress.ip_address(address[0]).is_loopback
        except ValueError:
            return address[0] == "localhost"

    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex
    original_sendto = socket.socket.sendto
    original_lookup = socket.getaddrinfo

    def connect(sock, address):
        if not local(address):
            raise AssertionError("External connection forbidden during runtime validation")
        return original_connect(sock, address)

    def connect_ex(sock, address):
        if not local(address):
            raise AssertionError("External connection forbidden during runtime validation")
        return original_connect_ex(sock, address)

    def sendto(sock, *args):
        if not args or not local(args[-1]):
            raise AssertionError("External datagram forbidden during runtime validation")
        return original_sendto(sock, *args)

    def lookup(host, *args, **kwargs):
        if not local((host, 0)):
            raise AssertionError("External DNS lookup forbidden during runtime validation")
        return original_lookup(host, *args, **kwargs)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.socket.sendto = sendto
    socket.getaddrinfo = lookup


def main():
    if sys.version_info[:2] != (3, 11):
        raise SystemExit("Run this verification with Python 3.11")
    output_dir = ROOT / ".git" / "python311-validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    for key in list(os.environ):
        if any(token in key.upper() for token in ("GMAIL", "GROQ", "MONGODB", "GOOGLE_APPLICATION_CREDENTIALS", "GFMD_SPECTRUM", "GFMD_EMAIL")):
            os.environ.pop(key, None)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    sys.path.insert(0, str(ROOT))
    block_external_connections()
    captured = io.StringIO()
    results = {}
    original_directory = Path.cwd()
    try:
        with tempfile.TemporaryDirectory(prefix="gfmd-runtime-offline-") as scratch:
            try:
                os.chdir(scratch)
                with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
                    for group in ("offline", "runtime"):
                        suite = unittest.TestLoader().discover(str(ROOT / "tests" / group))
                        result = unittest.TextTestRunner(stream=captured, verbosity=2).run(suite)
                        results[group] = {"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors)}
            finally:
                os.chdir(original_directory)
    finally:
        os.chdir(original_directory)
    (output_dir / "test-results.txt").write_text(captured.getvalue(), encoding="utf-8")
    summary = {
        "python": sys.version, "platform": platform.platform(), "suites": results,
        "external_network_blocked": True, "credentials_removed": True, "temporary_working_directory": True,
        "database": "mongomock in-memory database", "gmail": "local MIME recorder; no Gmail API connection",
        "versions": {name: importlib.metadata.version(name) for name in ("pymongo", "groq", "google-api-python-client", "numpy", "sentence-transformers", "mongomock")},
    }
    (output_dir / "runtime-verification.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if any(value["failures"] or value["errors"] for value in results.values()):
        print(captured.getvalue())
        raise SystemExit(1)


if __name__ == "__main__":
    main()
