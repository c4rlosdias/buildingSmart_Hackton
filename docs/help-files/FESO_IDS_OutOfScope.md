# FESO — IDS and SHACL Normative Out-of-Scope
## Fire Extinguisher Standard (ABNT NBR 15808 / ABNT NBR 12693)

This document enumerates, with direct correspondence to the standard, all requirements from:

- ABNT NBR 15808 (portable fire extinguishers)
- ABNT NBR 12693 (installation and distribution)

that cannot be represented or validated using:

- IDS
- SHACL

Only requirements that are strictly out-of-scope for each technology are listed.

---

# 1. Pressure Safety Relationships (ABNT NBR 15808)

## Normative requirement

The rupture pressure (PR — *pressão de ruptura / burst pressure*) shall satisfy:

- Direct pressurisation (*pressurização direta / direct pressurisation*), non-welded joints (*juntas não soldadas / non-welded joints*):
  - PR ≥ 5 × PNC (*pressão nominal de carregamento / nominal charging pressure*)
  - PR ≥ 5 MPa

- Direct pressurisation, welded joints (*juntas soldadas / welded joints*):
  - PR ≥ 8 × PNC
  - PR ≥ 5 MPa

- Indirect pressurisation (*pressurização indireta / indirect pressurisation*), non-welded joints:
  - PR ≥ 4 × PNC
  - PR ≥ 5 MPa

- Indirect pressurisation, welded joints:
  - PR ≥ 7 × PNC
  - PR ≥ 5 MPa

## IDS out-of-scope

IDS cannot:

- compare one property against another property
- evaluate multiplication factors
- combine multiple numeric conditions in a single rule
- apply the rule conditionally based on:
  - pressurisation type
  - joint type

## SHACL out-of-scope

This requirement is not out-of-scope for SHACL, provided that:

- PR is explicitly represented
- PNC is explicitly represented
- pressurisation type is explicitly represented
- joint type is explicitly represented

---

# 2. Coverage per Floor Area for Class A (ABNT NBR 12693)

## Normative requirement

Maximum area covered per Class A unit:

- Light risk (*risco leve / light hazard*) → 500 m² per unit  
- Moderate risk (*risco moderado / ordinary hazard*) → 250 m² per unit  
- High risk (*risco alto / high hazard*) → 150 m² per unit  

Total required units:

- required_units = ceil(floor_area / area_per_unit)

## IDS out-of-scope

IDS cannot:

- perform division
- perform ceiling/rounding
- relate floor area to required extinguisher units
- aggregate units provided by multiple extinguishers on the same storey
- compare required total units against provided total units

## SHACL out-of-scope

SHACL cannot robustly validate this requirement directly from a standard IFC-derived graph unless an external execution layer first computes or materialises:

- floor area per storey
- extinguishing units contributed by each extinguisher
- total required units per storey
- total provided units per storey

The following parts are therefore out-of-scope for SHACL alone:

- deriving the storey floor area from geometry or quantities when not already materialised
- deriving numerical Class A units from extinguisher capacity notation when not already materialised
- computing the total provided units across all extinguishers serving the storey when that service relationship is not explicitly materialised
- computing the ceiling function for required units in a stable and reusable way across validators working directly from raw IFC-derived RDF

---

# 3. Protection for Flammable Liquids — Class B (ABNT NBR 12693)

## Normative requirement

For flammable liquids (*líquidos inflamáveis / flammable liquids*):

- Moderate risk:
  - 1 unit B per m² of liquid surface
  - minimum 20B

- High risk:
  - 2 units B per m² of liquid surface
  - minimum 40B

## IDS out-of-scope

IDS cannot:

- multiply liquid surface area by a factor
- apply minimum thresholds
- compare required Class B protection against provided Class B rating
- aggregate Class B rating across multiple extinguishers
- relate liquid surface area to extinguisher provision

## SHACL out-of-scope

SHACL cannot robustly validate this requirement directly from a standard IFC-derived graph unless an external execution layer first materialises:

- the liquid surface area subject to protection
- the required B units for that area
- the B rating contributed by each extinguisher
- the scope of which extinguishers serve that protected area

The following parts are therefore out-of-scope for SHACL alone:

- deriving liquid surface area from geometric or engineering model data when not already materialised
- deriving numerical B units from extinguisher rating strings when not already materialised
- calculating required B units including the normative minimum threshold logic as a reusable, implementation-independent rule over raw IFC-derived data
- determining which extinguishers are intended to protect a given flammable-liquid hazard area when that service relationship is not explicitly represented

---

# 4. Maximum Travel Distance (ABNT NBR 12693)

## Normative requirement

Maximum distance from any point to an extinguisher:

- Light risk → 20 m  
- Moderate risk → 20 m  
- High risk → 15 m  

## IDS out-of-scope

IDS cannot:

- compute distances between positions
- analyse paths of travel
- interpret spatial geometry
- determine the farthest protected point
- relate travel distance compliance to risk class

## SHACL out-of-scope

SHACL cannot validate this requirement directly from the model unless travel distances are precomputed and explicitly provided.

The following parts are out-of-scope for SHACL alone:

- computing the path of travel from any point to an extinguisher
- computing the maximum travel distance across a protected area
- distinguishing Euclidean distance from accessible travel path distance
- evaluating layout obstructions, circulation constraints, or actual reachability
- determining whether the placement satisfies the normative maximum distance for the applicable risk class based on geometry alone

---

# 5. Mounting Height vs Mass (ABNT NBR 12693)

## Normative requirement

Mounting height depends on extinguisher mass:

- ≤ 4 kg → maximum handle height = 1.60 m  
- > 4 kg → maximum handle height = 1.00 m  

## IDS out-of-scope

IDS cannot:

- compare mass against a threshold
- compare mounting height against a threshold
- express conditional branching
- relate mass to allowed mounting height

## SHACL out-of-scope

This requirement is not out-of-scope for SHACL, provided that:

- extinguisher mass is explicitly represented
- handle height is explicitly represented

However, the following is out-of-scope for SHACL alone:

- deriving the actual installed handle height from raw IFC geometry when that value is not explicitly materialised

---

# 6. Hydrostatic Test Validity (ABNT NBR 15808 / ABNT NBR 12962)

## Normative requirement

- hydrostatic test (*ensaio hidrostático / hydrostatic test*) shall be performed every 5 years  
- the extinguisher shall not remain in service with expired hydrostatic test validity  

## IDS out-of-scope

IDS cannot:

- compare dates against the current date
- calculate elapsed time
- evaluate whether 5 years have passed
- determine whether the extinguisher is expired

## SHACL out-of-scope

SHACL can compare explicitly represented dates, but the following remain out-of-scope for SHACL alone:

- reliable validation against a dynamic current date across different runtimes
- deriving validity from maintenance history instead of explicit date
- reconstructing validity from event sequences

---

# 7. Disposable Extinguisher Constraints (ABNT NBR 15808)

## Normative requirement

Disposable extinguishers (*extintores descartáveis / disposable extinguishers*) shall satisfy:

- maximum agent charge = 1 kg  
- service life = 5 years  

## IDS out-of-scope

IDS cannot:

- compare charge against threshold
- evaluate service life
- relate type to lifecycle rules

## SHACL out-of-scope

SHACL can validate the 1 kg threshold if explicit.

However, the following remains out-of-scope:

- determining service life from current date
- deriving lifecycle from manufacture date without explicit expiry

---

# 8. Agent Compatibility with Fire Classes (ABNT NBR 15808)

## Normative requirement

- Water → Class A, not C  
- Dry Chemical BC → Classes B and C, not A  
- CO2 → Classes B and C, not A  
- Foam → Classes A and B, not C  
- Dry Chemical ABC → Classes A, B and C  

## IDS out-of-scope

IDS cannot:

- express conditional compatibility rules
- restrict values based on other values
- define forbidden combinations

## SHACL out-of-scope

Not out-of-scope for SHACL if data is explicit.

---

# 9. Minimum Provision per Storey (ABNT NBR 12693)

## Normative requirement

Each storey shall have:

- at least one extinguisher  
- sufficient extinguishing capacity  

## IDS out-of-scope

IDS cannot validate sufficiency.

## SHACL out-of-scope

SHACL cannot compute sufficiency without:

- precomputed area
- precomputed capacity aggregation

---

# 10. Distribution and Accessibility (ABNT NBR 12693)

## Normative requirement

Extinguishers shall be:

- accessible  
- within travel distance  
- positioned for immediate use  

## IDS out-of-scope

IDS cannot evaluate any of these.

## SHACL out-of-scope

SHACL cannot evaluate:

- accessibility
- obstruction
- real usability
- spatial adequacy

---

# 11. System-Level Compliance

## Normative requirement

Compliance depends on:

- combination of extinguishers  
- total coverage  
- distribution  

## IDS out-of-scope

IDS cannot evaluate system behaviour.

## SHACL out-of-scope

SHACL cannot derive system behaviour from raw data.

---

# 12. Final Statement

IDS defines what data must exist.  
SHACL defines what explicit data must satisfy.  

Neither defines system behaviour from raw model data.
