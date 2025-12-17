# **PrimerLab — Environment Blueprint**

This blueprint defines the **full environment strategy** for PrimerLab, including:

* Python version requirements
* dependency management
* reproducibility guarantees
* virtual environment rules
* optional WSL2 usage (Windows)
* future containerization
* supported platforms
* behavior in constrained environments

Environment stability is critical for bioinformatics pipelines—this document ensures PrimerLab remains reproducible, installable, and predictable.

---

# **1. Purpose of This Blueprint**

This blueprint explains:

* how developers must configure their environment
* how PrimerLab ensures reproducibility
* how the dependency chain is defined and managed
* how to prevent version conflicts with external tools
* how automated contributors should set up environments for development
* how future Docker support will integrate without breaking the pipeline

PrimerLab requires strict control of dependencies, due to reliance on:

* thermodynamic calculation libraries
* external tools (Primer3, BLAST)
* numerical consistency across platforms

---

# **2. Supported Platforms**

PrimerLab officially supports:

| Platform                  | Status                                    |
| ------------------------- | ----------------------------------------- |
| **Ubuntu Linux 20.04+**   | Full support (primary development target) |
| **WSL2 (Ubuntu)**         | Full support                              |
| **macOS 12+ (Intel/ARM)** | Supported, not primary                    |
| **Windows (native)**      | Limited (requires additional setup)       |

**Primary development target:**
✔ Linux / WSL2 with Python 3.11

---

# **3. Python Version Requirements**

Required Python version:

```
Python 3.11.x
```

Rules:

* Python 3.12+ NOT supported until scientific libraries catch up
* Python 3.10 and below NOT supported (end-of-life)
* Python 3.14 must NOT be used for development

Reason:
3.11 provides the best compatibility vs. performance for scientific pipelines.

---

# **4. Virtual Environment Blueprint**

Every developer must use:

```
python3.11 -m venv .venv
```

Rules:

* Never install globally
* Never commit `.venv/`
* Use `.gitignore` to exclude environment directories
* All development and tests must run **inside** the virtual environment
* The environment must be lightweight and fast to recreate

---

# **5. Dependency Management Blueprint**

Dependencies are defined in:

```
primerlab/requirements.txt
primerlab/requirements-dev.txt
```

### 5.1 requirements.txt

Contains:

* minimal stable runtime deps
* pinned versions when needed
* scientific libraries required for QC and sequence handling

Example categories:

```
biopython
pyyaml
numpy
rich
```

### 5.2 requirements-dev.txt

Contains:

* pytest
* pytest-mock
* ruff
* mypy (future)

Rules:

* No optional/experimental libraries in main requirements
* Heavy libraries (e.g., ViennaRNA Python bindings) are moved to optional extras

### 5.3 Optional Dependencies

Inside `setup.cfg`, define extras:

```
[options.extras_require]
structure = viennarna
blast = biopython
```

Workflows must gracefully degrade if optional tools are absent.

---

# **6. External Tool Integration Blueprint**

PrimerLab relies on optional external tools:

| Tool      | Purpose               | Required?           |
| --------- | --------------------- | ------------------- |
| Primer3   | primer design backend | optional (mockable) |
| BLAST     | off-target analysis   | optional            |
| ViennaRNA | structure predictions | future optional     |

Rules:

* Tools MUST NOT be installed automatically
* Users configure paths via config YAML
* Workflows must fail cleanly if a required tool is missing
* Mocked versions are used in test environments

---

# **7. File System Requirements**

PrimerLab must run on:

* local filesystem
* mounted WSL2 filesystem
* remote mounts (NFS)
* CI ephemeral filesystem

Rules:

* always write using UTF-8
* do not require admin permissions
* avoid OS-specific path handling
* use `pathlib` exclusively

---

# **8. Environment Validation Blueprint**

Before running any workflow, PrimerLab executes:

```python
primerlab.core.env.validate()
```

This function checks:

### **8.1 Python version**

Stop if Python < 3.11.

### **8.2 Required libraries installed**

Missing modules → raise ConfigError.

### **8.3 Optional tools available (if enabled in config)**

If off-target enabled but BLAST not found → raise ToolExecutionError.

### **8.4 Write permissions**

Check output dir is writable.

### **8.5 Config file validity**

Validated before workflow starts.

All validations must occur before any runtime side effects.

---

# **9. Environment Metadata**

During workflow execution, the environment state must be written to:

```
run_metadata.json
```

Including:

* Python version
* OS name
* platform (Linux, macOS, Windows-WSL2)
* PrimerLab version
* external tool versions (when used)

Example snippet:

```json
{
  "python": "3.11.7",
  "platform": "Linux",
  "primerlab_version": "0.1.0",
  "tools": {
    "primer3": "2.6.1",
    "blast": null
  }
}
```

---

# **10. Determinism Blueprint**

PrimerLab MUST produce identical results across systems when:

* same input
* same config
* same Python version
* same dependency versions
* same thermodynamic algorithm path

To maintain determinism:

* hash inputs
* hash configs
* use stable Tm/QC algorithms
* avoid RNG
* avoid system-dependent temp dir naming
* pin versions when necessary

---

# **11. Development Environment Setup Blueprint**

Suggested workflow:

```
# create venv
python3.11 -m venv .venv

# activate
source .venv/bin/activate

# install main deps
pip install -r primerlab/requirements.txt

# install dev tools
pip install -r primerlab/requirements-dev.txt

# verify environment
primerlab --version
```

Developers must NOT:

* mix pip + conda
* use system Python
* rely on global installations

---

# **12. WSL2 Blueprint**

For Windows users:

✔ Always recommend WSL2 instead of native Windows.

WSL2 must run **Ubuntu 22.04+** with Python 3.11.

Advantages:

* full Linux compatibility
* better file IO performance
* easier external tool installation
* consistent path handling

---

# **13. Future Docker Blueprint**

PrimerLab will later provide Docker images:

```
primerlab/base:latest
primerlab/full-tools:latest
primerlab/workflows:latest
```

Blueprint is:

### Base image

* Python 3.11
* minimal dependencies

### Full tools image

* Primer3
* BLAST
* ViennaRNA
* nukelib

### Workflow image

* pipeline-ready containerization for reproducible research

Docker support must **NOT** introduce breaking changes to local installation.

---

# **14. Continuous Integration Environment**

CI pipeline must install:

* Python 3.11
* requirements + requirements-dev
* mock external tools
* run all tests in <5 seconds

CI must use:

```
pytest --disable-warnings
```

and must fail if:

* environment validation fails
* coverage < 80%
* golden outputs mismatch

---

# **15. Summary**

This blueprint defines the entire environment strategy for PrimerLab:

* supported platforms
* Python version requirements
* dependency management
* external tool handling
* environment validation
* reproducibility rules
* metadata storage
* future containerization
* CI environment

Following this blueprint ensures PrimerLab runs consistently across systems and is easy to develop, test, and deploy.

