import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis"))

import check_readme_consistency as checker  # noqa: E402


def test_required_figures_are_declared():
    figures = checker.required_figures()
    assert figures, "The checklist must not be empty"
    for label, value, docs in figures:
        assert label and value and docs
        for doc in docs:
            assert os.path.exists(doc), f"Declared document missing: {doc}"


def test_documentation_matches_results():
    assert checker.main() == 0, (
        "Documentation has drifted from results/. Regenerate with "
        "`make baselines && make ablate && make failure-analysis`, then update the prose."
    )


def test_guard_detects_drift(tmp_path, monkeypatch):
    # A document that omits the measured figures must be reported as drift.
    stale = tmp_path / "STALE.md"
    stale.write_text(
        "RiceKG identifies 0 out of 5 positive cases (0.0% recall, micro-F1 0.00).\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(checker, "README", str(stale))
    monkeypatch.setattr(checker, "LIMITATIONS", str(stale))
    monkeypatch.setattr(checker, "POSITIONING", str(stale))

    assert checker.main() == 1, "The guard must fail when prose no longer quotes the measured figures"


def test_guard_catches_stale_line_185_claim():
    # A regression test asserting that stale line-185 text is flagged by the consistency scanner.
    fixture_text = "RiceKG achieves 92.50% ± 2.24% exact match, significantly outperforming ML baselines... all p < 0.001"
    errs = checker.scan_for_stale_metrics(fixture_text, "README.md")
    assert len(errs) > 0, "Guard must detect stale pre-P0-5 line-185 claim 'RiceKG achieves 92.50% exact match'"
    assert "92.50%" in errs[0]


def test_guard_catches_stale_scope_claims():
    # Pre-Part-5 text claiming insect classes are diagnosed must be flagged.
    fixture_text = (
        "- **Four Threat Classes Have No Field Case**: `Grasshopper` ... are unrepresented.\n"
        "title = {Expert System for Rice Pest and Disease Diagnosis}\n"
    )
    errs = checker.scan_for_stale_metrics(fixture_text, "README.md")
    assert len(errs) == 2


def test_guard_catches_false_positive_drift(monkeypatch):
    # README quoting 0 false positives while the failure analysis reports 3 must fail.
    monkeypatch.setattr(checker, "negative_control_false_positives", lambda: (3, 27))
    stale = "| **False alarm on negative controls** | **0/17** [0.0, 19.5] | **0 of 27** [0.0, 12.8] | [link] |"
    assert checker.check_false_positive_claim(stale)
    assert not checker.check_false_positive_claim(stale.replace("0 of 27", "3 of 27"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
