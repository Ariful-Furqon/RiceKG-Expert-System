import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis"))

import competency_questions as cq  # noqa: E402

DOC = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "COMPETENCY_QUESTIONS.md"
)


@pytest.fixture(scope="module")
def results():
    # Run the full competency-question suite once; each run invokes Pellet per scenario.
    return cq.run_all()


def test_at_least_fifteen_questions_are_declared():
    # P1-5 requires no fewer than fifteen competency questions.
    assert len(cq.QUESTIONS) >= 15, (
        f"Only {len(cq.QUESTIONS)} competency questions declared; the methodology requires 15+"
    )


def test_every_question_is_well_formed():
    seen = set()
    for q in cq.QUESTIONS:
        assert q["id"] not in seen, f"Duplicate competency question id: {q['id']}"
        seen.add(q["id"])
        assert q["question"].strip().endswith("?"), f"{q['id']} is not phrased as a question"
        assert q["status"] in {"satisfied", "gap"}, f"{q['id']} has an unknown status"
        assert "SELECT" in q["sparql"], f"{q['id']} carries no SPARQL query"
        if q["status"] == "gap":
            assert q.get("note", "").strip(), f"{q['id']} is a gap but states no reason"


def test_declared_status_matches_the_ontology(results):
    # Each query must behave as declared. Divergence in either direction is a failure.
    mismatched = [r["id"] for r in results if not r["holds"]]
    assert not mismatched, (
        "These competency questions no longer behave as documented: "
        f"{mismatched}. Regenerate with `make competency` and update the declared status."
    )


def test_documentation_is_present_and_lists_every_question(results):
    assert os.path.exists(DOC), "docs/COMPETENCY_QUESTIONS.md must be generated"
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()
    for r in results:
        assert r["id"] in text, f"{r['id']} missing from docs/COMPETENCY_QUESTIONS.md"


def test_competency_questions_status_and_gaps(results):
    # Verifies that all 16 competency questions are satisfied with 0 gaps in the redesigned ontology.
    gaps = {r["id"] for r in results if r["status"] == "gap"}
    satisfied = {r["id"] for r in results if r["status"] == "satisfied"}
    assert len(satisfied) == 16, f"Expected 16 satisfied questions, got {len(satisfied)}"
    assert len(gaps) == 0, f"Expected 0 gaps after Part 4 redesign, found {gaps}"
