# **PrimerLab — Exception Handling Strategy**

## **1. Purpose of This Document**

This document defines how PrimerLab handles errors and exceptions across all layers.

A consistent exception-handling strategy ensures:

* deterministic workflow behavior
* clear error propagation
* readable logs
* predictable CLI output
* safety for automated contributors
* maintainability and extensibility

These rules apply across **CLI**, **Workflows**, and **Core** layers.

---

# **2. Exception Handling Principles**

PrimerLab uses the following core principles:

### **2.1 Fail Fast on Critical Errors**

If the workflow cannot continue safely, execution must stop immediately.

### **2.2 Fail Safe on Optional Features**

Optional components (e.g., off-target analysis) may soft-fail without stopping the workflow.

### **2.3 No Silent Failures**

Exceptions must never be swallowed or ignored.

### **2.4 Use Specific Custom Exceptions**

Every error must raise a subclass of PrimerLab’s exception classes.

### **2.5 Error Codes Always Required**

Every exception must reference one of the standardized error codes from `error-codes.md`.

### **2.6 Controlled Error Propagation**

Errors should propagate up to the workflow wrapper, where they are:

* logged
* attached to debug files
* converted to CLI-friendly messages

---

# **3. Exception Class Hierarchy**

Defined in:

```
primerlab/core/exceptions.py
```

All exceptions extend from a single base class:

```python
class PrimerLabException(Exception):
    code: str
```

### **3.1 Category Classes**

Each category has its own subclass:

```python
class SequenceError(PrimerLabException): ...
class ConfigError(PrimerLabException): ...
class ToolExecutionError(PrimerLabException): ...
class QCError(PrimerLabException): ...
class WorkflowExecutionError(PrimerLabException): ...
class IOErrorCustom(PrimerLabException): ...
class ValidationError(PrimerLabException): ...
class InternalError(PrimerLabException): ...
```

### **3.2 Required Constructor**

Each must accept:

```python
def __init__(self, message: str, code: str):
    super().__init__(f"{code}: {message}")
    self.code = code
```

---

# **4. Raising Exceptions (Rules)**

### ✔ Always use explicit exception classes

### ✔ Always attach the correct error code

### ✔ Include human-readable explanation

### ✔ Prefer raising early rather than later

### ✔ Provide enough context for debugging

### Example:

```python
from primerlab.core.exceptions import ConfigError

raise ConfigError(
    "Missing required key: primer_size",
    code="ERR_CONFIG_003"
)
```

---

# **5. Workflow-Level Exception Handling**

Each workflow has an internal wrapper:

```python
def run_workflow(config):
    try:
        ...
    except PrimerLabException as e:
        log.error(str(e))
        _write_debug_traceback()
        raise
```

### Responsibilities at workflow level:

1. **Catch known PrimerLabException**
2. Log error to `log.txt`
3. Write traceback to `debug/traceback.txt`
4. Propagate upward to CLI

### **Do NOT handle exceptions silently.**

---

# **6. CLI-Level Exception Handling**

The CLI is **the only layer** allowed to present user-facing error messages.

CLI behavior when catching a `PrimerLabException`:

1. Print a formatted error block
2. Provide error code prominently
3. Point user to debug folder
4. Exit with non-zero status

Example CLI output:

```
[ERROR] ERR_CONFIG_003: Missing required key: primer_size
See debug/traceback.txt for full technical details.
```

---

# **7. Soft-Fail vs Hard-Fail Rules**

Not all errors have the same severity.
PrimerLab defines strict rules:

---

## **7.1 Hard-Fail Errors (Must Stop Workflow)**

Raise immediately:

* Sequence invalid
* Config invalid
* Primer3 missing or crashing
* Critical QC failure during primer-pair assembly
* Off-target database missing while off-target is required
* Internal errors (logic broken)

### Hard-fails → raise exception → workflow stops.

---

## **7.2 Soft-Fail Errors (Continue Workflow)**

Allowed to continue:

* BLAST unavailable but optional
* Hairpin borderline but not catastrophic
* No valid primer pairs found (workflow returns empty result)
* Non-critical warnings in QC
* Missing advanced features (e.g., optional structure modeling)

Soft-fails **must log warnings**, not raise exceptions.

Example:

```python
log.warning("Hairpin ΔG borderline for primer X (−2.8 kcal/mol)")
```

---

# **8. Debugging Output**

When any exception occurs at workflow level:

### CLI must ensure the following debug files exist:

```
debug/
    traceback.txt
    primer3_raw.txt           (if enabled)
    blast_raw_output.txt      (if used)
    config_final.json
    workflow_steps.log
```

Traceback file contains:

* full Python traceback
* workflow name
* timestamp
* system info (OS, Python version)

This is essential for reproducibility.

---

# **9. Recoverable vs Non-Recoverable Errors**

### **9.1 Recoverable**

* Optional tool missing
* No valid GC content hits
* No primer pairs found
* Sub-QC but usable candidates

Workflow returns:

```json
{
  "primers": [],
  "qc": { "warnings": [...], "errors": [...] }
}
```

### **9.2 Non-Recoverable**

* Bad config
* Unreadable input file
* Invalid sequence
* Corrupted Primer3 output
* Core module misbehavior

Workflow must terminate.

---

# **10. Exception Safety in Specific Layers**

---

## **10.1 Core Layer**

Core must:

* never swallow exceptions
* never convert known exceptions into InternalError
* raise specific errors immediately
* use explicit exception types

Core must NOT catch errors from:

* Primer3
* BLAST
* filesystem

except to wrap them:

```python
raise ToolExecutionError("Primer3 failed", "ERR_TOOL_002")
```

---

## **10.2 Workflow Layer**

Workflow layer may:

* catch exceptions only to log and rethrow
* convert soft errors into warnings
* validate combinatorial requirements

Workflow layer must NOT:

* reclassify exception categories
* override error messages or codes

---

## **10.3 CLI Layer**

CLI is responsible for:

* presenting messages
* formatting errors
* returning non-zero exit codes

CLI must NOT:

* add technical details to user-facing errors
* modify codes
* raise new exceptions

---

# **11. Interaction With Testing**

Every error path must be testable.

Unit tests must assert:

* correct exception class
* correct error code
* correct message pattern

Example:

```python
with pytest.raises(ConfigError) as e:
    load_and_merge_config("bad.yaml")

assert e.value.code == "ERR_CONFIG_002"
```

---

# **12. Extending Error Handling**

When adding new workflows or features:

1. Add error codes in `error-codes.md`
2. Add or extend custom exception classes if needed
3. Document new raising rules here
4. Update workflow wrappers
5. Add unit tests
6. Maintain backward compatibility

---

# **13. Summary**

The exception handling strategy ensures:

* clear separation of responsibilities
* robust error detection
* predictable behavior for contributors
* reproducible runs
* high observability via debug outputs
* zero ambiguity in failure modes

All contributors must implement exceptions strictly following this document.
