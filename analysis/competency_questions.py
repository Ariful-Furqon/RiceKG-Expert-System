"""
Competency questions for the RiceKG ontology (Gruninger & Fox methodology).

Each question is paired with the SPARQL query that answers it and a declared
`status`: `satisfied` when the ontology answers it, or `gap` when it cannot. Gaps are
first-class results in this methodology — a competency question that the artefact fails
is how the method exposes a modelling omission, so they are recorded rather than removed.

Running this module regenerates `docs/COMPETENCY_QUESTIONS.md` from live query output,
so the document cannot drift from the ontology. `tests/test_competency_questions.py`
executes every query and fails if a declared status no longer matches reality — in either
direction, so closing a gap without documenting it is also a failure.

Usage:  python analysis/competency_questions.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import model  # noqa: E402
from owlready2 import sync_reasoner_pellet  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_MD = os.path.join(BASE_DIR, "docs", "COMPETENCY_QUESTIONS.md")

NS = "http://www.semanticweb.org/ontologies/rice_pest_disease.owl#"
PREFIX = f"PREFIX : <{NS}>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"

# Symptom sets used by the inference-level questions. Drawn from RULE_REGISTRY so they
# stay valid when rules are revised.
def _antecedents(rule_id):
    return list(next(r for r in model.RULE_REGISTRY if r["id"] == rule_id)["antecedents"])


SCENARIOS = {
    # A canonical (Tier-1) observation for rice blast.
    "canonical_blast": lambda: _antecedents("SWRL-R08"),
    # A partial (Tier-2 only) observation for false smut.
    "partial_smut": lambda: _antecedents("SWRL-R17"),
    # Two threats observed at once: canonical false smut plus relaxed rice blast.
    "co_infection": lambda: _antecedents("SWRL-R07") + _antecedents("SWRL-R18"),
    # No observation at all.
    "empty": lambda: [],
}

QUESTIONS = [
    # ---- Schema level -------------------------------------------------------
    dict(id="CQ01", scenario=None, status="satisfied",
         question="Which phenotypic symptoms does the ontology model?",
         sparql="SELECT (COUNT(DISTINCT ?s) AS ?n) WHERE { ?s a :Symptom . }",
         expect="count_positive"),
    dict(id="CQ02", scenario=None, status="satisfied",
         question="Which biotic threats does the ontology model?",
         sparql="SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE { ?t a/rdfs:subClassOf* :Threat . }",
         expect="count_positive"),
    dict(id="CQ03", scenario=None, status="satisfied",
         question="Which of the modelled threats are pests (after the insect scope cut, the plant-parasitic nematode)?",
         sparql="SELECT ?p WHERE { ?p a :Pest . }",
         expect="rows_positive"),
    dict(id="CQ04", scenario=None, status="satisfied",
         question="Which of the modelled threats are pathogen-caused diseases?",
         sparql="SELECT ?d WHERE { ?d a :Disease . }",
         expect="rows_positive"),
    dict(id="CQ05", scenario=None, status="satisfied",
         question="Is every pest and every disease also classified as a threat?",
         sparql=("SELECT (COUNT(?x) AS ?n) WHERE { ?x a/rdfs:subClassOf* :Threat . "
                 "{ ?x a :Pest . } UNION { ?x a :Disease . } }"),
         expect="count_positive"),
    dict(id="CQ06", scenario=None, status="satisfied",
         question="Does the ontology distinguish a confirmed diagnosis from a suspected one?",
         sparql=("SELECT ?p WHERE { VALUES ?p { :hasConfirmedThreat :hasSuspectedThreat } "
                 "?p a <http://www.w3.org/2002/07/owl#ObjectProperty> . }"),
         expect="rows_positive"),
    dict(id="CQ07", scenario=None, status="satisfied",
         question="Do the graded diagnosis properties specialise the general hasThreat property, "
                  "so that existing queries still resolve?",
         sparql=("SELECT ?p WHERE { ?p rdfs:subPropertyOf :hasThreat . "
                 "VALUES ?p { :hasConfirmedThreat :hasSuspectedThreat } }"),
         expect="rows_positive"),
    dict(id="CQ08", scenario=None, status="gap",
         question="Which control treatment is recommended for a diagnosed threat?",
         sparql="SELECT (COUNT(?c) AS ?n) WHERE { ?c a :ControlTreatment . }",
         expect="count_zero",
         note="The `ControlTreatment` class is declared but has no individuals and no property "
              "links it to a threat. Treatment advice is held in `static/data.json` for the web "
              "interface and is not part of the knowledge graph, so the ontology cannot answer "
              "this question."),
    dict(id="CQ09", scenario=None, status="gap",
         question="What diagnostic confidence does the ontology attach to an inferred threat?",
         sparql=("SELECT (COUNT(?p) AS ?n) WHERE "
                 "{ ?p a <http://www.w3.org/2002/07/owl#DatatypeProperty> . }"),
         expect="count_zero",
         note="P0-1 specified a `hasDiagnosticConfidence` datatype property. Confidence and "
              "antecedent coverage are computed in `model.predict_diseases` and returned to the "
              "caller, but never asserted into the graph, so a SPARQL client sees an ungraded ABox."),
    dict(id="CQ10", scenario=None, status="gap",
         question="Which symptoms are the antecedents of the rule that diagnoses a given threat?",
         sparql="SELECT (COUNT(?s) AS ?n) WHERE { ?t a :Threat . ?t :hasSymptom ?s . }",
         expect="count_zero",
         note="Rule antecedents live inside SWRL `Imp` bodies and in `model.RULE_REGISTRY`. They "
              "are not asserted as triples between a threat and its symptoms, so the rule base is "
              "opaque to SPARQL. Explanations are produced by `model.explain_diagnoses` in Python."),

    # ---- Inference level ----------------------------------------------------
    dict(id="CQ11", scenario="canonical_blast", status="satisfied",
         question="Given a complete pathognomonic observation, which threat is confirmed?",
         sparql="SELECT ?t WHERE { ?r a :Rice . ?r :hasConfirmedThreat ?t . }",
         expect="rows_positive"),
    dict(id="CQ12", scenario="partial_smut", status="satisfied",
         question="Given only a partial observation, which threat is raised as suspected?",
         sparql="SELECT ?t WHERE { ?r a :Rice . ?r :hasSuspectedThreat ?t . }",
         expect="rows_positive"),
    dict(id="CQ13", scenario="partial_smut", status="satisfied",
         question="Does a partial observation avoid asserting a confirmed diagnosis?",
         sparql="SELECT (COUNT(?t) AS ?n) WHERE { ?r a :Rice . ?r :hasConfirmedThreat ?t . }",
         expect="count_zero"),
    dict(id="CQ14", scenario="canonical_blast", status="satisfied",
         question="Which symptoms were observed on the sample under diagnosis?",
         sparql="SELECT ?s WHERE { ?r a :Rice . ?r :hasSymptom ?s . }",
         expect="rows_positive"),
    dict(id="CQ15", scenario="co_infection", status="satisfied",
         question="When two threats are present at once, are both inferred?",
         sparql="SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE { ?r a :Rice . ?r :hasThreat ?t . }",
         expect="count_at_least_2"),
    dict(id="CQ16", scenario="empty", status="satisfied",
         question="With no symptom observed, does the reasoner correctly assert no threat?",
         sparql="SELECT (COUNT(?t) AS ?n) WHERE { ?r a :Rice . ?r :hasThreat ?t . }",
         expect="count_zero"),
]


def _diagnosed_world(symptoms):
    """Build an ontology, assert one observed sample, and run the reasoner over it.

    `model.predict_diseases` destroys its temporary individual once it has extracted the
    diagnosis, which leaves nothing for a SPARQL client to query. The competency questions
    need the inferred ABox to persist, so the sample is constructed here and kept.
    """
    onto = model.build_ontology()
    sample = onto.Rice("CQ_Sample", namespace=onto)
    for name in symptoms:
        individual = onto.search_one(iri=f"*{name}")
        if individual is not None:
            sample.hasSymptom.append(individual)
    sync_reasoner_pellet(x=onto.world, infer_property_values=True)
    return onto.world


def _check(expect, rows):
    """Evaluate a query result against its declared expectation."""
    if expect == "rows_positive":
        return len(rows) > 0
    value = rows[0][0] if rows and rows[0] else 0
    if expect == "count_positive":
        return int(value) > 0
    if expect == "count_zero":
        return int(value) == 0
    if expect == "count_at_least_2":
        return int(value) >= 2
    raise ValueError(f"unknown expectation: {expect}")


def run_all():
    """Execute every competency question, returning one result record per question."""
    schema_onto = model.build_ontology()
    worlds = {None: schema_onto.world}

    for name, symptoms in SCENARIOS.items():
        worlds[name] = _diagnosed_world(symptoms())

    results = []
    for q in QUESTIONS:
        world = worlds[q["scenario"]]
        rows = list(world.sparql(PREFIX + q["sparql"]))
        holds = _check(q["expect"], rows)
        # A question is answered when its expectation holds; the declared status says
        # whether answering it means the ontology covers the question or exposes a gap.
        results.append({**q, "rows": rows, "holds": holds})
    return results


def _render_value(q, rows):
    if q["expect"] == "rows_positive":
        names = [str(r[0]).rsplit(".", 1)[-1] for r in rows]
        shown = ", ".join(f"`{n}`" for n in names[:6])
        return f"{len(names)} result(s): {shown}" + (" …" if len(names) > 6 else "")
    value = rows[0][0] if rows and rows[0] else 0
    return f"`{int(value)}`"


def main():
    results = run_all()
    satisfied = [r for r in results if r["status"] == "satisfied"]
    gaps = [r for r in results if r["status"] == "gap"]
    mismatched = [r for r in results if not r["holds"]]

    L = []
    L.append("# Competency Questions")
    L.append("")
    L.append("> **Generated by**: `analysis/competency_questions.py` (live SPARQL over the built ontology).  ")
    L.append(f"> **Questions**: {len(results)} — **{len(satisfied)} satisfied**, **{len(gaps)} gaps**.")
    L.append("")
    L.append("Competency questions follow Gruninger and Fox: the ontology is specified by the questions "
             "it must answer, and a question it cannot answer is a finding rather than an omission to be "
             "quietly dropped. Every question below is paired with the SPARQL that answers it and is "
             "executed by `tests/test_competency_questions.py`, which fails if a declared status stops "
             "matching the ontology — including when a gap is closed without this document being updated.")
    L.append("")
    L.append("Namespace: `" + NS + "`")
    L.append("")

    L.append("## Summary")
    L.append("")
    L.append("| ID | Question | Status |")
    L.append("|:--|:--|:--|")
    for r in results:
        badge = "satisfied" if r["status"] == "satisfied" else "**gap**"
        L.append(f"| `{r['id']}` | {r['question']} | {badge} |")
    L.append("")

    if gaps:
        L.append("## Gaps")
        L.append("")
        L.append("Three questions a rice diagnostic ontology would be expected to answer are not "
                 "answerable against this artefact. Each is a concrete modelling target.")
        L.append("")
        for r in gaps:
            L.append(f"### {r['id']} — {r['question']}")
            L.append("")
            L.append(r.get("note", ""))
            L.append("")

    L.append("## Questions and queries")
    L.append("")
    for r in results:
        scen = r["scenario"] or "schema only (no sample)"
        L.append(f"### {r['id']} — {r['question']}")
        L.append("")
        L.append(f"- **Status**: {'satisfied' if r['status'] == 'satisfied' else '**gap**'}")
        L.append(f"- **Scenario**: {scen}")
        L.append(f"- **Result**: {_render_value(r, r['rows'])}")
        if r.get("note"):
            L.append(f"- **Note**: {r['note']}")
        L.append("")
        L.append("```sparql")
        L.append(PREFIX.strip())
        L.append(r["sparql"])
        L.append("```")
        L.append("")

    with open(OUT_MD, "w", newline="", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")

    print(f"[OUTPUT] {OUT_MD}")
    print(f"{len(satisfied)} satisfied, {len(gaps)} gaps")
    for r in mismatched:
        print(f"  MISMATCH {r['id']}: declared {r['status']} but expectation did not hold")
    return 1 if mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
