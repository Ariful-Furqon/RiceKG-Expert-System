# Evaluation Framework

RiceKG is a deterministic, untrained, rule-based expert system whose output is graded
(`confirmed`, `suspected`, `possible`), can abstain, and can reject a case as out of scope, and
every diagnosis carries a derivation trace. This document says how such a system is evaluated
here, and why the confusion-matrix protocol used for the supervised baselines is not its headline
measure.

## Why not a cross-validated confusion matrix

A confusion matrix scores each output as right or wrong against a label. For RiceKG this is
insufficient in four ways.

1. **Cross-validation has nothing to train.** RiceKG gives the same output for a case whatever
   fold it sits in, so a 5×2-fold average only re-weights a fixed set of outputs. When one negative
   control (FIELD_24) was rejected in ontology v2.2.0, the fold-averaged positive recall moved from
   35.00% to 31.67% although no diagnosis changed. Cross-validation is kept only where something is
   trained: the supervised baselines.
2. **The grades disappear.** A `confirmed` and a `possible` output count the same, so the table
   cannot show whether the grades mean anything.
3. **Errors are not equal.** Naming the wrong disease (a misfire) can lead to a wrong pesticide;
   abstaining or rejecting a case as out of scope is a safe failure. Accuracy treats them alike.
4. **Aggregate accuracy is dominated by controls.** 17 of the 22 `eval` cases are negative
   controls on which `No_Diagnosis` is correct.

The confusion-matrix figures remain in [`results/baselines.md`](../results/baselines.md), where they
compare RiceKG with the supervised models under one common protocol.

## The framework

Evaluation follows the verification-and-validation split used for knowledge-based systems:
*verification* asks whether the knowledge base was built right, and *validation* asks whether it
gives the right answers.

| Part | Question | Evidence | Status |
|---|---|---|---|
| V1. Knowledge-base verification | Is the rule base consistent, non-redundant and grounded? | [`results/kb_verification.md`](../results/kb_verification.md) | Done |
| V2. Competency | Can the ontology answer the questions it was built for? | [`docs/COMPETENCY_QUESTIONS.md`](COMPETENCY_QUESTIONS.md) | Done |
| A1. Validation against field ground truth | On published cases, does it name the right disease, and how does it fail? | [`results/graded_evaluation.md`](../results/graded_evaluation.md) | Done |
| A2. Validation against experts | Given the same text, does it agree with agronomists as often as they agree with each other? | [`results/expert_validation.md`](../results/expert_validation.md) | Done (2 raters) |
| A3. Explanation quality | Do experts judge the derivation trace correct and useful? | [`results/expert_validation.md`](../results/expert_validation.md) | Done (2 raters) |
| R. Robustness | How does performance fall as observations go missing? | [`results/degradation_curve.md`](../results/degradation_curve.md) | Done |
| C. Comparison | How do baselines do under the same protocol? | [`results/graded_evaluation.md`](../results/graded_evaluation.md) (rule baselines); [`results/learning_curve.md`](../results/learning_curve.md) (ML trained on `dev`, tested on `eval`) | Done |

### V1. Knowledge-base verification

No test cases are needed. The checks are: logical consistency under Pellet; that every Tier-2
antecedent set lies inside its Tier-1 set, so a confirmed diagnosis implies the suspected one;
that no rule for one threat contains another threat's rule, which would force a co-diagnosis;
which antecedents several threats share and how much rules overlap (Jaccard); which vocabulary
terms no rule or gate uses; and what share of antecedent links cite a source.

### A1. Graded case-level validation

Every system runs once on every case. Each case receives one outcome:

| Positive case (true threat *T*) | Negative control |
|---|---|
| `correct`: *T* committed (confirmed or suspected) | `false_alarm`: a threat committed |
| `misfire`: another threat committed, *T* not | `possible_alarm`: only `possible` output |
| `possible_hit`: *T* only at `possible` | `explicit_rejection`: out-of-scope message |
| `possible_miss`: only other threats at `possible` | `silent_abstention`: no output |
| `rejected`: out-of-scope message | |
| `abstain`: no output | |

Reported per split, each as a count with an exact Clopper–Pearson 95% interval:

- **Committed recall** — share of positive cases with the true disease committed.
- **Recall including `possible`** — what the weakest grade adds.
- **Misfire rate** — share of positive cases where a wrong disease was committed.
- **Committed precision** — share of committed diagnoses that are correct, over all cases.
- **Precision by grade** — the grades are valid only if precision falls from `confirmed` to
  `suspected` to `possible`.
- **False-alarm rate** on controls, committed and including `possible`.
- **Explicit-rejection rate** on controls — how often the system says *why* it declines.

Systems are compared on the same cases with an exact McNemar test on per-case success
(positive: `correct`; control: no committed alarm).

### A2 and A3. Expert-based validation

Two or three agronomists read each case's symptom text with disease and pathogen names
redacted, and independently:

1. **encode the symptoms** with the ontology vocabulary and its definitions (validates the input
   step; agreement per term);
2. **give a diagnosis** from the in-scope classes, "other/out of scope" or "cannot decide"
   (inter-expert Fleiss' κ is the ceiling a system can be expected to reach; system–expert
   agreement is compared with it);
3. **rate the RiceKG derivation trace** for each case on correctness, completeness and usefulness.

The criterion for A2 is whether system–expert agreement falls within the range of
expert–expert agreement, not whether it matches the published label.

## Current findings (RiceKG strict, `eval` / `dev`+`eval`)

- Committed recall **2/5** / **6/12**, with no misfire and no false alarm on 17 / 26 controls.
  Every committed diagnosis is correct (2/2, 6/6).
- **No field case reaches `confirmed`.** Every correct diagnosis comes from a Tier-2 rule, so the
  Tier-1 rules are untested on field evidence.
- The `possible` grade raises recall to 5/5 / 11/12 but fires on 8/17 / 10/26 controls, and only
  5 of its 23 `dev`+`eval` candidates are correct. It is a screening aid, not a diagnosis.
- `Necrotic_Spots` is a Tier-1 antecedent of four threats, three of them without a cited source,
  and 10 vocabulary terms are used by no rule or gate — including `Bacterial_Ooze`, a recognized
  sign of bacterial leaf blight.

Expert-based validation (two agronomists, all 56 cases; [`results/expert_validation.md`](../results/expert_validation.md)):

- The raters agree with each other at Cohen's κ = 0.885; RiceKG agrees with them at κ ≈ 0.29
  (difference −0.595, 95% CI −0.741 to −0.442). From the same redacted text the raters name the
  published disease in 26/30 and 25/30 positive cases; RiceKG in 11/30.
- The raters' symptom encodings agree closely (mean Jaccard 0.929), but the authors' benchmark
  encoding matches the rater consensus in only 28/56 cases (mean Jaccard 0.685). The authors
  added terms the text does not support mostly among the shared, weakly discriminating
  antecedents (`Yellowing_Leaves` 9 cases, `Stunted_Growth` 5, `Necrotic_Spots` 4).
- Every correct RiceKG diagnosis and every explicit out-of-scope rejection was judged acceptable
  by both raters; silent abstentions were judged least useful (mean 1.98 of 5).

With two raters there is no Fleiss' κ and no strict majority beyond agreement of both.

The `eval` split is development-informed and `holdout` is development-exposed
([`LIMITATIONS.md`](LIMITATIONS.md) Section 2); none of these figures is a strictly held-out estimate.
