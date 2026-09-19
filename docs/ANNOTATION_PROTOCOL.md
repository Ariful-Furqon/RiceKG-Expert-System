# Multi-Rater Annotation Protocol

This protocol implements the expert-based validation (parts A2 and A3) of
[`EVALUATION_FRAMEWORK.md`](EVALUATION_FRAMEWORK.md). It replaces `annotator_id = "unassigned"`
in `data/benchmark_field.csv` with independent agronomist judgements, and it doubles as the
review of the draft term definitions in `ontology/term_definitions.csv`.

## What raters do

| Stage | Task | Measures |
|---|---|---|
| Practice | 4 cases from `data/rejected_field_candidates.csv` (textbook descriptions; not analysed), discussed with the coordinator | Calibration on the vocabulary and the answer options |
| A | For each of the 56 benchmark cases, read the redacted symptom text; record every observation it states, using the ontology vocabulary; give one diagnosis and a confidence | Symptom-encoding agreement; diagnosis agreement (rater–rater, RiceKG–rater, rater–published label) |
| A | Rate each of the 67 term definitions (adequate / needs revision / inadequate) and suggest wording | Definition review |
| B | For the same cases, rate RiceKG's conclusion and derivation trace | Explanation quality |

Stage B is sent to a rater only after their Stage A has been returned, because the trace reveals
RiceKG's conclusion and would bias the rater's own diagnosis.

Diagnosis options: the six in-scope classes, "another disease or pest outside these six", and
"cannot be decided from the text". Explanation items: B1 acceptable (yes / partly / no); B2
agronomic correctness of the reasoning, B3 completeness, B4 usefulness to a field officer
(each 1–5).

## Blinding

- **Names.** Disease names, pathogen names and disease abbreviations are replaced by
  `[disamarkan]` (`annotation/redaction.py`). Signs, vectors and the host are kept.
- **Codes and order.** Cases carry pseudonymous codes (`K01`–`K56`) from a fixed seed, and each
  rater sees them in a different order.
- **Hidden information.** No rater sees the source, location, date, split, published label,
  the authors' symptom encoding (before Stage B) or another rater's answers.
- **Non-English texts.** Translated texts show the English version followed by the redacted
  original.

The automatic redaction is broad but not guaranteed. **Before sending**, the coordinator reads
every row of the key workbook's `Redaksi` sheet and ticks it, fixing any remaining give-away by
editing the pattern list and rebuilding, never by hand-editing a rater's workbook.

## Raters

- Two or three agronomists or plant pathologists with field diagnostic experience on rice
  (for example lecturers in plant protection, or pest and disease observers, POPT). Three
  raters allow Fleiss' κ and a strict majority.
- None of the RiceKG authors, and nobody who helped build the rule base or the benchmark.
- Informed consent: the purpose of the study, that answers are reported only in aggregate and
  under codes R1–R3, and that participation is voluntary. No personal data enters the workbooks.
  Record consent separately from the workbooks.
- Estimated effort: about 3 h for Stage A including practice, 45 min for the definition review,
  and 1.5 h for Stage B. Suggest two or three sessions per stage.

## Procedure

1. `python annotation/build_packet.py --raters 3` writes `annotation/packet/` (git-ignored):
   `R1_TahapA.xlsx`, `R1_TahapB.xlsx`, ... and `KUNCI_koordinator_JANGAN_DIKIRIM.xlsx`.
   **Never send the key.**
2. Coordinator checks the `Redaksi` sheet (see Blinding).
3. Send each rater only their own `Rx_TahapA.xlsx`. Hold a short calibration meeting on the
   practice sheet; do not discuss study cases.
4. When Stage A comes back, save it unchanged in `annotation/returned/` and send `Rx_TahapB.xlsx`.
5. `python annotation/import_returns.py` validates every answer against the dropdown options
   and writes the de-identified tables in `data/`. It stops on any value outside the options;
   ask the rater, do not guess.
6. `python analysis/agreement.py` (diagnosis κ) and
   `python analysis/expert_validation.py --rerun` produce `results/expert_validation.md`.
7. The import also writes `data/symptom_encoding_consensus.csv` (terms chosen by a strict
   majority of raters), which `ricekg.evaluate.load_data` then uses as the field benchmark's
   encoding. Regenerate every field result afterwards (`make reproduce`).
8. After the definition review, revise `ontology/term_definitions.csv`, set `status` to
   `reviewed` for each accepted term, and rebuild the ontology.

Do not change the rule base in response to the diagnosis results before the planned fresh
held-out partition is sourced; that would repeat the development exposure recorded in
[`LIMITATIONS.md`](LIMITATIONS.md) Section 2.

One such change has been made: ruleset v2.4.0 (diagnostic-sign rules, removal of unsourced
antecedents) was written after the two-rater annotations had been analysed, with a
literature-based criterion fixed before any re-run. [`LIMITATIONS.md`](LIMITATIONS.md) Section 2
records the resulting exposure; the rule base is now frozen at v2.4.0.

## Conduct of the first round

Two raters (R1, R2) took part; a third could not be recruited, so there is no Fleiss' κ. Workbooks
were returned over WhatsApp, and the file times in `annotation/returned/` are the coordinator's
download times, not completion times: R2's Stage A and Stage B files share a time because they were
downloaded together. The coordinator confirmed that R2 completed the workbooks without help. The
high agreement between them (diagnosis κ = 0.885, encoding Jaccard 0.929) therefore rests on that
account; the files themselves cannot demonstrate independence.

## Re-rating after ruleset v2.4.0

The Stage B ratings of the first round were given on RiceKG v2.3 outputs for the authors'
encoding. After the switch to the expert-consensus encoding and ruleset v2.4.0, 47 of the 56 cases
show a different conclusion, encoding or explanation (25 a different conclusion), so the first-round
ratings no longer describe the system. The follow-up round:

1. `python annotation/build_rerating_packet.py --raters 2 --review R2` writes
   `annotation/packet/v24/` (git-ignored): `Rx_TahapB_v24.xlsx` for every rater (all 56 cases, same
   codes and per-rater order as the first round, v2.4.0 outputs on the consensus encoding),
   `R2_ReviewDefinisi.xlsx` (R2 did not return the definition review in the first round) and a cover
   letter `Surat_Rx.txt`. `--only-changed` restricts Stage B to the 25 cases whose conclusion changed.
2. Raters work without their first-round answers; the instructions say so.
3. Save the returned files unchanged in `annotation/returned/` and run
   `python annotation/import_returns.py`, which writes `data/annotations_explanations_v24.csv` and adds
   R2's definition ratings to `data/definition_review.csv`.
4. `python analysis/expert_validation.py --rerun` reports both rounds side by side. Every
   explanation table is grouped by the output the rater saw (`shown_output`), not by the current
   RiceKG outcome.

## Analysis

`analysis/expert_validation.py` computes:

- **Diagnosis:** Fleiss' κ and pairwise Cohen's κ between raters; Cohen's κ of RiceKG against
  each rater; the difference between mean RiceKG–rater and mean rater–rater κ with a
  case-bootstrap 95% CI. The criterion is whether RiceKG falls within the rater–rater range.
  RiceKG's committed diagnosis is its label; an out-of-scope rejection counts as "other"; no
  committed output counts as "cannot be decided".
- **Human baseline:** agreement of each rater and of the rater majority with the published label,
  over all cases and over positive cases, beside RiceKG's.
- **Encoding:** per-term κ on presence, mean pairwise Jaccard, agreement between the authors'
  encoding and the rater majority, and (with `--rerun`) RiceKG's outcomes on the majority encoding.
- **Explanations:** distribution of B1–B4, overall and by RiceKG outcome category.
- **Definitions:** counts and every term a rater flagged.

## Files

| Path | Content | In git |
|---|---|---|
| `annotation/build_packet.py`, `import_returns.py`, `redaction.py` | Instrument and import | yes |
| `annotation/packet/` | Workbooks and coordinator key | **no** |
| `annotation/returned/` | Completed workbooks | **no** |
| `data/annotations_*.csv`, `data/definition_review.csv` | De-identified answers (R1–R3) | yes |
| `results/expert_validation.*` | Analysis | yes |
