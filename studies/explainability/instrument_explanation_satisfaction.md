# Measurement Instrument: Explanation Satisfaction & Trust in Automation

This instrument contains standardized measurement scales adapted for evaluating decision support explainability in agricultural pest and disease diagnostics.

---

## Part 1: Explanation Satisfaction Scale (Hoffman et al., 2018)

*Reference: Hoffman, R. R., Mueller, S. T., Klein, G., & Litman, J. (2018). Metrics for explainable AI: Challenges and prospects. arXiv preprint arXiv:1812.04608.*

**Scoring**: 5-point Likert scale (1 = Strongly Disagree, 2 = Disagree, 3 = Neutral / Undecided, 4 = Agree, 5 = Strongly Agree).  
Items marked `[R]` are reverse-scored prior to analysis.

| Item ID | Construct / Dimension | Statement (English) | Statement (Bahasa Indonesia) |
|:---|:---|:---|:---|
| **ESS_01** | Understandability | I understand how the software diagnostic system concluded this diagnosis. | Saya memahami bagaimana sistem pakar menyimpulkan diagnosis ini. |
| **ESS_02** | Completeness | This explanation of how the software worked is sufficiently complete. | Penjelasan mengenai cara kerja perangkat lunak ini sudah cukup lengkap. |
| **ESS_03** | Sufficiency of Detail | This explanation tells me how the system arrived at the conclusion with the right amount of detail. | Penjelasan ini memberi tahu saya bagaimana sistem mencapai kesimpulan dengan tingkat kerincian yang tepat. |
| **ESS_04** | Trustworthiness | This explanation helps me know whether I can trust the software's diagnosis. | Penjelasan ini membantu saya mengetahui apakah saya dapat mempercayai diagnosis perangkat lunak ini. |
| **ESS_05** | Logic Transparency | This explanation makes it clear how the symptoms observed in the field relate to the pathogen. | Penjelasan ini memperjelas hubungan antara gejala di lapangan dengan patogen penyebabnya. |
| **ESS_06** | Actionability | The explanation provides enough information for me to choose the appropriate pest management action (IPM). | Penjelasan ini memberikan informasi yang memadai bagi saya untuk memilih tindakan pengendalian hama terpadu (PHT) yang tepat. |
| **ESS_07** | Deceptiveness `[R]` | The explanation is misleading, confusing, or conceals the system's reasoning flaws. | Penjelasan ini membingungkan, menyesatkan, atau menyembunyikan kelemahan penalaran sistem. |
| **ESS_08** | Cognitive Satisfaction | Overall, I am satisfied with the diagnostic explanation provided by the system. | Secara keseluruhan, saya puas dengan penjelasan diagnostik yang diberikan oleh sistem ini. |

---

## Part 2: Trust in Automation Scale (Jian, Bisantz, & Drury, 2000)

*Reference: Jian, J. Y., Bisantz, A. M., & Drury, C. G. (2000). Foundations for an empirically determined scale of trust in automated systems. International Journal of Cognitive Ergonomics, 4(1), 53-71.*

**Scoring**: 7-point Likert scale (1 = Not at all, 4 = Neutral, 7 = Extremely).  
Items `TIA_01` through `TIA_05` measure distrust (`[R]`), items `TIA_06` through `TIA_12` measure trust.

| Item ID | Dimension | Survey Item Statement |
|:---|:---|:---|
| **TIA_01** | Distrust `[R]` | The diagnostic system is deceptive. |
| **TIA_02** | Distrust `[R]` | The diagnostic system behaves in an underhanded manner. |
| **TIA_03** | Distrust `[R]` | I am suspicious of the system's outputs. |
| **TIA_04** | Distrust `[R]` | I am wary of the system. |
| **TIA_05** | Distrust `[R]` | The system's recommendations can be harmful to farm management. |
| **TIA_06** | Trust | I am confident in the diagnostic system. |
| **TIA_07** | Trust | The diagnostic system provides security against misdiagnosis. |
| **TIA_08** | Trust | The diagnostic system is dependable. |
| **TIA_09** | Trust | The diagnostic system is reliable. |
| **TIA_10** | Trust | The diagnostic system has integrity. |
| **TIA_11** | Trust | I can trust the diagnostic system. |
| **TIA_12** | Trust | I am willing to base agronomic decisions on this system. |

---

## Part 3: Qualitative Cognitive Walkthrough Prompts

Post-trial semi-structured qualitative interview items:
1. **Critical Feature Identification**: *Which specific element in the explanation trace was most influential in your decision to accept or reject the diagnosis (e.g., rule formula, observed vs unmet symptom checklist, or confidence grade)?*
2. **Missing Evidence Recognition**: *Did the explanation help you notice unobserved symptoms that you should check again in the field before spraying?*
3. **Black-Box Contrast**: *How did your confidence differ when viewing a single percentage score (Condition A) versus the rule derivation tree (Condition B)?*
