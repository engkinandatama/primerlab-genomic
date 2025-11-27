# **PrimerLab — Configuration System Design**

## **1. Purpose of This Document**

This document defines the structure, philosophy, and required rules for all configuration files used in PrimerLab.

PrimerLab uses **YAML-based configuration** as the single source of truth for:

* workflow parameters
* primer design settings
* thermodynamic thresholds
* tool paths
* output folder rules
* reporting behavior

This ensures reproducibility, transparency, and consistency across workflows.

---

# **2. Configuration Principles**

PrimerLab adheres to six core configuration principles:

### **2.1 Explicit Over Implicit**

Every configurable behavior must be controlled explicitly by YAML keys.

### **2.2 Separation of Concerns**

Configuration files define **parameters**, not logic.
All logic exists in workflow and core layers.

### **2.3 Predictable Merging**

Config merging follows a deterministic three-level hierarchy:

1. **Default config** (bundled with workflow)
2. **User-provided config**
3. **CLI overrides**

### **2.4 Validation Required**

All configuration values must be validated:

* type validation
* range/constraint validation
* presence of required keys

### **2.5 Stability**

Key names and structure must remain stable across versions.

### **2.6 Workflow Isolation**

Each workflow has its own config file — configurations never overlap.

---

# **3. Configuration Folder Structure**

Config files are placed in:

```
primerlab/config/
    pcr_default.yaml
    qpcr_default.yaml
    crispr_default.yaml
    multiplex_default.yaml
    ...
```

User configs are external files passed via CLI.

---

# **4. Standard Configuration Format (YAML)**

All workflow config files follow the exact same high-level structure:

```yaml
workflow: pcr

input:
  sequence: "ATCG..."           # Inline sequence OR
  sequence_path: "input.fasta"  # FASTA file path

parameters:
  primer_size:
    min: 18
    opt: 20
    max: 27

  tm:
    min: 57
    opt: 60
    max: 63

  gc_content:
    min: 40
    max: 60

  product_size:
    min: 70
    max: 200

qc:
  hairpin_dg_min: -3.0
  dimer_dg_min: -5.0
  tm_diff_max: 3.0

offtarget:
  enabled: false
  blast_path: "blastn"
  database: ""

output:
  directory: "primerlab_output"
  report_format: "md"
  save_intermediate: true

advanced:
  primer3_raw: false
  debug: true
```

---

# **5. Required Top-Level Keys**

Every workflow config file must have these keys:

| Key          | Purpose                                       |
| ------------ | --------------------------------------------- |
| `workflow`   | workflow name (`pcr`, `qpcr`, `crispr`, etc.) |
| `input`      | where sequence comes from                     |
| `parameters` | design parameters (primer length, Tm, etc.)   |
| `qc`         | QC thresholds and constraints                 |
| `offtarget`  | external tool behavior                        |
| `output`     | output directory + report settings            |
| `advanced`   | deeper flags and debugging                    |

Any missing key must raise:

```
ERR_CONFIG_003
```

---

# **6. Input Section Rules**

The `input` section must include exactly one of:

### **6.1 Inline Sequence**

```yaml
sequence: "ATCGATCGATCG..."
```

### **6.2 File Path**

```yaml
sequence_path: "geneX.fasta"
```

### **6.3 Mutually exclusive**

If both are provided → raise `ERR_CONFIG_004`.

### **6.4 Optional Region**

```yaml
region:
  start: 100
  end: 350
```

Must validate:

* start ≥ 0
* end > start
* end <= sequence length (after load)

Invalid → raise `ERR_SEQ_004` or `ERR_SEQ_005`.

---

# **7. Parameters Section Rules**

Different workflows will require different parameters, but all parameter keys must:

* be in snake_case
* have `min/opt/max` if applicable
* follow Primer3 mapping where appropriate
* be validated

Example:

```yaml
primer_size:
  min: 18
  opt: 20
  max: 25
```

If a required parameter is missing:

```
ERR_CONFIG_003
```

If values violate constraints:

```
ERR_CONFIG_005
```

---

# **8. QC Section Rules**

These thresholds apply after primer candidates are generated.

### Example:

```yaml
hairpin_dg_min: -3.0
dimer_dg_min: -6.5
tm_diff_max: 2.5
```

If QC rules fail:

* either raise `ERR_QC_xxx` or
* soft-fail (workflow-dependent)

QC severity logic is defined per workflow (PCR vs CRISPR differ).

---

# **9. Off-Target Section Rules**

The off-target configuration controls BLAST or mismatch search.

```yaml
offtarget:
  enabled: true
  blast_path: "blastn"
  database: "nt"
  max_hits: 10
```

Rules:

* If enabled but tools missing → `ERR_TOOL_003` or `ERR_TOOL_004`
* If enabled with no DB → must warn and auto-disable

Off-target is optional for PCR but mandatory for CRISPR.

---

# **10. Output Section Rules**

```yaml
output:
  directory: "primerlab_out"
  report_format: "md"
  save_intermediate: true
```

Requirements:

* directory must be writable → otherwise `ERR_IO_003`
* allowed report formats: `md`, `txt`, `json`
* with optional PDF conversion later

---

# **11. Advanced Section Rules**

Advanced flags control diagnostic behavior.

```yaml
advanced:
  primer3_raw: true
  debug: true
```

### `primer3_raw`

Writes raw Primer3 output to:

```
debug/primer3_raw.txt
```

### `debug`

Enables additional debug logging and dumps.

---

# **12. Config Merging Rules**

PrimerLab merges config from three levels:

### **12.1 Level 1 — Default Config**

Defined in `primerlab/config/<workflow>_default.yaml`.

### **12.2 Level 2 — User Config**

Loaded from the config passed ot CLI.

### **12.3 Level 3 — CLI Overrides**

Example:

```
primerlab pcr --config pcr.yaml --out custom_dir
```

Mapping:

* `--out custom_dir` overrides `output.directory`

### **12.4 Conflict Resolution**

* Type mismatch → `ERR_CONFIG_004`
* Unknown config key → warning (not fatal)
* Override takes precedence only for matching keys

---

# **13. Config Loader Behavior**

Defined in:

```
primerlab/core/config_loader.py
```

### Responsibilities:

* load YAML
* deep-merge dictionaries
* validate required keys
* ensure correct data types
* return a final validated config

No workflow logic is allowed here.

---

# **14. Workflow-Specific Config Extensions**

Each workflow may add its own parameters under:

```
parameters:
  qpcr:
    probe_type: hydrolysis
    probe_length:
      min: 18
      opt: 20
      max: 30
```

Each workflow has a corresponding blueprint in:

`Docs/Blueprints/Workflows/<workflow>-blueprint.md`

---

# **15. Adding New Config Keys**

When contributors add configuration keys:

1. Must update this document
2. Must update default config
3. Must update blueprint
4. Must add validation rules
5. Must add tests
6. Must ensure backward compatibility

---

# **16. Summary**

The PrimerLab configuration system is:

* explicit
* stable
* modular
* workflow-isolated
* validated
* reproducible

This enables deterministic runs, cross-platform consistency, and a predictable user experience.

