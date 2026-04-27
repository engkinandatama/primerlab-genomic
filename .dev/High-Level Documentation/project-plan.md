# **PrimerLab — Project Plan & Roadmap**

## **1. Purpose of This Document**

This document outlines the strategic development plan for PrimerLab, covering short-term, mid-term, long-term, and future phases.
It defines:

* the project’s development stages,
* the scope and deliverables for each phase,
* priority order of modules,
* dependencies between components,
* and a clear roadmap for future expansion.

This plan ensures consistent development for both human contributors and AI coding assistants.

---

## **2. Vision Summary**

PrimerLab aims to become a unified, modular, and extensible bioinformatics framework for designing and validating:

* PCR primers
* qPCR primers & probes
* CRISPR guide RNAs
* Cloning and mutagenesis primers
* Multiplex and tiled amplicon panels
* Amplicon structure modeling
* Future RNA/DNA assay design tools

The project emphasizes clean architecture, strict modularity, reproducibility, and long-term scalability.

---

## **3. Milestone Structure**

The development timeline is divided into four major phases:

* **Short-Term (v0.1.x)**
* **Mid-Term (v0.2.x – v0.3.x)**
* **Long-Term (v0.4.x – v1.0.x)**
* **Future / Research Extensions (post v1.0)**

Each phase builds toward a more comprehensive assay design toolkit.

---

# **4. Short-Term Roadmap (v0.1.x)**

🎯 **Goal:** Build the core framework and deliver complete PCR and qPCR workflows.

### **4.1 Core System Foundation**

Deliverables:

* Fully structured 3-layer architecture:

  * CLI Layer
  * Workflows Layer
  * Core Layer
* Unified YAML configuration system
* Robust logging + progress bar (rich-based)
* Standardized output system (run folder + result.json + report.md)
* Debug folder system
* Error handling with custom error codes
* Core utilities:

  * sequence IO
  * thermodynamic QC functions
  * BLAST interface
  * report builders

### **4.2 PCR Workflow (Minimal Complete Package)**

Includes:

* Primer3 wrapper
* Basic QC:

  * Tm, GC, length
  * hairpin ΔG
  * self/hetero dimers
* Amplicon size validation
* Optional BLAST off-target screening
* In-silico PCR for validation
* Markdown report generator

### **4.3 qPCR Workflow (Minimal Complete Package)**

Includes:

* Primer + hydrolysis probe design
* Probe Tm/GC constraints
* Primer–probe compatibility
* QC rules specific to qPCR
* Integrated report

### **4.4 Developer Infrastructure**

* AI Helper documentation suite
* Naming and coding style conventions
* Architecture and blueprint files
* Test guidelines + initial test suite
* Initial GitHub repository setup

---

# **5. Mid-Term Roadmap (v0.2.x – v0.3.x)**

🎯 **Goal:** Expand beyond basic primer workflows into CRISPR and advanced QC.

### **5.1 CRISPR Workflow**

Supports:

* gRNA candidate enumeration
* PAM filtering (NGG, NAG, etc.)
* Off-target scanning
* Scoring models (simple rule-based first)
* Batch design for multiple targets
* JSON & Markdown output

### **5.2 Advanced QC (“QC Engine v2”)**

Includes:

* RNA secondary structure prediction integrations
* More accurate ΔG models (ViennaRNA integration)
* Primer–primer interaction matrix
* Restriction-site awareness (for cloning workflows later)

### **5.3 Docker Release**

* Docker image for reproducible environment
* Pre-configured BLAST databases
* Executable CLI entrypoint within container

### **5.4 CLI Enhancements**

* Interactive mode
* Config validation tool
* Workflow auto-detection (optional)

---

# **6. Long-Term Roadmap (v0.4.x – v1.0.x)**

🎯 **Goal:** Turn PrimerLab into a complete assay design framework.

### **6.1 Cloning & Mutagenesis Workflows**

* Site-directed mutagenesis primer design
* Overhang/assembly primer design
* Gibson/Golden Gate compatible modules

### **6.2 Multiplex PCR**

* Primer compatibility matrix
* Cross-dimer avoidance scoring
* Amplicon spacing visualization

### **6.3 Amplicon Structure Modeling**

* 1D/2D amplicon modeling
* Thermodynamic stability analysis
* Secondary structure heatmaps
* Primer–amplicon binding simulation

### **6.4 Performance & Scalability**

* Batch-mode (design 100–1000 primers per run)
* Parallelization support
* Integration with GPU-based or cloud tools (optional)

---

# **7. Future R&D (Post v1.0)**

These features are exploratory and may be introduced gradually:

* ML/AI-based primer scoring
* Automated parameter optimization
* Universal CRISPR scoring models (Doench-style)
* RNA-targeting workflows (siRNA, ASO)
* Experimental data integration
* Web interface or Streamlit dashboard
* Remote BLAST/cloud compute integration

These are not commitments but research directions.

---

# **8. Release Strategy**

* Patch versions (v0.1.x) → bug fixes
* Minor versions (v0.2.x, v0.3.x) → new workflows
* Major version (v1.0.x) → stable production release

Each release will include:

* CHANGELOG updates
* version tag
* updated documentation
* test suite validation
* release checklist compliance

---

# **9. Summary**

PrimerLab's development roadmap is structured to ensure:

* rapid short-term progress (PCR/qPCR),
* strategic mid-term expansion (CRISPR + QC engine v2),
* robust long-term growth (cloning, mutagenesis, multiplex),
* and future-ready integration of advanced computational tools.

This plan serves as the master development guide for all contributors.
