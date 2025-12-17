# **PrimerLab — System Architecture**

## **1. Purpose of This Document**

This document defines the complete architectural model of PrimerLab.
It describes:

* the foundational 3-layer architecture,
* the internal folder structure,
* import rules and their rationale,
* the relationship between modules,
* execution flow from CLI to final output,
* expansion pathways for future modules.

This architecture serves as the backbone for all development, ensuring long-term maintainability and AI-friendly extensibility.

---

# **2. Architectural Philosophy**

PrimerLab follows four core principles:

### **(1) Layer Separation**

Logic is separated into distinct layers:

* CLI layer
* Workflow layer
* Core engine layer

Each layer has strict boundaries.

### **(2) Modular Workflows**

Each assay type (PCR, qPCR, CRISPR, etc.) is implemented as its own workflow package.

### **(3) Reusable Core Logic**

Shared bioinformatics functions live in the `core/` directory and are workflow-agnostic.

### **(4) AI-Friendly Structure**

File layout and rules are optimized for automated development by AI coding assistants.

---

# **3. The Three-Layer Architecture**

At the heart of PrimerLab is the **3-layer architecture**:

```
CLI Layer  →  Workflow Layer  →  Core Layer
```

Below is a detailed description of each layer.

---

## **3.1 CLI Layer**

Location:
`primerlab/cli/`

### **Responsibilities**

* Parse command-line arguments
* Read and merge configuration files
* Select the correct workflow
* Initialize logging and output directories
* Handle user errors gracefully
* Call the workflow’s `run_workflow(config)` entrypoint

### **Important Constraints**

* **No bioinformatics logic**
* **No direct dependency on workflow internals**
* **No knowledge of how primers are designed**

The CLI purely orchestrates.

---

## **3.2 Workflow Layer**

Location:
`primerlab/workflows/<workflow_name>/`

Example:

* `primerlab/workflows/pcr/`
* `primerlab/workflows/qpcr/`
* `primerlab/workflows/crispr/`

### **Responsibilities**

* Define the step-by-step process for a specific workflow
* Manage execution sequences (design → QC → off-target → report)
* Access core utilities (Primer3 wrapper, QC engine, IO tools)
* Define workflow-specific configuration and validation
* Generate final JSON object
* Trigger Markdown report generation
* Provide step list for progress bar

### **Contents per Workflow**

Each workflow contains:

* `workflow.py` (main controller)
* `design.py` (primer/probe design)
* `qc.py` (thermodynamic QC rules)
* `offtarget.py` (BLAST or other)
* `insilico.py` (optional in-silico PCR)
* `report.py`
* `progress.py` (step definitions)
* `__init__.py`

### **Important Constraints**

* Workflow modules **must not** import from:

  * other workflows
  * CLI
* Workflow logic should be **thin**, delegating heavy logic to `core/`.

---

## **3.3 Core Layer**

Location:
`primerlab/core/`

### **Responsibilities**

This is the “engine” of PrimerLab.

Contains:

* Sequence IO utilities
* Primer3 interface
* Thermodynamic QC calculation
* BLAST wrapper
* General utility functions
* Data model constructors
* Logging tools
* Config loader
* Exceptions and error code definitions

### **Important Constraints**

* Core **must never import workflow modules**
* Core **must never import CLI logic**
* Core should be workflow-agnostic and reusable

This ensures high modularity and prevents circular imports.

---

# **4. Folder Structure Overview**

```
primerlab/
  cli/
    main.py
    __init__.py

  workflows/
    pcr/
      workflow.py
      design.py
      qc.py
      report.py
      progress.py
      __init__.py

    qpcr/
      workflow.py
      design.py
      qc.py
      report.py
      progress.py
      __init__.py

    crispr/
      workflow.py
      design.py
      qc.py
      report.py
      progress.py
      __init__.py

    ...

  core/
    seq_io.py
    tm_qc.py
    structure_qc.py
    blast.py
    config_loader.py
    logger.py
    exceptions.py
    data_models.py
    __init__.py
```

This structure is optimized for:

* clear modularity
* easy integration of new modules
* painless AI-assisted coding
* minimal circular dependencies

---

# **5. Execution Flow**

Below is the end-to-end workflow when a user runs a command like:

```
primerlab pcr --config my_pcr.yaml
```

### **Step-by-step Flow**

1. **CLI parses arguments**

2. **CLI loads & merges config**

3. **CLI initializes output directory**

4. **CLI creates logger & progress system**

5. **CLI selects workflow**

6. **CLI calls:**

   ```
   run_workflow(config)
   ```

7. **Workflow handles:**

   * sequence loading
   * primer/probe design
   * QC
   * off-target analysis
   * report generation
   * JSON assembly

8. **Workflow returns result object to CLI**

9. **CLI writes result.json, report.md, log.txt**

10. **Run completes**

---

# **6. Import Rules (Strict Enforcement)**

PrimerLab enforces **strict import boundaries**:

### ✔ Allowed

```
cli → workflows
cli → core
workflows → core
```

### ✖ Not Allowed

```
workflow → other workflows
core → workflows
core → cli
workflow ↔ CLI (bi-directional)
```

These rules prevent circular dependencies and maintain clean separation.

---

# **7. Extensibility Model**

PrimerLab supports clean expansion:

### To add a new workflow:

Create a folder:

```
primerlab/workflows/newmodule/
```

Include:

* workflow.py
* design.py
* qc.py
* steps.py
* report.py
* **init**.py

Then register it in CLI.

### To add new core logic:

Add functions inside `core/` and import them into workflows.
Never place workflow-specific logic inside `core/`.

---

# **8. Summary**

The PrimerLab architecture ensures:

* strong modularity
* clean layer separation
* predictable imports
* extensibility for many future workflows
* AI-friendly code generation and refactoring
* long-term maintainability

This architecture document is a mandatory reference for all developers before implementing or modifying any module in PrimerLab.

