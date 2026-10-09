"""Rerun source/static validation and record actual commands and exit codes."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--fresh", action="store_true", help="Read Excel again rather than the SHA256-keyed local cache")
args = parser.parse_args()
steps = [
    [sys.executable, "scripts/reconcile.py"] + (["--fresh"] if args.fresh else []),
    [sys.executable, "scripts/crosscheck_xml.py"],
    ["dotnet", "run", "--no-restore", "--project", "scripts/tmdl-check/TmdlCheck.csproj", "--", "powerbi/project/uk-online-retail-sales-analysis.SemanticModel/definition", "evidence/validation/final-tom.json"],
    [sys.executable, "scripts/validate_model.py"],
    [sys.executable, "scripts/validate_report.py"],
    [sys.executable, "scripts/validate_json.py", "--output", "evidence/validation/final-json-schema.json"],
    [sys.executable, "scripts/validate_integrity.py"],
    ["git", "diff", "--check"],
]
env = dict(os.environ, DOTNET_CLI_HOME=str(REPO / ".tools/dotnet"), NUGET_PACKAGES=str(REPO / ".tools/nuget"), DOTNET_CLI_TELEMETRY_OPTOUT="1")
records = []
started = datetime.now(timezone.utc).isoformat()
failed = False
for command in steps:
    print("Checking: " + " ".join(command[1:] if command[0] == sys.executable else command), flush=True)
    before = time.monotonic()
    executed = subprocess.run(command, cwd=REPO, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    record = {"command": command, "exit_code": executed.returncode, "duration_seconds": round(time.monotonic() - before, 3), "stdout": executed.stdout, "stderr": executed.stderr}
    records.append(record)
    print(f"Exit {executed.returncode}; {record['duration_seconds']} seconds", flush=True)
    if executed.returncode:
        print(executed.stdout + executed.stderr, flush=True)
        failed = True
        break
result = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "status": "FAIL" if failed else "PASS_SOURCE_AND_STATIC_CHECKS_WITH_PARTIAL_SCHEMA_COVERAGE", "excel_read_fresh": args.fresh, "native_dax_m_refresh_render_interactions_tested": False, "steps": records}
(REPO / "evidence/validation/validation-run.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
raise SystemExit(failed)
