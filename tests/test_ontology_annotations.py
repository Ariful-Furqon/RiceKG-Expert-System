"""
tests/test_ontology_annotations.py
----------------------------------
Guards the published `rice_ontology.owl` metadata (NEXT_TASK.md PART 4, 4-G):

1. SKOS, Dublin Core and VANN annotations use their standard namespaces, not
   properties minted in the RiceKG namespace.
2. External alignments are IRI-valued and point at the AGROVOC / PO concepts that
   were verified by label (a previous revision linked threats to unrelated
   concepts such as "X rays" and "Rhododendron simsii").
3. Every class, object property, datatype property and individual carries an
   rdfs:comment.
4. The qualified-cardinality `possible` classes use the same k as model.build_ontology.
"""

import math
import os

import pytest
import rdflib
from rdflib.namespace import OWL, RDF, RDFS, SKOS

import model
from analysis import build_ontology_owl as builder

OWL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rice_ontology.owl")
BASE = rdflib.Namespace(model.ONTOLOGY_IRI + "#")
DCTERMS = rdflib.Namespace("http://purl.org/dc/terms/")
VANN = rdflib.Namespace("http://purl.org/vocab/vann/")


@pytest.fixture(scope="module")
def graph():
    g = rdflib.Graph()
    g.parse(OWL_PATH, format="xml")
    return g


def test_no_annotation_properties_minted_in_local_namespace(graph):
    for local in ("exactMatch", "closeMatch", "title", "creator", "license"):
        assert (BASE[local], None, None) not in graph
        assert (None, BASE[local], None) not in graph


def test_ontology_metadata_uses_standard_vocabularies(graph):
    onto = rdflib.URIRef(model.ONTOLOGY_IRI)
    for prop in (DCTERMS.title, DCTERMS.creator, DCTERMS.license, VANN.preferredNamespacePrefix, OWL.versionInfo):
        assert graph.value(onto, prop) is not None, f"ontology lacks {prop}"


@pytest.mark.parametrize("name,relation,iri,label", builder.CLASS_ALIGNMENTS + builder.THREAT_ALIGNMENTS)
def test_alignment_is_iri_valued(graph, name, relation, iri, label):
    assert (BASE[name], SKOS[relation], rdflib.URIRef(iri)) in graph


def test_every_entity_has_rdfs_comment(graph):
    missing = []
    for rdf_type in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.NamedIndividual):
        for s in graph.subjects(RDF.type, rdf_type):
            if isinstance(s, rdflib.URIRef) and str(s).startswith(str(BASE)):
                if graph.value(s, RDFS.comment) is None:
                    missing.append(str(s))
    assert not missing, f"{len(missing)} entities without rdfs:comment: {missing[:10]}"


def test_possible_cardinality_matches_model(graph):
    for threat, meta in model.SWRL_RULES_METADATA.items():
        t2 = meta["tier2"]["antecedents"]
        k = max(1, int(math.ceil(len(t2) * model.POSSIBLE_COVERAGE_THRESHOLD)))
        restriction = graph.value(BASE[f"{threat}Possible"], OWL.equivalentClass)
        assert restriction is not None
        values = {int(o) for o in graph.objects(None, OWL.minQualifiedCardinality)}
        assert k in values, f"{threat}: expected min {k}"
