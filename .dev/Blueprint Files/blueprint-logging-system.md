# **PrimerLab — Logging System Blueprint**

This blueprint describes *how to implement* the full logging system for PrimerLab, following the rules defined in `logging-progress.md`.
It covers:

* logger architecture
* log file layout
* severity handling
* workflow integration
* debug dump handling
* implementation constraints
* extension guidance

This is the technical instruction for contributors building the logging subsystem.

---

# **1. Purpose of This Blueprint**

To define **how the logging system must be constructed**, including:

* module responsibilities
* file creation
* automatic folder generation
* severity-level behavior
* logging format
* progress logging interaction
* debug file writing

The goal:
**All workflows produce consistent, structured, deterministic logs.**

---

# **2. Logger Architecture Overview**

PrimerLab uses a centralized logging module:

```
primerlab/core/logger.py
```

This module exposes a single logger instance used throughout the system.

### No workflow or module may create its own logger.

---

# **3. Logger Responsibilities**

The logger must:

1. Write logs to `log.txt` inside the workflow output directory
2. Support `INFO`, `WARNING`, `ERROR`
3. Support silent initialization before output directory exists
4. Be safe for repeated initialization
5. Never duplicate log entries
6. Work across Windows, macOS, and Linux
7. Never print to stdout (CLI handles printing)
8. Accept arbitrary text safely

---

# **4. Logging Format Blueprint**

Each log entry must follow:

```
[YYYY-MM-DD HH:MM:SS][LEVEL] message
```

Example:

```
[2025-02-20 21:15:44][INFO] Designing primers
```

### Format rules:

* timestamp: 24-hour format
* LEVEL: `INFO`, `WARNING`, or `ERROR`
* message: single-line
* no stack traces (they go to debug folder)
* no trailing spaces

---

# **5. Logger Implementation Structure**

### 5.1 The `Logger` class

The logger must expose:

```python
class Logger:
    def info(self, message: str): ...
    def warning(self, message: str): ...
    def error(self, message: str): ...
    def set_output_path(self, path: Path): ...
```

### 5.2 Global logger instance

```python
log = Logger()
```

Imported everywhere via:

```python
from primerlab.core.logger import log
```

---

# **6. Initialization Blueprint**

Because the workflow output folder is not known until runtime, the logger must support two phases:

---

### **6.1 Phase 1 — Pre-initialization**

Before output path is known:

* log entries must be buffered in memory
* no files are written yet

---

### **6.2 Phase 2 — Activation**

When workflow output folder is created:

```python
log.set_output_path(output_dir)
```

The logger must:

* write all buffered messages to `log.txt`
* write all future messages directly to the file

---

# **7. Log File Management**

The log file resides at:

```
<run_folder>/log.txt
```

Rules:

1. Overwrite the file every run
2. Flush after each write
3. Avoid file locking issues
4. Never write multi-line messages
5. Use `utf-8` encoding

---

# **8. Integration With Progress System**

The progress system is defined in `progress.py` inside workflows.
Logging must integrate as:

### **8.1 When a step starts**

```
log.info(f"Step {i}/{n}: {step_name}... STARTED")
```

### **8.2 When a step completes**

```
log.info(f"Step {i}/{n}: {step_name}... OK")
```

### **8.3 When skipped**

```
log.warning(f"Step {i}/{n}: {step_name}... SKIPPED ({reason})")
```

### **8.4 When failed**

```
log.error(f"Step {i}/{n}: {step_name}... FAILED ({error_code})")
```

Every CLI progress message must have a corresponding log entry.

---

# **9. Debug Folder Logging Blueprint**

Within the workflow output directory:

```
debug/
    traceback.txt
    primer3_raw.txt (optional)
    blast_raw_output.txt (optional)
    config_final.json
    workflow_steps.log
```

### The logger does NOT write these.

These files are written directly by workflow utility functions.

### Logger only writes:

* `log.txt`

---

# **10. Error Logging Blueprint**

When errors occur:

1. Workflow layer logs `.error()` with error code
2. Exception is propagated upward
3. CLI catches it and prints formatted output
4. Debug traceback file is written

Example logged entry:

```
[2025-02-20 21:25:10][ERROR] ERR_TOOL_002: Primer3 execution failed
```

---

# **11. Logging in Core Layer**

Core modules:

* log significant technical operations
* must not log "workflow-level" info
* must avoid writing too much verbosity

Examples allowed:

```
log.info("Running Primer3 subprocess")
log.error("Failed to execute BLAST command")
```

Examples NOT allowed:

```
log.info("Starting PCR workflow")  ← CLI/workflow job
log.info("Returning primer results")  ← too high-level
```

---

# **12. Logging in Workflows**

Workflows must:

* log each progress step (start + end)
* log important stages (QC, off-target, Primer3 calls)
* log number of candidates found
* log warnings for borderline QC
* log summary messages

Workflows must NOT:

* log CLI messages
* print text
* include traceback text

---

# **13. Thread Safety / Async Considerations**

PrimerLab is currently synchronous.
However, logger must be:

* safe for concurrent functions inside workflows
* using simple file write locks (Python default is enough)
* prepared for future async pipelines

---

# **14. Extension Blueprint**

The logging system must be designed to support:

* optional JSON logging in the future
* “machine-readable” logs for consumption by automated contributors
* multi-workflow pipelines
* task-parallel runs (future)
* web service logging integration

All extensions must remain backward-compatible.

---

# **15. Summary**

This blueprint defines the technical implementation plan for the logging system:

* unified logger
* two-phase initialization
* structured severity formatting
* progress + logging integration
* debug folder separation
* workflow + core logging rules
* clear error handling strategy

Following this blueprint ensures **reliable, consistent, reproducible logging behavior across all PrimerLab workflows**.


