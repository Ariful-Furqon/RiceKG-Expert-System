"""
Verification script for data/benchmark_field.csv citations.

Queries Crossref API (https://api.crossref.org/works/{doi}) for every row
in data/benchmark_field.csv, asserts HTTP 200, and verifies that the paper's
real title appears verbatim (modulo whitespace/case/HTML markup) in the citation.
Exits with code 1 if any title mismatches or DOI fails to resolve.
"""

import csv
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def clean_html(text: str) -> str:
    """Remove HTML/XML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def normalize_for_comparison(text: str) -> str:
    """Normalize text for robust string matching (case-insensitive, alphanumeric only)."""
    text = clean_html(text).lower()
    text = unicodedata.normalize("NFKD", text)
    return re.sub(r"[^a-z0-9]", "", text)


def verify_benchmark_citations(csv_path: str = "data/benchmark_field.csv") -> bool:
    if not os.path.exists(csv_path):
        print(f"ERROR: Benchmark file not found at {csv_path}")
        return False

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Verifying {len(rows)} citations in {csv_path} against Crossref API...")

    headers = {
        "User-Agent": "RiceKG-CitationVerifier/1.0 (mailto:ariful.furqon@unej.ac.id)"
    }
    all_passed = True
    seen_dois = {}

    for idx, row in enumerate(rows):
        case_id = row.get("case_id", f"ROW_{idx+1}")
        doi = row.get("doi", "").strip()
        citation = row.get("citation", "").strip()

        if not doi:
            print(f"[{case_id}] FAILED: Missing DOI.")
            all_passed = False
            continue

        if not citation:
            print(f"[{case_id}] FAILED: Missing citation.")
            all_passed = False
            continue

        # Fetch from Crossref API (or use cache if DOI repeated)
        if doi in seen_dois:
            cr_title = seen_dois[doi]
        else:
            url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status != 200:
                        print(f"[{case_id}] FAILED: HTTP {resp.status} for DOI {doi}")
                        all_passed = False
                        continue
                    data = json.loads(resp.read().decode("utf-8"))
                    msg = data.get("message", {})
                    titles = msg.get("title", [])
                    if not titles:
                        print(f"[{case_id}] FAILED: No title returned from Crossref for DOI {doi}")
                        all_passed = False
                        continue
                    cr_title = titles[0]
                    seen_dois[doi] = cr_title
            except Exception as e:
                print(f"[{case_id}] FAILED: Request error for DOI {doi}: {e}")
                all_passed = False
                continue

            time.sleep(0.2)

        norm_cr = normalize_for_comparison(cr_title)
        norm_cit = normalize_for_comparison(citation)

        if norm_cr not in norm_cit:
            print(f"[{case_id}] FAILED: Title mismatch!")
            print(f"   Crossref title: {cr_title}")
            print(f"   Citation text : {citation}")
            all_passed = False
        else:
            print(f"[{case_id}] PASSED: {doi} -> {clean_html(cr_title)[:60]}...")

    if all_passed:
        print("\nAll citations verified successfully against Crossref API!")
        return True
    else:
        print("\nOne or more citations FAILED verification!")
        return False


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "data/benchmark_field.csv"
    success = verify_benchmark_citations(csv_file)
    sys.exit(0 if success else 1)
