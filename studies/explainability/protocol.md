# Empirical Evaluation Protocol: Explainable AI (XAI) in Rice Pest & Disease Diagnosis

## 1. Executive Summary & Study Rationale

In high-stakes agronomic decision support, accuracy alone is insufficient: agricultural extension officers and farmers must verify the pathological reasoning before committing to expensive, potentially hazardous chemical or biological interventions.

This study implements a rigorous within-subject randomized controlled trial evaluating whether **RiceKG's formal Horn-clause derivation traces (symbolic XAI)** improve human decision quality, task efficiency, subjective understanding, and appropriate automation reliance compared to a state-of-the-art **black-box supervised machine learning baseline (Random Forest / Multi-Layer Perceptron)**.

---

## 2. Experimental Design

- **Design**: Within-subject, counterbalanced 2-condition design ($2 \times 1$ Factorial):
  - **Condition A (Control / Black-Box ML)**: System presents the predicted diagnosis, an opaque confidence probability ($p \in [0, 1]$), and prescriptive IPM treatments without internal logic traces.
  - **Condition B (Experimental / RiceKG Symbolic XAI)**: System presents the predicted diagnosis, confidence grade (`confirmed` vs `suspected`), the active Horn-clause rule ID, formula, matched vs unmet antecedents checklist, and collapsible Modus Ponens proof tree.
- **Counterbalancing**: Latin-square order randomization (half receive Condition A first, half receive Condition B first) with a 15-minute washout period between blocks to mitigate carryover and learning effects.
- **Diagnostic Case Battery**: 12 verified rice scouting scenarios drawn from independent field literature:
  - 6 Concordant Cases: Model suggestions are correct (tests appropriate trust and calibration).
  - 3 Adversarial / Near-Miss Cases: Model suggestions are borderline or subtly incorrect due to overlapping symptoms (tests detection of false positives / over-trust mitigation).
  - 3 Negative / Inconclusive Control Cases: Insufficient or non-diagnostic symptoms (tests recognition of uncertainty).

---

## 3. Participant Recruitment & Eligibility Criteria

- **Target Sample Size ($N$)**: 20–30 domain practitioners (power analysis indicates $N=24$ achieves $1-\beta=0.85$ to detect a medium effect size $d=0.55$ at $\alpha=0.05$ for paired comparisons).
- **Target Populations**:
  1. Field Agricultural Extension Officers (Penyuluh Pertanian Lapangan / PPL, Dinas Pertanian).
  2. University Agronomy & Plant Protection Researchers / Extension Specialists.
  3. Experienced Rice Scouting Farmers (Kelompok Tani / Gapoktan leaders).
- **Inclusion Criteria**:
  - Minimum 1 year of practical rice cultivation or agricultural advisory experience.
  - Basic familiarity with digital smartphone/tablet interfaces.
  - Signed informed consent under institutional ethics guidelines (see `docs/ETHICS.md`).

---

## 4. Participant Tasks & Trial Workflow

For each presented scouting case:
1. **Case Review**: Participant inspects field scouting observations (foliar lesions, stem damage, grain symptoms, crop stage).
2. **System Inspection**: Participant reviews the system suggestion under the assigned condition (Opaque ML probability vs RiceKG Proof Trace).
3. **Clinical Decision**: Participant records:
   - Acceptance: Whether they accept or reject the system's primary diagnosis (Binary: Yes/No).
   - Confirmed Threat: Final diagnosed causal agent chosen from standardized threat catalog.
   - Treatment Selection: Recommended Integrated Pest Management (IPM) action (Cultural, Biological, Chemical, or Rescout/Lab test).
4. **Subjective Confidence**: Rating of their own diagnostic confidence (5-point Likert: 1 = Very Low to 5 = Very High).
5. **Post-Block Evaluation**: Completion of the standardized Explanation Satisfaction Scale and Trust in Automation survey.

---

## 5. Dependent Variables & Operationalization

| Construct | Operational Metric | Measurement Instrument |
|:---|:---|:---|
| **Decision Accuracy** | Proportion of diagnostic decisions matching verified ground-truth etiology. | Ground truth comparison ($0/1$ per case). |
| **Decision Latency** | Time elapsed (seconds) from initial case display to final treatment submission. | Automated server timestamp logging (ms precision). |
| **Appropriate Reliance** | 1. **Over-Trust (Automation Bias)**: Accepting an incorrect model recommendation.<br>2. **Under-Trust**: Rejecting a correct model recommendation.<br>3. **Appropriate Reliance**: Agreement with correct advice + rejection of incorrect advice. | Cross-tabulation of participant decision vs model correctness vs ground truth. |
| **Explanation Satisfaction** | Perceived clarity, completeness, sufficiency, and trustworthiness of explanation. | Hoffman et al. (2018) Explanation Satisfaction Scale (8 items, $\alpha \ge 0.80$). |
| **Automation Trust** | Generalized cognitive and affective trust in the diagnostic system. | Jian et al. (2000) Trust in Automation Scale (12 items). |

---

## 6. Statistical Analysis Plan

All quantitative hypotheses are evaluated in `studies/explainability/analyse.py`:
1. **Decision Accuracy**: Paired Wilcoxon signed-rank test comparing mean accuracy between Condition A and Condition B.
2. **Decision Latency**: Paired $t$-test on log-transformed completion seconds.
3. **Appropriate Reliance**: McNemar's test for paired binary discordant reliance classifications (Over-trust error reduction).
4. **Satisfaction & Trust**: Paired $t$-test / Wilcoxon test on composite scale means, accompanied by Cronbach's $\alpha$ scale internal consistency verification.
5. **Reporting Standards**: Effect sizes (Cohen's $d$, odds ratios), 95% bootstrap confidence intervals, and full disclosure of null findings.

---

## 7. Data Collection & Ethics Oversight

- Responses are recorded anonymously in `studies/explainability/responses.csv` indexed by synthetic participant identifiers (`P01`, `P02`, ...).
- The study adheres strictly to Universitas Jember Institutional Review Board guidelines (Ethics Approval Protocol detailed in `docs/ETHICS.md`).

