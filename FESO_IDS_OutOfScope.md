# Limitations of IDS for Fire Extinguisher Standard Validation  
## (Based on NBR 15808 and NBR 12693)

This document describes which aspects of the fire extinguisher standards **cannot be fully validated using IDS (Information Delivery Specification)**, and therefore require complementary approaches such as rule engines, SHACL, or application-level logic.

---

## 1. Context

The IDS developed for the *Fire Extinguisher Standard Model (FESM)* successfully validates:

- Presence of required entities (e.g. `IfcFireSuppressionTerminal`)
- Mandatory properties (type, capacity, certification)
- Allowed values (e.g. extinguisher types)
- Simple value constraints (boolean, pattern matching)

However, fire safety standards include **operational, spatial, and conditional rules** that go beyond IDS capabilities.

---

## 2. Coverage and Area-Based Calculations (NBR 12693)

### Requirement

The standard defines that each extinguisher (or set of extinguishers) must cover a maximum floor area depending on the risk level:

- Light risk → 500 m² per unit  
- Moderate risk → 250 m² per unit  
- High risk → 150 m² per unit  

### Why IDS cannot validate this

IDS does not support:

- Arithmetic operations (e.g. `area / coverage`)
- Aggregation of multiple elements
- Cross-object evaluation (sum of capacities vs total area)

### What is needed instead

- Rule engine or script (e.g. Python)
- Or SHACL with advanced functions

---

## 3. Travel Distance Constraints

### Requirement

Maximum distance to reach an extinguisher:

- 20 m (light/moderate risk)
- 15 m (high risk)

### Why IDS cannot validate this

IDS cannot:

- Evaluate spatial relationships
- Calculate distances between elements
- Interpret geometry or positioning in the model

### What is needed instead

- Spatial analysis using IFC geometry
- BIM tool or custom validation script

---

## 4. Fire Class Compatibility (Agent vs Fire Type)

### Requirement

Each extinguisher agent is only suitable for certain fire classes:

- Water → Class A only (not C)
- CO2 → Classes B and C
- ABC → Classes A, B, and C

### Why IDS cannot fully validate this

IDS cannot express:

- Conditional logic such as:
  - *If agent = CO2, then allowed classes = B and C*
- Relationships between multiple properties

### What is needed instead

- Rule engine (semantic or procedural)
- SHACL constraints
- Ontology-based validation (e.g. FESM)

---

## 5. Pressure Safety Relationships (PNC vs PR)

### Requirement

The rupture pressure (PR) must be proportional to the nominal pressure (PNC):

- e.g. PR ≥ 5 × PNC

### Why IDS cannot validate this

IDS does not support:

- Mathematical comparisons between two properties
- Expressions or formulas

### What is needed instead

- Validation script
- SHACL with SPARQL constraints

---

## 6. Minimum Extinguishers per Storey (Contextual)

### Requirement

At least one extinguisher per floor, and sufficient capacity based on total area.

### What IDS can do

- Validate that at least one extinguisher exists per storey

### What IDS cannot do

- Verify if the **capacity is sufficient**
- Relate floor area to extinguisher capacity

---

## 7. Installation Height Constraints

### Requirement

Mounting height depends on extinguisher weight:

- ≤ 4 kg → up to 1.60 m  
- > 4 kg → up to 1.00 m  

### Why IDS cannot validate this

IDS cannot express:

- Conditional thresholds based on another property
- Comparisons between values (mass vs height)

---

## 8. Maintenance and Lifecycle Rules

### Requirement

- Hydrostatic test every 5 years
- Periodic inspections depending on type

### Why IDS cannot validate this

IDS cannot:

- Perform date comparisons (e.g. expired vs current date)
- Evaluate temporal logic

---

## 9. Spatial Distribution and Positioning

### Requirement

- Extinguishers must be distributed according to accessibility
- Cannot exceed maximum travel distance
- Must be properly located (e.g. not obstructed)

### Why IDS cannot validate this

IDS does not support:

- Spatial reasoning
- Accessibility logic
- Path analysis

---

## 10. Composite Validation (System-Level Compliance)

### Requirement

Compliance is often evaluated at system level:

- Combination of multiple extinguishers
- Coverage redundancy
- Distribution across zones

### Why IDS cannot validate this

IDS operates at:

- **Element-level validation**

It does not support:

- System-level reasoning
- Group-based constraints

---

## 11. Summary

IDS is highly effective for:

- Data completeness
- Data correctness
- Standardisation of attributes

However, it is **not sufficient for full regulatory compliance**, as fire safety standards require:

- Calculations
- Spatial reasoning
- Conditional logic
- Temporal validation
- System-level analysis

---

## 12. Recommended Architecture

To achieve full compliance:

| Layer | Responsibility |
|------|--------------|
| IDS | Data contract (structure and presence) |
| Ontology (FESM) | Semantic rules and relationships |
| SHACL / Python | Advanced validation (logic, math, spatial) |
| CDE / UI | Visualisation and reporting |

---

## 13. Key Message

> IDS ensures that the data exists.  
> The model ensures that the data makes sense.
