# **PrimerLab — Test Guidelines**

## **1. Purpose of This Document**

This document defines the testing strategy and standards for PrimerLab.
It ensures that all contributors write tests that are:

* deterministic
* reproducible
* workflow-agnostic
* aligned with PrimerLab’s architecture
* safe to run on local or CI environments
* not dependent on external internet resources

These guidelines apply to **all core modules**, **all workflows**, and **all future modules**.

---

# **2. Test Philosophy**

PrimerLab follows these principles:

### **2.1 Deterministic Behavior**

All tests must give identical results every run.
No randomness unless explicitly seeded.

### **2.2 No External Dependencies**

Tests must not require:

* internet access
* external databases
* large BLAST databases
* external command-line tools unless mocked

### **2.3 Isolated**

Each test must be independent and not rely on prior state.

### **2.4 Representative**

Tests should reflect realistic PCR/qPCR/CRISPR scenarios.

### **2.5 Layered Testing**

PrimerLab uses four levels of tests:

* **Unit tests** → Core layer
* **Module tests** → workflow utilities
* **Workflow tests** → end-to-end without external tools
* **Integration tests** → fully end-to-end with mocked tools

---

# **3. Test Folder Structure**

All tests are placed under:

```
tests/
    unit/
    module/
    workflow/
    integration/
    resources/
```

### **3.1 tests/unit/**

Tests for individual functions in `primerlab/core/`.

### **3.2 tests/module/**

Tests for workflow-specific helpers
(e.g., pcr/design.py, qpcr/qc.py).

### **3.3 tests/workflow/**

End-to-end workflow tests without external tools
(Primer3/BLAST must be mocked).

### **3.4 tests/integration/**

Full pipeline tests using mocked CLI invocation.

### **3.5 tests/resources/**

Sample FASTA files, YAML configs, mock tool outputs.
All must be **small** and **deterministic**.

---

# **4. Unit Test Guidelines**

Unit tests cover *core functionality*:

* sequence loading
* Tm calculation
* GC calculation
* hairpin/dimer detection logic
* config merging
* error code correctness
* exceptions

### Example (pytest):

```python
from primerlab.core.tm_qc import calculate_tm

def test_calculate_tm_basic():
    assert calculate_tm("ATGC") == pytest.approx(10.0, rel=0.1)
```

### Hard Requirements:

* no file I/O unless testing I/O modules
* fast execution (<50 ms)
* isolated input/output

---

# **5. Module Test Guidelines**

Module tests check workflow helpers but **not the full workflow**.

Examples:

* Primer3 parsing function
* Probe design function
* Internal scoring functions
* CRISPR PAM scanning

### Requirements:

* must not call Primer3 directly
* must not require BLAST
* must mock external calls

---

# **6. Workflow Test Guidelines**

Workflow tests simulate:

```
run_<workflow>_workflow(config_dict)
```

without calling external binaries.

### Requirements:

* use small example sequences
* use minimal config files
* assert correct WorkflowResult structure
* assert correct error handling
* assert QC warnings appear when expected
* assert all required fields exist

### Mocking Requirement:

Workflow tests MUST mock:

* Primer3 calls
* BLAST calls
* structure tools

Using monkeypatch or pytest-mock.

### Example:

```python
def test_pcr_workflow_basic(mock_primer3):
    result = run_pcr_workflow(pcr_minimal_config)
    assert "primers" in result.to_dict()
    assert result.meta["workflow"] == "PCR"
```

---

# **7. Integration Test Guidelines**

Integration tests simulate:

```
primerlab pcr --config example.yaml
```

but…

### ❗ WITHOUT calling real external tools.

We use:

* monkeypatched subprocess
* mock return values for Primer3 and BLAST
* temporary directories for output

### Tests must verify:

* correct output folder structure
* logs are created
* debug folder exists
* CLI exit codes
* correct handling of missing config
* correct workflow dispatch

---

# **8. Mocking Guidelines**

External tools must ALWAYS be mocked in tests.

Tools requiring mocking:

* Primer3
* BLAST
* ViennaRNA / structure tools
* any future dependency

Suggested approach:

### **8.1 Mock Primer3**

Return a small deterministic output like:

```
PRIMER_LEFT_0_SEQUENCE=ATCGATCGATCG
PRIMER_RIGHT_0_SEQUENCE=CGATCGATCGAT
```

### **8.2 Mock BLAST**

Return a small snippet representing no hits.

### **8.3 Mock Time Functions**

For runtime determinism:

```python
monkeypatch.setattr(time, "time", lambda: 1000.0)
```

### **8.4 Mock File Writes**

Ensure workflow writes expected files to temp dir.

---

# **9. Exception Testing**

Every error code and exception class must have tests.

Example:

```python
from primerlab.core.exceptions import ConfigError

def test_missing_config_key():
    with pytest.raises(ConfigError) as e:
        load_and_merge_config("invalid.yaml")
    assert e.value.code == "ERR_CONFIG_003"
```

Coverage needed for:

* SEQ, CONFIG, TOOL, QC, WORKFLOW, IO, VALIDATION, INTERNAL
* error propagation
* CLI formatting of errors

---

# **10. Golden Test Cases**

PrimerLab includes **golden output tests** stored in:

```
tests/resources/golden/
```

These contain expected JSON outputs for minimal runs.

Every workflow must have at least one golden output.

Rules:

* Do NOT regenerate golden outputs unless version changes
* Golden outputs must be small
* Golden files must use canonical ordering

---

# **11. Performance Constraints**

To keep CI fast:

* individual test < 100 ms
* workflow tests < 300 ms
* integration tests < 700 ms

Full test suite must run in **< 5 seconds** locally.

---

# **12. CI Requirements (Future)**

Automated contributors will rely on tests to avoid regressions.

CI pipeline must:

1. install PrimerLab
2. run unit tests
3. run workflow tests
4. run integration tests
5. verify no warnings or errors
6. verify deterministic output SHA for golden tests

This ensures safe automated contributions.

---

# **13. Coverage Requirements**

Minimum coverage:

* **80% overall**
* **90% core/**
* **90% workflows/**
* **100% exception handling paths**

Low coverage is unacceptable.

---

# **14. Test Naming Rules**

Use consistent naming:

### File naming:

```
test_tm_qc.py
test_seq_io.py
test_pcr_workflow.py
test_cli_pcr.py
```

### Function naming:

```
test_calculate_tm_basic()
test_pcr_workflow_no_primers()
test_config_missing_key()
test_cli_invalid_workflow()
```

---

# **15. Allowed Libraries**

PrimerLab tests must use:

* pytest
* pytest-mock / monkeypatch
* tempfile
* pathlib

NOT allowed:

* unittest.mock unless needed
* heavy testing frameworks
* network-based libraries

---

# **16. Summary**

PrimerLab’s test system ensures:

* deterministic behavior
* reproducible workflows
* safety during automated contributions
* future-proof development
* robust validation of all layers (CLI → workflow → core)

All contributors must follow this document strictly when writing or updating tests.

