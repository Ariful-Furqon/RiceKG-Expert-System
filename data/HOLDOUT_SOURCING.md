# Holdout Field Partition — Sourcing Log

Status: **in progress** — 18 positive cases staged (9 tier A, 6 tier B, 3 tier C). Two tier-C cases
(former HOLD_17, HOLD_19) were removed on source verification; see "Tier-C verification".

## Protocol

- **Rule-base freeze point**: commit `385caf9`. No change to `model.RULE_REGISTRY`, the vocabulary or
  the insect gate may be made until the holdout partition is locked and evaluated once.
- **Blinding**: staged cases live in `data/field_holdout_staging.csv`, which no evaluation script reads.
  The reasoner has not been run on any staged case, and must not be until sourcing is closed.
- **Text source**: `raw_symptom_text` is copied from the publisher-deposited abstract (Crossref / Europe PMC),
  the open-access full text (PMC), official institutional pest reports, or the PDF in `data/Paper/`
  (git-ignored, copyrighted), never from a search-engine summary. `[...]` marks an omitted sentence;
  `[Fig. 1 caption]` marks caption text.
- **Separation**: no staged DOI or URL appears in `benchmark_field.csv` or `rejected_field_candidates.csv`.
- **Mapping caveat**: symptom mapping follows the precedents in `symptom_mapping.csv` and existing rows
  (FIELD_04, FIELD_36), but was performed by an annotator who has seen the rule base. Mappings are
  preliminary until an independent annotator, blind to `RULE_REGISTRY`, re-maps them from
  `raw_symptom_text`. New `unmapped_terms` slugs must be added to `symptom_mapping.csv` when the partition
  is merged.

## Evidence tiers (decision of 2026-09-14)

The author chose to include candidates across three distinct evidence tiers rather than rejecting on source
type alone. Results will be reported for **tier A alone, A + B, and A + B + C side by side**, allowing the
reader to evaluate whether relaxed sources impact diagnostic conclusions.

| Tier | Meaning |
|---|---|
| **A** | Meets the original P0-3/P0-5 gate: peer-reviewed journal article with DOI, observed field symptom sentence, ground truth recorded. |
| **B** | Encodable but relaxed on at least one axis: conference proceedings; venue on predatory-publisher watch lists; symptom text that is a population-level summary, an identification criterion or a figure caption; host other than cultivated *O. sativa*. Requires DOI and stated reason in `tier_note`. |
| **C** | Official institutional outbreak report without a DOI (EPPO Reporting Service, IPPC NPPO pest reports, municipal/national agricultural agency field observation reports). Requires canonical `source_url`, `accessed` date (`YYYY-MM-DD`), and verified Wayback Machine snapshot (`archive_url`). Ground truth must be `lab_confirmed` (stating laboratory test method) or `expert_visual` (by official plant-protection authority). Stated reason in `tier_note`. |

**The evidence requirement itself was not relaxed.** A candidate with no observed symptom text cannot be
encoded: the only way to give it symptoms would be to copy them from the disease name or a textbook,
which reproduces the circular first field benchmark that scored 100% and was discarded. Such candidates
are recorded as rejected, with the reason.

## Staged cases per class

| Class | Tier A | Tier B | Tier C | Total | Cases |
|---|:---:|:---:|:---:|:---:|---|
| Bacterial_Leaf_Blight | 1 | 1 | 0 | 2 | HOLD_01, HOLD_13 |
| Rice_Root_Nematode | 2 | 0 | 1 | 3 | HOLD_02, HOLD_10, HOLD_20 |
| False_Smut | 2 | 2 | 0 | 4 | HOLD_03, HOLD_09, HOLD_12, HOLD_15 |
| Rice_Grassy_Stunt | 2 | 0 | 0 | 2 | HOLD_04, HOLD_05 |
| Rice_Tungro_Virus | 0 | 2 | 1 | 3 | HOLD_06, HOLD_14, HOLD_16 |
| Rice_Blast | 1 | 2 | 1 | 4 | HOLD_07, HOLD_08, HOLD_11, HOLD_18 |
| **Total** | **9** | **6** | **3** | **18** | |

Case IDs are not renumbered after removals; HOLD_17 and HOLD_19 are retired.

Rice_Tungro_Virus has no tier-A case yet; it has 2 tier-B cases and 1 tier-C case.

### Mapping notes:
- **HOLD_01**: follows FIELD_36 ("turned yellow" → `Yellowing_Leaves`).
- **HOLD_03**: maps only the yellowish-orange phase to `Rusty_Grain_Balls`, because "olive-green" does not match the existing dark-green-powder slug; **HOLD_09** and **HOLD_12** map "dark green or almost black" and "black smut ball" to `Blackened_Grain_Balls`.
- **HOLD_04**: maps "yellow-orange discoloration" to `Orange_Leaf_Discoloration`.
- **HOLD_08, HOLD_11**: "Spindle-shaped" and "fusiform" lesions map to `Diamond_Shaped_Lesions`.
- **HOLD_16 (Tier C)**: "Perubahan warna daun menjadi oranye atau kuning terang" maps to `Orange_Leaf_Discoloration` and `Yellowing_Leaves`. Unmapped: `daun_kuning_kecoklatan`.
- **HOLD_18 (Tier C)**: "bercak coklat berbentuk belah ketupat" maps to `Diamond_Shaped_Lesions` and `Necrotic_Spots`. Unmapped: `pinggir_bercak_coklat`.
- **HOLD_20 (Tier C)**: "chlorosis and stunted growth, and numerous swellings and galls on the roots" maps to `Yellowing_Leaves`, `Stunted_Growth`, and `Root_Knot_Swelling`. *Corrected*: the first mapping used `Hook_Like_Root_Swelling`, but the source mentions swellings and galls without hooked tips.

## Accepted Tier C cases

1. **HOLD_16** (`Rice_Tungro_Virus`): Subak Babakan Kerobokan, Desa Kerobokan, Sawan, Buleleng, Bali, Indonesia (17 Feb 2025). Issuer: Dinas Pertanian Kabupaten Buleleng. Expert visual field diagnosis by agricultural extension officers (POPT). Verbatim text: *"Gejala serangan : Perubahan warna daun menjadi oranye atau kuning terang sampai kuning kecoklatan."*
2. **HOLD_18** (`Rice_Blast`): Subak Bale Bandung, Desa Kalibukbuk, Buleleng, Bali, Indonesia (24 Jun 2022). Issuer: Dinas Pertanian Kabupaten Buleleng. Expert visual field diagnosis by POPT officers. Verbatim text: *"Pada hari jumat tanggal 24 juni 2022 Gejala serangan blas ditemukan di subak bale bandung [...] yaitu pada daun terdapat bercak coklat berbentuk belah ketupat dan memanjang searah dengan urat daun, pinggir bercak berwarna coklat dengan bagian tengah berwarna putih keabuan."* The lead-in is included so the text is visibly a field observation; `[...]` omits the farm owner's name.
3. **HOLD_20** (`Rice_Root_Nematode`): Buronzo (Vercelli), Mottalciata and Gifflenga (Biella), Piemonte, Italy (Jul 2016). Issuer: EPPO Reporting Service (2016/211). Official NPPO Italy notification; laboratory confirmation by morphological and molecular identification. Verbatim text: *"During inspection of rice fields, plants showing symptoms of chlorosis and stunted growth, and numerous swellings and galls on the roots could be observed."*.

## Rejected candidates and deduplications

Recorded with reasons in `data/rejected_field_candidates.csv`:

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
| HREJ_12 | Bacterial_Leaf_Blight | Deduplication failure: EPPO 2023/253 reports the Dec 2019 Madagascar outbreak already in `FIELD_03` |
| HREJ_13 | Rice_Tungro_Virus | Deduplication failure: IRRI 2025 press release reports the Santa Cruz, Laguna outbreak already staged as `HOLD_04` |
| HREJ_14 | Rice_Root_Nematode | EPPO 2018/196 reports survey detection across 37 ha in Lombardia with no case symptom observation |
| HREJ_15 | Rice_Root_Nematode | Deduplication failure: EPPO 2020/052 is a follow-up survey of the 2016 Piemonte outbreak already in `HOLD_20` |
| HREJ_16 | Rice_Tungro_Virus | Dinas Pertanian Buleleng (2020) Subak Sambangan describes generic textbook symptoms rather than field case observation |
| HREJ_17 | Rice_Tungro_Virus | Subak Bebau, Kayuputih: only a photo gallery exists (no date, no symptom text); cited article not locatable; earlier dedup reason was wrong — re-reviewed, see below |
| HREJ_18 | Rice_Tungro_Virus | Former HOLD_17 (Subak Banyuatis, 2023): field report only states "padi terkena tungro"; quoted symptoms are a general RTBV/RTSV explanation |
| HREJ_19 | Bacterial_Leaf_Blight | Former HOLD_19 (Subak Suralepang, 2025): symptom sentence is a general description in an explanatory paragraph, not this field |

## Tier-C verification (2026-09-14)

Every tier-C row was checked against the live source page and its Wayback snapshot, reading the raw HTML
rather than a fetch-tool summary. All five pages and snapshots exist and every quoted sentence is present
verbatim; the question was whether the quoted text is an **observation of that field** or a general
description of the disease.

| Case | Outcome | Finding |
|---|---|---|
| HOLD_16 | kept | Symptom line is item 5 of the officers' observation results (17 Feb 2025, Ciherang, 0.50 ha). |
| HOLD_17 | **removed → HREJ_18** | Observation says only that the rice was affected by tungro; the symptom sentences explain RTBV/RTSV in general. |
| HOLD_18 | kept, text extended | Full sentence reads "Gejala serangan blas ditemukan di subak bale bandung … yaitu pada daun terdapat bercak …", a field observation. |
| HOLD_19 | **removed → HREJ_19** | Symptom sentence sits in a paragraph on seasonal spread and describes the disease generally. The original row also mapped lesion expansion ("meluas") to `Rapid_Disease_Spread`, which denotes field-level spread, and its `archive_url` (`/web/2/`) was not a snapshot. |
| HOLD_20 | kept, mapping corrected | EPPO 2016/211 text is verbatim and NPPO-confirmed; galls without hooked tips map to `Root_Knot_Swelling`. |

**HREJ_17 re-review (closed, still rejected).** It had been rejected as a duplicate of HOLD_17, which is
itself now rejected, so the case was re-examined on the evidence test:

- The only locatable source is a photo gallery,
  `https://distankan.bulelengkab.go.id/foto/detail/16_pengamatan-penyakit-tungro-di-subak-bebau-desa-kayuputih`:
  a title and three photographs, with no date and no symptom text. Nothing can be encoded.
- The news article previously cited ("Gerdal Penyakit Tungro di Subak Bebau Desa Kayuputih") was not found
  through the site search of either agency domain (`distankan`, `distan`) or in the Wayback Machine CDX index,
  and the recorded URL was truncated. The citation could not be substantiated and has been replaced by the
  gallery page.
- The earlier deduplication reason was factually wrong: Desa Kayuputih is in **Kecamatan Sukasada** (the
  agency's own archived URLs read `desa-kayuputih-kecamatan-sukasada`), not Kecamatan Banjar.

Lesson for future sourcing: a rejection reason must be checked as carefully as an acceptance, and a
citation that cannot be opened is not recorded as if it had been read.

## Genuine Coverage Gaps

Per stopping rule 6-D:
- Sourcing stopped when targets or limits were met without resorting to circularity or unconfirmed claims.
- `Rice_Grassy_Stunt` remains at 2 cases (both Tier A). No institutional outbreak reports with observed case symptoms were found.
- `Bacterial_Leaf_Blight` stands at 2 cases (1 A, 1 B, 0 C).
- `Rice_Root_Nematode` stands at 3 cases (2 A, 0 B, 1 C).
- `False_Smut` stands at 4 cases (2 A, 2 B, 0 C).
- `Rice_Tungro_Virus` stands at 3 cases (0 A, 2 B, 1 C).
- `Rice_Blast` stands at 4 cases (1 A, 2 B, 1 C).

These gaps are reported as genuine findings regarding the availability of empirical case-level field literature, not smoothed over.

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
