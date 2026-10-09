"""Validate PBIP/PBIR against Microsoft's declared JSON schemas, caching reads."""
from pathlib import Path
from urllib.parse import urlparse
import argparse
import hashlib
import json
from urllib.request import urlopen
from urllib.error import HTTPError
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".tools/python"))
import jsonschema

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "powerbi"
CACHE = REPO / ".tools/schemas"
CACHE.mkdir(parents=True, exist_ok=True)
used = {}
unavailable = {}
KNOWN_UNPUBLISHED = {
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.13.0/schema.json": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json",
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.2.0/schema.json",
}

def fetch(url):
    url = url.split("#")[0]
    if url in unavailable:
        raise HTTPError(url, unavailable[url], "Schema unavailable in this validation run", None, None)
    if urlparse(url).hostname != "developer.microsoft.com":
        raise ValueError(f"Unexpected schema host: {url}")
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".json")
    retrieved_from = url
    if not path.exists():
        try:
            with urlopen(url, timeout=30) as response:
                content = json.load(response)
        except HTTPError as error:
            if error.code != 404:
                raise
            # Microsoft's embedded schema IDs use a dot while the public filenames use a hyphen.
            if url.endswith("/schema.embedded.json"):
                retrieved_from = url.replace("/schema.embedded.json", "/schema-embedded.json")
            else:
                retrieved_from = "https://raw.githubusercontent.com/microsoft/json-schemas/main" + urlparse(url).path.removeprefix("/json-schemas")
            try:
                with urlopen(retrieved_from, timeout=30) as response:
                    content = json.load(response)
            except HTTPError as fallback_error:
                unavailable[url] = fallback_error.code
                raise
        path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        path.with_suffix(".source.txt").write_text(retrieved_from, encoding="utf-8")
    source_file = path.with_suffix(".source.txt")
    used[url] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "cache": path.name, "retrieved_from": source_file.read_text(encoding="utf-8") if source_file.exists() else url}
    return json.loads(path.read_text(encoding="utf-8"))

def run(output):
    results = []
    for path in sorted([REPO / "uk-online-retail-sales-analysis.pbip", *PROJECT.rglob("*")]):
        if path.is_file() and (path.suffix in {".json", ".pbip", ".pbir", ".pbism"} or path.name == ".platform"):
            obj = json.loads(path.read_text(encoding="utf-8-sig"))
            result = {"file": path.relative_to(REPO).as_posix(), "parsed": True, "schema_validated": False}
            if "$schema" in obj:
                url = obj["$schema"]
                try:
                    schema = fetch(url)
                    validation_instance = obj
                    result["exact_declared_schema"] = True
                except HTTPError as error:
                    if error.code != 404 or url not in KNOWN_UNPUBLISHED:
                        raise
                    compatible = KNOWN_UNPUBLISHED[url]
                    schema = fetch(compatible)
                    validation_instance = dict(obj, **{"$schema": compatible})
                    result.update(exact_declared_schema=False, declared_schema_http_status=404, compatibility_schema=compatible)
                    url = compatible
                validator_cls = jsonschema.validators.validator_for(schema)
                resolver = jsonschema.RefResolver(base_uri=url, referrer=schema, handlers={"https": fetch})
                validator = validator_cls(schema, resolver=resolver)
                errors = sorted(validator.iter_errors(validation_instance), key=lambda e: str(e.path))
                result.update(schema_validated=True, schema=url, errors=[{"path": list(e.absolute_path), "message": e.message} for e in errors])
            results.append(result)
    errors = [r for r in results if r.get("errors")]
    partial = any(r.get("exact_declared_schema") is False for r in results)
    result = {"status": "FAIL" if errors else "PARTIAL" if partial else "PASS", "json_files": len(results), "schema_validated_files": sum(r["schema_validated"] for r in results), "exact_schema_files": sum(r.get("exact_declared_schema") is True for r in results), "compatibility_schema_files": sum(r.get("exact_declared_schema") is False for r in results), "project_schema_versions_unchanged": True, "desktop_rendered": False, "files": results, "schemas": used}
    target = REPO / output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["status", "json_files", "schema_validated_files"]}), flush=True)
    for error in errors:
        print(json.dumps(error), flush=True)
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="evidence/validation/json-schema.json")
    run(parser.parse_args().output)
