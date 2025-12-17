# **PrimerLab — Logging & Progress System Specification**

## **1. Purpose of This Document**

This document defines how PrimerLab handles:

* logging
* progress indicators
* debug dumps
* runtime observability

The goal is to ensure that:

* contributors have clear visibility into workflow execution
* users never feel “blind” during long operations
* debug outputs are consistent and reproducible
* logs are structured and predictable

This document is strictly followed by all workflows.

---

# **2. Logging System Overview**

PrimerLab uses:

* A **unified logger** (`primerlab.core.logger`)
* A **per-run log file** (`log.txt`)
* Structured logging for reproducibility
* Clear severity levels (INFO, WARNING, ERROR)

All logging must go through the central logger.

### No workflow or core module may call `print()`.

---

# **3. Log File Structure**

Each workflow run produces:

```
<workflow>_run_<timestamp>/
    log.txt
    debug/
        traceback.txt
        primer3_raw.txt (optional)
        blast_raw_output.txt (optional)
        config_final.json
        workflow_steps.log
```

### **3.1 log.txt (Main Log File)**

Contains structured entries:

```
[2025-02-20 11:14:22][INFO] Loaded sequence (1483 bp)
[2025-02-20 11:14:23][INFO] Designing primers...
[2025-02-20 11:14:25][WARNING] Hairpin ΔG borderline for primer P2
[2025-02-20 11:14:28][ERROR] Primer3 execution failed (ERR_TOOL_002)
```

### Requirements:

* timestamp
* severity
* message
* no traceback (traceback goes to debug folder)
* no multiline entries in main log

---

# **4. Logging Severity Levels**

PrimerLab uses 3 levels:

---

## **4.1 INFO**

General information about workflow execution:

* loading files
* executing Primer3
* calculating QC
* writing output files

Example:

```
[INFO] Starting QC evaluation
```

---

## **4.2 WARNING**

Soft issues, non-fatal:

* hairpin borderline
* dimer borderline
* no primer pairs found
* off-target skipped
* user config uses deprecated key

Example:

```
[WARNING] No primer pairs passed QC filters
```

---

## **4.3 ERROR**

Hard issues:

* missing config
* invalid FASTA
* Primer3 failure
* fatal QC mismatch
* off-target must run but failed

Example:

```
[ERROR] ERR_SEQ_001: Invalid nucleotide found (R)
```

---

# **5. Progress Bar System**

### Why?

Users must never see a "frozen terminal."

Workflow execution uses a **progress indicator** (terminal-based) built using a lightweight text system.

### Requirements:

* simple and cross-platform
* descriptive step names
* updated frequently
* no heavy animations

---

## **5.1 Progress Step Definitions**

Each workflow has a `progress.py` defining:

```python
STEPS = [
    "Load sequence",
    "Design primers",
    "Evaluate QC",
    "Off-target analysis",
    "Generate report",
]
```

### Rules:

* steps must appear in fixed order
* step names must be human-readable
* every workflow must define at least 3 steps
* number of steps must match workflow design logic

---

## **5.2 Progress Display Format**

### CLI displays:

```
[1/5] Load sequence... OK
[2/5] Design primers... OK
[3/5] Evaluate QC... OK
[4/5] Off-target analysis... SKIPPED
[5/5] Generate report... OK

Workflow completed in 2.41 seconds.
```

### Allowed status labels:

* `OK`
* `SKIPPED`
* `FAILED`

---

# **6. Runtime Behavior Between Steps**

Between progress steps, long operations must log sub-events:

Examples:

```
Designing primers (Primer3)...
Primer3 returned 32 candidates
Evaluating primer QC (hairpin)...
Evaluating primer QC (dimers)...
Sorting primer pairs by QC score...
```

This prevents users from thinking the process "froze".

---

# **7. Debug Output Specification**

The `debug/` folder must contain detailed files.

---

## **7.1 traceback.txt**

Contains:

* full Python traceback
* workflow name
* timestamp
* OS + Python version
* config summary

---

## **7.2 primer3_raw.txt**

Only created if:

```yaml
advanced:
  primer3_raw: true
```

Contents:

* raw Primer3 stdout
* raw Primer3 stderr
* exact commands executed

This helps debugging parameter issues.

---

## **7.3 blast_raw_output.txt**

Created if off-target is enabled.

Contents:

* raw BLAST output
* command-line parameters
* processed hit summary

---

## **7.4 config_final.json**

The exact configuration after merging:

* default
* user config
* CLI overrides

Ensures reproducibility.

---

## **7.5 workflow_steps.log**

A plaintext log of progress progression:

```
[STEP] Load sequence
[STEP] Design primers
[STEP] Evaluate QC
...
```

This file is useful for automated debugging or analysis.

---

# **8. Logging Rules in Core Layer**

Core modules must:

* include minimal logging
* avoid workflow context
* log only domain-relevant events
* never log user-facing messages

Examples:

```
log.info("Calculating Tm using nearest-neighbor model")
log.error("BLAST execution failed: ...")
```

Core must NOT:

* print progress
* interact with CLI
* display human-facing text

---

# **9. Logging Rules in Workflows**

Workflows must:

* log each major operation
* use warnings for soft QC issues
* log Primer3 and BLAST events
* log off-target counts
* log sequence load results
* report number of valid primer pairs
* log report generation

Workflows must NOT:

* silence core-layer errors
* catch errors without rethrowing

---

# **10. Logging Rules in CLI**

CLI must:

* print progress steps
* show final success/failure summary
* display errors cleanly
* never display stack traces
* direct technical details to debug folder

Example CLI output:

```
Workflow finished successfully.
Results saved to: pcr_run_2025-02-21_18-33-01/
```

---

# **11. Extending Logging Behavior**

When introducing new workflows:

1. Add progress steps in `progress.py`
2. Integrate core logger
3. Ensure debug dumps capture workflow-specific data
4. Add workflow-specific warnings when applicable
5. Update this document if new rules are needed

---

# **12. Summary**

PrimerLab’s logging and progress system ensures:

* clear visibility during execution
* structured and reproducible logs
* strong debugging ability
* predictable per-step status output

All contributors must follow this specification strictly.

---

If you're ready, the next file is:
