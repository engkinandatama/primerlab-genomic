# **PrimerLab — Naming Conventions**

## **1. Purpose of This Document**

This document defines all naming conventions used in PrimerLab.
Consistent naming is essential for:

* readability
* maintainability
* avoiding confusion in multi-module systems
* enabling stable AI-assisted development
* reducing bugs caused by inconsistent names

All contributors and AI assistants **must follow these conventions**.

---

# **2. General Style Rules**

### **2.1 Case Conventions**

PrimerLab uses standardized naming formats across all files:

| Item             | Format           | Example          |
| ---------------- | ---------------- | ---------------- |
| Python modules   | snake_case       | `design.py`      |
| Python functions | snake_case       | `run_workflow()` |
| Python variables | snake_case       | `primer_pair`    |
| Python classes   | PascalCase       | `PrimerPair`     |
| Constants        | UPPER_SNAKE_CASE | `MAX_TM_DELTA`   |
| CLI commands     | kebab-case       | `primerlab pcr`  |
| Config keys      | snake_case       | `primer_size`    |
| Output filenames | snake_case       | `primers.txt`    |
| Folder names     | snake_case       | `primerlab_out/` |

---

# **3. Repository Folder Naming**

## **3.1 Core Folders**

These names are fixed and must not be changed:

```
primerlab/
  core/
  workflows/
  cli/
  config/
  helper/
  docs/ or Docs/
```

Rules:

* All lowercase
* snake_case
* short and descriptive

---

# **4. Workflow Module Naming**

Each workflow uses a dedicated lowercase folder:

```
primerlab/workflows/pcr/
primerlab/workflows/qpcr/
primerlab/workflows/crispr/
primerlab/workflows/multiplex/
primerlab/workflows/cloning/
primerlab/workflows/mutagenesis/
primerlab/workflows/structure/
```

Workflows **must not** use uppercase or hyphens.

---

# **5. File Naming Conventions**

## **5.1 Workflow Files**

Each workflow must contain core files named exactly:

| File           | Purpose                        |
| -------------- | ------------------------------ |
| `workflow.py`  | Main workflow controller       |
| `design.py`    | Primer/probe/gRNA design logic |
| `qc.py`        | QC validation functions        |
| `offtarget.py` | BLAST/off-target analysis      |
| `insilico.py`  | In-silico PCR or equivalent    |
| `report.py`    | Markdown/JSON assembly         |
| `progress.py`  | Step definitions               |
| `__init__.py`  | Package initializer            |

Optional workflow modules follow the same style:

* `scoring.py`
* `compatibility.py`
* `dimer_matrix.py`

---

## **5.2 Core Files**

Standard files in `primerlab/core/` include:

| File               | Purpose                         |
| ------------------ | ------------------------------- |
| `seq_io.py`        | FASTA/sequence parsing          |
| `tm_qc.py`         | Tm/GC calculations              |
| `structure_qc.py`  | Hairpin/dimer ΔG checks         |
| `blast.py`         | BLAST wrapper                   |
| `config_loader.py` | YAML config merging             |
| `logger.py`        | Logging utilities               |
| `exceptions.py`    | Custom exceptions + error codes |
| `data_models.py`   | Data model constructors         |

Never name core files with workflow-specific terms.

---

## **5.3 CLI Files**

Under `primerlab/cli/`:

* `main.py`
* `__init__.py`

No additional files unless required.

---

# **6. Naming Conventions for Python Functions**

### **6.1 Function Name Format**

All functions must be snake_case:

Examples:

```python
load_sequence()
design_primers()
evaluate_hairpin()
run_pcr_workflow()
calculate_tm()
merge_configs()
write_result_file()
```

### **6.2 Function Prefixes**

Use consistent prefixes based on purpose:

| Prefix      | Meaning                 | Example                   |
| ----------- | ----------------------- | ------------------------- |
| `load_`     | loading/parsing         | `load_fasta()`            |
| `parse_`    | interpret raw data      | `parse_primer3_output()`  |
| `design_`   | generate candidates     | `design_probe()`          |
| `evaluate_` | QC check                | `evaluate_dimer()`        |
| `run_`      | execute workflow        | `run_qpcr_workflow()`     |
| `build_`    | assemble object or file | `build_json_output()`     |
| `write_`    | write files             | `write_markdown_report()` |

---

# **7. Variable Naming Rules**

### **7.1 Sequence-Related Variables**

Use explicit names:

```
sequence
target_region
forward_primer
reverse_primer
probe
amplicon
```

Avoid vague names like `seq`, `fp`, `rp`.

### **7.2 QC Metrics**

```
tm_forward
tm_reverse
gc_content
hairpin_dg
dimer_dg
```

### **7.3 Config Variables**

Use the same key format as YAML config:

```
primer_size
tm_range
product_size
probe_length
```

---

# **8. Data Model Naming**

Data model constructors must follow:

### **8.1 Primer Models**

```python
Primer
PrimerPair
Probe
GuideRNA
```

### **8.2 QC Models**

```python
QCResult
ThermoResult
OffTargetResult
```

### **8.3 Workflow Results**

Always:

```python
WorkflowResult
```

Returned as:

```python
{
  "meta": {...},
  "primers": [...],
  "qc": {...},
  ...
}
```

---

# **9. Output File Naming**

All outputs must use snake_case lowercase:

| File         | Example                 |
| ------------ | ----------------------- |
| JSON results | `result.json`           |
| Primer list  | `primers.txt`           |
| Probe list   | `probes.txt`            |
| Report       | `report.md`             |
| Logs         | `log.txt`               |
| Debug        | `debug/primer3_raw.txt` |

Output folders:

```
pcr_run_2025-02-18_21-44-59/
qpcr_run_2025-02-19_11-07-23/
```

Format:

```
{workflow}_run_{timestamp}
```

---

# **10. Class Naming Rules**

* PascalCase
* Must not be abbreviated
* Represent real domain entities

Examples:

```python
class Primer:
class PrimerPair:
class Probe:
class GuideRNA:
class QCResult:
class WorkflowResult:
```

---

# **11. Error Code Naming**

Error codes always use:

```
ERR_<CATEGORY>_<NUMBER>
```

Examples:

```
ERR_SEQ_001
ERR_CONFIG_002
ERR_TOOL_003
ERR_QC_004
```

Categories include:

* SEQ
* CONFIG
* TOOL
* QC
* WORKFLOW

---

# **12. Summary**

These naming conventions ensure:

* readability
* consistent structure
* easy AI-assisted expansion
* predictable code generation
* zero ambiguity between layers or modules

All contributors must strictly follow these conventions throughout the project.