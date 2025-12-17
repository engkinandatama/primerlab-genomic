# **PrimerLab — Error Handling Blueprint**

This blueprint defines how the **entire error-handling system** of PrimerLab is implemented.
It translates the conceptual rules in `error-codes.md` and `exception-handling.md` into a *concrete technical design*.

This document ensures all contributors implement errors consistently across:

* core modules
* workflows
* CLI
* config system
* external tool wrappers
* output/IO handlers

---

# **1. Purpose of This Blueprint**

This blueprint explains:

* how exceptions are structured
* how error codes propagate
* how workflows must handle failures
* how CLI formats error messages
* how debug information is written
* how to avoid leaking stack traces
* how to keep failures deterministic

The goal: **Stable, predictable, user-friendly, machine-readable error behavior.**

---

# **2. PrimerLab Error Model**

PrimerLab uses a **three-layer error model**:

```
Core Layer Errors        → raised by core
Workflow Layer Errors    → raised by workflows
CLI Layer Errors          → formatted for terminal output
```

Technical flow:

```
Core raises Exception → Workflow catches or propagates → CLI prints summary
```

---

# **3. Exception Classes Blueprint**

All exceptions must be defined in:

```
primerlab/core/exceptions.py
```

And follow this structure:

```python
class PrimerLabException(Exception):
    code: str  # ERR_XXXX_###
    message: str
    details: Optional[dict]
```

Subclasses:

* `ConfigError`
* `SequenceError`
* `ToolExecutionError`
* `QCError`
* `WorkflowError`
* `IOError` (PrimerLab-specific, not Python’s built-in)
* `ValidationError`
* `InternalError`

Each must have:

* a prefix (ERR_CONFIG, ERR_SEQ, ERR_QC, etc.)
* a numeric suffix
* readable message

---

# **4. Error Code Structure**

Error codes follow the pattern:

```
ERR_<CATEGORY>_<NUMBER>
```

Examples:

| Category | Example Code     | Meaning                     |
| -------- | ---------------- | --------------------------- |
| CONFIG   | ERR_CONFIG_003   | missing required config key |
| SEQ      | ERR_SEQ_002      | invalid nucleotide          |
| QC       | ERR_QC_005       | primer fails ΔG threshold   |
| TOOL     | ERR_TOOL_002     | Primer3 execution failed    |
| IO       | ERR_IO_001       | failed to write output      |
| WORKFLOW | ERR_WORKFLOW_004 | invalid step sequence       |
| INTERNAL | ERR_INTERNAL_999 | unexpected issue            |

Codes are defined in detail in `error-codes.md`.

---

# **5. Exception Raising Rules**

### **5.1 Always raise specific subclasses**

Correct:

```python
raise ConfigError("Missing key: parameters.tm.min", "ERR_CONFIG_003")
```

Incorrect:

```python
raise ValueError("tm missing")  # ❌ not allowed
```

---

### **5.2 Never raise raw Python exceptions in user-facing layers**

Allowed only inside core and immediately wrapped:

```python
try:
    perform_io()
except OSError as e:
    raise IOError("Cannot write output", "ERR_IO_001") from e
```

---

### **5.3 Messages must be short + machine-friendly**

Message must not contain:

* file paths
* stack traces
* multi-line text
* CLI formatting

---

# **6. Workflow Error Propagation Blueprint**

Workflow steps follow this pattern:

```python
def run_pcr_workflow(config):
    try:
        step(...)
        step(...)
    except PrimerLabException as e:
        log.error(...)
        write_debug_traceback(e)
        raise  # propagate to CLI
```

Rules:

* workflow must not catch exceptions silently
* each workflow step must log failures
* workflows do not format error messages
* raising stops the workflow immediately

---

# **7. Debug Output Blueprint**

When an exception is raised:

### The workflow must write:

```
debug/traceback.txt
```

Containing:

* exception code
* exception message
* stack trace (full)
* workflow name
* step where it failed

Example content:

```
ERR_QC_004: Primer hairpin ΔG too strong
Traceback (most recent call last):
  ...
```

This file is for developers, not end-users.

---

# **8. CLI Error Formatting Blueprint**

CLI (`primerlab/cli/main.py`) is responsible for user-friendly error output:

### CLI prints:

```
❌ Workflow failed  
Code: ERR_QC_004  
Message: Primer hairpin ΔG too strong  
See: <run_dir>/debug/traceback.txt
```

Rules:

* must not print stack trace
* must not print Python-level exception names
* must show the error code
* must show the human-readable message
* must show path to debug folder

---

# **9. Core Error Handling Blueprint**

The core layer must:

* never produce side effects after raising
* never print to stdout
* never swallow tool errors
* always wrap external tool failures using `ToolExecutionError`

Example:

```python
try:
    subprocess.run(...)
except subprocess.CalledProcessError:
    raise ToolExecutionError("Primer3 failed", "ERR_TOOL_002")
```

---

# **10. Config Error Handling Blueprint**

### Validation failures:

```python
raise ConfigError("Tm.min > Tm.max", "ERR_CONFIG_007")
```

### Mutual exclusivity:

```python
if seq and seq_path:
    raise ConfigError("Only one of sequence or sequence_path allowed", "ERR_CONFIG_006")
```

### Missing keys:

```python
if "parameters" not in cfg:
    raise ConfigError("Missing 'parameters' section", "ERR_CONFIG_003")
```

---

# **11. Sequence Error Handling Blueprint**

Raised in:

* FASTA parsing
* sequence normalization
* ambiguous bases
* empty sequences

Example:

```python
if any(n not in "ATGCN" for n in seq):
    raise SequenceError("Invalid nucleotide", "ERR_SEQ_002")
```

---

# **12. QC Error Handling Blueprint**

QC errors may be:

* warnings → workflow continues
* failures → workflow stops

Fatal QC errors:

```python
raise QCError("Primer dimer ΔG threshold exceeded", "ERR_QC_005")
```

Warnings are logged, not raised:

```python
log.warning("Primer ΔG borderline")
```

---

# **13. Workflow Error Handling Blueprint**

Each step must follow this pattern:

```python
try:
    run_step()
except PrimerLabException:
    mark_step_failed()
    propagate
```

Workflow steps must not continue after a failure.

---

# **14. IO Error Handling Blueprint**

When writing files:

```python
try:
    write_json(...)
except OSError:
    raise IOError("Failed to write primers.json", "ERR_IO_001")
```

IO errors must always propagate.

---

# **15. INTERNAL Error Handling Blueprint**

Used when something “should never happen.”

Rules:

* only allowed in core or workflow internals
* must indicate a real internal bug

Example:

```python
raise InternalError("Unreachable code executed", "ERR_INTERNAL_999")
```

---

# **16. Error Logging Blueprint**

Every raised exception must also produce:

* log.txt → `.error()` with code
* workflow_steps.log → `FAILED`
* traceback.txt → technical details

No exceptions to this rule.

---

# **17. CLI Return Codes Blueprint**

Process exit codes:

| Error Type            | Exit Code |
| --------------------- | --------- |
| Success               | 0         |
| PrimerLabException    | 1         |
| CLI errors (argparse) | 2         |
| Unhandled exceptions  | 3         |

This ensures machine automation compatibility.

---

# **18. Testing Error Handling**

Required tests:

* every error code must have a test
* workflows must stop at correct step
* CLI prints correct messages
* debug folder always created
* traceback always written

The test suite ensures the system remains reliable.

---

# **19. Future Extension Blueprint**

The error-handling system must support:

* remote execution errors
* multi-target workflows with partial failure
* soft-fail recovery
* per-step error summaries
* structured error serialization

All future enhancements must remain backward-compatible.

---

# **20. Summary**

This blueprint defines:

* complete exception architecture
* strict error propagation rules
* CLI error formatting
* debug file writing
* core/workflow separation
* type-specific error handling
* deterministic behavior
* testing requirements

Following this blueprint ensures PrimerLab’s error-handling system remains consistent, predictable, and robust.

