"""Verify recovery archives, canonical structure and local publication boundary."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

REPO = Path(__file__).resolve().parents[1]
BASE = "83d0e32e56e1ae539151ab383099565c3571ef2c"
records = json.loads((REPO / "evidence/baseline/original_manifest.json").read_text(encoding="utf-8"))

def digest(data):
    return hashlib.sha256(data).hexdigest()

backup = REPO / "backups/original-recovered-project.zip"
with zipfile.ZipFile(backup) as archive:
    assert archive.testzip() is None
    for record in records:
        name = record["path"].replace("\\", "/")
        assert digest(archive.read(name)) == record["sha256"], name
    source = REPO / "data/raw/Online Retail.xlsx"
    assert source.read_bytes() == archive.read("online+retail/Online Retail.xlsx")
    original_pbix = REPO / "backups/uk-online-retail-sales-analysis-original.pbix"
    assert original_pbix.read_bytes() == archive.read("uk-online-retail-sales-analysis.pbix")
with zipfile.ZipFile(original_pbix) as archive:
    assert archive.testzip() is None

def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)

receipt = json.loads((REPO / "evidence/validation/consolidation-backup.json").read_text())
review_archive = REPO / "backups" / receipt["review_archive"]
assert digest(review_archive.read_bytes()) == receipt["review_archive_sha256"]
with zipfile.ZipFile(review_archive) as archive:
    assert archive.testzip() is None
    assert archive.read("powerbi/online-retail-sales-analysis .pbix") == git("show", f"{BASE}:powerbi/online-retail-sales-analysis .pbix")
branch = git("branch", "--show-current").decode().strip()
assert branch == "codex/retail-dashboard-corrections", branch
assert git("rev-parse", "main").decode().strip() == BASE
assert git("rev-parse", "origin/main").decode().strip() == BASE
assert git("merge-base", "--is-ancestor", receipt["head_before_consolidation"], "HEAD") == b""
assert not (REPO / "review").exists()
active_projects = [p.relative_to(REPO).as_posix() for p in REPO.rglob("*.pbip") if not any(part in {"backups", ".git", ".tools"} for part in p.relative_to(REPO).parts)]
assert active_projects == ["uk-online-retail-sales-analysis.pbip"], active_projects
assert not list((REPO / "powerbi").rglob("*.pbix")), "An obsolete PBIX is still presented as current"
protected = git("diff", "--name-only", BASE, "--", "data/data-dictionary.md", "docs/cleaning-notes.md", "LICENSE", "DATA_LICENSE.md").decode().strip()
assert not protected, protected
for filename in ["sales-overview.png", "product-customer-insights.png"]:
    assert (REPO / "screenshots" / filename).read_bytes() == git("show", f"{BASE}:dashboard/{filename}")

result = {
    "status": "PASS",
    "original_backup_zip_members_verified": len(records),
    "original_backup_sha256": digest(backup.read_bytes()),
    "review_archive_sha256": digest(review_archive.read_bytes()),
    "original_pbix_bytes_preserved_as_snapshot": True,
    "excel_original_and_versioned_match": True,
    "source_sha256": digest(source.read_bytes()),
    "canonical_pbip": active_projects[0],
    "active_pbip_count": len(active_projects),
    "obsolete_review_workspace_removed": True,
    "branch": branch,
    "main_local_and_tracking_unchanged": BASE,
    "remote_live_check_in_this_script": False,
    "prior_local_commits_retained": True,
    "placeholder_preserved_in_archive_not_presented_as_current": True,
    "licenses_legacy_dictionary_cleaning_and_screenshot_bytes_preserved": True,
    "new_pbix_exported": False,
    "power_bi_service_published": False,
}
(REPO / "evidence/validation/original-integrity.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
