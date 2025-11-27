# **PrimerLab — Configuration System Blueprint**

This blueprint provides a **technical implementation plan** for the entire configuration system of PrimerLab.
It translates the rules defined in `config-design.md` into:

* folder structure
* code module responsibilities
* YAML merge logic
* validation rules
* config→workflow interaction
* CLI override mapping
* error-handling strategy
* future-proofing considerations

This document guides contributors through building and extending the configuration subsystem.

---

# **1. Purpose of This Blueprint**

The configuration system is a central component of PrimerLab.
It supports:

* default workflow configurations
* user-defined YAML files
* CLI overrides
* parameter validation
* workflow isolation
* reproducibility

This blueprint explains the **exact technical mechanics** of how config loading, merging, validation, and delivery to workflows must work.

---

# **2. Core Components**

The configuration system is made of:

```
primerlab/core/config_loader.py
primerlab/config/<workflow>_default.yaml
primerlab/cli/main.py
primerlab/core/exceptions.py
primerlab/core/logger.py
```

Each plays a distinct role:

| Component        | Responsibility                           |
| ---------------- | ---------------------------------------- |
| default YAML     | defines baseline parameters per workflow |
| config_loader.py | load, merge, validate                    |
| CLI              | passes user file + overrides             |
| workflows        | never load YAML directly                 |
| exceptions       | raise errors when invalid                |
| logging          | record config loading steps              |

---

# **3. Folder Structure**

```
primerlab/
 ├─ config/
 │    ├─ pcr_default.yaml
 │    ├─ qpcr_default.yaml
 │    ├─ crispr_default.yaml
 │    └─ ...
 │
 ├─ core/
 │    ├─ config_loader.py
 │    ├─ exceptions.py
 │    └─ ...
 │
 ├─ cli/
 │    └─ main.py
```

Each workflow MUST have its own default config file.

---

# **4. Configuration Load Flow**

The loading sequence must follow this order:

```
1. Load default config (internal)
2. Load user config (YAML)
3. Load CLI overrides
4. Deep-merge all three
5. Validate final config
6. Freeze and pass to workflow
```

### 4.1 Flow diagram:

```
        ┌────────────────┐
        │ default config │
        └───────┬────────┘
                ▼
        ┌────────────────┐
        │ user config    │
        └───────┬────────┘
                ▼
        ┌────────────────┐
        │ CLI overrides  │
        └───────┬────────┘
                ▼
        ┌────────────────────┐
        │ merged final config│
        └───────┬────────────┘
                ▼
        ┌───────────────┐
        │ validation     │
        └───────┬────────┘
                ▼
        ┌───────────────┐
        │ workflow run   │
        └───────────────┘
```

---

# **5. Default Config Blueprint**

Each default config must contain:

```yaml
workflow: pcr

input:
  sequence: null
  sequence_path: null

parameters:
  primer_size:
    min: 18
    opt: 20
    max: 27

  tm:
    min: 57
    opt: 60
    max: 63

qc:
  hairpin_dg_min: -3.0
  dimer_dg_min: -6.0
  tm_diff_max: 3.0

offtarget:
  enabled: false
  blast_path: "blastn"
  database: null

output:
  directory: "primerlab_out"
  report_format: "md"
  save_intermediate: true

advanced:
  primer3_raw: false
  debug: false
```

All workflow default configs must follow the **same top-level schema**, even if some fields are unused.

---

# **6. Merging Logic Blueprint**

### 6.1 Deep Merge Rules

Merging is **recursive:**

```
dict + dict = merge keys  
list + list = override  
scalar + scalar = override  
```

Example:

```yaml
default:
  tm:
    min: 50
    max: 60

user:
  tm:
    min: 55
```

Result:

```yaml
tm:
  min: 55
  max: 60
```

### 6.2 CLI Overrides → flatten into dict

CLI:

```
primerlab pcr --out custom_dir
```

Becomes:

```python
{"output": {"directory": "custom_dir"}}
```

---

# **7. Validation Blueprint**

Validation is strict and must raise exceptions referencing `error-codes.md`.

### Validation must check:

| Category          | Validation                                     |
| ----------------- | ---------------------------------------------- |
| Required keys     | `workflow`, `input`, `parameters`, etc.        |
| Input exclusivity | cannot set both `sequence` and `sequence_path` |
| Parameter ranges  | Tm, GC %, primer size, product size            |
| QC bounds         | ΔG thresholds must be numeric                  |
| Off-target        | if enabled → require BLAST path                |
| Output            | directory must be writable                     |
| Null values       | allowed only if default allows                 |

### Example error:

```python
raise ConfigError("Missing required key: parameters.tm", "ERR_CONFIG_003")
```

### 7.1 Type constraints:

* all numeric must be int/float
* min ≤ opt ≤ max
* booleans must not be strings
* paths must be string or None

---

# **8. Workflow Interaction Blueprint**

Workflows MUST NOT read YAML directly.

Workflow call signature:

```python
def run_pcr_workflow(config: dict) -> WorkflowResult:
```

The config passed here is the **final merged & validated config**.

Workflows use the config like:

```python
tm_min = config["parameters"]["tm"]["min"]
```

### Workflows must NOT:

* modify config
* write to config
* re-validate config

---

# **9. CLI Override Blueprint**

CLI options map to config keys.
Allowed overrides:

| CLI Option            | Config Target             |
| --------------------- | ------------------------- |
| `--out <dir>`         | `output.directory`        |
| `--workflow <name>`   | override workflow field   |
| `--debug`             | `advanced.debug=true`     |
| `--disable-offtarget` | `offtarget.enabled=false` |

CLI override resolution:

1. convert option to nested dictionary
2. merge using deep merge rules
3. pass to config_loader

CLI MUST NOT bypass config_loader.

---

# **10. Config Loader Architecture Blueprint**

`config_loader.py` must implement:

### 10.1 Functions

#### **load_yaml(path)**

Load user YAML with safe loader.

#### **deep_merge(base, override)**

Recursive function merging dictionaries.

#### **validate_config(config)**

Implement rules in Section 7.

#### **load_and_merge_config(workflow_name, user_config_path, cli_overrides)**

Top-level function used by CLI.

---

# **11. Error Handling Blueprint**

Configuration system uses:

* `ERR_CONFIG_*`
* `ERR_SEQ_*`
* `ERR_IO_*`

### All errors must be raised as:

```python
raise ConfigError("message", "ERR_CONFIG_XXX")
```

### Fatal errors include:

* invalid YAML syntax
* missing required keys
* type mismatch
* mutually exclusive fields
* invalid ranges
* nonexistent files

Soft errors are not allowed in config.

---

# **12. Logging Blueprint**

`config_loader` must log:

```
Loading default config...
Loading user config...
Applying CLI overrides...
Validating config...
Config loaded successfully.
```

If debug enabled → log final merged config path in:

```
debug/config_final.json
```

---

# **13. Future Extension Blueprint**

The config system must be future-proof for:

* custom thermodynamic models
* organism-specific presets
* per-target overrides
* multi-target design
* advanced reporting configs
* multi-workflow pipelines

These must always remain backward-compatible.

---

# **14. Summary**

This blueprint defines:

* full flow of config loading
* structure of default and user configs
* merge logic
* validation rules
* CLI override mapping
* interactions with workflows
* error and logging strategy
* extension roadmap

Adhering to this blueprint ensures the configuration system remains:

* stable
* predictable
* scalable
* maintainable
* safe for contributors

