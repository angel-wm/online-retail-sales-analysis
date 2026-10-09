"""Verify original preservation, recoverable backup and local publication boundary."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_ROOT = REPO.parent
BASE = "83d0e32e56e1ae539151ab383099565c3571ef2c"
records = json.loads((REPO / "evidence/baseline/original_manifest.json").read_text(encoding="utf-8"))
def digest(data):
    return hashlib.sha256(data).hexdigest()
for record in records:
    path = ORIGINAL_ROOT / record["path"]
    assert path.exists() and digest(path.read_bytes()) == record["sha256"], path
backup = ORIGINAL_ROOT / "backups/original-recovered-project.zip"
with zipfile.ZipFile(backup) as archive:
    assert archive.testzip() is None
    for record in records:
        name = record["path"].replace("\\", "/")
        assert digest(archive.read(name)) == record["sha256"], name
source = REPO / "data/raw/Online Retail.xlsx"
original_excel = ORIGINAL_ROOT / "online+retail/Online Retail.xlsx"
assert digest(source.read_bytes()) == digest(original_excel.read_bytes())
def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)
branch = git("branch", "--show-current").decode().strip()
assert branch == "codex/retail-dashboard-corrections", branch
assert git("rev-parse", "main").decode().strip() == BASE
assert git("rev-parse", "origin/main").decode().strip() == BASE
placeholder_path = "powerbi/online-retail-sales-analysis .pbix"
placeholder = (REPO / placeholder_path).read_bytes()
assert len(placeholder) == 2 and placeholder == git("show", f"{BASE}:{placeholder_path}")
changed = git("diff", "--name-only", BASE, "--", "README.md", "README.es.md", "data/data-dictionary.md", "docs/cleaning-notes.md", "LICENSE", "DATA_LICENSE.md", "dashboard", placeholder_path).decode().strip()
assert not changed, changed
result = {"status": "PASS", "original_files_sha256_preserved": len(records), "backup_zip_members_verified": len(records), "backup": str(backup), "backup_sha256": digest(backup.read_bytes()), "excel_original_and_versioned_match": True, "source_sha256": digest(source.read_bytes()), "branch": branch, "main_local_and_tracking_unchanged": BASE, "remote_live_checked_separately": True, "placeholder_original_bytes_preserved": len(placeholder), "root_original_and_existing_public_docs_unchanged": True, "new_pbix_exported": False, "power_bi_service_published": False}
(REPO / "evidence/validation/original-integrity.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
