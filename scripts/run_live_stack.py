"""Run a temporary HTTPS/WSS tunnel and the local FastAPI service together."""

from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = PROJECT_ROOT / ".runtime"
PUBLIC_URL_FILE = RUNTIME_DIR / "public_base_url"
TUNNEL_URL = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


def _forward(stream, *, capture_url: list[str]) -> None:
    for raw_line in iter(stream.readline, ""):
        line = raw_line.rstrip()
        match = TUNNEL_URL.search(line)
        if match and not capture_url:
            candidate = match.group(0)
            if candidate != "https://api.trycloudflare.com" and "failed" not in line.lower():
                capture_url.append(candidate)
        print(f"[tunnel] {line}", flush=True)


def _terminate(process: subprocess.Popen[str] | None) -> None:
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> int:
    cloudflared = shutil.which("cloudflared")
    if not cloudflared:
        print("cloudflared is required but was not found on PATH.", file=sys.stderr)
        return 2

    tunnel: subprocess.Popen[str] | None = None
    server: subprocess.Popen[str] | None = None
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_URL_FILE.unlink(missing_ok=True)

    def stop(_signum=None, _frame=None) -> None:
        _terminate(server)
        _terminate(tunnel)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    try:
        tunnel = subprocess.Popen(
            [cloudflared, "tunnel", "--url", "http://127.0.0.1:8000", "--no-autoupdate"],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert tunnel.stdout is not None
        captured_url: list[str] = []
        reader = threading.Thread(
            target=_forward,
            args=(tunnel.stdout,),
            kwargs={"capture_url": captured_url},
            daemon=True,
        )
        reader.start()

        deadline = time.monotonic() + 30
        while not captured_url and time.monotonic() < deadline:
            if tunnel.poll() is not None:
                print("Tunnel exited before publishing a URL.", file=sys.stderr)
                return 3
            time.sleep(0.1)
        if not captured_url:
            print("Timed out waiting for a public tunnel URL.", file=sys.stderr)
            return 4

        public_url = captured_url[0]
        PUBLIC_URL_FILE.write_text(public_url + "\n", encoding="utf-8")
        os.chmod(PUBLIC_URL_FILE, 0o600)
        env = os.environ.copy()
        env["PUBLIC_BASE_URL"] = public_url
        print(f"\nLive callback URL: {public_url}", flush=True)
        print("Keep this process running while placing and receiving call callbacks.\n", flush=True)

        server = subprocess.Popen(
            [
                str(PROJECT_ROOT / ".venv" / "bin" / "uvicorn"),
                "pgai_voicebot.app:app",
                "--app-dir",
                "src",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=PROJECT_ROOT,
            env=env,
        )
        return server.wait()
    finally:
        stop()
        PUBLIC_URL_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
