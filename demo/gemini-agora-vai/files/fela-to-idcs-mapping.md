# FELA → IDCS Mapping Specification

## Purpose

This document defines a deterministic transformation contract between:

- FELA Rule Ontology (TTL)
- IDCS Constraint Specification (XML)

The goal is to ensure that any transformation performed by an LLM or system produces:

- Structurally consistent XML
- No semantic loss
- No algebraic simplification
- Fully traceable constraints

---

## Fundamental Principle

The transformation is **structural, not interpretative**.

> The LLM MUST NOT reinterpret, simplify, or optimize rules.  
> It MUST translate the ontology graph into an equivalent XML structure.

---

## Global Rules

1. Each `fela:NormativeRule` MUST generate exactly one `<constraint>`.
2. Each `fela:Condition` MUST generate explicit `<condition>` elements.
3. Each `fela:Constraint` MUST generate explicit XML comparison elements.
4. Algebraic simplifications are FORBIDDEN.
5. Aggregated expressions (`max`, `min`, etc.) MUST NOT be introduced unless explicitly present in ontology.
6. Multiple constraints MUST NOT be merged into a single expression.
7. The structure of expressions MUST mirror the ontology graph.

---

## Mapping Table

### Rule Level

| FELA | IDCS |
|------|------|
| `fela:NormativeRule` | `<constraint>` |
| `rdfs:label` | `constraint @name` |
| `fela:hasRequirementText` | `<annotation><normativeText>` |

---

### Applies To

| FELA | IDCS |
|------|------|
| `fela:appliesToClass` | `<appliesTo><entity>` |

Value must be resolved using IFC binding if available.

---

### Conditions

| FELA | IDCS |
|------|------|
| `fela:EqualsCondition` | `<equals>` |
| `fela:AndCondition` | `<and>` |
| `fela:OrCondition` | `<or>` |

#### EqualsCondition mapping

```text
conditionLeftOperand → property
conditionRightOperand → value