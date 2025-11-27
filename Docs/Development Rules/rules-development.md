# **PrimerLab — Development Rules**

## **1. Purpose of This Document**

This document defines the mandatory development rules for PrimerLab.
All contributors — whether writing code manually or through automated systems — must follow these rules to ensure:

* consistency
* maintainability
* reproducibility
* clear architectural boundaries
* predictable behavior across all modules

These rules form the foundation for safe and scalable development.

---

# **2. Fundamental Principles**

### **2.1 Single Source of Truth**

All architectural, structural, and API-related decisions are documented in the `/Docs` folder.
No contributor may redefine or override these decisions elsewhere.

### **2.2 Layer Isolation**

PrimerLab uses a strict 3-layer architecture:

```
CLI  →  Workflows  →  Core
```

No cross-layer imports or logic violations are permitted.

### **2.3 Consistent Coding Style**

* snake_case for variables and functions
* PascalCase for classes
* no abbreviations unless standard in bioinformatics
* consistent naming across modules

Use the `naming-convention.md` as reference.

### **2.4 Modularity**

Each workflow is a standalone module with its own:

* workflow controller
* design logic
* QC logic
* off-target logic
* progress steps
* reporting functions

Workflows must not depend on each other.

### **2.5 Purity of Core Layer**

Core logic must remain:

* workflow-agnostic
* general-purpose
* reusable across modules

No workflow-specific logic may be added to `core/`.

---

# **3. Architectural Rules (Strict Enforcement)**

### ✔ Allowed Imports:

```
cli → workflows  
cli → core  
workflows → core  
```

### ✖ Prohibited Imports:

```
core → workflows  
core → cli  
workflows → cli  
workflows → workflows  
```

If a workflow requires functionality found in another workflow, that logic must be moved into `core/`.

---

# **4. File Structure Rules**

### **4.1 Workflow Modules**

Each workflow folder **must** contain the following files:

```
workflow.py  
design.py  
qc.py  
report.py  
progress.py  
__init__.py
```

Optional:

```
offtarget.py
insilico.py
scoring.py
compatibility.py
```

No other naming patterns are allowed.

### **4.2 Core Modules**

Files inside `core/` must represent general-purpose functionality.
Each file should contain a single responsibility:

* `seq_io.py` → sequence handling
* `tm_qc.py` → thermodynamic calculations
* `structure_qc.py` → secondary structure estimations
* `blast.py` → off-target search
* `logger.py` → logging utilities
* `exceptions.py` → error codes & exception classes
* `config_loader.py` → YAML merging & validation
* `data_models.py` → data model constructors

---

# **5. Contribution Rules**

### **5.1 New Features**

Before adding new features:

* check relevant blueprint files
* check module-plan
* check naming conventions
* ensure imports follow architectural rules

If unclear, update the `design-decisions.md` file before implementation.

### **5.2 Editing Existing Code**

Edits must:

* maintain function signatures unless documented
* preserve data structure formats defined in `data-model.md`
* maintain determinism and reproducibility
* not modify unrelated workflows/layers

### **5.3 Adding New Workflow Modules**

When adding a new folder in `workflows/`:

1. Ensure the new module is listed in `module-plan.md`
2. Create required files:

   ```
   workflow.py
   design.py
   qc.py
   report.py
   progress.py
   __init__.py
   ```
3. Register the workflow in the CLI dispatcher
4. Add configuration templates
5. Document all new logic in blueprint or rules files

### **5.4 Editing Config Keys**

Any change affecting config schema must:

* update default config files
* update config-design.md
* not silently break existing workflows
* increment minor version if breaking changes occur

---

# **6. Error Handling Rules**

### **6.1 Use Standard Error Codes**

Every raised exception must use a defined error code:

```
ERR_SEQ_001
ERR_CONFIG_005
ERR_TOOL_003
ERR_QC_004
ERR_WORKFLOW_002
```

Refer to `error-codes.md`.

### **6.2 Fail-Fast vs Fail-Safe**

* Fail-fast for: corrupted sequences, invalid config, missing requirements
* Fail-safe for: QC borderline, BLAST unavailability (optional), minor scoring issues

---

# **7. Logging & Progress Rules**

### **7.1 Logging**

All modules must use the unified Logger in `core/logger.py`:

* `log.info()`
* `log.warning()`
* `log.error()`

Log format follows `logging-progress.md`.

### **7.2 Progress Indicators**

Use progress steps defined in each workflow’s `progress.py`.
Progress belongs only in CLI output, not in log files.

---

# **8. Testing Rules**

### **8.1 Unit Tests**

Every core utility function must include a minimal unit test.

### **8.2 Workflow Tests**

Each workflow must have:

* a test using a small mock sequence
* deterministic output for expected results

### **8.3 No External DB reliance**

Tests must not depend on external BLAST databases or internet access.

---

# **9. Documentation Rules**

### **9.1 Mandatory Documentation**

Any new file in:

* `core/`
* `workflow/`

must include:

* a docstring explaining purpose
* function-level docstrings for all public functions
* inline comments for non-obvious logic

### **9.2 Updating Documentation**

If code changes affect:

* config behavior
* architecture
* data model
* error codes
* CLI interface

the relevant document in `/Docs` must be updated accordingly.

---

# **10. Versioning Rules**

PrimerLab follows semantic versioning:

```
MAJOR.MINOR.PATCH
```

* **PATCH** → bug fixes
* **MINOR** → new workflows, new features
* **MAJOR** → breaking architectural decisions

---

# **11. Prohibited Practices**

### ❌ No logic inside CLI

### ❌ No workflow → workflow imports

### ❌ No core → workflow imports

### ❌ No silent errors (must log or raise)

### ❌ No ambiguous variable names

### ❌ No untracked config keys

### ❌ No inconsistent naming across modules

---

# **12. Summary**

These development rules ensure that PrimerLab remains:

* scalable
* maintainable
* predictable
* safe
* and collaboration-friendly

All contributors must follow this document strictly.

