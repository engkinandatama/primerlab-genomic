# **PrimerLab — Technical Roadmap**

This document defines the long-term technical roadmap for PrimerLab.
It outlines:

* architectural evolution
* feature milestones
* module expansion
* future workflows
* performance and reliability improvements
* compatibility strategy
* long-term maintenance expectations

The roadmap is intentionally forward-looking and designed to support multi-year development.

---

# **1. Purpose of This Document**

This roadmap provides:

* a strategic overview of how PrimerLab should evolve
* milestone-based development planning
* guidance for contributors (including automated agents)
* clarity on short-, mid-, long-term priorities
* constraints to ensure backward-compatible growth

PrimerLab must remain stable while supporting advanced molecular workflows.

---

# **2. Versioning Milestones Overview**

PrimerLab will evolve across four major stages:

| Stage       | Version Range | Focus                                          |
| ----------- | ------------- | ---------------------------------------------- |
| **Stage 1** | v0.1.x        | Core architecture + PCR MVP                    |
| **Stage 2** | v0.2–0.3      | Workflow expansion + QC hardening              |
| **Stage 3** | v0.4–1.0      | Tooling integration + advanced modules         |
| **Stage 4** | v1.1+         | Research-grade capabilities + ecosystem growth |

Each stage progressively strengthens reliability, scalability, and modularity.

---

# **3. Stage 1 — Core Foundation (v0.1.x)**

### **Goal:** Fully functional PCR workflow with robust architecture.

### Key Deliverables:

* Core 3-layer architecture
* Config system (YAML + CLI override)
* Error handling + codes + exceptions
* Logging system + progress system
* Output system (JSON, Markdown report)
* PCR workflow MVP
* Primer3 wrapper (mocked & optional)
* Sequence utilities (GC, Tm, hairpin/dimer)
* WorkflowResult data model
* Testing suite (unit + workflow + integration)
* Basic CLI:

  ```
  primerlab pcr --config file.yaml
  ```

### Quality Targets:

* Deterministic results
* 80%+ test coverage
* Zero circular imports
* Fully reproducible output directories

**Result:**
Stable minimal product demonstrating the core capability of PrimerLab.

---

# **4. Stage 2 — Workflow Expansion (v0.2.x – v0.3.x)**

### **Goal:** Add additional workflows on top of the stable architecture.

### New Workflows:

1. **qPCR primer + probe design**
2. **Basic CRISPR gRNA design (Cas9, Cas12a)**
3. **Multiplex PCR (basic compatibility checks)**

### Enhancements:

* Expanded QC engine
* Dimer scoring improvements
* Probe QC (RNA–DNA hybrids)
* PAM scanning, off-target score filters
* Workflow-level parallelization (future-ready thread-safe design)

### Architecture Improvements:

* Abstract Workflow template
* Unified parameter schema across workflows
* Workflow-level plugin interface (internal only)

### Reliability Targets:

* Better validation messages
* Hardened exception handling
* More robust input parsing
* Cross-workflow regression tests

**Result:**
PrimerLab expands from a “single-module tool” into a **multi-workflow molecular design framework**.

---

# **5. Stage 3 — Advanced Module Integration (v0.4.x – v1.0)**

### **Goal:** Research-grade capabilities + advanced modeling.

### Advanced Modules:

1. **Amplicon Secondary Structure Modeling (DNA/RNA)**

   * fold prediction
   * ΔG calculation
   * mispriming region detection

2. **CRISPR Off-Target Modeling**

   * scoring using mismatch matrices
   * bulge-tolerant scanning
   * integration with BLAST or Bowtie (optional)

3. **Multiplex Primer Optimization**

   * cross-dimer screening
   * Tm balancing heuristics
   * candidate ranking

4. **Primer3 full-parameter exposure**

   * complete external parameter mapping
   * internal XML output support

### Tool Integrations (optional extras):

* ViennaRNA Python bindings
* Bowtie (via wrapper)
* DNA thermodynamics libraries

### Infrastructure Expansion:

* Docker images
* Cross-platform tool validation
* HPC/cluster-friendly execution structure

### Documentation:

* API reference
* usage examples for qPCR and CRISPR
* benchmarking reports

**Result:**
PrimerLab transitions from practical tool to **research-ready computational assay design platform**.

---

# **6. Stage 4 — Post-v1.0 Ecosystem Growth (v1.1+)**

### **Goal:** Establish PrimerLab as a modular ecosystem.

### Future-Ready Additions:

* **Plugin system** for community workflows
* GUI / Web interface (optional future project)
* REST API mode
* Cloud execution engine
* Multi-target design workflows (panel design)
* RNA primer design (RT-PCR & LAMP)
* Long-read amplicon planning
* Host-integrated extenders:

  * plasmid design
  * GC clamp optimization
  * in silico PCR visualization

### Research-Facing Features:

* Full thermodynamic model extensions
* machine learning–based primer scoring
* Deep learning models for off-target prediction

### Enterprise-Ready Features:

* audit logs
* run reproducibility bundle
* workflow provenance tracking

**Result:**
PrimerLab becomes a complete ecosystem suitable for community contribution, long-term research, and industrial workflows.

---

# **7. Backward Compatibility Strategy**

Once v0.1 is released:

* Public API signatures remain stable
* JSON output schema cannot change without version bump
* Config fields cannot be renamed
* Deprecated features require warnings for at least two versions
* Heavy refactoring must remain internal

Backward compatibility ensures PrimerLab can safely support a growing ecosystem.

---

# **8. Testing Milestones**

Each development stage increases testing rigor.

### v0.1.x

* Unit + workflow tests
* Golden output tests

### v0.2–0.3

* Cross-workflow regression tests
* Mocked external tool tests

### v0.4–1.0

* parallel workflow tests
* external integration tests
* performance tests

### v1.1+

* plugin system tests
* plugin compatibility tests
* compatibility tests across multiple operating systems

---

# **9. Performance Roadmap**

### Short-term:

* optimize Tm and GC calculations
* minimal overhead in config loader
* lazy loading of heavy modules

### Mid-term:

* caching Primer3 calls
* fast BLAST wrappers
* vectorized QC operations

### Long-term:

* parallelization (per-primer candidate)
* batch workflows
* GPU support for structure prediction (optional)

---

# **10. Risk & Complexity Forecast**

| Feature            | Complexity | Risk   | Notes                                 |
| ------------------ | ---------- | ------ | ------------------------------------- |
| PCR workflow       | Low        | Low    | Already stable                        |
| qPCR               | Medium     | Low    | QC complexity increases               |
| CRISPR             | Medium     | Medium | Off-target scoring is tricky          |
| Multiplex          | High       | Medium | Many pairwise comparisons             |
| Structure modeling | Very High  | High   | Thermodynamics is non-trivial         |
| Plugin system      | High       | Medium | Requires stable internal architecture |
| Cloud mode         | Very High  | High   | Many subsystems change                |

This helps prioritize safe development order.

---

# **11. Roadmap Summary**

PrimerLab will evolve through four strategic phases:

* **v0.1.x** → Core foundation + PCR workflow
* **v0.2–0.3** → Workflow expansion (qPCR, CRISPR, Multiplex)
* **v0.4–1.0** → Advanced modeling + tool integration
* **v1.1+** → Ecosystem growth + research-grade capabilities

The roadmap is designed to ensure:

* stability
* predictability
* modular growth
* backward compatibility
* sustainable contributor expansion

