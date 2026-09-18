# Scientific Positioning: Accuracy, Explainability, and What the Evidence Supports

On the `eval` partition of the field benchmark ([`data/benchmark_field.csv`](../data/benchmark_field.csv),
*n*=22, of which 5 are in-scope disease cases), RiceKG commits to the correct disease in **2/5** positive
cases (exact 95% CI 5.3–85.3%), never names a wrong disease, and raises no false alarm on the
17 negative controls ([`results/graded_evaluation.md`](../results/graded_evaluation.md)). Under the
5×2-fold protocol used for the ML comparison the same outputs average to **31.67%** positive recall and a
micro-F1 of **41.00** [95% CI 33.3, 75.7]. Its aggregate exact match of 86.36% is not a diagnostic
result: 17 of the 22 cases are out-of-scope negative controls on which returning `No_Diagnosis` is
correct. Across both partitions RiceKG resolves **6 of 12** positive cases. **Diagnostic efficacy on
authentic field cases is not established**, and the `eval` figures are themselves
development-informed rather than strictly held out — see [`docs/LIMITATIONS.md`](LIMITATIONS.md)
Section 2 — so they should be read as an optimistic bound.

The ontology and rule remediation carried out in P0-5 makes this precise. Extending the vocabulary
from 45 to 54 terms and revising five Tier-2 rules, every change argued from published agronomy,
raised `dev` positive recall from 19.17% to 63.33% while leaving `eval` flat to slightly lower
(38.33% to 35.00%). A gain confined to the partition that was visible during the work is the
signature of overfitting to development data, and it is reported here as such rather than as
progress.

Against baselines on `eval`, supervised classifiers evaluated via 5×2-fold CV within `eval` remain far behind — the strongest reaches
0.00% positive recall with only 11 training cases per fold and 2–3 positive instances to learn from (a protocol artifact of training-fold class sparsity and 77% negative imbalance, rather than model incompetence) — and RiceKG exceeds the
ontology-free nearest-prototype matcher by 9.1 percentage points of exact match (Holm-adjusted
$p = 0.0117$) and by 31.67% against 15.00% on positive recall. The prototype matcher nevertheless
holds a higher micro-F1 (57.05 against 41.00), so a trivial symptom-count heuristic has
not been cleanly beaten.


The 60.00% exact match now recorded on [`data/verification_suite.csv`](../data/verification_suite.csv)
should not be read as degradation. That set is `rule_derived`: its cases were generated from the
antecedents the reasoner executes, so revising those antecedents necessarily lowers agreement. The
earlier 92.50% measured consistency with the rule base, never diagnostic ability. The collapse is the
clearest available demonstration that the figure was circular from the start.

What the artifact contributes defensibly is therefore not predictive accuracy. It is **cold-start
operation with zero training data**, **auditable deductive derivations** in which every diagnosis
names the rules that fired and the antecedents left unmet, and **graded confidence** separating
pathognomonic confirmation (`hasConfirmedThreat`) from partial-observation screening
(`hasSuspectedThreat`) — a distinction that matters wherever an incorrect pesticide recommendation
carries real cost. The architectural ablation ([`results/ablation.md`](../results/ablation.md))
remains candid: tier stratification and DL reasoning buy no accuracy over pure set-matching, and
their justification rests on explainability and open-world consistency rather than performance.

Two obstacles now bound what further engineering can achieve. Four of the ten modelled threats,
including every insect pest, have no positive field case at all, because insect pests are not
published as first-report disease notes. And the signs the literature identifies as *discriminating*
for the two virus classes — excessive tillering for grassy stunt, orange discoloration for tungro —
are recorded by no descriptor in the benchmark, so those rules cannot fire on the present case set.
Both are limits of the available evidence rather than of the reasoner.

---

## Cold-Start Quantification and Sample Efficiency

In the cold-start learning-curve experiment ([`results/learning_curve.md`](../results/learning_curve.md)), no supervised baseline exceeded the zero-shot knowledge base (31.67% positive-case recall under 5×2 CV; 40.0% pooled) at any training budget available in this study under the test-set uncertainty criterion (up to $N=73$ rule-derived cases in Pool A, and $N=16$ real field cases in Pool B). While several supervised classifiers achieve point recall above the reference at larger budgets, the paired difference 95% bootstrap confidence interval over the test set spans zero in every case. The independent field evaluation set contains only 5 positive disease cases ($\Delta = 0.20$ quantisation step), rendering the field comparison substantially underpowered with a minimum detectable effect of $\pm 29.5\%$ accuracy ($\alpha = 0.05$, $80\%$ power). Consequently, apparent small margins on field data (such as Decision Tree reaching 36.2% at $N=4$ or Random Forest reaching 40.0% at $N=16$) fall well within random variation and should not be interpreted as demonstrated inductive superiority over the zero-shot symbolic knowledge base.

---

## Parameterised Benchmark Generation and Incomplete Observation Degradation

Beyond static test suites, this repository contributes a **parameterised generator for multi-label knowledge-based diagnosis benchmarks** ([`data/generator.py`](../data/generator.py)). Rather than evaluating on a single fixed rule-derived CSV that invites circularity objections, the generator parameterises antecedent occlusion, non-diagnostic contextual distractors, multi-threat co-infections, and out-of-vocabulary negative controls under reproducible random seeds.

This instrument enables a continuous characterisation of **symbolic-versus-supervised degradation along the observation-incompleteness axis** ([`results/degradation_curve.md`](../results/degradation_curve.md), [`results/figures/degradation_curve.png`](../results/figures/degradation_curve.png)). It measures robustness to symptom occlusion under the rule base's own vocabulary, not field accuracy, and the findings are reported in that file rather than restated here. In summary, the strict knowledge base keeps its precision but loses recall quickly as antecedents are hidden; tier stratification changes the reported grade but not the diagnosed set; supervised classifiers trained on separately generated cases are more robust along this axis; and enabling the `possible` grade recovers part of the recall at a cost in precision.

Crucially, synthetic benchmarks cannot cross two boundaries already documented in [`docs/LIMITATIONS.md`](LIMITATIONS.md):
1. **Vocabulary Realism**: Synthetic generation cannot validate whether the vocabulary matches authentic field scouting language or reporting practices.
2. **Excluded Classes**: It cannot supply empirical grounding for the four insect pest classes that lack independent peer-reviewed field cases.

