# FELA IDCS — Multi-View Engineering Representation

---

## 🔧 DirectNonWeldedPressure

**Applies to:** IfcFireSuppressionTerminalType  

---

## 🧩 1. Engineering View (WHEN / THEN)

### ⚙️ WHEN
- PressurisationMode = Direct  
- JointType = NonWelded  

### 📏 THEN
- BurstPressure ≥ 5 × NominalChargingPressure  
- BurstPressure ≥ 5 MPa  

👥 **Primary users:**
- Design Engineers  
- Model Authors  
- QA / Model Review  

💡 **Why they like it:**
- Separates condition vs requirement clearly  
- Fast to read  
- Matches how engineers think  

---

## 🧠 2. Logical View (IF / THEN)

IF  
  PressurisationMode = Direct  
  JointType = NonWelded  
THEN  
  BurstPressure ≥ 5 × NominalChargingPressure  
  BurstPressure ≥ 5 MPa  

👥 **Primary users:**
- Software Developers  
- Automation Engineers  
- Systems Engineers  

💡 **Why they like it:**
- Maps directly to code logic  
- Easy to implement  
- Explicit execution structure  

---

## 🌳 3. Formal Expression (Mathematical / Tree View)

AND
├── BurstPressure ≥ (5 × NominalChargingPressure)
└── BurstPressure ≥ 5 MPa

👥 **Primary users:**
- Advanced Engineers  
- Data / Semantic Engineers  
- "Nerds"  😄

💡 **Why they like it:**
- Shows exact structure of the rule  
- No ambiguity  
- Enables full machine interpretation and transformation  

---

## 📖 4. Normative View (Standard Text)

The burst pressure shall be at least five times the nominal charging pressure and not less than 5 MPa for directly pressurised extinguishers with non-welded joints.

👥 **Primary users:**
- Auditors  
- Certification Bodies  
- Asset Owners (e.g. Petrobras)  

💡 **Why they like it:**
- Direct traceability to the standard  
- Legal and contractual confidence  
- No loss of original meaning  

---

## ⚙️ 5. Source View (IDCS / XML)

```xml
<fela:constraint name="DirectNonWeldedPressure">
  ...
</fela:constraint>
```

👥 **Primary users:**
- Developers  
- Tooling / Integration Teams  
- Ontology Engineers  

💡 **Why they like it:**
- Full fidelity  
- Machine-readable  
- Integration with systems  

---

# 💡 Notes

This document demonstrates how a single engineering rule can be represented in multiple complementary ways, each optimized for a different audience.

---

# 🚀 Key Insight

This is not just validation.

This is:

👉 **One rule — multiple representations — multiple stakeholders**

Enabling:

- Engineers → understand  
- Developers → implement  
- Auditors → trust  
- Systems → execute  

---

# 🔥 Strategic Value

Transforms:

❌ Static PDF standards  
➡️  
✅ Executable, multi-view engineering knowledge  

---