# **PrimerLab — API Design Specification**

## **1. Purpose of This Document**

This document defines the API design philosophy and interface standards for PrimerLab.

It specifies:

* how workflows are executed
* how core functions are accessed
* what the public API looks like
* how contributors should design new workflow interfaces
* how the CLI and Python library APIs remain stable

A consistent API ensures that all workflows behave predictably and integrate seamlessly with the larger system.

---

# **2. API Principles**

PrimerLab follows six core API principles:

### **2.1 Stability**

Public API signatures must remain stable across minor releases unless explicitly versioned.

### **2.2 Predictability**

All workflow APIs follow the same structure and naming patterns.

### **2.3 Explicitness**

No hidden parameters, side effects, or implicit state.

### **2.4 Layer Separation**

The API never breaks architectural boundaries:

* CLI → workflows
* workflows → core
* core never depends on workflows

### **2.5 Clear Input / Output Contracts**

Inputs must be well-defined.
Outputs must be structured and JSON-ready.

### **2.6 Minimal Surface Area**

Only necessary functions are public.
Internal helpers must be private (`_function_name`).

---

# **3. High-Level API Structure**

PrimerLab provides **two public API pathways**:

1. **Command-Line Interface (CLI)**
2. **Python Library API**

Both lead to the same workflow engine.

---

# **4. Command-Line API (CLI)**

The CLI entrypoint is:

```
primerlab
```

General structure:

```
primerlab <workflow> --config <config_path> [options]
```

### **4.1 CLI Commands**

Each workflow corresponds to a subcommand:

```
primerlab pcr --config pcr.yaml
primerlab qpcr --config qpcr.yaml
primerlab crispr --config crispr.yaml
```

Future workflows follow the same pattern.

### **4.2 Standard CLI Options**

| Option       | Description                          |
| ------------ | ------------------------------------ |
| `--config`   | Path to YAML config file             |
| `--out`      | Override output directory            |
| `--workflow` | (Alternative way to choose workflow) |
| `--verbose`  | Enable verbose logging               |
| `--dry-run`  | Validate config without executing    |
| `--version`  | Show PrimerLab version               |
| `--help`     | Show help                            |

### **4.3 CLI Behavior**

* Loads config
* Merges overrides
* Initializes logging
* Dispatches to workflow
* Writes result JSON, markdown, log, and debug files

The CLI layer includes **no domain logic**.

---

# **5. Python Library API**

PrimerLab exposes a consistent Python API that allows developers to run workflows programmatically.

Primary entrypoint:

```python
from primerlab.workflows.pcr import run_pcr_workflow
result = run_pcr_workflow(config)
```

---

# **6. Workflow API Specification**

Every workflow must expose:

```python
def run_<workflow>_workflow(config: dict) -> WorkflowResult:
```

Examples:

```python
run_pcr_workflow(config)
run_qpcr_workflow(config)
run_crispr_workflow(config)
```

### **6.1 Required Behavior**

Each workflow:

1. Validates config
2. Runs design logic
3. Runs QC
4. Runs off-target analysis (if enabled)
5. Assembles a `WorkflowResult` object
6. Logs each step
7. Returns the result to CLI

### **6.2 Function Signature (Mandatory)**

```python
def run_workflow(config: dict) -> dict:
    """
    Executes the workflow and returns a structured result dictionary.
    """
```

Where the return format matches the **WorkflowResult** data model.

---

# **7. Workflow Internal API Design**

Inside each workflow:

### **7.1 Required Functions**

Every workflow must contain:

```python
design_primers()
evaluate_qc()
run_offtarget()
build_report()
assemble_result()
```

Names may vary slightly, but the responsibility structure must remain consistent.

### **7.2 Step List API**

Each workflow defines:

```python
STEPS = [
    "Load sequence",
    "Design primers",
    "Evaluate QC",
    "Off-target analysis",
    "Generate report",
]
```

Located in `progress.py`.

---

# **8. Core Layer API (Public Utilities)**

The core provides workflow-agnostic utilities.

Available public functions include:

### **8.1 Sequence IO**

```python
from primerlab.core.seq_io import load_sequence, parse_fasta
```

### **8.2 Thermodynamics**

```python
from primerlab.core.tm_qc import calculate_tm, calculate_gc
```

### **8.3 Structure Prediction (Basic)**

```python
from primerlab.core.structure_qc import evaluate_hairpin, evaluate_dimer
```

### **8.4 Off-Target Tools**

```python
from primerlab.core.blast import run_blast
```

### **8.5 Logging**

```python
from primerlab.core.logger import log
```

### **8.6 Config Loader**

```python
from primerlab.core.config_loader import load_and_merge_config
```

### **8.7 Exception Classes**

```python
from primerlab.core.exceptions import ConfigError, SequenceError
```

The core API **must remain stable** across minor versions.

---

# **9. Result API (Unified JSON Structure)**

Each workflow returns a `WorkflowResult` object with:

```python
{
  "meta": {
    "workflow": "PCR",
    "runtime_sec": 1.53,
    "version": "0.1.0"
  },
  "input": {...},
  "primers": [...],
  "qc": {...},
  "offtarget": {...},
  "amplicon": {...},
  "report_path": "report.md"
}
```

### Required fields:

| Field         | Purpose                                          |
| ------------- | ------------------------------------------------ |
| `meta`        | metadata about run                               |
| `input`       | standardized representation of config + sequence |
| `primers`     | list of primers/probes/gRNAs                     |
| `qc`          | QC metrics and results                           |
| `offtarget`   | BLAST or mismatch results                        |
| `amplicon`    | PCR-specific product structure                   |
| `report_path` | markdown report location                         |

This format is workflow-agnostic and stable.

---

# **10. Internal API Rules**

### **10.1 Private Helpers**

Functions not exposed as part of the publicly stable API must be named with a leading underscore:

```python
def _parse_primer3_output(...):
```

### **10.2 No Global State**

All state must be passed explicitly through arguments and return values.

### **10.3 No Cross-Workflow Calls**

Workflows may only call:

* their own internal modules
* core utilities

Never another workflow.

---

# **11. Adding New Public API Elements**

When adding new functions, classes, or workflows:

1. Ensure naming aligns with conventions.
2. Document behavior in this file.
3. Add to Python and CLI API lists if intended to be public.
4. Update the module blueprint.
5. Add tests covering the new API.

Public API changes require a **minor version increase**.

---

# **12. Summary**

The PrimerLab API is intentionally minimal, predictable, and structured.
This consistency ensures:

* easy integration into pipelines
* stable programmatic usage
* simplified maintenance
* scalability to many future workflows

All contributors must follow this API design without deviation.

