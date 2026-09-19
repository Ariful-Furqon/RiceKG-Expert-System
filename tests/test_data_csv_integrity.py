# Every CSV under data/ must parse to a constant column count.
#
# An unquoted comma in a free-text field silently shifts every later column:
# DictReader then files the overflow under a None key and the citation, DOI and
# locator columns carry the wrong values without raising. This happened in
# noisy_or_parameters.csv (eight rows) and symptom_mapping.csv (one row).

import csv
import glob
import os

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSVS = sorted(glob.glob(os.path.join(BASE_DIR, "data", "*.csv")))


@pytest.mark.parametrize("path", DATA_CSVS, ids=os.path.basename)
def test_constant_column_count(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    width = len(rows[0])
    bad = [i for i, row in enumerate(rows[1:], start=2) if row and len(row) != width]
    assert not bad, f"{os.path.basename(path)}: lines {bad} do not have {width} columns (unquoted comma?)"
