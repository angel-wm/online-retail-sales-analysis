"""Preserve the supplied project and recover its source into this review branch."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

REPO = Path(__file__).resolve().parents[1]
ORIGINAL = REPO.parent
AUDIT = Path(r"C:\Users\angel\.codex\visualizations\2026\10\08\01a11ddb-f3f9-71b1-924b-6c498e362a69\audit")
BASELINE = REPO / "evidence" / "baseline"
BASELINE.mkdir(parents=True, exist_ok=True)
manifest = json.loads((AUDIT / "initial_manifest.json").read_text(encoding="utf-8"))
for record in manifest:
    actual = hashlib.sha256((ORIGINAL / record["path"]).read_bytes()).hexdigest()
    assert actual == record["sha256"], record["path"]
backup = ORIGINAL / "backups" / "original-recovered-project.zip"
backup.parent.mkdir(exist_ok=True)
if not backup.exists():
    with zipfile.ZipFile(backup, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for record in manifest:
            archive.write(ORIGINAL / record["path"], record["path"])
with zipfile.ZipFile(backup) as archive:
    for record in manifest:
        assert hashlib.sha256(archive.read(record["path"].replace("\\", "/"))).hexdigest() == record["sha256"]
(BASELINE / "original_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
(BASELINE / "backup.json").write_text(json.dumps({
    "archive": "../backups/original-recovered-project.zip",
    "sha256": hashlib.sha256(backup.read_bytes()).hexdigest(),
    "original_files": len(manifest),
    "all_archive_members_hash_verified": True,
    "remote_main_commit": "83d0e32e56e1ae539151ab383099565c3571ef2c",
}, indent=2), encoding="utf-8")
target = REPO / "powerbi" / "project"
target.mkdir(parents=True, exist_ok=True)
for path in ORIGINAL.glob("*.pbip"):
    shutil.copy2(path, target / path.name)
for pattern in ("*.SemanticModel", "*.Report"):
    for path in ORIGINAL.glob(pattern):
        shutil.copytree(path, target / path.name, ignore=shutil.ignore_patterns(".pbi"))
for name in ("AUDITORIA.md", "raw_profile.json", "data_reconciliation.json", "calculation_crosscheck.json", "monthly_reconciliation.csv"):
    shutil.copy2(AUDIT / name, BASELINE / name)
source = ORIGINAL / "online+retail" / "Online Retail.xlsx"
remote_source = REPO / "data" / "raw" / "Online Retail.xlsx"
assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(remote_source.read_bytes()).digest()
print(json.dumps({"backup_verified": str(backup), "files": len(manifest), "recovered_pbip": str(target), "excel_matches_remote": True}))
