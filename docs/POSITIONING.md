# Scientific Positioning: Accuracy, Explainability, and What the Evidence Supports

On the `eval` partition of the field benchmark ([`data/benchmark_field.csv`](../data/benchmark_field.csv),
*n*=23, of which 5 are in-scope disease cases), RiceKG attains **35.00%** positive-case recall and a
micro-F1 of **40.67** [95% CI 34.8, 74.3]. Its aggregate exact match of 86.82% is not a diagnostic
result: 18 of the 23 cases are out-of-scope negative controls on which returning `No_Diagnosis` is
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

Against baselines on `eval`, every supervised classifier remains far behind — the strongest reaches
10.00% positive recall with at most five positive examples to learn from — and RiceKG exceeds the
ontology-free nearest-prototype matcher by 13.0 percentage points of exact match (Holm-adjusted
$p = 0.0004$) and by 35.00% against 17.50% on positive recall. The prototype matcher nevertheless
holds a marginally higher micro-F1 (43.29 against 40.67), so a trivial symptom-count heuristic has
not been cleanly beaten.

The 60.00% exact match now recorded on [`data/benchmark_synthetic.csv`](../data/benchmark_synthetic.csv)
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

In the cold-start learning-curve experiment ([`results/learning_curve.md`](../results/learning_curve.md)), supervised learning requires at least $N^* = 40$ labelled cases in the rule-derived synthetic pool before all five supervised architectures exceed the zero-shot knowledge base (35.00% positive-case recall) with non-overlapping 95% bootstrap confidence intervals, while on independent real field training data, two of five supervised baselines (Multinomial Naive Bayes and Logistic Regression) fail to exceed the zero-shot baseline at any budget up to $N = 16$. However, this comparison carries an essential statistical counterweight: the independent field evaluation set contains only 5 positive disease cases ($\Delta = 0.20$ quantisation step), rendering the field comparison substantially underpowered with a minimum detectable effect of $\pm 29.5\%$ accuracy ($\alpha = 0.05$, $80\%$ power). Consequently, apparent small margins on field data (such as Decision Tree reaching 36.2% at $N=4$ or Random Forest reaching 40.0% at $N=16$) fall well within the margin of random variation and should not be interpreted as demonstrated inductive superiority over the zero-shot symbolic knowledge base.

