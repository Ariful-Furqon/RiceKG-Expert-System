# Holdout Field Partition — Sourcing Log

Status: **in progress** — 15 positive cases staged (9 tier A, 6 tier B) toward a target of ~30.

## Protocol

- **Rule-base freeze point**: commit `385caf9`. No change to `model.RULE_REGISTRY`, the vocabulary or
  the insect gate may be made until the holdout partition is locked and evaluated once.
- **Blinding**: staged cases live in `data/field_holdout_staging.csv`, which no evaluation script reads.
  The reasoner has not been run on any staged case, and must not be until sourcing is closed.
- **Text source**: `raw_symptom_text` is copied from the publisher-deposited abstract (Crossref / Europe PMC),
  the open-access full text (PMC), or the PDF in `data/Paper/` (git-ignored, copyrighted), never from a
  search-engine summary. `[...]` marks an omitted sentence; `[Fig. 1 caption]` marks caption text.
- **Separation**: no staged DOI appears in `benchmark_field.csv` or `rejected_field_candidates.csv`.
- **Mapping caveat**: symptom mapping follows the precedents in `symptom_mapping.csv` and existing rows
  (FIELD_04, FIELD_36), but was performed by an annotator who has seen the rule base. Mappings are
  preliminary until an independent annotator, blind to `RULE_REGISTRY`, re-maps them from
  `raw_symptom_text`. New `unmapped_terms` slugs must be added to `symptom_mapping.csv` when the partition
  is merged.

## Evidence tiers (decision of 2026-09-14)

The author chose to include every candidate that can be encoded, rather than rejecting on source type.
Inclusion is therefore split into two tiers, and results must be reported for **tier A alone and for
A + B**, so that a reader can see whether the relaxed sources change any conclusion.

| Tier | Meaning |
|---|---|
| **A** | Meets the original P0-3/P0-5 gate: peer-reviewed journal article, an observed field symptom sentence, ground truth recorded. |
| **B** | Encodable but relaxed on at least one axis: conference proceedings; venue on predatory-publisher watch lists; symptom text that is a population-level summary, an identification criterion or a figure caption; host other than cultivated *O. sativa*. The reason is stated per row in `tier_note`. |

**The evidence requirement itself was not relaxed.** A candidate with no observed symptom text cannot be
encoded: the only way to give it symptoms would be to copy them from the disease name or a textbook,
which reproduces the circular first field benchmark that scored 100% and was discarded. Such candidates
are recorded as rejected, with the reason.

## Staged cases per class

| Class | Tier A | Tier B | Cases |
|---|:---:|:---:|---|
| Bacterial_Leaf_Blight | 1 | 1 | HOLD_01, HOLD_13 |
| Rice_Root_Nematode | 2 | 0 | HOLD_02, HOLD_10 |
| False_Smut | 2 | 2 | HOLD_03, HOLD_09, HOLD_12, HOLD_15 |
| Rice_Grassy_Stunt | 2 | 0 | HOLD_04, HOLD_05 |
| Rice_Tungro_Virus | 0 | 2 | HOLD_06, HOLD_14 |
| Rice_Blast | 1 | 2 | HOLD_07, HOLD_08, HOLD_11 |
| **Total** | **9** | **6** | 15 |

Rice_Tungro_Virus has no tier-A case yet.

Mapping notes: HOLD_01 follows FIELD_36 ("turned yellow" → `Yellowing_Leaves`). HOLD_03 maps only the
yellowish-orange phase to `Rusty_Grain_Balls`, because "olive-green" does not match the existing
dark-green-powder slug; HOLD_09 and HOLD_12 map "dark green or almost black" and "black smut ball" to
`Blackened_Grain_Balls`. HOLD_04 maps "yellow-orange discoloration" to `Orange_Leaf_Discoloration`.
"Spindle-shaped" and "fusiform" lesions (HOLD_08, HOLD_11) map to `Diamond_Shaped_Lesions`.

## Rejected — cannot be encoded

Recorded with reasons in `rejected_field_candidates.csv`:

| ID | Class | Reason |
|---|---|---|
| HREJ_01 | Bacterial_Leaf_Blight | Conference paper with no symptom sentence (incidence/severity only) |
| HREJ_03 | Rice_Tungro_Virus | Detection on weed hosts, not rice |
| HREJ_04, HREJ_05 | False_Smut | Laboratory characterisation only |
| HREJ_06 | Rice_Tungro_Virus | Vector population-dynamics study, no case-level symptoms |
| HREJ_07 | Rice_Grassy_Stunt | Diagnosis only "tentatively related to grassy stunt"; greenhouse symptoms |
| HREJ_08 | Rice_Blast | Nigeria — full text has no symptom description and no confirmation |
| HREJ_09 | False_Smut | India — symptoms from artificial inoculation only |
| HREJ_10 | False_Smut | Bangladesh — smut-ball counts only; symptom text is a cited textbook sentence |
| HREJ_11 | Rice_Blast | Bangladesh — incidence tables and culture morphology only |

## Still to obtain (PDF not yet provided)

| # | DOI | Class | Note |
|---|---|---|---|
| 5 | 10.1080/09670879109371595 | Rice_Tungro_Virus | South Sulawesi, Indonesia incidence |
| 6 | 10.1080/09670878109413653 | Rice_Grassy_Stunt / Rice_Tungro_Virus | Indonesia |
| 7 | 10.5958/2249-4677.2025.00049.1 | Rice_Tungro_Virus | Philippines, co-infection with rice orange leaf phytoplasma |
| 8 | 10.1094/pdis-12-15-1391-pdn | Rice_Blast | Puerto Rico |
| 16 | 10.1094/pdis-06-17-0844-pdn | Rice_Root_Nematode | Hunan, China |
| 17 | 10.1094/pdis-06-17-0832-pdn | Rice_Root_Nematode | Zhejiang, China |
| 18 | 10.1094/pdis-12-16-1805-pdn | Rice_Root_Nematode | Hubei, China |
| 20 | 10.5958/2230-7338.2014.00869.6 | Rice_Root_Nematode | Udham Singh Nagar, India |
| 21 | 10.5958/0974-0163.2018.00082.4 | Rice_Root_Nematode | Siddharthnagar, India |

Items 5–7 matter most: they are the only remaining candidates for a tier-A Rice_Tungro_Virus case.
