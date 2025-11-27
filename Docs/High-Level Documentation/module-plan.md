# **PrimerLab — Module Plan**

## **1. Purpose of This Document**

This document provides a structured overview of all modules that PrimerLab will support.
Each module represents one molecular workflow (PCR, qPCR, CRISPR, etc.) and is implemented under:

```
primerlab/workflows/<module_name>/
```

This plan describes:

* the purpose of each module
* required subcomponents
* complexity level
* dependencies
* priority per development phase
* future pathways for expansion

It also acts as a roadmap for AI-assisted development.

---

## **2. Module Categories**

Modules in PrimerLab are organized into **four categories** based on complexity and development timeline:

### **Category A — Core Workflows (Short-Term)**

Essential modules required for initial release.

### **Category B — Advanced Workflows (Mid-Term)**

Modules expanding the toolkit beyond basic primer design.

### **Category C — High-Complexity & Specialized Workflows (Long-Term)**

Require advanced QC, modeling, or additional scientific knowledge.

### **Category D — Exploratory / R&D Modules (Future)**

Experimental features that may evolve based on research needs.

---

# **3. Category A — Core Workflows (Short-Term)**

These workflows represent the Minimum Viable Product (MVP) of PrimerLab.

---

## **3.1 PCR Workflow**

**Folder:** `primerlab/workflows/pcr/`
**Priority:** Highest (short-term)
**Purpose:** Standard primer design and QC for classical PCR.

### Required Submodules:

* `workflow.py` — controls step sequence
* `design.py` — Primer3 wrapper + candidate generation
* `qc.py` — Tm/GC validation, dimer & hairpin screening
* `offtarget.py` — BLAST search (optional)
* `insilico.py` — in-silico PCR simulation
* `report.py` — Markdown + JSON assembly
* `progress.py` — step definitions

### Dependencies:

* Core: sequence IO, QC, thermodynamics, BLAST

---

## **3.2 qPCR Workflow**

**Folder:** `primerlab/workflows/qpcr/`
**Priority:** Short-term
**Purpose:** Design primers and hydrolysis probes for quantitative PCR.

### Required Submodules:

* `workflow.py`
* `design.py` (primer + probe design)
* `qc.py` (primer/probe compatibility rules)
* `report.py`
* `progress.py`

### Dependencies:

* PCR module patterns
* Core QC functions with probe-specific extensions

---

# **4. Category B — Advanced Workflows (Mid-Term)**

More complex workflows that extend PrimerLab’s capabilities beyond basic primer design.

---

## **4.1 CRISPR Workflow**

**Folder:** `primerlab/workflows/crispr/`
**Priority:** Mid-term
**Purpose:** Guide RNA discovery, scoring, and off-target analysis.

### Required Submodules:

* `workflow.py`
* `scan.py` (PAM scanning and gRNA enumeration)
* `qc.py` (gRNA length, GC, motif rules)
* `scoring.py` (simple scoring model first)
* `offtarget.py` (BLAST or genomic mismatch search)
* `report.py`
* `progress.py`

### Dependencies:

* Advanced sequence parsing
* Off-target module enhancements

---

## **4.2 Multiplex PCR Workflow**

**Folder:** `primerlab/workflows/multiplex/`
**Purpose:** Select primer sets that do not cross-react.

### Required Submodules:

* `compatibility.py`
* `dimer_matrix.py`
* `workflow.py`
* `report.py`

### Dependencies:

* PCR QC engine v2
* Pairwise ΔG scanning

---

## **4.3 Amplicon Panel / Tiling Workflow**

**Folder:** `primerlab/workflows/panel/`
**Purpose:** Genome tiling with amplicon sets (viral panels, sequencing panels).

### Dependencies:

* multiplex QC
* amplicon spacing logic

---

# **5. Category C — High-Complexity Workflows (Long-Term)**

Large workflows requiring deeper modeling or multi-step logic.

---

## **5.1 Cloning Workflow**

**Folder:** `primerlab/workflows/cloning/`
**Purpose:** Primer design for Gibson assembly, Golden Gate, overhang design.

### Dependencies:

* restriction site detection
* assembly logic
* melting temperature balancing

---

## **5.2 Site-Directed Mutagenesis Workflow**

**Folder:** `primerlab/workflows/mutagenesis/`
**Purpose:** Mutation introduction primers with long overhangs.

### Dependencies:

* core QC engine v2
* mismatch tolerance modeling

---

## **5.3 Amplicon Structure Modeling Workflow**

**Folder:** `primerlab/workflows/structure/`
**Purpose:** Predict DNA/RNA secondary structure of amplicons.

### Dependencies:

* external modeling tools (ViennaRNA, mfold)
* visualization components

---

# **6. Category D — Research & Experimental Modules (Future)**

Highly exploratory, added after PrimerLab stabilizes.

---

## **6.1 AI-Based Primer Scoring**

Learn-based scoring for:

* primer quality
* probe performance
* gRNA efficiency

---

## **6.2 siRNA / ASO Workflow**

Targeting RNA sequences.

---

## **6.3 Automated Parameter Optimization**

AI-driven optimization of Primer3 & QC parameters.

---

## **6.4 Hybrid Pipelines**

Mixing CRISPR with PCR primers for targeted sequencing (amplicon-to-edit pipelines).

---

# **7. Inter-Module Relationships**

| Module             | Depends on                     | Provides to                       |
| ------------------ | ------------------------------ | --------------------------------- |
| PCR                | Core QC, Primer3               | Base patterns for qPCR, multiplex |
| qPCR               | PCR logic + probe QC           | Foundation for panel workflows    |
| CRISPR             | sequence scanning + off-target | Future hybrid workflows           |
| Multiplex          | QC engine v2                   | Panel workflows                   |
| Cloning            | sequence IO, overhang logic    | none                              |
| Mutagenesis        | PCR engine v2                  | none                              |
| Structure Modeling | external tools                 | QC v3                             |

---

# **8. Development Priority Summary**

The recommended order of development is:

### **Short-Term**

1. PCR
2. qPCR
3. Core utilities & architecture

### **Mid-Term**

4. CRISPR
5. QC Engine v2
6. Docker environment

### **Long-Term**

7. Multiplex
8. Cloning
9. Mutagenesis
10. Structure modeling

### **Future**

11. AI-based modules
12. Parameter optimization
13. RNA-targeting workflows

---

# **9. Summary**

This module plan outlines all workflows that PrimerLab will support, their purposes, dependencies, complexity levels, and recommended development prioritization.

It serves as a long-term blueprint for structured and scalable expansion of the PrimerLab ecosystem.

