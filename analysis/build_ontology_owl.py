"""
analysis/build_ontology_owl.py
------------------------------
Generates the complete, publication-grade OWL 2 DL ontology file `rice_ontology.owl`
implementing PART 4 requirements (4-A through 4-H):
- Stratified observation property hierarchy (hasObservation, hasSymptom, hasOrganismSighting, hasVectorSighting, hasEpidemiologicalContext)
- Two-axis symptom taxonomy (anatomical and phenomenological)
- OWL 2 Defined Classes (ThreatConfirmed, ThreatSuspect, ThreatPossible) with provable DL subsumption
- Control treatments with peer-reviewed IPM recommendations and DOIs (CQ08)
- Datatype property hasDiagnosticConfidence (CQ09)
- OWL-introspectable antecedent relations threat.hasSymptom (CQ10)
- AllDifferent, AllDisjointClasses axioms
- AGROVOC and Plant Ontology (PO) SKOS alignments
- Dublin Core metadata and rdfs:comment on all entities
"""

import os
import sys
import types

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from owlready2 import (
    get_ontology, Thing, AllDifferent, AllDisjoint,
    World, AnnotationProperty
)

import model
OUTPUT_OWL = os.path.join(BASE_DIR, "rice_ontology.owl")


def build_and_save_ontology(output_path=OUTPUT_OWL):
    world = World()
    onto = world.get_ontology(model.ONTOLOGY_IRI)

    with onto:
        # -------------------------------------------------------------
        # Metadata and Annotation Properties
        # -------------------------------------------------------------
        class exactMatch(AnnotationProperty): pass
        class closeMatch(AnnotationProperty): pass
        class title(AnnotationProperty): pass
        class creator(AnnotationProperty): pass
        class license(AnnotationProperty): pass

        onto.comment = [
            "RiceKG: OWL 2 DL Ontology for Rice Pathogen and Pest Diagnosis. "
            "Formally axiomatised with defined classes, symptom taxonomies, and provable subsumption."
        ]

        # -------------------------------------------------------------
        # Core Class Hierarchy
        # -------------------------------------------------------------
        class Rice(Thing):
            comment = ["Oryza sativa plant individual under diagnosis."]
            exactMatch = ["http://aims.fao.org/aos/agrovoc/c_5438"]

        class Observation(Thing):
            comment = ["Top-level entity for any empirical observation made in a rice field or scout report."]

        class Symptom(Observation):
            comment = ["Direct plant sign or phenotypic manifestation of biotic injury on Oryza sativa."]
            exactMatch = ["http://aims.fao.org/aos/agrovoc/c_7568"]

        class OrganismSighting(Observation):
            comment = ["Direct physical sighting of an insect or pest organism (adults, nymphs, egg clutches, frass)."]

        class VectorSighting(Observation):
            comment = ["Entomological sighting of a known insect vector of viral phytopathogens."]

        class EpidemiologicalContext(Observation):
            comment = ["Stand-level, environmental, or temporal condition modulating outbreak probability."]

        # -------------------------------------------------------------
        # Anatomical Axis (aligned with Plant Ontology)
        # -------------------------------------------------------------
        class LeafSign(Symptom):
            comment = ["Pathological sign manifested on the leaf blade or sheath."]
            exactMatch = ["http://purl.obolibrary.org/obo/PO_0025034"]

        class StemSign(Symptom):
            comment = ["Pathological sign manifested on the culm or tiller stem."]
            exactMatch = ["http://purl.obolibrary.org/obo/PO_0009047"]

        class RootSign(Symptom):
            comment = ["Pathological sign manifested on the root system or subterranean crowns."]
            exactMatch = ["http://purl.obolibrary.org/obo/PO_0009005"]

        class PanicleSign(Symptom):
            comment = ["Pathological sign manifested on the inflorescence, panicle neck, or rachis."]
            exactMatch = ["http://purl.obolibrary.org/obo/PO_0009049"]

        class GrainSign(Symptom):
            comment = ["Pathological sign manifested on the spikelet, caryopsis, or mature grain."]
            exactMatch = ["http://purl.obolibrary.org/obo/PO_0009010"]

        class WholePlantSign(Symptom):
            comment = ["Systemic sign manifested across the entire rice plant architecture."]
            exactMatch = ["http://purl.obolibrary.org/obo/PO_0000003"]

        # -------------------------------------------------------------
        # Phenomenological Axis
        # -------------------------------------------------------------
        class Chlorosis(Symptom):
            comment = ["Foliar yellowing, discoloration, or loss of chlorophyll pigments."]
            exactMatch = ["http://aims.fao.org/aos/agrovoc/c_1568"]

        class Necrosis(Symptom):
            comment = ["Localized or extensive death and breakdown of plant cells and tissues."]
            exactMatch = ["http://aims.fao.org/aos/agrovoc/c_5097"]

        class Stunting(Symptom):
            comment = ["Suppression of plant elongation, height reduction, or dwarfing."]
            exactMatch = ["http://aims.fao.org/aos/agrovoc/c_2404"]

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
            exactMatch = ["http://aims.fao.org/aos/agrovoc/c_5969"]

        class Pest(Threat):
            comment = ["Animal or nematode pest infesting rice crops."]
            exactMatch = ["http://aims.fao.org/aos/agrovoc/c_5739"]

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

        class hasPest(hasThreat):
            domain = [Rice]
            range = [Pest]

        class hasConfirmedDisease(hasConfirmedThreat, hasDisease):
            domain = [Rice]
            range = [Disease]

        class hasSuspectedDisease(hasSuspectedThreat, hasDisease):
            domain = [Rice]
            range = [Disease]

        class hasConfirmedPest(hasConfirmedThreat, hasPest):
            domain = [Rice]
            range = [Pest]

        class hasSuspectedPest(hasSuspectedThreat, hasPest):
            domain = [Rice]
            range = [Pest]

        class hasControlTreatment(Threat >> ControlTreatment):
            comment = ["Links a diagnosed threat to its peer-reviewed IPM recommendation."]

        class hasDiagnosticConfidence(Rice >> str):
            comment = ["Datatype property recording the diagnostic confidence grade (confirmed, suspected, possible)."]

        # -------------------------------------------------------------
        # Instantiate Symptoms and Observations
        # -------------------------------------------------------------
        obs_individuals = {}
        for s_name in model.ALL_SYMPTOMS:
            prop_name = model.OBSERVATION_CATEGORIES.get(s_name, "hasSymptom")
            types_list = []

            if prop_name == "hasOrganismSighting":
                types_list.append(OrganismSighting)
            elif prop_name == "hasVectorSighting":
                types_list.append(VectorSighting)
            elif prop_name == "hasEpidemiologicalContext":
                types_list.append(EpidemiologicalContext)
            else:
                types_list.append(Symptom)
                # Apply taxonomy
                tax = model.SYMPTOM_TAXONOMY.get(s_name, {})
                anat = tax.get("anatomical")
                phen = tax.get("phenomenological")
                if anat and hasattr(onto, anat):
                    types_list.append(getattr(onto, anat))
                if phen and hasattr(onto, phen):
                    types_list.append(getattr(onto, phen))
                if s_name in model.INSECT_DAMAGE_SIGNS:
                    types_list.append(InsectDamageSign)

            # Create individual with multiple types
            inst = types_list[0](s_name, namespace=onto)
            for extra_type in types_list[1:]:
                inst.is_a.append(extra_type)
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
            p_inst = Pest(p_name, namespace=onto)
            threat_individuals[p_name] = p_inst

        for d_name in model.DISEASES:
            d_inst = Disease(d_name, namespace=onto)
            threat_individuals[d_name] = d_inst

        # AGROVOC mappings for threats
        agrovoc_threat_map = {
            "Rice_Blast": "http://aims.fao.org/aos/agrovoc/c_330663",
            "Bacterial_Leaf_Blight": "http://aims.fao.org/aos/agrovoc/c_8457",
            "False_Smut": "http://aims.fao.org/aos/agrovoc/c_8109",
            "Rice_Grassy_Stunt": "http://aims.fao.org/aos/agrovoc/c_24853",
            "Rice_Tungro_Virus": "http://aims.fao.org/aos/agrovoc/c_6615",
            "Rice_Root_Nematode": "http://aims.fao.org/aos/agrovoc/c_34645"
        }
        for t_name, uri in agrovoc_threat_map.items():
            if t_name in threat_individuals:
                threat_individuals[t_name].exactMatch.append(uri)

        AllDifferent(list(threat_individuals.values()))
        AllDisjoint([Pest, Disease])

        # Link Control Treatments and Canonical Symptoms
        for t_name, t_inst in threat_individuals.items():
            if t_name in control_individuals:
                t_inst.hasControlTreatment = [control_individuals[t_name]]
            # Link symptoms from canonical Tier 1 rule (CQ10)
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

            # Tier 2 Suspect Defined Class
            susp_expr = Rice
            for a in t2_ants:
                if a in obs_individuals:
                    susp_expr = susp_expr & hasObservation.value(obs_individuals[a])

            susp_cls_name = f"{t_name}Suspect"
            susp_cls = types.new_class(susp_cls_name, (Rice,))
            susp_cls.equivalent_to = [susp_expr]
            susp_cls.is_a.append(hasSuspectedThreat.value(t_inst))
            susp_cls.comment = [f"Tier 2 composite definition for suspected {t_name}."]

            # Tier 1 Confirmed Defined Class (Strict superset of Tier 2)
            conf_expr = Rice
            for a in t1_ants:
                if a in obs_individuals:
                    conf_expr = conf_expr & hasObservation.value(obs_individuals[a])

            conf_cls_name = f"{t_name}Confirmed"
            conf_cls = types.new_class(conf_cls_name, (Rice,))
            conf_cls.equivalent_to = [conf_expr]
            conf_cls.is_a.append(hasConfirmedThreat.value(t_inst))
            conf_cls.comment = [f"Tier 1 pathognomonic definition for confirmed {t_name}."]

            # Tier 3 Possible Defined Class (Qualified Cardinality)
            k = max(1, int(len(t2_ants) * model.POSSIBLE_COVERAGE_THRESHOLD))
            obs_cls_name = f"{t_name}Observation"
            obs_cls = types.new_class(obs_cls_name, (Observation,))
            for a in t2_ants:
                if a in obs_individuals:
                    obs_individuals[a].is_a.append(obs_cls)

            poss_cls_name = f"{t_name}Possible"
            poss_cls = types.new_class(poss_cls_name, (Rice,))
            poss_cls.equivalent_to = [Rice & hasObservation.min(k, obs_cls)]
            poss_cls.comment = [f"Tier 3 qualified cardinality definition (min {k}) for possible {t_name}."]

    onto.save(file=output_path, format="rdfxml")
    print(f"[OK] Ontology successfully generated and saved to: {output_path}")
    return onto


if __name__ == "__main__":
    build_and_save_ontology()
