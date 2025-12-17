# **PrimerLab — Output System Blueprint**

This blueprint defines the complete architecture of the output-generation system for PrimerLab.
The output subsystem must:

* produce structured folders
* support multiple output formats
* ensure reproducibility
* enable debugging
* maintain predictable file names
* scale to multiple workflows

This document translates the rules in `config-design.md`, `data-model.md`, and `logging-progress.md` into explicit implementation details.

---

# **1. Purpose of This Blueprint**

The output system handles:

* directory creation
* file generation
* JSON/MD export
* debug dump operations
* naming conventions
* structured workflow result management

The goal: **Every PrimerLab workflow produces consistent, portable, versioned results.**

---

# **2. Output Architecture Overview**

Output resides inside a **dedicated run folder** created for each workflow execution:

```
<output_dir>/
    results/
        primers.json
        amplicons.json
    report/
        report.md (or .html/.pdf in future)
    debug/
        traceback.txt
        workflow_steps.log
        config_final.json
        primer3_raw.txt
        blast_raw.txt
    log.txt
    run_metadata.json
```

The design must be:

* deterministic
* human-readable
* machine-readable
* safely parsable by automated contributors

---

# **3. Output Directory Creation Blueprint**

Workflows call a utility function:

```python
output_path = create_output_structure(base_dir, workflow_name)
```

This function must:

1. Create the base output folder
2. Create subdirectories:

   * results/
   * report/
   * debug/
3. Initialize `log.txt` (through logger activation)
4. Generate `run_metadata.json`
5. Generate an empty `workflow_steps.log`

Rules:

* Folder creation must succeed even if folders exist
* Overwrite allowed for repeated runs (not incremental)
* No mixed output between runs

---

# **4. Output File Naming Rules**

### **4.1 Results Folder**

Files must follow:

```
primers.json
amplicons.json
qc.json
offtarget.json
workflow_result.json
```

### **4.2 Report Folder**

Depending on configuration:

```
report.md
```

(Optional future: report.html, report.pdf)

### **4.3 Debug Folder**

Files include:

```
traceback.txt
config_final.json
workflow_steps.log
primer3_raw.txt
blast_raw.txt
```

### **4.4 Log File**

Top-level:

```
log.txt
```

### **4.5 Metadata File**

```
run_metadata.json
```

Contains:

```json
{
    "workflow": "PCR",
    "timestamp": "...",
    "version": "0.1.0",
    "input_hash": "...",
    "config_hash": "..."
}
```

---

# **5. Workflow Result to Output Blueprint**

Workflows return a `WorkflowResult` object (as defined in the data model) which contains:

* primers
* amplicons
* qc data
* metadata
* warnings
* internal raw structures

### Export flow:

```
WorkflowResult → results/*.json
WorkflowWarnings → results/qc.json
Metadata → run_metadata.json
Debug dumps → debug/*.txt
Report builder → report/report.md
```

Workflows never write files directly except:

* debug raw outputs
* temporary primer3/BLAST dumps

---

# **6. JSON Output Standards**

All JSON files must comply with:

* UTF-8 encoding
* sorted keys
* newline at end of file
* no trailing commas
* compact but readable formatting

Use:

```python
json.dump(data, file, indent=2, sort_keys=True)
```

---

# **7. Markdown Report Blueprint**

The report builder must generate a clean, monolithic markdown file:

```
# PCR Primer Design Report

## Input Summary
<sequence, length, GC content>

## Primer Results
- Forward primer: ...
- Reverse primer: ...
- Product length: ...

## QC Evaluation
- Tm difference: ...
- Hairpin ΔG: ...
- Dimer ΔG: ...

## Off-target Analysis
- Enabled: No/Yes
- Hits: ...

## Workflow Steps
(loaded from workflow_steps.log)

## Metadata
(timestamp, workflow, version)
```

Rules:

* all sections must exist
* optional sections appear but contain “N/A”
* must reference JSON in `/results/`

---

# **8. Debug Output Blueprint**

Debug outputs are always written to:

```
debug/
```

### Required debug files:

| File                 | Purpose             |
| -------------------- | ------------------- |
| `traceback.txt`      | for exceptions      |
| `config_final.json`  | final merged config |
| `workflow_steps.log` | step status log     |
| `primer3_raw.txt`    | raw Primer3 output  |
| `blast_raw.txt`      | raw BLAST output    |

Rules:

* debug files must be written even if workflow fails
* debug files must be small and always readable
* no binary or compressed files

---

# **9. Error Output Behavior**

If workflow fails:

1. Partial results are allowed
2. log.txt records failure
3. CLI prints formatted error summary
4. traceback.txt is required
5. workflow_steps.log must contain step status (FAIL or SKIPPED)
6. report.md is NOT generated

Error flows must be deterministic and standardized across workflows.

---

# **10. Output System Interfaces**

### 10.1 Public Interface

```python
from primerlab.core.output import create_output_structure, write_json, write_report
```

### 10.2 Workflow Usage

Minimal example in workflow:

```python
output_dir = create_output_structure(config["output"]["directory"], "PCR")

write_json(result.to_dict(), output_dir / "results" / "workflow_result.json")
generate_report(result, output_dir / "report" / "report.md")
```

Workflows must NOT manage filepaths manually.

---

# **11. Hashing Blueprint**

To ensure reproducibility:

* input sequence hash
* config hash
* workflow hash

These must be written to:

```
run_metadata.json
```

Hashes use SHA-256.

---

# **12. Multi-Run Behavior**

Outputs must **never** overwrite subdirectories of other runs unless explicitly intended.

Default behavior:

```
primerlab_out/
    <timestamp_based_run>/
         ...
    <timestamp_based_run>/
         ...
```

Format:

```
YYYYMMDD_HHMMSS_PCR/
```

Config option to override:

```
output.directory: "my_run"
```

---

# **13. Extension Blueprint**

Future outputs may include:

* HTML reports
* PDF reports
* FASTA exports
* CSV formatted summaries
* visualization plots
* multi-workflow combined reports
* cloud execution metadata
* remote download bundle generation

All extensions must remain backward-compatible.

---

# **14. Summary**

This blueprint defines:

* deterministic run folder structure
* naming conventions
* JSON and MD standards
* debug output design
* how workflows export results
* error-case output handling
* reproducibility metadata
* extensibility roadmaps

Following this blueprint ensures every PrimerLab run produces structured, clear, reproducible output packages suitable for both human inspection and machine processing.

