"""
analysis/build_ontology_owl.py
------------------------------
Generates the OWL 2 DL ontology file `rice_ontology.owl` for PART 4 (4-A through 4-H):
- Stratified observation property hierarchy (hasObservation, hasSymptom, hasOrganismSighting, hasVectorSighting, hasEpidemiologicalContext)
- Two-axis symptom taxonomy (anatomical and phenomenological)
- OWL 2 Defined Classes (ThreatConfirmed, ThreatSuspect, ThreatPossible)
- Control treatments with cited IPM recommendations and DOIs (CQ08)
- Datatype property hasDiagnosticConfidence (CQ09)
- OWL-introspectable antecedent relations threat.hasSymptom (CQ10)
- AllDifferent axioms and Pest/Disease disjointness
- SKOS alignments to AGROVOC and Plant Ontology (PO), written as IRI-valued
  skos:exactMatch / closeMatch / broadMatch / relatedMatch assertions
- Dublin Core (dcterms), VANN and owl:versionInfo ontology metadata, and an
  rdfs:comment on every class, property and individual
- Bilingual (en/id) skos:prefLabel, operational skos:definition and skos:scopeNote
  for every observation term and threat, read from ontology/term_definitions.csv;
  dcterms:source cites only DOIs already verified in data/noisy_or_parameters.csv

Every AGROVOC concept below was checked against the AGROVOC Skosmos REST API
(https://agrovoc.fao.org/browse/rest/v1/) on 2026-09-15; the preferred label is
recorded next to each IRI. `tests/test_ontology_annotations.py` pins the mapping.
"""

import csv
import math
import os
import sys
import types

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from owlready2 import (
    Thing, AllDifferent, AllDisjoint,
    World, AnnotationProperty, locstr, Or
)

from ricekg import model
OUTPUT_OWL = os.path.join(BASE_DIR, "ontology", "rice_ontology.owl")
DEFINITIONS_CSV = os.path.join(BASE_DIR, "ontology", "term_definitions.csv")

SKOS_IRI = "http://www.w3.org/2004/02/skos/core#"
DCTERMS_IRI = "http://purl.org/dc/terms/"
VANN_IRI = "http://purl.org/vocab/vann/"
AGROVOC = "http://aims.fao.org/aos/agrovoc/"
OBO = "http://purl.obolibrary.org/obo/"

ONTOLOGY_VERSION = "2.4.0"

EDITORIAL_NOTES = {
    "draft": ("Operational definition drafted by the RiceKG authors from the cited source and "
              "standard rice pathology descriptions; pending review by independent agronomists."),
    "reviewed": ("Operational definition reviewed and judged adequate by an independent agronomist "
                 "(reviewer R1, RiceKG multi-rater study, September 2026)."),
    "revised": ("Operational definition revised following review by an independent agronomist "
                "(reviewer R1, RiceKG multi-rater study, September 2026)."),
}

# (entity name, SKOS relation, target IRI, verified preferred label)
CLASS_ALIGNMENTS = [
    ("Rice", "exactMatch", AGROVOC + "c_5438", "Oryza sativa"),
    ("Symptom", "exactMatch", AGROVOC + "c_7566", "symptoms"),
    ("Chlorosis", "exactMatch", AGROVOC + "c_1579", "chlorosis"),
    ("Necrosis", "exactMatch", AGROVOC + "c_15509", "necrosis"),
    ("Stunting", "exactMatch", AGROVOC + "c_4426a431", "stunting"),
    ("Disease", "closeMatch", AGROVOC + "c_5962", "plant diseases"),
    ("Pest", "closeMatch", AGROVOC + "c_5741", "pests"),
    # Anatomical sign classes are signs *located on* a PO structure, not the structure itself.
    ("LeafSign", "relatedMatch", OBO + "PO_0025034", "leaf"),
    ("StemSign", "relatedMatch", OBO + "PO_0009047", "stem"),
    ("RootSign", "relatedMatch", OBO + "PO_0009005", "root"),
    ("PanicleSign", "relatedMatch", OBO + "PO_0009049", "inflorescence"),
    ("GrainSign", "relatedMatch", OBO + "PO_0009010", "seed"),
    ("WholePlantSign", "relatedMatch", OBO + "PO_0000003", "whole plant"),
]

# Threat individuals denote a disease of rice; AGROVOC indexes the causal organism, so the
# relation is closeMatch (or broadMatch where only the genus exists).
THREAT_ALIGNMENTS = [
    ("Rice_Blast", "closeMatch", AGROVOC + "c_16025", "Pyricularia oryzae"),
    ("Bacterial_Leaf_Blight", "closeMatch", AGROVOC + "c_24383", "Xanthomonas oryzae"),
    ("False_Smut", "broadMatch", AGROVOC + "c_31622", "Ustilaginoidea"),
    ("Rice_Grassy_Stunt", "closeMatch", AGROVOC + "c_ce4b70ea", "rice grassy stunt tenuivirus"),
    ("Rice_Tungro_Virus", "closeMatch", AGROVOC + "c_f6940eb3", "rice tungro bacilliform virus"),
    ("Rice_Tungro_Virus", "closeMatch", AGROVOC + "c_f48899c1", "rice tungro spherical virus"),
    ("Rice_Root_Nematode", "closeMatch", AGROVOC + "c_31070", "Meloidogyne graminicola"),
]


def load_term_definitions(path=DEFINITIONS_CSV):
    with open(path, encoding="utf-8", newline="") as f:
        return {row["term"]: row for row in csv.DictReader(f)}


def build_and_save_ontology(output_path=OUTPUT_OWL):
    world = World()
    onto = world.get_ontology(model.ONTOLOGY_IRI)
    skos = onto.get_namespace(SKOS_IRI)
    dcterms = onto.get_namespace(DCTERMS_IRI)
    vann = onto.get_namespace(VANN_IRI)

    with skos:
        class exactMatch(AnnotationProperty): pass
        class closeMatch(AnnotationProperty): pass
        class broadMatch(AnnotationProperty): pass
        class relatedMatch(AnnotationProperty): pass
        class prefLabel(AnnotationProperty): pass
        class altLabel(AnnotationProperty): pass
        class definition(AnnotationProperty): pass
        class scopeNote(AnnotationProperty): pass
        class editorialNote(AnnotationProperty): pass
    with dcterms:
        class title(AnnotationProperty): pass
        class creator(AnnotationProperty): pass
        class license(AnnotationProperty): pass
        class description(AnnotationProperty): pass
        class source(AnnotationProperty): pass
    with vann:
        class preferredNamespacePrefix(AnnotationProperty): pass
        class preferredNamespaceUri(AnnotationProperty): pass

    skos_props = {p.name: p for p in (exactMatch, closeMatch, broadMatch, relatedMatch)}

    def link(entity, relation, iri):
        """Assert an IRI-valued (not string-literal) annotation triple."""
        onto._add_obj_triple_spo(entity.storid, skos_props[relation].storid, onto._abbreviate(iri))

    definitions = load_term_definitions()

    def describe(entity):
        """Attach the curated labels, definition and supporting source for one term."""
        row = definitions[entity.name]
        entity.label = [locstr(row["label_en"], lang="en")]
        entity.prefLabel = [locstr(row["label_en"], lang="en"), locstr(row["label_id"], lang="id")]
        if row["alt_label_en"]:
            entity.altLabel = [locstr(a.strip(), lang="en") for a in row["alt_label_en"].split(";")]
        entity.definition = [locstr(row["definition"], lang="en")]
        if row["scope_note"]:
            entity.scopeNote = [locstr(row["scope_note"], lang="en")]
        if row["source_doi"]:
            onto._add_obj_triple_spo(entity.storid, source.storid,
                                     onto._abbreviate("https://doi.org/" + row["source_doi"]))
        elif row["source_citation"]:
            entity.source = [f"{row['source_citation']} {row['source_locator']}".strip()]
        entity.editorialNote = [locstr(EDITORIAL_NOTES[row["status"]], lang="en")]

    with onto:
        # -------------------------------------------------------------
        # Ontology metadata
        # -------------------------------------------------------------
        onto.metadata.title = ["RiceKG: an OWL 2 DL ontology for rice disease diagnosis"]
        onto.metadata.creator = ["RiceKG Expert System contributors"]
        onto.metadata.description = [
            "Six in-scope rice disease classes (five pathogens and one plant-parasitic nematode) "
            "defined by OWL 2 defined classes over a two-axis symptom taxonomy; insect damage is "
            "represented as out-of-scope evidence."
        ]
        onto.metadata.preferredNamespacePrefix = ["ricekg"]
        onto.metadata.preferredNamespaceUri = [model.ONTOLOGY_IRI + "#"]
        onto.metadata.versionInfo = [ONTOLOGY_VERSION]
        onto.metadata.comment = [
            "RiceKG: OWL 2 DL ontology for rice disease diagnosis with defined classes, a symptom "
            "taxonomy and provable tier subsumption."
        ]
        onto._add_obj_triple_spo(onto.storid, license.storid,
                                 onto._abbreviate("https://opensource.org/licenses/MIT"))

        # -------------------------------------------------------------
        # Core Class Hierarchy
        # -------------------------------------------------------------
        class Rice(Thing):
            comment = ["Oryza sativa plant individual under diagnosis."]

        class Observation(Thing):
            comment = ["Top-level entity for any empirical observation made in a rice field or scout report."]

        class Symptom(Observation):
            comment = ["Direct plant sign or phenotypic manifestation of biotic injury on Oryza sativa."]

        class OrganismSighting(Observation):
            comment = ["Direct physical sighting of an insect or pest organism (adults, nymphs, egg clutches, frass)."]

        class VectorSighting(Observation):
            comment = ["Entomological sighting of a known insect vector of viral phytopathogens."]

        class EpidemiologicalContext(Observation):
            comment = ["Stand-level, environmental, or temporal condition modulating outbreak probability."]

        # -------------------------------------------------------------
        # Anatomical Axis
        # -------------------------------------------------------------
        class LeafSign(Symptom):
            comment = ["Pathological sign manifested on the leaf blade or sheath."]

        class StemSign(Symptom):
            comment = ["Pathological sign manifested on the culm or tiller stem."]

        class RootSign(Symptom):
            comment = ["Pathological sign manifested on the root system or subterranean crowns."]

        class PanicleSign(Symptom):
            comment = ["Pathological sign manifested on the inflorescence, panicle neck, or rachis."]

        class GrainSign(Symptom):
            comment = ["Pathological sign manifested on the spikelet, caryopsis, or mature grain."]

        class WholePlantSign(Symptom):
            comment = ["Systemic sign manifested across the entire rice plant architecture."]

        # -------------------------------------------------------------
        # Phenomenological Axis
        # -------------------------------------------------------------
        class Chlorosis(Symptom):
            comment = ["Foliar yellowing, discoloration, or loss of chlorophyll pigments."]

        class Necrosis(Symptom):
            comment = ["Localized or extensive death and breakdown of plant cells and tissues."]

        class Stunting(Symptom):
            comment = ["Suppression of plant elongation, height reduction, or dwarfing."]

        class MechanicalDamage(Symptom):
            comment = ["Physical perforation, chewing, severance, or feeding injury."]

        class GrainAbnormality(Symptom):
            comment = ["Spikelet sterility, empty glumes, spore replacement, or grain spotting."]

        class OutOfScopeSign(Symptom):
            comment = ["Sign associated with threats outside the primary diagnostic scope of the six core diseases."]

        class InsectDamageSign(OutOfScopeSign, MechanicalDamage):
            comment = ["Damage symptom caused specifically by insect feeding."]

        # -------------------------------------------------------------
        # Biotic Threat Hierarchy
        # -------------------------------------------------------------
        class Threat(Thing):
            comment = ["Biotic causal agent (pathogen or parasitic pest) inflicting economic injury on rice."]

        class Disease(Threat):
            comment = ["Infectious disease of rice caused by fungal, bacterial, or viral phytopathogens."]

        class Pest(Threat):
            comment = ["Animal or nematode pest infesting rice crops."]

        class ControlTreatment(Thing):
            comment = ["Integrated Pest Management (IPM) recommendation or intervention for managing a threat."]

        # -------------------------------------------------------------
        # Object & Datatype Properties
        # -------------------------------------------------------------
        class hasObservation(Rice >> Observation):
            comment = ["Associates a rice plant sample with an observed field sign or context."]

        class hasSymptom(hasObservation):
            domain = [Rice]
            range = [Symptom]
            comment = ["Associates a rice plant sample with a plant pathological symptom."]

        class hasOrganismSighting(hasObservation):
            domain = [Rice]
            range = [OrganismSighting]
            comment = ["Associates a rice plant sample with an observed organism presence."]

        class hasVectorSighting(hasObservation):
            domain = [Rice]
            range = [VectorSighting]
            comment = ["Associates a rice plant sample with an observed insect vector presence."]

        class hasEpidemiologicalContext(hasObservation):
            domain = [Rice]
            range = [EpidemiologicalContext]
            comment = ["Associates a rice plant sample with stand-level epidemiological context."]

        class hasThreat(Rice >> Threat):
            comment = ["Inferred threat affecting the rice plant individual."]

        class hasConfirmedThreat(hasThreat):
            comment = ["High-specificity, pathognomonic diagnostic inference (Tier 1)."]

        class hasSuspectedThreat(hasThreat):
            comment = ["High-sensitivity, partial scouting diagnostic inference (Tier 2)."]

        class hasDisease(hasThreat):
            domain = [Rice]
            range = [Disease]
            comment = ["Unstratified link from a rice sample to an inferred disease (flat single-tier baseline)."]

        class hasPest(hasThreat):
            domain = [Rice]
            range = [Pest]
            comment = ["Unstratified link from a rice sample to an inferred pest (flat single-tier baseline)."]

        class hasConfirmedDisease(hasConfirmedThreat, hasDisease):
            domain = [Rice]
            range = [Disease]
            comment = ["Tier-1 (confirmed) inference of a disease."]

        class hasSuspectedDisease(hasSuspectedThreat, hasDisease):
            domain = [Rice]
            range = [Disease]
            comment = ["Tier-2 (suspected) inference of a disease."]

        class hasConfirmedPest(hasConfirmedThreat, hasPest):
            domain = [Rice]
            range = [Pest]
            comment = ["Tier-1 (confirmed) inference of a pest."]

        class hasSuspectedPest(hasSuspectedThreat, hasPest):
            domain = [Rice]
            range = [Pest]
            comment = ["Tier-2 (suspected) inference of a pest."]

        class hasControlTreatment(Threat >> ControlTreatment):
            comment = ["Links a diagnosed threat to its cited IPM recommendation."]

        class hasDiagnosticConfidence(Rice >> str):
            comment = ["Datatype property recording the diagnostic confidence grade (confirmed, suspected, possible)."]

        for cls_name, relation, iri, _label in CLASS_ALIGNMENTS:
            link(getattr(onto, cls_name), relation, iri)

        # -------------------------------------------------------------
        # Instantiate Symptoms and Observations
        # -------------------------------------------------------------
        obs_individuals = {}
        for s_name in model.ALL_SYMPTOMS:
            prop_name = model.OBSERVATION_CATEGORIES.get(s_name, "hasSymptom")
            types_list = []
            descr = []

            if prop_name == "hasOrganismSighting":
                types_list.append(OrganismSighting)
                descr.append("organism sighting")
            elif prop_name == "hasVectorSighting":
                types_list.append(VectorSighting)
                descr.append("vector sighting")
            elif prop_name == "hasEpidemiologicalContext":
                types_list.append(EpidemiologicalContext)
                descr.append("epidemiological context")
            else:
                types_list.append(Symptom)
                descr.append("plant symptom")
                tax = model.SYMPTOM_TAXONOMY.get(s_name, {})
                anat = tax.get("anatomical")
                phen = tax.get("phenomenological")
                if anat and hasattr(onto, anat):
                    types_list.append(getattr(onto, anat))
                    descr.append(f"anatomical axis {anat}")
                if phen and hasattr(onto, phen):
                    types_list.append(getattr(onto, phen))
                    descr.append(f"phenomenological axis {phen}")
                if s_name in model.INSECT_DAMAGE_SIGNS:
                    types_list.append(InsectDamageSign)
                    descr.append("insect damage, out of diagnostic scope")

            inst = types_list[0](s_name, namespace=onto)
            for extra_type in types_list[1:]:
                inst.is_a.append(extra_type)
            inst.comment = [f"Observation term '{s_name.replace('_', ' ')}': " + "; ".join(descr) + "."]
            describe(inst)
            obs_individuals[s_name] = inst

        AllDifferent(list(obs_individuals.values()))

        # -------------------------------------------------------------
        # Instantiate Control Treatments (CQ08)
        # -------------------------------------------------------------
        control_individuals = {}
        for threat_key, c_data in model.CONTROL_TREATMENTS.items():
            c_inst = ControlTreatment(c_data["id"], namespace=onto)
            c_inst.comment = [f"{c_data['name']}: {c_data['recommendation']} Citation: {c_data['citation']} DOI: {c_data['doi']}"]
            control_individuals[threat_key] = c_inst

        # -------------------------------------------------------------
        # Instantiate Threats & Link Treatments / Antecedents (CQ08 & CQ10)
        # -------------------------------------------------------------
        threat_individuals = {}
        for p_name in model.PESTS:
            threat_individuals[p_name] = Pest(p_name, namespace=onto)

        for d_name in model.DISEASES:
            threat_individuals[d_name] = Disease(d_name, namespace=onto)

        for t_name, relation, iri, _label in THREAT_ALIGNMENTS:
            if t_name in threat_individuals:
                link(threat_individuals[t_name], relation, iri)

        AllDifferent(list(threat_individuals.values()))
        AllDisjoint([Pest, Disease])

        for t_name, t_inst in threat_individuals.items():
            kind = "Pest" if t_name in model.PESTS else "Disease"
            t_inst.comment = [
                f"In-scope {kind.lower()} '{t_name.replace('_', ' ')}'. hasSymptom lists its Tier-1 "
                f"canonical antecedents; hasControlTreatment links its cited IPM recommendation."
            ]
            describe(t_inst)
            if t_name in control_individuals:
                t_inst.hasControlTreatment = [control_individuals[t_name]]
            t1_meta = model.SWRL_RULES_METADATA.get(t_name, {}).get("tier1", {})
            canonical_ants = t1_meta.get("antecedents", [])
            t_inst.hasSymptom = [obs_individuals[a] for a in canonical_ants if a in obs_individuals]

        # -------------------------------------------------------------
        # Defined Classes for Classification & Machine-Provable Subsumption
        # -------------------------------------------------------------
        for t_name, t_inst in threat_individuals.items():
            meta = model.SWRL_RULES_METADATA.get(t_name, {})
            t1_ants = meta.get("tier1", {}).get("antecedents", [])
            t2_ants = meta.get("tier2", {}).get("antecedents", [])

            # Tier 2 Suspect Defined Class: union over the threat's Tier-2 rules
            disjuncts = []
            for rule_meta in meta.get("tier2_rules", []):
                expr = Rice
                for a in rule_meta["antecedents"]:
                    if a in obs_individuals:
                        expr = expr & hasObservation.value(obs_individuals[a])
                disjuncts.append(expr)
            susp_expr = disjuncts[0] if len(disjuncts) == 1 else Or(disjuncts)

            susp_cls = types.new_class(f"{t_name}Suspect", (Rice,))
            susp_cls.equivalent_to = [susp_expr]
            susp_cls.is_a.append(hasSuspectedThreat.value(t_inst))
            rule_ids = ", ".join(m["rule_id"] for m in meta.get("tier2_rules", []))
            susp_cls.comment = [f"Tier 2 definition for suspected {t_name}: union of rules {rule_ids}."]

            # Tier 1 Confirmed Defined Class (superset of Tier 2 antecedents)
            conf_expr = Rice
            for a in t1_ants:
                if a in obs_individuals:
                    conf_expr = conf_expr & hasObservation.value(obs_individuals[a])

            conf_cls = types.new_class(f"{t_name}Confirmed", (Rice,))
            conf_cls.equivalent_to = [conf_expr]
            conf_cls.is_a.append(hasConfirmedThreat.value(t_inst))
            conf_cls.comment = [f"Tier 1 pathognomonic definition for confirmed {t_name}."]

            # Possible Defined Class (Qualified Cardinality); k must match model.build_ontology
            k = max(1, int(math.ceil(len(t2_ants) * model.POSSIBLE_COVERAGE_THRESHOLD)))
            obs_cls = types.new_class(f"{t_name}Observation", (Observation,))
            obs_cls.comment = [f"Defined grouping of the Tier-2 antecedent observations of {t_name}."]
            for a in t2_ants:
                if a in obs_individuals:
                    obs_individuals[a].is_a.append(obs_cls)

            poss_cls = types.new_class(f"{t_name}Possible", (Rice,))
            poss_cls.equivalent_to = [Rice & hasObservation.min(k, obs_cls)]
            poss_cls.comment = [f"Qualified cardinality definition (min {k}) for possible {t_name}."]

    onto.save(file=output_path, format="rdfxml")
    print(f"[OK] Ontology successfully generated and saved to: {output_path}")
    return onto


if __name__ == "__main__":
    build_and_save_ontology()
