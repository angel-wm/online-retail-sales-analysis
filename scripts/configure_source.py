"""Set the sole Excel location parameter in an existing PBIP, without touching data."""
from pathlib import Path
import argparse
import re
import zipfile

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", type=Path, help="Source XLSX path; defaults to this checkout's versioned data/raw workbook")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    source = (args.excel or repo / "data/raw/Online Retail.xlsx").resolve(strict=True)
    if source.suffix.lower() != ".xlsx" or not zipfile.is_zipfile(source):
        raise ValueError("Source must be a valid XLSX file")
    parameter = repo / "powerbi/project/uk-online-retail-sales-analysis.SemanticModel/definition/expressions.tmdl"
    content = parameter.read_text(encoding="utf-8")
    value = str(source).replace('"', '""')
    content, count = re.subn(r'(?m)^(expression SourceFilePath = )"(?:[^"]|"")*"( meta .*)$', lambda m: m[1] + '"' + value + '"' + m[2], content)
    if count != 1:
        raise ValueError("Expected exactly one SourceFilePath parameter")
    parameter.write_text(content, encoding="utf-8")
    print(f"SourceFilePath set to {source}. Open the PBIP and Refresh in Desktop.")

if __name__ == "__main__":
    main()
