"""Check portable source/assets, with optional verification of local recovery copies."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import struct
import zipfile

REPO = Path(__file__).resolve().parents[1]
IGNORED_DIRECTORIES = {".git", ".cache", ".tools", ".pbi", "backups", ".venv", "venv", "bin", "obj", "__pycache__"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run(local_recovery=False):
    manifest = json.loads((REPO / "evidence/baseline/original_manifest.json").read_text(encoding="utf-8"))
    original_source = next(record for record in manifest if record["path"].replace("\\", "/") == "online+retail/Online Retail.xlsx")
    source = REPO / "data/raw/Online Retail.xlsx"
    source_sha256 = digest(source.read_bytes())
    assert source_sha256 == original_source["sha256"], "Versioned Excel differs from the recovered source"
    financial = json.loads((REPO / "evidence/financial/before_after.json").read_text(encoding="utf-8"))
    assert source_sha256 == financial["source_sha256"], "Financial evidence refers to another source"
    with zipfile.ZipFile(source) as archive:
        assert archive.testzip() is None

    active_projects = []
    for directory, directories, filenames in os.walk(REPO):
        directories[:] = [name for name in directories if name not in IGNORED_DIRECTORIES]
        active_projects.extend((Path(directory) / name).relative_to(REPO).as_posix() for name in filenames if name.endswith(".pbip"))
    assert sorted(active_projects) == ["uk-online-retail-sales-analysis.pbip"], active_projects
    project = json.loads((REPO / active_projects[0]).read_text(encoding="utf-8-sig"))
    report = (REPO / project["artifacts"][0]["report"]["path"]).resolve(strict=True)
    definition = json.loads((report / "definition.pbir").read_text(encoding="utf-8-sig"))
    model = (report / definition["datasetReference"]["byPath"]["path"]).resolve(strict=True)
    assert (model / "definition.pbism").is_file()
    assert not list((REPO / "powerbi").rglob("*.pbix")), "An obsolete PBIX is presented as current"
    export = REPO / "exports/uk-online-retail-sales-analysis.pbix"
    assert export.is_file() and export.stat().st_size > 100_000, "Missing or placeholder PBIX export"
    assert zipfile.is_zipfile(export), "PBIX export is not a ZIP package"
    with zipfile.ZipFile(export) as archive:
        assert archive.testzip() is None, "Corrupt member in PBIX export"
        members = set(archive.namelist())
        assert "Report/Layout" in members, f"PBIX has no classic Report/Layout. Package entries: {sorted(members)[:120]}"
        assert "DataModel" in members or "DataModelSchema" in members, "PBIX semantic model is missing"
    for name in ("LICENSE", "DATA_LICENSE.md"):
        assert (REPO / name).is_file() and (REPO / name).stat().st_size > 0
    screenshots = []
    for filename in ("sales-overview.png", "product-customer-insights.png"):
        data = (REPO / "screenshots" / filename).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR", filename
        width, height = struct.unpack(">II", data[16:24])
        assert width > 0 and height > 0
        screenshots.append({"path": f"screenshots/{filename}", "sha256": digest(data), "width": width, "height": height})
    result = {
        "status": "PASS_PORTABLE_PROJECT_INTEGRITY",
        "source_sha256": source_sha256,
        "source_matches_original_manifest_and_financial_evidence": True,
        "source_xlsx_zip_verified": True,
        "canonical_pbip": active_projects[0],
        "active_pbip_count": len(active_projects),
        "report_and_model_paths_resolve": True,
        "license_documents_present": True,
        "pbix_export": "exports/uk-online-retail-sales-analysis.pbix",
        "pbix_zip_structure_verified": True,
        "pbix_desktop_open_verified_by_this_check": False,
        "current_screenshots": screenshots,
        "requires_local_backups_or_git_history": False,
        "native_refresh_render_or_export_executed": False,
    }
    output = REPO / "evidence/validation/project-integrity.json"
    if local_recovery:
        backup = REPO / "backups/original-recovered-project.zip"
        original_pbix = REPO / "backups/uk-online-retail-sales-analysis-original.pbix"
        with zipfile.ZipFile(backup) as archive:
            assert archive.testzip() is None
            for record in manifest:
                assert digest(archive.read(record["path"].replace("\\", "/"))) == record["sha256"], record["path"]
            assert source.read_bytes() == archive.read("online+retail/Online Retail.xlsx")
            assert original_pbix.read_bytes() == archive.read("uk-online-retail-sales-analysis.pbix")
        with zipfile.ZipFile(original_pbix) as archive:
            assert archive.testzip() is None
        receipt = json.loads((REPO / "backups/consolidation-backup.json").read_text(encoding="utf-8"))
        review_archive = REPO / "backups" / receipt["review_archive"]
        assert digest(review_archive.read_bytes()) == receipt["review_archive_sha256"]
        with zipfile.ZipFile(review_archive) as archive:
            assert archive.testzip() is None
        result.update(status="PASS_LOCAL_RECOVERY_AND_PORTABLE_PROJECT_INTEGRITY", local_backup_members_verified=len(manifest), original_backup_sha256=digest(backup.read_bytes()), review_backup_sha256=digest(review_archive.read_bytes()), original_pbix_preserved=True, requires_local_backups_or_git_history=True)
        output = REPO / "backups/recovery-check.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-recovery", action="store_true", help="Also verify ignored recovery archives; write the result under backups")
    run(parser.parse_args().local_recovery)
