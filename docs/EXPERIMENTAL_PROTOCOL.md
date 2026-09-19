# Experimental Protocol

> **This document is hand-written and must remain metric-free.**
> All quantitative results are stored in `results/*.json` and indexed in
> `docs/RESULTS_INDEX.md`, which is generated automatically.
> Do not inline any numerical figure here.

This document describes *what* was done and *why* at each stage of the
RiceKG study. It is written at the level of a manuscript Methods section
and is intended to be stable across rule revisions; the companion file
`docs/RESULTS_INDEX.md` carries the corresponding numbers.

---

## 1. Knowledge Base Construction

### 1.1 Ontology scope and the six diagnosable classes

The knowledge base diagnoses six rice disease classes that are (a)
agronomically significant across South-East and South Asian production
systems, (b) diagnosable from plant-level visual signs without laboratory
access, (c) documented with discriminating symptom descriptions in the
primary phytopathological literature, and (d) represented by at least one
independent peer-reviewed field case (Section 2). The six are five
pathogen-caused diseases and one plant-parasitic nematode:

Bacterial\_Leaf\_Blight (*Xanthomonas oryzae* pv. *oryzae*), False\_Smut
(*Ustilaginoidea virens*), Rice\_Blast (*Magnaporthe oryzae*),
Rice\_Grassy\_Stunt (Rice grassy stunt virus), Rice\_Tungro\_Virus (Rice
tungro bacilliform virus + Rice tungro spherical virus), and
Rice\_Root\_Nematode (*Meloidogyne graminicola*, the species in every field
case for this class).

**Scope narrowing.** The knowledge base originally also diagnosed four insect
pests (Brown\_Planthopper, Grasshopper, Rice\_Bug, Rice\_Stem\_Borer). They
were removed from the diagnostic scope because the evidence pipeline of
Section 2 cannot supply field cases for them (see `docs/ONTOLOGY.md`, Part 5).
Their damage vocabulary is retained: when no in-scope rule fires and at least
two distinct insect-specific signs (the organism, its eggs, or a feeding
mechanism no pathogen reproduces) are observed, the system returns an explicit
"insect damage, outside diagnostic scope" response rather than a silent
`No_Diagnosis`. Non-specific signs shared with pathogens or abiotic stress,
such as general yellowing or empty grains, never trigger that response. The
planthopper and leafhopper remain in the vocabulary as vector sightings for
the two viral diseases.

Threats outside this set — *Rhizoctonia solani* (sheath blight),
*Sarocladium oryzae* (sheath rot), nutrient deficiencies, abiotic stress
— are represented only as out-of-scope negative controls.

### 1.2 Vocabulary derivation and the 45 → 54 extension

The initial 45-term symptom vocabulary was derived from domain literature
(Ou 1985; Hibino 1996; Bridge et al. 2005) and targeted the original ten
threat classes, including the four insect classes later removed from scope. Following a structured audit of field-sourced case reports
(Section 2), nine additional terms were added in two rounds to close the
most consequential coverage gaps. The extension is documented in full in
`docs/ONTOLOGY.md` with per-term source citations. Six of the nine added
terms are *expressivity-only* (not wired into any inference rule) because
they denote symptoms of threats outside the modelled classes; wiring
them would manufacture false positives. Three terms were added as rule
antecedents: `Water_Soaked_Lesions`, `Excessive_Tillering`, and
`Orange_Leaf_Discoloration`.

Every vocabulary decision is recorded in `data/symptom_mapping.csv`
alongside its justification and the source sentence that motivated it.

### 1.3 SWRL rule authoring and the two-tier stratification

Inference rules are expressed in Semantic Web Rule Language (SWRL) and
executed by the Pellet DL reasoner over an OWL 2 Description Logic
knowledge base. Rules are stratified into two tiers:

- **Tier 1 (Pathognomonic / Canonical)**: high-cardinality antecedent sets
  (four to seven symptoms). A Tier-1 match asserts `hasConfirmedThreat`,
  indicating that the observed symptom combination is considered
  definitively diagnostic in the literature.
- **Tier 2 (Relaxed Composite)**: low-cardinality antecedent sets (two to
  three symptoms). A Tier-2 match asserts `hasSuspectedThreat`, a sub-property
  of `hasThreat`, indicating a probable but not pathognomonic finding.

The stratification is designed for field scouting scenarios in which a
scout observes some but not all canonical signs. Its valid scientific
contribution is *epistemic* (distinguishing confirmed from suspected
findings) rather than *probabilistic* (see Section 5 and
`docs/LIMITATIONS.md` Section 5 for the calibration rejection).

Six Tier-1 rules and twelve Tier-2 rules are registered in
`model.RULE_REGISTRY`: one Tier-1 and one composite Tier-2 rule per diagnosable class, plus six
single-sign diagnostic rules added in ruleset v2.4.0 (`docs/ONTOLOGY.md`). The eight rules of the
removed insect classes were deleted without renumbering the survivors.
`tests/test_p0_2_ablation.py` enforces these counts as a CI invariant, so
a future rule addition or deletion will break the build rather than
propagate silently.

### 1.4 The subsumption defect and its resolution

In the initial engineering, Tier-2 antecedents were a strict subset of
Tier-1 antecedents for every rule pair. Under Horn-clause semantics this
made Tier-1 rules logically redundant: any case that satisfied the
higher-cardinality Tier-1 set necessarily satisfied the lower-cardinality
Tier-2 set first. Both tiers fired, but Tier 1 added no information to the
inferred threat set. The defect was detected during benchmark development
and resolved by assigning distinct consequents (`hasConfirmedThreat` for
Tier 1 vs `hasSuspectedThreat` for Tier 2), which made the tiers
genuinely complementary. The full account is in `docs/LIMITATIONS.md`
Section 5 and `docs/ONTOLOGY.md`.

---

## 2. Benchmark Construction

### 2.1 The synthetic rule-derived set: tier structure T1–T6

`data/verification_suite.csv` (eighty cases, provenance `rule_derived`)
is derived mechanically from `RULE_REGISTRY`. It is structured into six
tiers:

| Tier | Construction | Purpose |
|------|-------------|---------|
| T1 | Exact Tier-1 antecedent set | Verifies Tier-1 rules fire |
| T2 | Exact Tier-2 antecedent set | Verifies Tier-2 rules fire |
| T3 | Disjoint antecedent union across two threats | Tests multi-label output |
| T4 | T2 set with distractor symptoms added | Tests specificity under noise |
| T5 | Partial (strict) subset of T1 | Tests Tier-2 fires when Tier-1 does not |
| T6 | Symptoms from no rule antecedent | Negative-control (No\_Diagnosis) |

This set is legitimate for verifying that rule firing is deductively
consistent. It is not a diagnostic performance benchmark: its cases were
generated from the antecedents the reasoner executes, so revising those
antecedents necessarily changes agreement. Both this design and its
consequences are documented in `docs/LIMITATIONS.md` Section 4.

### 2.2 The independent field set: source restriction

`data/benchmark_field.csv` is restricted to peer-reviewed case reports
with laboratory-confirmed identification. Accepted source types are
*Plant Disease* Disease Notes (APS), *New Disease Reports* (BSPP), and
comparable first-report or diagnostic-note sections in peer-reviewed
journals. The following source types are explicitly excluded:

- Reviews and population-genetics studies (symptom text is textbook
  description, not a reported observation)
- Efficacy, management, or control trials (symptoms are incidental or
  induced)
- Caged infestation experiments (artificial field conditions)
- Conference papers and preprints
- Sources where the diagnosis was stated but no symptom sentence was
  observed and can be pointed to

The same restriction yields no field case for any insect pest: insect pests
are managed as persistent population densities and are not published as
first-report disease notes. This is why the four insect classes were removed
from the diagnostic scope (Section 1.1) rather than evaluated on
rule-derived cases alone.

Rejected candidates are preserved with per-row stated reasons in
`data/rejected_field_candidates.csv`. The gate is enforced by
`tests/test_p0_5_field.py`.

### 2.3 The verbatim extraction gate

Every field case must carry a `raw_symptom_text` cell containing a span
copied verbatim from the fetched source. Paraphrased or composed symptom
descriptions are grounds for rejection. The gate was applied in two stages:

- **Stage A**: for each candidate, fetch the paper, record `raw_symptom_text`
  verbatim, note `doi`, `location`, `observation_date`, and
  `ground_truth_method` (lab\_confirmed or expert\_visual).
- **Stage B**: map the verbatim text to ontology symptom terms
  (`symptom_1` … `symptom_6`). Mapping is done separately from extraction
  to prevent the symptom vocabulary from contaminating the source selection.

### 2.4 Crossref DOI verification

Every DOI in `data/benchmark_field.csv` is verified against the Crossref
API by `analysis/verify_citations.py`. The script asserts HTTP 200 and
checks that the title returned by Crossref appears verbatim (modulo
whitespace and case) in the `citation` column. DOIs that fail this gate
are removed from the benchmark, not corrected. The Crossref User-Agent is
`RiceKG-CitationVerifier/1.0`.

### 2.5 DOI-level dev/eval partitioning

The field benchmark is partitioned at the DOI level: both rows from the
same paper must fall in the same split to prevent information leakage
across the partition boundary. The split is stratified by diagnosis class
to the extent possible given the small case count. The `dev` split was
visible during rule and vocabulary work; the `eval` split's individual
cases were not inspected during that work, though aggregate `eval` scores
were observed across two revision rounds. Consequently, `eval` figures are
development-informed rather than strictly held out. This downgrade is
documented in `docs/LIMITATIONS.md` Section 2.

### 2.6 Rejection criteria

A candidate is rejected and moved to `data/rejected_field_candidates.csv`
if any of the following applies:

- The DOI does not resolve to HTTP 200 on Crossref
- The Crossref title does not appear in the citation text
- The paper contains no observable symptom span (review, methods section,
  generic species description)
- The symptom text is a textbook description rather than an observed case
- The source is a preprint or conference paper
- The paper shares a DOI with another accepted case across the
  dev/eval boundary

---

## 3. Evaluation Protocol

### 3.1 Multi-label metrics

Each case may carry zero or more ground-truth diagnosis labels. The
reasoner's output is a set of predicted labels for each case. Three metrics
are reported:

- **Positive-case recall**: the fraction of ground-truth labels recovered
  across in-scope positive cases (those whose truth set is non-empty and
  whose true class falls within the six diagnosable classes). This is the
  headline metric because it measures whether the system actually identifies
  the threat.
- **Exact match**: the fraction of cases for which the predicted label set
  equals the truth set exactly. This penalises any over- or under-prediction
  and is the most conservative metric.
- **Micro-F1**: harmonic mean of micro-precision and micro-recall across all
  label positions. This is a compromise metric sensitive to class imbalance.

Exact match is not the headline metric despite being the most commonly
reported set-matching figure, because on a benchmark where the majority of
cases are negative controls, returning `No_Diagnosis` for every case
achieves high exact match trivially. Positive-case recall cannot be gamed
the same way.

### 3.2 5×2-fold cross-validation

For supervised baselines evaluated on the field benchmark, a 5×2-fold
protocol is used: five replications of 2-fold stratified cross-validation.
This protocol was chosen because the benchmark is too small for a standard
k-fold. The folds are stratified by diagnosis class to the extent class
frequency allows. With only twenty-three evaluation cases, each fold
contains at most two positive class instances for the rarest threats, and
some folds contain zero. This fold-level class sparsity is the reason
supervised baselines report zero positive recall on the field benchmark's
`eval` split under the 5×2-fold protocol, not model incompetence. This is a
*protocol artifact*, not a finding about the models. The learning-curve
experiment (Section 6), which trains and tests on a different budget and
population, does not replicate the 5×2-fold protocol artifact.

### 3.3 Statistical tests

Pairwise comparisons between the full RiceKG system and each baseline use
McNemar's test on per-case exact-match outcomes, corrected for multiple
comparisons with the Holm-Bonferroni procedure. Because the field benchmark
is small, the minimum detectable effect at α = 0.05 with 80% power is
substantial; the exact value is recorded in `docs/LIMITATIONS.md` Section
2. Differences below that threshold are underpowered and should not be
interpreted as evidence of equivalence.

### 3.4 Bootstrap confidence intervals

Non-parametric bootstrap confidence intervals (B = 1,000 resamples) are
computed for micro-F1 and positive-case recall. Cases are resampled with
replacement at the case level. The 95% CI is the 2.5th and 97.5th
percentiles of the bootstrap distribution. The coarse step size of the
field set's positive-case recall (one missed or recovered case shifts recall
by a full quantisation step) means these intervals are wide and should be
read as such.

---

## 4. Ablation Design

`analysis/ablation.py` answers three questions, all on the field benchmark (expert-consensus
encoding) or generated cases; the verification suite is used only as input to part A.

**A. Does the DL reasoner change any diagnosis?** Pellet (`model.predict_diseases`) and a pure
set-matching implementation of the same rules are compared on the full graded output (threat and
grade, including `possible` and out-of-scope responses) for every field case and every
verification-suite case, with per-case latency. This is an equivalence check, not an accuracy
comparison.

**B. What does each rule component contribute on field evidence?** Rule-base variants, run by set
matching (equivalent to Pellet by A) and scored with the graded outcomes of
`analysis/graded_evaluation.py`, with exact McNemar tests against the full system:

| Variant | Description |
|---------|-------------|
| `full` | Ruleset v2.4.0: Tier-1, composite Tier-2 and diagnostic-sign Tier-2 rules, out-of-scope gates |
| `no_diagnostic_signs` | Without the single-sign Tier-2 rules `SWRL-R21`–`R26` |
| `tier1_only` | Tier-1 rules only |
| `no_scope_gates` | Without the insect and non-modelled-pathogen out-of-scope gates |

**C. Robustness.** The first three variants on the occlusion sweep of
`analysis/degradation_curve.py` (same generator settings and seeds).

---

## 5. Baseline Protocol

### 5.1 Model set

Five supervised classifiers are evaluated as baselines: Decision Tree,
Random Forest, Multinomial Naive Bayes, k-Nearest Neighbours, and Logistic
Regression (one-versus-rest). All are implemented via scikit-learn with
default hyperparameters, without tuning, to reflect the cold-start scenario
the knowledge base targets.

Two additional rule-based baselines are included: `Rule: Flat Single-Tier`
(identical to the `flat_match` ablation variant) and `Rule: Nearest
Prototype` (ontology-free symptom-count heuristic).

### 5.2 Training budgets and encoding

On the verification suite, supervised classifiers train on forty cases per
fold (half of eighty). On the field benchmark, the 5×2-fold protocol
allocates roughly eleven training cases per fold (half of twenty-three).

Features are binary indicator vectors of length equal to the symptom
vocabulary size. The symptom order is governed by `ml_baselines.SYMPTOM_ORDER`,
which tracks `model.ALL_SYMPTOMS`; `tests/test_p0_4_baselines.py` enforces
their correspondence as a CI invariant.

Multi-label output is handled by scikit-learn's `MultiOutputClassifier`
wrapper. No threshold tuning is applied; the classifier's default decision
boundary is used throughout.

---

## 6. Learning-Curve Protocol

### 6.1 The two pools

The learning-curve experiment uses two training pools:

- **Pool A**: the eighty synthetic rule-derived cases from
  `data/verification_suite.csv`. This pool supplies the smooth scaling
  reference. In all pool draws, training cases are drawn from Pool A and
  tested on the field evaluation set; the pool and the test set are
  disjoint by construction. The leakage assertion in
  `analysis/learning_curve.py` enforces this programmatically, and
  `tests/test_learning_curve.py` tests that the assertion triggers if
  the pool and test set overlap.
- **Pool B**: the sixteen real field cases in `data/benchmark_field.csv`
  with `split == dev`. This pool supplies the ecological validity
  reference. As above, draws come from Pool B and are tested on the
  `eval` partition; the two sets are disjoint by the DOI-level
  partitioning.

### 6.2 Training budgets

Pool A budgets: 5, 10, 20, 40 cases, each kept only if smaller than the
pool, followed by the full pool size as the terminal budget.
Pool B budgets: 2, 4, 8, 16 cases.

At the terminal Pool A budget, the only possible subsample is the full
pool, so all draws are identical and the training-subsample
variance collapses to zero. This is noted in `results/REPORT.md#learning-curve`
and must not be presented as if it were a regular confidence interval.

### 6.3 Resampling

At each budget *N*, *R* = 200 draws are taken (stratified by diagnosis
class where possible). For each draw, the supervised models are trained on
the *N* drawn cases and evaluated on the full test set (five positive
disease cases in `eval`). RiceKG is evaluated on the same test set without
training (zero-shot). The *R* point estimates per budget are aggregated to
produce a mean and a training-subsample variance component.

### 6.4 Crossover criterion and the two variance components

A crossover budget *N\** is the smallest budget at which a supervised
model's positive-case recall exceeds RiceKG's zero-shot recall. Two
variance components are reported separately and the crossover criterion is
defined in terms of the *test-set* component:

- **Training-subsample variance**: variance of the model's positive-case
  recall across the *R* draws at a fixed budget. This measures sensitivity
  to which training subset is selected.
- **Test-set sampling variance**: variance that comes from having a small
  test set. Estimated by paired bootstrap over the test cases (resample
  cases with replacement, recompute both ML and RiceKG recall on each
  resample, take the difference). This is the component that determines
  whether an observed margin is real.

A crossover requires the 95% bootstrap confidence interval of the
**test-set paired difference** (ML recall minus RiceKG recall) to exclude
zero. Training-subsample variance alone is not sufficient, because it
narrows as *R* increases regardless of test-set size, making every margin
"significant" at large enough *R*.

---

## 7. Threats to Validity

The following threats are documented in full in `docs/LIMITATIONS.md`;
cross-references are given here:

- **The held-out partition is development-informed** (Section 2): `eval`
  figures should be read as an optimistic bound rather than an independent
  estimate. A fresh held-out partition, sourced after the rule base is
  frozen, is required for a genuinely independent estimate.
- **Insect pests are outside the diagnostic scope** (Section 1.1): the
  system makes no diagnostic claim about them. Its out-of-scope insect
  response is exercised only on rule-derived controls, never on field cases.
- **The verification suite is circular** (Section 4): it measures
  deductive consistency with the rule base, not diagnostic ability.
- **Vocabulary coverage is partial** (Section 3): nine symptom descriptors
  extracted from the field literature remain unmapped; the two discriminating
  signs for the virus classes (`Excessive_Tillering`, `Orange_Leaf_Discoloration`)
  appear in no benchmark case, so those rules cannot fire on the present
  case set.
- **The calibration claim is rejected** (Section 5): tier stratification
  does not provide statistically significant probabilistic calibration.
  Brier-score improvement under out-of-sample cross-validation is
  functionally indistinguishable from zero.
- **The field benchmark is severely underpowered** (Section 2): the minimum
  detectable effect is large enough that most pairwise comparisons between
  RiceKG and ML baselines cannot be distinguished from random variation.

---

## 8. Methodological Corrections During Development

This section collects the formal corrections made during the development of
this system. An AI venue audience should recognise these as evidence of
protocol discipline; each correction pre-empts the objection a reviewer
would otherwise raise.

### 8.1 Tier-1/Tier-2 subsumption defect

**What happened**: In the initial engineering, Tier-2 antecedent sets were
strict subsets of Tier-1 antecedent sets. Under Horn-clause semantics, if
the Tier-2 set is satisfied then the Tier-1 set is also satisfied, making
every Tier-1 rule redundant. Neither tier independently altered the
inferred extension of `hasThreat` beyond what the other alone would infer.

**Detected**: during benchmark development, when the ablation showed that
disabling Tier-1 rules had no measurable effect on any metric.

**Resolved**: consequents were split into distinct sub-properties
(`hasConfirmedThreat` for Tier 1, `hasSuspectedThreat` for Tier 2),
making the two tiers genuinely complementary.

**Documented in**: `docs/LIMITATIONS.md` Section 5, `docs/ONTOLOGY.md`.

### 8.2 The circular first field benchmark

**What happened**: the first field benchmark was constructed by selecting
cases whose symptom text matched Tier-2 rule antecedents verbatim. The
system achieved near-perfect accuracy on this set by construction; the
result contained no information about diagnostic ability.

**Detected**: during the P0-3 gate review, which identified that the
extraction procedure was essentially a lookup against the rule base.

**Resolved**: the benchmark was discarded and rebuilt under the verbatim
extraction gate described in Section 2. Candidates are now drawn from
peer-reviewed case reports and must carry a verbatim observed symptom span.

**Documented in**: `data/rejected_field_candidates.csv`,
`docs/LIMITATIONS.md` Section 4.

### 8.3 Circular calibration

**What happened**: an initial confidence calibration sweep fitted probability
estimates for `hasConfirmedThreat` and `hasSuspectedThreat` on the same
dataset that the Brier score was then evaluated on. The calibration
procedure maximised apparent performance on its own training signal.

**Detected**: during code review, when it was noticed that the Brier score
was computed over the set that supplied the parameters.

**Resolved**: out-of-sample cross-validation was used to estimate the
probability parameters, and the improvement over uncalibrated predictions
was assessed on held-out folds. The improvement was found to be
functionally indistinguishable from zero, and the calibration claim was
formally rejected. This is reported as a negative result.

**Documented in**: `docs/LIMITATIONS.md` Section 5, `docs/ONTOLOGY.md`
"Calibration, and a calibration error".

### 8.4 Withdrawn intermediate rule revision

**What happened**: the first pass of the Tier-2 rule revision specified
`SWRL-R16` (Bacterial\_Leaf\_Blight) as `Water_Soaked_Lesions ∧
Bacterial_Ooze`, and `SWRL-R19` (Rice\_Grassy\_Stunt) as `Stunted_Growth
∧ Leaf_Mottling`. Both antecedent pairs are listed for their respective
diseases in the primary literature. However, bacterial exudate is a
genus-level sign shared with several other *Xanthomonas* and *Burkholderia*
species present in the negative controls, and stunting with mottling is
shared across rice viruses. The revision produced four false positives on
the negative controls.

**Resolved**: rules were re-specified around discriminating signs —
tip-and-margin lesion onset for bacterial blight, excessive tillering for
grassy stunt. False positives returned to zero.

**Lesson**: listing a sign for a disease is not the same as the sign
distinguishing that disease from others in the negative-control set. The
selection criterion for rule antecedents is discriminating specificity, not
mere association.

**Documented in**: `docs/ONTOLOGY.md` "A withdrawn intermediate revision",
`docs/LIMITATIONS.md` Section 1.

### 8.5 P0-5 overfitting signature

**What happened**: the P0-5 vocabulary extension and rule revision (Steps 2
and 3) raised `dev` positive-case recall substantially while leaving `eval`
recall flat to slightly lower. This is the characteristic signature of
overfitting to the visible partition: every individual change was argued
from published agronomy rather than from a benchmark case, yet the gains
were confined to the data that was accessible during the work.

**Consequence**: the `eval` partition's independence was downgraded to
"development-informed". The `eval` figures must be read as an optimistic
bound rather than an independent estimate of diagnostic efficacy.

**Documented in**: `docs/LIMITATIONS.md` Sections 1 and 2,
`docs/ONTOLOGY.md`.

### 8.6 Data rejected under the verbatim extraction gate

Fourteen candidate field cases were excluded from `data/benchmark_field.csv`
after source documents were fetched and found not to contain an observable
symptom span. Reasons include: symptom text is a textbook description of
the pathogen, source is a control-efficacy trial, source is a caged
infestation experiment, and source is a population-genetics study. All
fourteen are preserved with per-row stated reasons in
`data/rejected_field_candidates.csv`. The gate is enforced automatically
by `tests/test_p0_5_field.py`.

---

## 8-F. Probabilistic Reasoning Layer Protocol (noisy-OR)

### 8-F.1 Division of Labor with the OWL Ontology
The noisy-OR probabilistic reasoning layer is complementary to, and strictly separated from, the OWL 2 Description Logic ontology. The probabilistic layer does not write probability values or uncertainty annotations into the OWL ontology and makes no claim of a probabilistic description logic (no P-SHIQ, no PR-OWL). The OWL ontology remains solely responsible for the symptom taxonomy, observation sub-property stratification, defined classes, machine-provable tier subsumption, and deductive proof explanations. The probabilistic layer operates as an independent scoring module to evaluate trade-offs between sensitivity and false alarm rates under partial observation.

### 8-F.2 Mathematical Formulation
Each of the six diagnosable threats $t \in \text{ALL\_DIAGNOSES}$ is modeled as an independent binary hypothesis in a multi-label framework. For each observation $e \in \text{ALL\_SYMPTOMS}$ with an elicited link to $t$:
- $P(e \text{ present} \mid t \text{ present}) = 1 - (1 - \text{leak}_e)(1 - p_{te})$
- $P(e \text{ present} \mid t \text{ absent}) = \text{leak}_e$

Evidence is handled as follows:
- **Observed present signs**: contribute their likelihood ratio $\frac{P(e \mid t)}{P(e \mid \neg t)}$.
- **Unrecorded signs**: are treated as unknown and marginalised out; they contribute nothing to the posterior.
- **Recorded absent signs**: contribute $\frac{1 - P(e \mid t)}{1 - P(e \mid \neg t)}$.
- **Unlinked observations**: contribute nothing to threat $t$.

Prior probabilities are fixed uniformly across all six threats at $P(t) = 0.10$ as a single constant, justified by the absence of epidemiological census data for the benchmark population.

### 8-F.3 Elicitation Protocol and Pre-Fixed Qualitative Scale
Conditional probabilities $p_{te} = P(e \mid t)$ are elicited exclusively from primary phytopathological literature, monographs, and peer-reviewed disease descriptions. Probabilities are never derived from `RULE_REGISTRY` and never estimated from benchmark data. When sources report quantitative frequencies, they are recorded directly as `quantitative`. For qualitative frequency words in primary sources, the mapping scale is fixed a priori before examining literature sources:

| Source Wording (Examples) | Conditional Probability $p_{te}$ |
|:---|:---:|
| characteristic, diagnostic, typical, always | 0.90 |
| common, usually, frequently | 0.70 |
| may, sometimes, often accompanied by | 0.40 |
| occasionally, rarely, in severe cases only | 0.15 |

### 8-F.4 Leak Probability Assignment Policy
Background leak probabilities $\text{leak}_e = P(e \text{ present} \mid \text{none of the six threats})$ represent non-target background rates from unmodeled diseases, abiotic disorders, or environmental context:
- **Sign-specific terms** ($\text{leak} = 0.01$): distinctive morphological hallmarks (e.g. `Hook_Like_Root_Swelling`, `Rusty_Grain_Balls`, `Bacterial_Ooze`) rarely produced outside specific pathogen or insect damage etiologies.
- **Generic phenomenological terms** ($\text{leak} = 0.05$): non-specific signs belonging to general chlorosis, necrosis, or stunting taxonomical categories (e.g. `Yellowing_Leaves`, `Necrotic_Spots`, `Stunted_Growth`) that occur across diverse stresses.
- **Epidemiological context terms** ($\text{leak} = 0.10$): broad stand-level or seasonal conditions (e.g. `Rainy_Season_Outbreak`, `Uniform_Field_Infection`, `Rapid_Disease_Spread`) that are widely distributed in rice-growing environments.

### 8-F.5 Decision Threshold Policy
The primary decision threshold is fixed a priori at $\text{DECISION\_THRESHOLD} = 0.50$. A threat is predicted if $P(t \mid E) \ge 0.50$. A full trade-off curve across a fixed grid of thresholds from 0.05 to 0.95 in steps of 0.05 is evaluated to characterize operating trade-offs.

### 8-F.6 Sensitivity and Robustness Protocol
To assess sensitivity to elicitation choices:
1. **Probability perturbation**: shifting every $p_{te}$ by $-0.10$ and $+0.10$ (clipped to $[0.01, 0.99]$).
2. **Alternative scale**: evaluating the alternative qualitative scale $\{0.95, 0.80, 0.50, 0.20\}$.
3. **Leak perturbation**: scaling all leak values by $\times 0.5$ and $\times 2.0$.
Any finding that reverses within these sensitivity spans is reported as inconclusive.

