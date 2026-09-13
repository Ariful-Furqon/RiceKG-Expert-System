# Design Science Research Mapping

This document positions RiceKG within Design Science Research (DSR), which is the appropriate
frame for an artefact-producing study submitted to *Acta Informatica Pragensia*. It maps the work
onto the six activities of the Peffers et al. (2007) Design Science Research Methodology and onto
Hevner et al.'s (2004) seven guidelines, and states plainly where the artefact currently falls
short of each.

## The three DSR components

**Artefact.** An OWL 2 DL ontology of rice biotic threats (54 symptom terms, 10 threat classes),
a stratified SWRL rule base of 20 rules divided into pathognomonic Tier-1 and relaxed Tier-2 rules,
a Pellet-backed reasoning service returning confidence-graded and rule-traced diagnoses
(`model.predict_diseases`), and a Flask interface for symptom selection. In Hevner's typology this
is an *instantiation* carrying an embedded *model* (the ontology) and *method* (the graded
inference procedure).

**Environment.** Smallholder rice production and the agricultural extension services that support
it, in Indonesia specifically. The people in this environment are extension officers who scout
fields and advise farmers, agronomists who hold diagnostic expertise and cannot be present at every
field, and farmers who observe symptoms daily but lack the vocabulary to name them. The pressing
organisational problem is not an absence of diagnostic knowledge; it is that the knowledge is
concentrated in scarce experts and transferred through in-person visits that do not scale.

**Knowledge base.** Rice phytopathology and nematology (Ou 1985; Hibino 1996; Bridge et al. 2005;
IRRI Rice Doctor), and semantic web methods: description logic, SWRL, ontology engineering
methodology (Grüninger & Fox), and the explainable-AI literature on explanation satisfaction and
appropriate reliance.

## Peffers et al. DSRM activities

### 1. Problem identification and motivation

Rice pest and disease diagnosis in smallholder systems depends on expert judgement that is scarce,
slow to reach the field, and undocumented in machine-readable form. Misdiagnosis carries direct
economic cost through yield loss and inappropriate pesticide application, and the latter carries
environmental and health externalities borne by the farming household.

### 2. Objectives of a solution

- Codify expert diagnostic knowledge so that it can be applied without an expert present.
- Operate with **zero training data**, since labelled field datasets for Indonesian rice systems do
  not exist at usable scale.
- Produce **auditable derivations**: every diagnosis names the rules that fired, the symptoms that
  satisfied them, and the antecedents left unmet.
- Distinguish **confirmed from suspected** diagnoses, so that a partial observation does not carry
  the authority of a complete one.

Objectives one to four are met by construction. Diagnostic accuracy on independent cases was *not*
adopted as an objective the artefact currently meets — see activity 5.

### 3. Design and development

Recorded in the repository's own history rather than reconstructed after the fact. The significant
design decisions and their corrections:

| Decision | Outcome |
|:--|:--|
| Two-tier rule stratification | Initially defective: Tier-2 antecedents were strict subsets of Tier-1 asserting the same consequent, making Tier 1 logically redundant. Corrected in P0-1 by splitting the consequent into `hasConfirmedThreat` and `hasSuspectedThreat`. |
| Declarative rule registry | `RULE_REGISTRY` with `build_ontology(enabled_tiers=...)` per isolated world, enabling genuine ablation (P0-2). |
| Vocabulary scope | Extended from 45 to 54 terms in P0-5 on literature grounds; six of the nine additions are expressivity only. Documented in `docs/ONTOLOGY.md`. |
| Tier-2 antecedent design | Three rules depended on observing an insect vector rather than a plant sign; revised in P0-5. A first revision pass was withdrawn after it produced false positives by using genus-level rather than discriminating signs. |

### 4. Demonstration

The artefact runs end to end: `make reproduce` regenerates every reported figure, and the Flask
interface performs live diagnosis. Demonstration is *not* evidence of utility, and is not presented
as such here.

### 5. Evaluation

Evaluation is deliberately separated into two benchmarks that are never pooled.

- `data/benchmark_augmented.csv` (n=80, `rule_derived`) verifies deductive consistency only. Its
  score moved from 92.50% to 60.00% when the rules were revised without the data being touched,
  which demonstrates directly that it measures agreement with the rule base rather than diagnostic
  ability.
- `data/benchmark_field.csv` (n=39, observed-case reports) is the empirical benchmark. On the
  `eval` partition RiceKG reaches 35.00% positive-case recall over 5 in-scope cases.

Against Hevner's evaluation guideline this is the artefact's weakest point, and the honest summary
is: **utility is not yet demonstrated**. The ontology-free nearest-prototype baseline is not
cleanly beaten, four of ten threat classes have no field case, the `eval` partition has been
downgraded to development-informed, and the minimum detectable effect (±29.5 points) exceeds any
difference the study could plausibly detect. `docs/LIMITATIONS.md` carries the detail.

### 6. Communication

This repository, the generated result artefacts under `results/`, and the manuscript in preparation.
Every figure quoted in documentation is regenerated by a script and gated by
`analysis/check_readme_consistency.py` in CI.

## Hevner et al. seven guidelines

| # | Guideline | Status |
|:--|:--|:--|
| 1 | **Design as an artefact** | Met. A running instantiation with an embedded ontology and inference method. |
| 2 | **Problem relevance** | Met. Expert scarcity in smallholder extension is a documented organisational problem; see `docs/SOCIOTECHNICAL_FRAMING.md`. |
| 3 | **Design evaluation** | **Partially met.** Descriptive and computational evaluation are thorough; observational and experimental evaluation with real users has not been performed. Instruments for it are the subject of P1-6 and P1-7. |
| 4 | **Research contributions** | **Qualified.** The contribution is the codified, auditable knowledge structure and the negative methodological findings — that a subsumption-defective tier design asserts nothing, that a rule-derived benchmark cannot evidence diagnostic ability, and that literature-justified remediation need not transfer to held-out cases. Predictive superiority is not claimed. |
| 5 | **Research rigour** | Met on the construction side: declarative rule registry, isolated reasoning worlds, real-reasoner ablation, a peer-reviewed case-report gate with Crossref verification, and dev/eval partitioning. Weak on the evaluation side because of sample size. |
| 6 | **Design as a search process** | Met and documented. The withdrawn Tier-2 revision in `docs/ONTOLOGY.md` is an explicit record of a search step that failed and was reversed. |
| 7 | **Communication of research** | Met for the technical audience. The managerial audience is addressed in `docs/SOCIOTECHNICAL_FRAMING.md`. |

## What would strengthen the DSR claim

1. A field benchmark with 15–20 verified positive cases per threat class, sourced after the rule
   base is frozen, restoring a genuinely independent evaluation.
2. The explainability study (P1-6): whether the rule trace changes an extension officer's decision
   accuracy and reliance compared with a black-box prediction.
3. The usability and adoption study (P1-7), supplying the observational evaluation Hevner's
   guideline 3 requires.

## References

- Peffers, K., Tuunanen, T., Rothenberger, M.A. & Chatterjee, S. (2007). A Design Science Research
  Methodology for Information Systems Research. *Journal of Management Information Systems*
  24(3):45–77.
- Hevner, A.R., March, S.T., Park, J. & Ram, S. (2004). Design Science in Information Systems
  Research. *MIS Quarterly* 28(1):75–105.
- Grüninger, M. & Fox, M.S. (1995). Methodology for the Design and Evaluation of Ontologies.
  *IJCAI Workshop on Basic Ontological Issues in Knowledge Sharing*.
