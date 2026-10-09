"""Rerun source/static validation and record actual commands and exit codes."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--fresh", action="store_true", help="Read Excel again rather than the SHA256-keyed local cache")
parser.add_argument("--resume-from", choices=["tmdl", "model", "report", "json", "integrity"], help="Reuse completed Excel checks from the prior receipt after a downstream failure")
args = parser.parse_args()
steps = [
    [sys.executable, "scripts/reconcile.py"] + (["--fresh"] if args.fresh else []),
    [sys.executable, "scripts/crosscheck_xml.py"],
    ["dotnet", "run", "--no-restore", "--project", "scripts/tmdl-check/TmdlCheck.csproj", "--", "powerbi/uk-online-retail-sales-analysis.SemanticModel/definition", "evidence/validation/final-tom.json"],
    [sys.executable, "scripts/validate_model.py"],
    [sys.executable, "scripts/validate_report.py"],
    [sys.executable, "scripts/validate_json.py", "--output", "evidence/validation/final-json-schema.json"],
    [sys.executable, "scripts/validate_integrity.py"],
    ["git", "diff", "--check"],
]
env = dict(os.environ, DOTNET_CLI_HOME=str(REPO / ".tools/dotnet"), NUGET_PACKAGES=str(REPO / ".tools/nuget"), DOTNET_CLI_TELEMETRY_OPTOUT="1")
records = []
first_step = 0
fresh_source_read = args.fresh
if args.resume_from:
    if args.fresh:
        parser.error("--fresh and --resume-from are mutually exclusive")
    previous = json.loads((REPO / "evidence/validation/validation-run.json").read_text(encoding="utf-8"))
    first_step = {"tmdl": 2, "model": 3, "report": 4, "json": 5, "integrity": 6}[args.resume_from]
    records = previous["steps"][:first_step]
    if len(records) != first_step or any(record["exit_code"] != 0 for record in records):
        raise ValueError("Prior receipt does not contain all prerequisite successful checks")
    source_digest = hashlib.sha256((REPO / "data/raw/Online Retail.xlsx").read_bytes()).hexdigest()
    financial = json.loads((REPO / "evidence/financial/before_after.json").read_text())
    if source_digest != financial["source_sha256"]:
        raise ValueError("Excel changed; rerun the source checks")
    fresh_source_read = previous["excel_read_fresh"]
started = datetime.now(timezone.utc).isoformat()
failed = False
for command in steps[first_step:]:
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
result = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "status": "FAIL" if failed else "PASS_SOURCE_AND_STATIC_CHECKS_WITH_PARTIAL_SCHEMA_COVERAGE", "excel_read_fresh": fresh_source_read, "reused_successful_prerequisites": first_step, "native_dax_m_refresh_render_interactions_tested": False, "steps": records}
(REPO / "evidence/validation/validation-run.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
raise SystemExit(failed)
