"""
Verification script for field benchmark and holdout staging citations.

Queries Crossref API (https://api.crossref.org/works/{doi}) for every DOI row,
asserts HTTP 200, and verifies that the paper's real title appears verbatim
(modulo whitespace/case/HTML markup) in the citation.

For tier-C outbreak report rows (with no DOI), asserts that the archive_url
resolves (HTTP 200). A dead source_url with a live archive is reported as a
warning, not a failure.

Exits with code 1 if any title mismatches, archive fails, or DOI fails to resolve.
"""

import argparse
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


def check_url_status(url: str, timeout: int = 15, headers: dict = None) -> tuple[int, str]:
    """Attempts a GET request with a range/stream to verify HTTP status."""
    if headers is None:
        headers = {
            "User-Agent": "RiceKG-CitationVerifier/1.0 (mailto:ariful.furqon@unej.ac.id)"
        }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except Exception as e:
        return 0, str(e)


def verify_citations(csv_path: str = "data/benchmark_field.csv") -> bool:
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found at {csv_path}")
        return False

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Verifying {len(rows)} citations in {csv_path}...")

    headers = {
        "User-Agent": "RiceKG-CitationVerifier/1.0 (mailto:ariful.furqon@unej.ac.id)"
    }
    all_passed = True
    seen_dois = {}

    for idx, row in enumerate(rows):
        case_id = row.get("case_id", f"ROW_{idx+1}")
        tier = row.get("evidence_tier", "").strip()
        doi = row.get("doi", "").strip()
        citation = row.get("citation", "").strip()
        source_url = row.get("source_url", "").strip()
        archive_url = row.get("archive_url", "").strip()

        # Handle Tier C (Official institutional outbreak reports without DOI)
        if tier == "C" or (not doi and archive_url):
            if not archive_url:
                print(f"[{case_id}] FAILED: Tier C row missing archive_url.")
                all_passed = False
                continue

            # Verify archive_url
            status, err = check_url_status(archive_url, timeout=20, headers=headers)
            if status != 200:
                print(f"[{case_id}] FAILED: Archive URL returned HTTP {status} ({err}): {archive_url}")
                all_passed = False
                continue

            # Check source_url (warning only if dead, as long as archive is live)
            if source_url:
                src_status, src_err = check_url_status(source_url, timeout=10, headers=headers)
                if src_status != 200:
                    print(f"[{case_id}] WARNING: Source URL {source_url} returned HTTP {src_status} ({src_err}), but archive URL verified.")
                else:
                    print(f"[{case_id}] PASSED: Tier C archive and source URL verified -> {archive_url[:70]}...")
            else:
                print(f"[{case_id}] PASSED: Tier C archive URL verified -> {archive_url[:70]}...")
            continue

        # Standard DOI validation (Tiers A, B, benchmark_field)
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
        print("\nAll citations verified successfully!")
        return True
    else:
        print("\nOne or more citations FAILED verification!")
        return False


def main():
    parser = argparse.ArgumentParser(description="Verify citations against Crossref or archive URLs.")
    parser.add_argument("--csv", dest="csv_path", default=None, help="Path to CSV dataset to verify")
    parser.add_argument("positional_csv", nargs="?", default="data/benchmark_field.csv", help="Fallback positional CSV path")
    args = parser.parse_args()

    target_csv = args.csv_path if args.csv_path else args.positional_csv
    success = verify_citations(target_csv)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
