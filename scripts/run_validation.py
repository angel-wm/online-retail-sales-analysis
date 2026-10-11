"""Run portable source/static checks; keep detailed diagnostics in the local cache."""
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
parser.add_argument("--resume-from", choices=["tmdl", "model", "report", "json", "integrity"], help="Reuse successful prerequisites from the previous run after a downstream failure")
args = parser.parse_args()
steps = [
    [sys.executable, "scripts/reconcile.py"] + (["--fresh"] if args.fresh else []),
    [sys.executable, "scripts/crosscheck_xml.py"],
    ["dotnet", "run", "--no-restore", "--project", "scripts/tmdl-check/TmdlCheck.csproj", "--", "powerbi/uk-online-retail-sales-analysis.SemanticModel/definition", "evidence/validation/final-tom.json"],
    [sys.executable, "scripts/validate_model.py"],
    [sys.executable, "scripts/validate_report.py"],
    [sys.executable, "scripts/validate_json.py", "--output", "evidence/validation/final-json-schema.json"],
    [sys.executable, "scripts/validate_integrity.py"],
]
if (REPO / ".git").exists():
    steps.append(["git", "diff", "--check"])

env = dict(os.environ, DOTNET_CLI_HOME=str(REPO / ".tools/dotnet"), NUGET_PACKAGES=str(REPO / ".tools/nuget"), DOTNET_CLI_TELEMETRY_OPTOUT="1")
output = REPO / "evidence/validation/validation-run.json"
output.parent.mkdir(parents=True, exist_ok=True)
logs = REPO / ".cache/validation"
logs.mkdir(parents=True, exist_ok=True)
records = []
first_step = 0
fresh_source_read = args.fresh
source_digest = hashlib.sha256((REPO / "data/raw/Online Retail.xlsx").read_bytes()).hexdigest()
prerequisite_paths = ["scripts/reconcile.py", "scripts/crosscheck_xml.py", "evidence/baseline/data_reconciliation.json"]
prerequisite_digest = {name: hashlib.sha256((REPO / name).read_bytes()).hexdigest() for name in prerequisite_paths}
if args.resume_from:
    if args.fresh:
        parser.error("--fresh and --resume-from are mutually exclusive")
    previous = json.loads(output.read_text(encoding="utf-8"))
    first_step = {"tmdl": 2, "model": 3, "report": 4, "json": 5, "integrity": 6}[args.resume_from]
    records = previous["steps"][:first_step]
    if len(records) != first_step or any(record["exit_code"] != 0 for record in records):
        raise ValueError("Prior receipt does not contain all prerequisite successful checks")
    if source_digest != previous.get("source_sha256") or prerequisite_digest != previous.get("source_check_implementation_sha256"):
        raise ValueError("Source or its check implementation changed; rerun without --resume-from")
    financial = json.loads((REPO / "evidence/financial/before_after.json").read_text(encoding="utf-8"))
    if source_digest != financial["source_sha256"]:
        raise ValueError("Financial evidence refers to another source; rerun all checks")
    fresh_source_read = previous["excel_read_fresh"]
started = datetime.now(timezone.utc).isoformat()
failed = False
for index, command in enumerate(steps[first_step:], start=first_step):
    display_command = ["python", *command[1:]] if command[0] == sys.executable else command
    print("Checking: " + " ".join(display_command), flush=True)
    before = time.monotonic()
    try:
        executed = subprocess.run(command, cwd=REPO, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return_code, stdout, stderr = executed.returncode, executed.stdout, executed.stderr
    except OSError as error:
        return_code, stdout, stderr = 1, "", str(error)
    log = logs / f"{index + 1:02d}.log"
    log.write_text(stdout + stderr, encoding="utf-8")
    record = {"command": display_command, "exit_code": return_code, "duration_seconds": round(time.monotonic() - before, 3), "local_log": log.relative_to(REPO).as_posix()}
    records.append(record)
    print(f"Exit {return_code}; {record['duration_seconds']} seconds", flush=True)
    if return_code:
        print(stdout + stderr, flush=True)
        failed = True
        break
partial_schema_coverage = False
if not failed:
    partial_schema_coverage = json.loads((REPO / "evidence/validation/final-json-schema.json").read_text(encoding="utf-8"))["status"] == "PARTIAL"
status = "FAIL" if failed else "PASS_SOURCE_AND_STATIC_CHECKS_WITH_PARTIAL_SCHEMA_COVERAGE" if partial_schema_coverage else "PASS_SOURCE_AND_STATIC_CHECKS"
result = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "status": status, "source_sha256": source_digest, "source_check_implementation_sha256": prerequisite_digest, "excel_read_fresh": fresh_source_read, "reused_successful_prerequisites": first_step, "native_dax_m_refresh_render_interactions_tested": False, "local_backups_required": False, "detailed_logs_versioned": False, "git_diff_check_performed": (REPO / ".git").exists(), "steps": records}
output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
raise SystemExit(failed)
