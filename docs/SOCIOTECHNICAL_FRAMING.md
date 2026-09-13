# Socio-Technical Framing: Knowledge, Organisation, and Risk

RiceKG is a technical artefact, but the problem it addresses is organisational. This document
states what the artefact changes about how diagnostic knowledge moves through the agricultural
extension system, why that matters for digital agriculture policy, and what happens when the system
is wrong. It supplies the social and organisational dimension that the technical documentation does
not.

## The extension knowledge chain

Diagnostic knowledge about rice pests and diseases in Indonesia is held by a small number of
agronomists, concentrated in research institutes and provincial extension offices. It reaches the
field along a narrow path:

1. **The agronomist holds the knowledge**, largely tacitly — as a trained ability to recognise a
   pattern of signs, formed through years of field exposure and not fully articulated even in
   training material.
2. **The extension officer carries it outward** through scouting visits, farmer field schools and
   informal consultation. One officer typically serves hundreds of farming households across
   villages that may be hours apart.
3. **The farmer observes daily and reports rarely.** Farmers see their crop continuously and are
   the first to notice a change, but often lack the controlled vocabulary to name what they see in
   terms an agronomist can act on remotely.

The binding constraint is not a shortage of knowledge. It is that the knowledge is **embodied in
scarce people and transferred by physical presence**, so its reach is bounded by travel time. A
farmer who notices lesions on a Tuesday may wait a week for an officer's visit, by which point the
decision has already been made, usually in favour of a broad-spectrum pesticide.

## What codification changes

Externalising this knowledge into an ontology and a rule base changes three things about the flow.

**It decouples availability from presence.** A codified rule base can be consulted when the
agronomist cannot travel. The knowledge no longer moves only at the speed of a motorcycle.

**It makes the reasoning inspectable.** This is the property that distinguishes the approach from a
statistical classifier. Each diagnosis names the rules that fired, the symptoms that satisfied them,
and the antecedents left unmet. An extension officer can therefore *disagree with a specific step*
rather than accept or reject an opaque output, and an agronomist can audit and correct the rule base
itself. Knowledge that is inspectable is knowledge that can be argued with, and knowledge that can
be argued with can be improved by the people who use it.

**It creates a shared vocabulary.** The 54 controlled symptom terms give farmers, officers and
agronomists a common way to describe what is observed. This is also the artefact's sharpest
limitation: a closed vocabulary that does not contain a farmer's observation silently discards it.
Nine of the twenty-five descriptors extracted from published case reports still have no ontology
term (`docs/LIMITATIONS.md` Section 3). A controlled vocabulary is a act of standardisation, and
standardisation always excludes something.

## Knowledge management framing

In Nonaka's SECI terms, the artefact performs **externalisation** — the conversion of tacit
agronomic expertise into explicit, codified form — and then enables **combination**, since codified
rules can be merged, versioned and compared in a way that tacit expertise cannot.

Two cautions belong with that framing rather than after it.

First, externalisation is **lossy by construction**. What survives the conversion is what the
vocabulary and rule language can express. The P0-5 finding that four of ten threat classes have no
field evidence, and that the signs the literature identifies as discriminating for two virus classes
are recorded by no descriptor in the benchmark, are both instances of this loss made measurable.

Second, the SECI cycle only closes if **internalisation** occurs — if officers and farmers actually
absorb the codified knowledge back into practice. Nothing in this repository evidences that. It is
precisely what the usability and adoption instruments (P1-7) are designed to measure, and until
they have been run with real participants, the organisational claim remains a design intention
rather than a finding.

## Implications for digital agriculture policy

**Low-connectivity deployment is a first-order requirement, not a deployment detail.** The rule base
is small, deterministic and executes without network access. Pellet inference costs roughly 500 ms
per case on commodity hardware, and `results/ablation.md` shows a pure set-matching implementation
reproduces the same diagnoses in under a millisecond. Where devices are constrained, the DL reasoner
can be reserved for consistency checking and explanation while a lightweight matcher serves the
interactive path — an architecture the ablation supports directly.

**Zero training data lowers the barrier to adoption for under-resourced systems.** A supervised
approach requires labelled field data that Indonesian rice extension does not have and would take
years to accumulate. A knowledge-based system can be authored from agronomic literature and expert
consultation, and corrected by the same experts when it is wrong, without a labelling programme.

**Auditability supports institutional accountability.** An extension service that issues advice must
be able to explain that advice. A rule trace is a record that can be reviewed after the fact by a
supervising agronomist, which a neural prediction is not.

## Risk, liability, and why graded confidence matters

The system can be wrong, and on independent field cases it currently is wrong more often than it is
right: 35.00% positive-case recall on the `eval` partition, with diagnostic efficacy **not
established**. Responsible framing has to start from that.

**What an error costs.** A false negative means an untreated infestation and yield loss. A false
positive is worse in one respect: it prompts an unnecessary pesticide application, which costs the
household money, exposes the applicator and the ecosystem to chemicals, and accelerates resistance
in the target population. The recent P0-5 experience is instructive — an intermediate rule revision
that appeared well-founded in the literature produced four false positives on out-of-scope pathogens
before being withdrawn.

**Why the confidence grading is a safety feature and not a presentation choice.** The separation of
`hasConfirmedThreat` from `hasSuspectedThreat` exists so that a partial observation cannot be
mistaken for a complete one. A suspected diagnosis is a prompt to look further or to escalate to an
agronomist; it is not a licence to spray. The ablation shows Tier-1 rules at 100% precision and 10%
recall against Tier-2's broader but less certain coverage: the two grades encode a real trade-off
between certainty and sensitivity, and surfacing it to the user is what keeps the trade-off in the
hands of the person who bears the consequence.

**Who is accountable.** The artefact is positioned as **decision support for extension officers, not
as an autonomous advisor for farmers**. The officer remains the decision-maker and the point of
accountability; the system supplies a traced hypothesis. Any deployment that removes the officer
from the loop changes the liability position materially and is not supported by the present evidence.

**Consent and ethics.** Any study involving extension officers or farmers requires informed consent
and institutional ethics approval from Universitas Jember before data collection begins. No human
participant data has been collected at the time of writing, and no such data exists in this
repository.

## References

- Nonaka, I. & Takeuchi, H. (1995). *The Knowledge-Creating Company*. Oxford University Press.
- Hevner, A.R., March, S.T., Park, J. & Ram, S. (2004). Design Science in Information Systems
  Research. *MIS Quarterly* 28(1):75–105.
