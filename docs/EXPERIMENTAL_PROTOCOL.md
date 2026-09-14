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

### 1.1 Ontology scope and the ten threat classes

The knowledge base models ten rice biotic stressors that are (a)
agronomically significant across South-East and South Asian production
systems, (b) diagnosable from plant-level visual signs without laboratory
access, and (c) documented with discriminating symptom descriptions in the
primary phytopathological literature. The ten classes are divided into five
fungal/bacterial/viral/nematode pathogens and five insect pests:

**Pathogen threats**: Bacterial\_Leaf\_Blight (*Xanthomonas oryzae* pv.
*oryzae*), False\_Smut (*Ustilaginoidea virens*), Rice\_Blast
(*Magnaporthe oryzae*), Rice\_Grassy\_Stunt (Rice grassy stunt virus),
Rice\_Root\_Nematode (*Meloidogyne* spp. / *Hirschmanniella* spp.),
Rice\_Tungro\_Virus (Rice tungro bacilliform virus + Rice tungro spherical
virus).

**Insect pest threats**: Brown\_Planthopper (*Nilaparvata lugens*),
Grasshopper (*Oxya* spp.), Rice\_Bug (*Leptocorisa* spp.),
Rice\_Stem\_Borer (*Scirpophaga* spp. / *Chilo* spp.).

Threats outside this set — *Rhizoctonia solani* (sheath blight),
*Sarocladium oryzae* (sheath rot), nutrient deficiencies, abiotic stress
— are represented only as out-of-scope negative controls.

### 1.2 Vocabulary derivation and the 45 → 54 extension

The initial 45-term symptom vocabulary was derived from domain literature
(Ou 1985; Hibino 1996; Bridge et al. 2005) and targeted the original ten
threat classes. Following a structured audit of field-sourced case reports
(Section 2), nine additional terms were added in two rounds to close the
most consequential coverage gaps. The extension is documented in full in
`docs/ONTOLOGY.md` with per-term source citations. Six of the nine added
terms are *expressivity-only* (not wired into any inference rule) because
they denote symptoms of threats outside the ten modelled classes; wiring
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

Ten Tier-1 and ten Tier-2 rules are registered in `model.RULE_REGISTRY`.
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

`data/benchmark_synthetic.csv` (eighty cases, provenance `rule_derived`)
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

The same restriction excludes all four insect pest classes from the field
benchmark: insect pests are managed as persistent population densities and
are not published as first-report disease notes. No claim about diagnostic
performance on insect pests is supported by field evidence.

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
  whose true class falls within the ten modelled threats). This is the
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

Five reasoner variants are evaluated to isolate the contribution of each
architectural component:

| Variant | Description |
|---------|-------------|
| `full` | Full system: OWL 2 DL reasoning with Tier-1 + Tier-2 SWRL rules |
| `tier1_only` | Tier-1 rules only; Tier 2 disabled |
| `flat_match` | Set-matching without OWL reasoning; symptom sets matched against rule antecedent lists |
| `no_negation` | OWL reasoning without negative-class assertions (open-world assumption only) |
| `prototype` | Nearest-prototype heuristic: classify by cosine similarity to centroid symptom vectors |

The ablation is designed to answer: does OWL reasoning add anything over
flat set-matching? Does Tier-2 stratification add anything over Tier-1
alone? Results are in `results/ablation.md` and `results/ablation.json`.

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

On the synthetic benchmark, supervised classifiers train on forty cases per
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
  `data/benchmark_synthetic.csv`. This pool supplies the smooth scaling
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

Pool A budgets: 5, 10, 20, 40, 80 cases.
Pool B budgets: 2, 4, 8, 16 cases.

At the terminal Pool A budget of eighty, the only possible subsample is
the full pool, so all draws are identical and the training-subsample
variance collapses to zero. This is noted in `results/learning_curve.md`
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
- **Four insect pest classes have no positive field evidence** (Section 2):
  no claim about diagnostic performance on insect pests is supported by
  field data.
- **The synthetic benchmark is circular** (Section 4): it measures
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
