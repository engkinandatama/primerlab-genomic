# **PrimerLab — Error Codes & Exception Map**

## **1. Purpose of This Document**

This document defines the standardized error codes used throughout PrimerLab.

The goals are to ensure that:

* every error is traceable
* contributors use consistent error naming
* workflows fail in predictable ways
* logs remain structured and searchable
* automated systems or users can identify the cause quickly
* debugging becomes straightforward

All exception classes and raised errors must reference one of the codes listed here.

---

# **2. Error Code Format**

PrimerLab uses a unified naming format:

```
ERR_<CATEGORY>_<NUMBER>
```

Example:

```
ERR_SEQ_001
ERR_CONFIG_004
ERR_TOOL_002
```

### Categories

* `SEQ` → Sequence / Input errors
* `CONFIG` → Configuration file issues
* `TOOL` → External tool or dependency failures
* `QC` → Quality control failure
* `WORKFLOW` → Workflow execution errors
* `IO` → File read/write errors
* `INTERNAL` → Unexpected internal errors
* `VALIDATION` → Constraint violation or value mismatch

Numbers increment per category.

---

# **3. Error Categories and Definitions**

Below is the complete error taxonomy used in PrimerLab, split by category.

---

# **3.1 Sequence Errors (SEQ)**

| Code            | Meaning                                                    |
| --------------- | ---------------------------------------------------------- |
| **ERR_SEQ_001** | Invalid nucleotide sequence (contains non-ATCG characters) |
| **ERR_SEQ_002** | Sequence is empty or missing                               |
| **ERR_SEQ_003** | FASTA header missing or malformed                          |
| **ERR_SEQ_004** | Region coordinates invalid (start ≥ end)                   |
| **ERR_SEQ_005** | Target region extends beyond sequence boundaries           |
| **ERR_SEQ_006** | Unsupported file format                                    |
| **ERR_SEQ_007** | Ambiguous bases not allowed for this workflow              |
| **ERR_SEQ_008** | Sequence length exceeds workflow constraints               |

## **3.1.1 Sequence Alias Codes**

| Code                   | Alias For     | Meaning                                |
| ---------------------- | ------------- | -------------------------------------- |
| **ERR_SEQ_EMPTY**      | ERR_SEQ_002   | Sequence is empty (convenient alias)   |
| **ERR_SEQ_READ**       | ERR_IO_001    | Failed to read sequence file           |
| **ERR_SEQ_INVALID_CHAR** | ERR_SEQ_001 | Invalid nucleotide characters          |
| **ERR_SEQ_TOO_SHORT**  | (new)         | Sequence too short for design (<50bp)  |

---

# **3.2 Configuration Errors (CONFIG)**

| Code               | Meaning                                         |
| ------------------ | ----------------------------------------------- |
| **ERR_CONFIG_001** | Config file missing                             |
| **ERR_CONFIG_002** | Config parsing error (YAML invalid)             |
| **ERR_CONFIG_003** | Required config key missing                     |
| **ERR_CONFIG_004** | Value type mismatch                             |
| **ERR_CONFIG_005** | Invalid parameter range (e.g., Tm min > Tm max) |
| **ERR_CONFIG_006** | Unknown workflow name                           |
| **ERR_CONFIG_007** | Output directory inaccessible                   |
| **ERR_CONFIG_008** | Unsupported config key or field                 |
| **ERR_CONFIG_009** | Invalid preset name                             |
| **ERR_CONFIG_010** | Preset configuration invalid                    |

---

# **3.3 Tool / External Dependency Errors (TOOL)**

| Code             | Meaning                                        |
| ---------------- | ---------------------------------------------- |
| **ERR_TOOL_001** | Primer3 not found or not executable            |
| **ERR_TOOL_002** | Primer3 execution failed                       |
| **ERR_TOOL_003** | BLAST+ binaries missing                        |
| **ERR_TOOL_004** | BLAST database missing or corrupted            |
| **ERR_TOOL_005** | In-silico PCR tool missing or failed           |
| **ERR_TOOL_006** | External dependency returned unexpected output |
| **ERR_TOOL_007** | Timeout while executing external tool          |
| **ERR_TOOL_008** | ViennaRNA or structure tool missing            |

## **3.3.1 Primer3-Specific Codes (TOOL_P3)**

| Code                     | Meaning                                         |
| ------------------------ | ----------------------------------------------- |
| **ERR_TOOL_P3_TIMEOUT**  | Primer3 process timeout (exceeded limit)        |
| **ERR_TOOL_P3_NO_PRIMERS** | No primers found (constraints too strict)     |
| **ERR_TOOL_P3_001**      | Primer3 execution failed                        |
| **ERR_TOOL_P3_CRASH**    | Primer3 crashed unexpectedly                    |

## **3.3.2 ViennaRNA-Specific Codes (TOOL_VR)**

| Code                      | Meaning                                         |
| ------------------------- | ----------------------------------------------- |
| **ERR_TOOL_RNAFOLD**      | RNAfold execution failed                        |
| **ERR_TOOL_RNAFOLD_PARSE**| RNAfold output parsing failed                   |
| **ERR_TOOL_RNACOFOLD**    | RNAcofold execution failed                      |
| **ERR_TOOL_RNACOFOLD_PARSE**| RNAcofold output parsing failed               |

---

# **3.4 QC Errors (QC)**

These are “fail-hard” QC rules.
(Soft QC warnings use logger instead.)

| Code           | Meaning                                     |
| -------------- | ------------------------------------------- |
| **ERR_QC_001** | Primer Tm out of allowed range              |
| **ERR_QC_002** | Primer GC content out of allowed range      |
| **ERR_QC_003** | Amplicon size outside expected range        |
| **ERR_QC_004** | Hairpin ΔG too strong (too stable)          |
| **ERR_QC_005** | Dimer ΔG too strong                         |
| **ERR_QC_006** | Forward/reverse primer Tm mismatch too high |
| **ERR_QC_007** | Probe/primer compatibility failed           |
| **ERR_QC_008** | CRISPR gRNA invalid (length/PAM mismatch)   |

---

# **3.5 Workflow Errors (WORKFLOW)**

| Code                 | Meaning                                  |
| -------------------- | ---------------------------------------- |
| **ERR_WORKFLOW_001** | Workflow entrypoint missing              |
| **ERR_WORKFLOW_002** | Workflow step failed unexpectedly        |
| **ERR_WORKFLOW_003** | Incomplete workflow result object        |
| **ERR_WORKFLOW_004** | Unsupported workflow for current config  |
| **ERR_WORKFLOW_005** | Progress step mismatch or undefined step |
| **ERR_WORKFLOW_SEQ** | Sequence loading failed in workflow      |

---

# **3.6 Input/Output Errors (IO)**

| Code           | Meaning                                       |
| -------------- | --------------------------------------------- |
| **ERR_IO_001** | Unable to read input file                     |
| **ERR_IO_002** | Unable to write output file                   |
| **ERR_IO_003** | Output directory missing or cannot be created |
| **ERR_IO_004** | Debug file writing failed                     |
| **ERR_IO_005** | Path does not exist or inaccessible           |

---

# **3.7 Validation Errors (VALIDATION)**

| Code                   | Meaning                          |
| ---------------------- | -------------------------------- |
| **ERR_VALIDATION_001** | Parameter failed validation rule |
| **ERR_VALIDATION_002** | Unsupported value encountered    |
| **ERR_VALIDATION_003** | Missing required value           |
| **ERR_VALIDATION_004** | Inconsistent data model detected |

---

# **3.8 Internal Errors (INTERNAL)**

Reserved for unexpected exceptions.

| Code                 | Meaning                                        |
| -------------------- | ---------------------------------------------- |
| **ERR_INTERNAL_001** | Unexpected internal state                      |
| **ERR_INTERNAL_002** | Unhandled exception caught by workflow wrapper |
| **ERR_INTERNAL_003** | Internal assertion failure                     |

---

# **4. Error Handling Requirements**

Every time an error is raised, it must include:

### **(1) The error code**

### **(2) A human-readable message**

### **(3) Context information if available**

Example:

```python
raise ConfigError(
    "Invalid Tm range: min=65 max=50",
    code="ERR_CONFIG_005"
)
```

Errors should be logged before raising **if possible**, unless the error is thrown during CLI startup.

---

# **5. Mapping Error Codes to Exception Classes**

Exception classes (defined in `core/exceptions.py`) must reflect these categories:

| Category   | Exception Class                         |
| ---------- | --------------------------------------- |
| SEQ        | `SequenceError`                         |
| CONFIG     | `ConfigError`                           |
| TOOL       | `ToolExecutionError`                    |
| QC         | `QCError`                               |
| WORKFLOW   | `WorkflowExecutionError`                |
| IO         | `IOErrorCustom` (not Python's built-in) |
| VALIDATION | `ValidationError`                       |
| INTERNAL   | `InternalError`                         |

The error code is attached as:

```python
class ConfigError(Exception):
    def __init__(self, message: str, code: str):
        super().__init__(f"{code}: {message}")
        self.code = code
```

---

# **6. Logging of Errors**

When an error is raised inside a workflow:

* it must be logged with `log.error()`
* the traceback must be captured in `debug/` when possible
* the final error message must include the error code

---

# **7. Extending the Error List**

When new modules introduce new failure types:

1. Add new codes under the correct category
2. Document them here
3. Add to `exceptions.py`
4. Update related tests
5. Update workflow error mapping if necessary

No duplicate numbers per category.

---

# **8. Summary**

PrimerLab uses a strict, centralized error code system to ensure clarity, maintainability, and predictable workflow behavior across all modules.

All contributors must follow this mapping consistently when raising or handling errors.
