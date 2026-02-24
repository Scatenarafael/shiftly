#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/shiftly_test"
PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "src" / "logs"
DEFAULT_LOG_FILE = LOG_DIR / "tests.log"
DEFAULT_PYTEST_ARGS = ["-vv", "-ra"]


def _build_env(test_database_url: str) -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("TEST_DATABASE_URL", test_database_url)

    current_pythonpath = env.get("PYTHONPATH")
    root_path = str(PROJECT_ROOT)
    if not current_pythonpath:
        env["PYTHONPATH"] = root_path
    elif root_path not in current_pythonpath.split(":"):
        env["PYTHONPATH"] = f"{root_path}:{current_pythonpath}"

    return env


def _run_pytest(pytest_args: list[str], env: dict[str, str], log_file: Path) -> int:
    command = [sys.executable, "-m", "pytest", *pytest_args]
    command_line = " ".join(command)

    log_file.parent.mkdir(parents=True, exist_ok=True)
    start_utc = datetime.now(timezone.utc).isoformat()

    print("Running:", command_line)
    print(f"Test log: {log_file}")

    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(f"\n=== Test Run Start (UTC): {start_utc} ===\n")
        fh.write(f"Command: {command_line}\n")
        fh.flush()

        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        try:
            assert process.stdout is not None
            for line in process.stdout:
                sys.stdout.write(line)
                fh.write(line)
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            process.wait()
            fh.write("Execution interrupted by user.\n")
            return 130
        finally:
            end_utc = datetime.now(timezone.utc).isoformat()
            fh.write(f"=== Test Run End (UTC): {end_utc} | Exit code: {process.returncode} ===\n")
            fh.flush()

    return int(process.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full application test suite.")
    parser.add_argument(
        "--db-url",
        default=DEFAULT_TEST_DATABASE_URL,
        help="Test database URL (default: local docker postgres on port 5433).",
    )
    parser.add_argument(
        "--log-file",
        default=str(DEFAULT_LOG_FILE),
        help=f"Path to test execution log file (default: {DEFAULT_LOG_FILE}).",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Additional pytest args. Example: -- -k users -x",
    )
    args = parser.parse_args()

    pytest_args = args.pytest_args or DEFAULT_PYTEST_ARGS
    env = _build_env(args.db_url)
    return _run_pytest(pytest_args, env, Path(args.log_file))


if __name__ == "__main__":
    raise SystemExit(main())
