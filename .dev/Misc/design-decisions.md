# **PrimerLab — Design Decisions (ADR-Style Document)**

This document captures all major architectural decisions in PrimerLab.
It follows a lightweight ADR (Architecture Decision Record) format so contributors understand:

* what decisions were made
* why those decisions were made
* what trade-offs they solve
* what constraints they impose
* what alternatives were rejected

This ensures future development remains stable, intentional, and consistent.

---

# **1. Purpose of This Document**

PrimerLab is a long-term technical project.
To maintain simplicity, stability, and contributor-friendly evolution:

* every core design decision must be recorded
* decisions must remain explicit and visible
* contributors must follow the established reasoning
* deviations require an ADR update

This document focuses on **high-impact** decisions only.

---

# **2. ADR-0001 — Three-Layer Architecture**

### **Decision:**

PrimerLab uses a strict 3-layer architecture:

```
Public API → Workflow Layer → Core Layer
```

### **Why:**

* Prevent circular imports
* Allow independent workflow development
* Make API stable for external developers
* Provide clean separation between domain logic and workflow coordination

### **Rejected Alternatives:**

* Single flat module (not scalable)
* Two-layer API (unclear separation of workflow orchestration)
* Framework-style plugin system (too early)

### **Status:**

Accepted; foundational.

---

# **3. ADR-0002 — Config System Based on YAML + CLI Override**

### **Decision:**

Configuration uses:

* YAML as primary
* CLI parameters override YAML
* merged into a validated config dictionary

### **Why:**

* YAML easy for domain scientists
* CLI override helps automation
* full determinism after merge
* works well with versioning + output metadata

### **Rejected Alternatives:**

* JSON only (less readable)
* TOML (not widely used in bioinformatics)
* pure CLI arguments

### **Status:**

Accepted.

---

# **4. ADR-0003 — Strict Data Models Using Dataclasses**

### **Decision:**

Workflow results and internal structures use `@dataclass`.

### **Why:**

* deterministic field ordering
* lightweight
* easy to test
* integrates well with JSON export

### **Rejected Alternatives:**

* NamedTuple (not flexible enough)
* Pydantic (heavy dependency, less stable across versions)

### **Status:**

Accepted.

---

# **5. ADR-0004 — Centralized Logging System (Two-Phase Initialization)**

### **Decision:**

One global logger instance with two phases:

* pre-initialization buffer
* activated when output folder is known

### **Why:**

* workflows do not know output folder at start
* prevents missing logs
* avoids logger duplication issues

### **Rejected Alternatives:**

* per-module loggers (too noisy)
* direct print statements (not allowed)

### **Status:**

Accepted.

---

# **6. ADR-0005 — Unified Output System**

### **Decision:**

All workflows must produce:

* JSON results
* Markdown report
* debug folder
* log.txt
* run metadata

### **Why:**

* consistent interface
* predictable output folders
* simplifies integration tests
* enables future batch workflows

### **Rejected Alternatives:**

* workflow-specific output format
* optional output folders

### **Status:**

Accepted.

---

# **7. ADR-0006 — Deterministic Behavior by Default**

### **Decision:**

All workflows must be deterministic.

### **Why:**

* essential for scientific reproducibility
* required for golden tests
* simplifies debugging
* ensures multiple contributors produce identical outputs

### **Rejected Alternatives:**

* timestamp-based randomness
* hidden heuristics

### **Status:**

Accepted.

---

# **8. ADR-0007 — Optional External Tools, Never Mandatory**

### **Decision:**

Primer3, BLAST, ViennaRNA are **optional extras**, not required.

### **Why:**

* many users cannot install external tools
* makes unit tests fast
* allows offline usage
* supports mocked tool calls

### **Rejected Alternatives:**

* bundling binaries (breaks PyPI compliance)
* requiring tools for installation

### **Status:**

Accepted.

---

# **9. ADR-0008 — Single Workflow Runner per Workflow Type**

### **Decision:**

Every workflow is executed by a single entry function:

Example:

```python
run_pcr_workflow(config)
```

### **Why:**

* simplifies CLI
* enables stable public API
* easier integration tests
* makes automated contributors safer

### **Rejected Alternatives:**

* dynamic workflow dispatch
* multiple entrypoints per workflow

### **Status:**

Accepted.

---

# **10. ADR-0009 — Exceptions Use Error Codes, Not Messages**

### **Decision:**

Every internal exception includes an **error code**.

### **Why:**

* machine-readable
* easier for automated contributors
* simplifies CLI error reporting
* prevents leaking sensitive data in messages

### **Rejected Alternatives:**

* free-form exception messages
* returning error messages in results

### **Status:**

Accepted.

---

# **11. ADR-0010 — CLI Never Prints Raw Exceptions**

### **Decision:**

CLI prints structured error messages, not traceback.

Traceback is written only to:

```
debug/traceback.txt
```

### **Why:**

* security
* convinces users that error handling is stable
* prevents clutter
* UX consistency

### **Rejected Alternatives:**

* letting Python throw exceptions to terminal
* mixing logs + traceback

### **Status:**

Accepted.

---

# **12. ADR-0011 — Lazy Import of Heavy Modules**

### **Decision:**

Modules like BLAST, Primer3, ViennaRNA are imported lazily.

### **Why:**

* improves initial CLI responsiveness
* avoids import errors when optional tools are missing
* supports mocked environments

### **Rejected Alternatives:**

* eager import (causes dependency failures)

### **Status:**

Accepted.

---

# **13. ADR-0012 — Workflow Logic Must Never Mutate Config**

### **Decision:**

Config dictionary is immutable at runtime.

### **Why:**

* ensures reproducibility
* allows caching
* improves debugging
* keeps debugging deterministic

### **Rejected Alternatives:**

* dynamic config adjustments
* implicit parameter mutations

### **Status:**

Accepted.

---

# **14. ADR-0013 — Public API Is Minimal and Stable**

### **Decision:**

Only curated functions are public:

```python
run_pcr, run_qpcr, run_crispr
load_config
WorkflowResult
Primer
Amplicon
```

### **Why:**

* easy for external developers
* reduces maintenance burden
* ensures backward compatibility

### **Rejected Alternatives:**

* fully exposing internal modules
* exporting all workflows

### **Status:**

Accepted.

---

# **15. ADR-0014 — Workflow Outputs Use Folder-Based Artifacts**

### **Decision:**

Every run writes results to a *dedicated output directory*.

### **Why:**

* clean separation
* simplifies debugging
* avoids accidental overwrites
* makes runs reproducible

### **Rejected Alternatives:**

* in-memory-only results
* centralized output folder

### **Status:**

Accepted.

---

# **16. ADR-0015 — No Multi-Threading in v0.x**

### **Decision:**

Single-thread execution only.

### **Why:**

* prevents race conditions
* keeps logs deterministic
* simplifies error handling
* easier to test

### **Future:**

Parallelization planned for post-v1.0.

---

# **17. ADR-0016 — Test-Driven & Regression-Safe Development**

### **Decision:**

Every change must pass:

* unit tests
* integration tests
* golden tests
* regression tests

### **Why:**

* protects against accidental behavioral changes
* stabilizes API
* enables collaboration with automated contributors

### **Status:**

Accepted.

---

# **18. ADR-0017 — No Database or Network State**

### **Decision:**

PrimerLab must remain fully file-system based, with no persistent DB.

### **Why:**

* reproducibility
* simplicity
* no migration issues
* lighter environment setup

### **Status:**

Accepted.

---

# **19. ADR-0018 — Workflows Must Be Extensible Without Refactoring Core**

### **Decision:**

New workflows should be addable without touching core logic.

### **Why:**

* ease of adding CRISPR, qPCR, multiplex workflows
* future community plugins
* safe modularity

### **Status:**

Accepted.

---

# **20. ADR-0019 — Output Reports Use Markdown Only**

### **Decision:**

Reports generated in Markdown, not HTML/PDF.

### **Why:**

* easy to read
* safe for contributors
* trivial to convert later
* avoids heavy dependencies

### **Status:**

Accepted.

---

# **21. Summary**

This document defines the most important architectural decisions in PrimerLab:

* strict 3-layer architecture
* stable public API
* YAML config system
* dataclass-based data model
* centralized logs
* optional tool wrappers
* deterministic execution
* safe CLI design
* immutable config
* directory-based output
* test-driven development
* plugin-ready workflow architecture

These decisions ensure PrimerLab evolves predictably, safely, and with long-term stability.


