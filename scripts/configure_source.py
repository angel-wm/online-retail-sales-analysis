"""Configure the local Excel parameter without committing machine-specific paths."""
from pathlib import Path
import argparse
import re
import zipfile

PLACEHOLDER = "SET_LOCAL_ONLINE_RETAIL_XLSX_PATH"
PARAMETER = re.compile(r'(?m)^(expression SourceFilePath = )"(?:""|[^"])*"( meta .*)$')


def main():
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--excel", type=Path, help="Alternate XLSX; defaults to data/raw/Online Retail.xlsx")
    choice.add_argument("--reset", action="store_true", help="Restore the portable version-controlled placeholder")
    choice.add_argument("--check-repository", action="store_true", help="Check that the committed value is portable; do not edit")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    parameter = repo / "powerbi/uk-online-retail-sales-analysis.SemanticModel/definition/expressions.tmdl"
    content = parameter.read_text(encoding="utf-8")
    matches = list(PARAMETER.finditer(content))
    if len(matches) != 1:
        raise ValueError("Expected exactly one SourceFilePath parameter")
    match = matches[0]

    if args.check_repository:
        expected = f'expression SourceFilePath = "{PLACEHOLDER}"'
        if not match.group(0).startswith(expected + " meta "):
            raise SystemExit("SourceFilePath contains a local path. Run --reset before committing.")
        print("Portable SourceFilePath placeholder verified.")
        return

    if args.reset:
        value = PLACEHOLDER
    else:
        source = (args.excel or repo / "data/raw/Online Retail.xlsx").resolve(strict=True)
        if source.suffix.lower() != ".xlsx" or not zipfile.is_zipfile(source):
            raise ValueError("Source must be a valid XLSX file")
        value = str(source)

    replacement = match.group(1) + '"' + value.replace('"', '""') + '"' + match.group(2)
    updated = content[:match.start()] + replacement + content[match.end():]
    if updated != content:
        parameter.write_text(updated, encoding="utf-8")
    if args.reset:
        print("Portable placeholder restored. Run without --reset before refreshing the PBIP.")
    else:
        print(f"SourceFilePath set to {value}. Open the PBIP and Refresh in Desktop.")
        print("This path is local: use --reset before committing expressions.tmdl.")


if __name__ == "__main__":
    main()
