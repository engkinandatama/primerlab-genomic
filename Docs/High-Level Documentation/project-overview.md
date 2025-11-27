# **PrimerLab — Project Overview**

## **1. Introduction**

PrimerLab is a modular, end-to-end bioinformatics framework designed to automate primer design, validation, and analysis across multiple molecular workflows.
The project began as a way to streamline PCR primer design while ensuring a scalable foundation that can grow into more advanced genomics workflows such as qPCR probe design, CRISPR guide design, cloning, mutagenesis, and amplicon modeling.

PrimerLab is built with the long-term vision of becoming a unified Python-based toolkit that supports:

* Sequence parsing
* Primer/probe/gRNA design
* Thermodynamic QC prediction
* Off-target screening
* In-silico amplification
* Structured JSON output
* Workflow extensibility for future molecular biology applications

The project emphasizes **clean architecture**, **strict modularity**, **AI-assist development**, and **high reproducibility**.

---

## **2. Project Goals**

PrimerLab is engineered to meet four main goals:

### **(1) End-to-End Automation**

Provide a fully automated pipeline from sequence input → primer/gRNA design → QC → off-target analysis → report generation.

### **(2) Modular Expansion**

Allow easy addition of new workflows:

* PCR
* qPCR
* CRISPR
* Cloning
* Mutagenesis
* Viral Amplicon Panels
* Long Amplicon Design (future)
* Amplicon Structure Modeling (future)

### **(3) AI-Friendly Development**

The framework is intentionally structured to work seamlessly with AI coding assistants (Antigravity, Qwen Coder, ChatGPT), using:

* Strict folder architecture
* Clean import rules
* Consistent naming conventions
* Dedicated helper documentation
* Blueprint design files
* AI helper instructions and task templates

### **(4) Developer-Friendly & Reproducible**

Including:

* clean logs
* structured configuration
* explicit error codes
* well-separated layers: **CLI → Workflow → Core**
* deterministic JSON outputs
* debug folders for reproducibility

---

## **3. High-Level Architecture Summary**

PrimerLab follows a strict 3-layer architecture:

```
CLI Layer       →   Workflows Layer   →   Core Layer
```

### ✔ CLI Layer

* Handles user input
* Loads configuration
* Selects workflow
* Manages run directory & logging

### ✔ Workflows Layer

* Defines PCR, qPCR, CRISPR modules
* Controls step-by-step processes
* Uses core utilities but contains no general logic

### ✔ Core Layer

* Contains reusable logic
* Sequence IO, Tm calculation, QC, BLAST, report assembly, logging tools
* Must not depend on workflows or CLI

This clean separation ensures scalability and maintainability.

---

## **4. Development Roadmap (Short, Mid, Long Term)**

### **Short-Term (v0.1.x)**

* PCR workflow
* qPCR workflow
* Unified output system
* YAML config system
* Logging + progress bar
* Core utilities (sequence IO, QC, Primer3 integration)

### **Mid-Term (v0.2.x – v0.3.x)**

* CRISPR module
* Off-target scoring models
* Improved thermodynamic modeling
* Docker environment

### **Long-Term (v0.4.x – v1.0.x)**

* Multiplex PCR
* Cloning & mutagenesis modules
* Amplicon structure modeling
* AI-driven parameter optimization

---

## **5. Documentation Map (This Folder)**

This `Docs/` directory contains all references, rules, blueprints, and prompts required for consistent development.

### **📁 High-Level Documentation/**

Contains the foundational context for the entire project:

* **project-overview.md** ← *this file*
* project-plan.md
* architecture.md
* module-plan.md
* naming-convention.md

### **📁 Development Rules/**

Defines how the system must be built:

* rules-development.md
* coding-style.md
* error-codes.md
* api-design.md
* config-design.md
* data-model.md
* logging-progress.md

### **📁 Blueprint Files/**

Detailed deep-dives into each system component (environment, config, error handling, etc.).

### **📁 AI Helper Files/**

Guides AI coding assistants:

* how to generate modules
* how to respect architecture rules
* task templates
* behavior constraints

### **📁 Misc/**

General documents:

* Contributing guidelines
* Versioning
* Release checklist
* Glossary
* Technical roadmap

---

## **6. How to Use This Documentation**

### **For Developers**

Start with:

1. architecture.md
2. rules-development.md
3. blueprint-api-layers.md
4. blueprint-import-architecture.md

Then follow workflow-specific blueprint files.

### **For AI Coding Assistants**

Start with:

1. ai-helper-overview.md
2. ai-helper-rules.md
3. ai-prompts.md
4. task-templates.md

Each file in this documentation set is designed to be **atomic** (one topic per file), ensuring the AI never gets lost in a long monolithic document.

---

## **7. Summary**

PrimerLab is designed as a scalable, modular, AI-friendly framework for automating molecular biology workflows—starting with PCR and qPCR, and expanding into advanced genomics applications.

This overview serves as the conceptual map for the entire project, helping both humans and AI contributors understand:

* what PrimerLab is,
* why it exists,
* how it will evolve, and
* how the documentation is organized.
