import csv
import itertools
import json
import os
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from owlready2 import World, sync_reasoner_pellet, OwlReadyInconsistentOntologyError

from ricekg import model

RESULTS_DIR = os.path.join(BASE_DIR, "results")
PARAMS_CSV = os.path.join(BASE_DIR, "data", "noisy_or_parameters.csv")
DEFINITIONS_CSV = os.path.join(BASE_DIR, "ontology", "term_definitions.csv")

THREATS = model.PESTS + model.DISEASES


def rules_by_threat():
    # threat -> list of its rules (id, tier, antecedent set), in RULE_REGISTRY order.
    out = {t: [] for t in THREATS}
    for r in model.RULE_REGISTRY:
        out[r["threat"]].append({"id": r["id"], "tier": r["tier"], "antecedents": set(r["antecedents"])})
    return out


def check_consistency():
    try:
        onto = model.build_ontology(enabled_tiers={"tier1", "tier2"}, world=World())
        sync_reasoner_pellet(x=onto.world, infer_property_values=False, debug=0)
        return {"consistent": True, "detail": "Pellet found no inconsistency in the TBox and rule base."}
    except OwlReadyInconsistentOntologyError as exc:
        return {"consistent": False, "detail": str(exc)}


def check_tier_subsumption(rules):
    rows = []
    for t, rs in rules.items():
        t1 = next((r for r in rs if r["tier"] == "tier1"), None)
        t2s = [r for r in rs if r["tier"] == "tier2"]
        ok = bool(t1 and t2s and all(r["antecedents"] <= t1["antecedents"] for r in t2s))
        rows.append({"threat": t, "tier1": t1 and t1["id"], "tier2": [r["id"] for r in t2s], "tier2_subset_of_tier1": ok})
    return rows


def check_cross_threat_subsumption(rules):
    # Pairs (A-rule, B-rule), A != B, where B's antecedents are contained in A's.
    flat = [(t, r["tier"], r) for t, rs in rules.items() for r in rs]
    hits = []
    for (ta, tier_a, ra), (tb, tier_b, rb) in itertools.permutations(flat, 2):
        if ta != tb and rb["antecedents"] <= ra["antecedents"]:
            hits.append({"firing_rule": ra["id"], "forces": rb["id"], "threats": [ta, tb]})
    return hits


def antecedent_sharing(rules):
    users = {}
    for t, rs in rules.items():
        for r in rs:
            for a in r["antecedents"]:
                users.setdefault(a, set()).add(t)
    shared = {a: sorted(ts) for a, ts in users.items() if len(ts) > 1}
    return users, dict(sorted(shared.items(), key=lambda kv: (-len(kv[1]), kv[0])))


def pairwise_overlap(rules, tier):
    # Jaccard overlap between threats of the union of their antecedents at `tier`.
    def ants(t):
        return set().union(*(r["antecedents"] for r in rules[t] if r["tier"] == tier))
    rows = []
    for ta, tb in itertools.combinations(THREATS, 2):
        a, b = ants(ta), ants(tb)
        inter = a & b
        rows.append({"pair": [ta, tb], "shared": sorted(inter), "jaccard": round(len(inter) / len(a | b), 3)})
    return sorted(rows, key=lambda r: -r["jaccard"])


def vocabulary_use(users):
    gate_terms = set(model.INSECT_SPECIFIC_SIGNS) | set(model.NON_MODELED_PATHOGEN_SIGNS)
    rule_terms = set(users)
    vocab = set(model.ALL_SYMPTOMS)
    return {
        "total": len(vocab),
        "used_by_rules": sorted(vocab & rule_terms),
        "gate_only": sorted((vocab & gate_terms) - rule_terms),
        "unused": sorted(vocab - rule_terms - gate_terms),
    }


def literature_backing(rules):
    with open(PARAMS_CSV, encoding="utf-8", newline="") as f:
        sourced = {(r["threat"], r["observation"]) for r in csv.DictReader(f)
                   if r["doi"] or r["citation"]}
    links = sorted({(t, a) for t, rs in rules.items() for r in rs for a in r["antecedents"]})
    unsourced = [f"{t}:{a}" for t, a in links if (t, a) not in sourced]
    with open(DEFINITIONS_CSV, encoding="utf-8", newline="") as f:
        defined = {r["term"] for r in csv.DictReader(f) if r["definition"]}
    rule_with_ref = sum(1 for r in model.RULE_REGISTRY if r.get("literature"))
    return {
        "antecedent_links": len(links),
        "sourced_links": len(links) - len(unsourced),
        "unsourced_links": unsourced,
        "rules_with_literature": rule_with_ref,
        "rules_total": len(model.RULE_REGISTRY),
        "terms_with_definition": len(set(model.ALL_SYMPTOMS) & defined),
        "terms_total": len(model.ALL_SYMPTOMS),
    }


def run():
    rules = rules_by_threat()
    users, shared = antecedent_sharing(rules)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "consistency": check_consistency(),
        "reachability": {t: sorted({r["tier"] for r in rs}) for t, rs in rules.items()},
        "tier_subsumption": check_tier_subsumption(rules),
        "cross_threat_subsumption": check_cross_threat_subsumption(rules),
        "shared_antecedents": shared,
        "overlap_tier1": pairwise_overlap(rules, "tier1"),
        "overlap_tier2": pairwise_overlap(rules, "tier2"),
        "vocabulary": vocabulary_use(users),
        "literature_backing": literature_backing(rules),
    }
    return report


def write_markdown(rep, path):
    voc, lit = rep["vocabulary"], rep["literature_backing"]
    tier_ok = sum(r["tier2_subset_of_tier1"] for r in rep["tier_subsumption"])
    unreachable = [t for t, tiers in rep["reachability"].items() if not tiers]
    L = [
        "# Knowledge-Base Verification",
        "",
        f"> **Generated by**: `analysis/kb_verification.py` on {rep['generated_at'][:19]} UTC.  ",
        "> **Scope**: properties of the rule base and ontology that hold independently of any test case.",
        "",
        "| Check | Result |",
        "|:---|:---|",
        f"| Logical consistency (Pellet) | {'consistent' if rep['consistency']['consistent'] else '**INCONSISTENT**'} |",
        f"| Reachability | {len(THREATS) - len(unreachable)}/{len(THREATS)} in-scope threats have rules |",
        f"| Tier-2 ⊆ Tier-1 (confirmed implies suspected) | {tier_ok}/{len(rep['tier_subsumption'])} threats |",
        f"| Cross-threat subsumption (forced co-diagnosis) | {len(rep['cross_threat_subsumption'])} rule pairs |",
        f"| Antecedent terms shared by more than one threat | {len(rep['shared_antecedents'])} |",
        f"| Vocabulary used by rules / gates only / unused | {len(voc['used_by_rules'])} / {len(voc['gate_only'])} / {len(voc['unused'])} of {voc['total']} |",
        f"| (threat, antecedent) links with a cited source | {lit['sourced_links']}/{lit['antecedent_links']} |",
        f"| Rules with a literature reference | {lit['rules_with_literature']}/{lit['rules_total']} |",
        f"| Observation terms with an operational definition | {lit['terms_with_definition']}/{lit['terms_total']} |",
        "",
        "## Shared antecedents",
        "",
        "A term used by several threats cannot discriminate between them on its own.",
        "",
        "| Term | Threats using it |",
        "|:---|:---|",
    ]
    L += [f"| `{a}` | {', '.join(ts)} |" for a, ts in rep["shared_antecedents"].items()]
    for tier in ("tier1", "tier2"):
        L += ["", f"## Pairwise rule overlap ({tier.replace('tier', 'Tier-')}, Jaccard > 0)", "",
              "| Threat pair | Shared antecedents | Jaccard |", "|:---|:---|:---:|"]
        L += [f"| {r['pair'][0]} / {r['pair'][1]} | {', '.join(f'`{s}`' for s in r['shared'])} | {r['jaccard']:.3f} |"
              for r in rep[f"overlap_{tier}"] if r["jaccard"] > 0]
    if rep["cross_threat_subsumption"]:
        L += ["", "## Cross-threat subsumption", "", "| Firing rule | Forces | Threats |", "|:---|:---|:---|"]
        L += [f"| {h['firing_rule']} | {h['forces']} | {' → '.join(h['threats'])} |" for h in rep["cross_threat_subsumption"]]
    L += ["", "## Vocabulary not used by any rule or gate", "",
          "These terms can be recorded but never change a diagnosis.", "",
          ", ".join(f"`{t}`" for t in voc["unused"]) or "_none_"]
    if lit["unsourced_links"]:
        L += ["", "## Antecedent links without a cited source", "",
              ", ".join(f"`{x}`" for x in lit["unsourced_links"])]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    rep = run()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "kb_verification.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    write_markdown(rep, os.path.join(RESULTS_DIR, "kb_verification.md"))
    print("Written: results/kb_verification.json, results/kb_verification.md")
