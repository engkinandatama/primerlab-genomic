# **PrimerLab — Integration Test Strategy**

This document defines the architecture, rules, and implementation strategy for **integration tests** in PrimerLab.

Integration tests validate the *entire stack*:

```
CLI → Config Loader → Workflow → Core → Tools (mocked) → Output System
```

They ensure PrimerLab works as a unified, stable system.

---

# **1. Purpose of This Document**

Integration tests ensure:

* CLI correctly dispatches workflows
* Config system loads & merges correctly
* Workflows run end-to-end
* Output system creates correct folder/file structure
* Logs and debug dumps are created
* Error handling and progress reporting behave correctly
* Mocked tool calls integrate seamlessly
* WorkflowResult is exported properly

These tests simulate **real user interactions**, not isolated units.

---

# **2. Scope**

Integration tests cover:

* PCR workflow (initial)
* Config loading + CLI overrides
* Output folder creation
* JSON & report generation
* Logging system integration
* Exception propagation into CLI
* Mocked Primer3/BLAST execution
* WorkflowResult correctness
* Deterministic output behavior

Integration tests do **NOT** test:

* raw Primer3 binaries
* raw BLAST binaries
* performance
* heavy computation
* multi-threading (future)

---

# **3. Folder Structure**

Integration tests are located in:

```
tests/integration/
```

Structure:

```
tests/integration/
    test_cli_pcr.py
    test_workflow_end_to_end.py
    test_error_handling_cli.py
    test_output_structure.py
    resources/
        sequences/
        configs/
        golden/
```

---

# **4. Required Mocks**

Integration tests **must not** call real external tools.

Mocks required:

* Primer3
* BLAST
* Structure prediction tools
* Time-dependent functions (for deterministic timestamps)
* Hash functions (optional deterministic mode)
* CLI progress output (optional)

Mock framework: `pytest-mock` or `monkeypatch`.

---

# **5. Integration Test Categories**

There are **six categories** of integration tests.

---

## **5.1 Category 1 — CLI Invocation**

Tests the full command:

```
primerlab pcr --config tests/.../pcr_basic.yaml
```

Must validate:

* CLI parses arguments
* workflow dispatch works
* config is loaded and merged
* environment is validated
* output folder created
* WorkflowResult generated
* CLI exit code = 0

Mock required:

```python
mock_primer3.return_value = PRIMER3_MOCK_RESULT
```

Example:

```python
def test_cli_pcr_basic(tmp_path, mock_primer3):
    config = TEST_DIR / "configs/pcr_basic.yaml"

    result = run_cli(["pcr", "--config", str(config), "--out", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "results" / "primers.json").exists()
```

---

## **5.2 Category 2 — Workflow End-to-End**

Tests the workflow entrypoint directly:

```python
result = run_pcr_workflow(config_dict)
```

Must validate:

* WorkflowResult structure
* QC is included (when enabled)
* amplicon calculations correct
* warnings appear correctly
* no exceptions unless expected

Example:

```python
def test_pcr_workflow_minimal(mock_primer3):
    cfg = load_config("pcr_basic.yaml")
    result = run_pcr_workflow(cfg)

    assert result.workflow == "PCR"
    assert len(result.primers) == 2
```

---

## **5.3 Category 3 — Output Folder Structure**

Test:

* correct directories created
* all JSON outputs exist
* debug folder populated
* log.txt generated
* no extra files
* report.md generated when appropriate

Expected structure:

```
run/
    log.txt
    results/
    report/
    debug/
    run_metadata.json
```

Test example:

```python
def test_output_structure(tmp_path, mock_primer3):
    cfg = load_config("pcr_basic.yaml")
    run_dir = run_pcr_workflow(cfg).output_path

    assert (run_dir / "results").exists()
    assert (run_dir / "debug").exists()
    assert (run_dir / "report" / "report.md").exists()
```

---

## **5.4 Category 4 — Logging + Progress Integration**

Tests:

* progress messages written to log
* workflow_steps.log populated
* error cases logged properly
* no duplication of log lines

Example checks:

```python
log = open(run_dir/"log.txt").read()
assert "Step 1" in log
assert "OK" in log
```

---

## **5.5 Category 5 — Error Handling Flow**

Tests simulate failures:

* missing config fields
* invalid sequence
* mocked Primer3 failures
* IO errors (unwritable directory)

Must validate:

* workflow stops immediately
* debug/traceback.txt exists
* log.txt contains FAILED
* CLI prints error summary
* exit code = 1

Example:

```python
def test_cli_error_missing_config(mock_primer3):
    result = run_cli(["pcr", "--config", "invalid.yaml"])
    assert result.exit_code == 1
```

---

## **5.6 Category 6 — Golden Output Tests**

Golden tests ensure future changes do NOT alter output format.

Files stored under:

```
tests/integration/resources/golden/pcr_basic.json
```

Workflow output must match:

```python
assert normalize_json(actual) == normalize_json(expected)
```

Golden outputs must be manually reviewed before updates.

---

# **6. Determinism Requirements**

Integration tests must produce deterministic results:

* seed RNG (if used)
* mock time functions
* fixed hash ordering
* mocked Primer3 results identical
* fixed timestamp for metadata (override time.time)
* consistent JSON ordering

Example:

```python
monkeypatch.setattr(time, "time", lambda: 1700000000)
```

---

# **7. Test Utilities**

Utilities in:

```
tests/util.py
```

Provide:

* `run_cli(args)` helper
* `normalize_json(obj)`
* test sequence loader
* deterministic timestamp generator
* mock result builders

---

# **8. Performance Constraints**

Integration test run time:

* each test < 700ms
* full suite < 5 seconds
* no heavy tool calls
* no large test sequences

---

# **9. Required Integration Tests**

Minimum required:

| Test Type | Required Tests                      |
| --------- | ----------------------------------- |
| CLI       | pcr_basic, invalid_config           |
| Workflow  | minimal, qc_enabled                 |
| Output    | folder_structure, report_generation |
| Logging   | logs_created, progress_logged       |
| Error     | primer3_fail, invalid_sequence      |
| Golden    | pcr_basic                           |

Additional workflows (qPCR, CRISPR, multiplex) will create parallel tests.

---

# **10. Future Integration Test Extensions**

Future workflows require new integration tests:

* qPCR → probe generation
* CRISPR → PAM detection, off-target scoring
* Multiplex → cross-dimer matrix

Future expansion:

* multi-workflow pipelines
* plugin-enabled workflows
* performance regression tests
* Docker-based environment tests
* optional external tool integration tests (later stages)

---

# **11. Summary**

Integration tests ensure:

* CLI + config loader + workflow + core are all connected
* output structure is correct
* logs + debug behavior is correct
* exceptions propagate cleanly
* public API stability
* reproducible workflow results
* protection against regressions

This document forms the backbone of PrimerLab’s end-to-end reliability strategy.
