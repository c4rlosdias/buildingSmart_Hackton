from pathlib import Path

from shared.capability.package.capability.plugin.capability.ttl_to_ids import TtlToIdsCapability


def test_read_ttl_fela_computable_rules_prefers_fr_is_expressible_in_ids(tmp_path: Path) -> None:
    ttl = tmp_path / "rules.ttl"
    ttl.write_text(
        """@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

@prefix fela: <https://example.org/fela#> .
@prefix fr:   <https://example.org/fela-nbr-rules#> .

fr:RuleA
    a fela:NormativeRule ;
    rdfs:label "Rule A" ;
    fela:appliesToClass fela:Thing ;
    fela:hasRequirementText "A requirement." ;
    fr:isExpressibleInIDS true .

fr:RuleB
    a fela:NormativeRule ;
    rdfs:label "Rule B" ;
    fela:appliesToClass fela:Thing ;
    fela:hasRequirementText "B requirement." ;
    fr:isExpressibleInIDS false ;
    fela:isComputableByIDS true .

fr:RuleC
    a fela:NormativeRule ;
    rdfs:label "Rule C" ;
    fela:appliesToClass fela:Thing ;
    fela:hasRequirementText "C requirement." ;
    fr:isExpressibleInIDS true ;
    fela:isComputableByIDS false .
""",
        encoding="utf-8",
    )

    cap = TtlToIdsCapability()
    rules = cap._read_ttl_fela_computable_rules(ttl)
    subjects = {r["subject"] for r in rules}

    assert len(rules) == 2
    assert "https://example.org/fela-nbr-rules#RuleA" in subjects
    assert "https://example.org/fela-nbr-rules#RuleC" in subjects


def test_read_ttl_fela_computable_rules_falls_back_to_fela_is_computable_by_ids(tmp_path: Path) -> None:
    ttl = tmp_path / "rules.ttl"
    ttl.write_text(
        """@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

@prefix fela: <https://example.org/fela#> .
@prefix fr:   <https://example.org/fela-nbr-rules#> .

fr:RuleX
    a fela:NormativeRule ;
    rdfs:label "Rule X" ;
    fela:appliesToClass fela:Thing ;
    fela:hasRequirementText "X requirement." ;
    fr:isExpressibleInIDS false ;
    fela:isComputableByIDS true .
""",
        encoding="utf-8",
    )

    cap = TtlToIdsCapability()
    rules = cap._read_ttl_fela_computable_rules(ttl)

    assert len(rules) == 1
    assert rules[0]["subject"] == "https://example.org/fela-nbr-rules#RuleX"
    assert rules[0]["label"] == "Rule X"
    assert rules[0]["requirement_text"] == "X requirement."
