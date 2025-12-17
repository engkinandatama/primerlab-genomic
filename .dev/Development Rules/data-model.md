# **PrimerLab — Data Model Specification**

## **1. Purpose of This Document**

This document defines all standardized data models used across PrimerLab.

A unified data model ensures:

* consistent representation of biological sequences
* predictable inputs/outputs for workflows
* stable JSON export formats
* compatibility across workflows and future modules
* clarity for contributors working across different layers

These models represent the core contract that enables PrimerLab to scale safely and remain maintainable.

---

# **2. Data Model Philosophy**

PrimerLab uses these principles:

### **2.1 Representation Over Computation**

Data models represent data; they do not perform calculations.

### **2.2 Serialization-Ready**

Every model must be JSON-safe and convertible to:

* JSON
* YAML
* Python dict

### **2.3 Stability**

Data model structures must remain stable across minor versions.

### **2.4 Workflow-Agnostic Core Models**

Core models apply to all workflows (PCR, qPCR, CRISPR, etc.).

---

# **3. Base Classes**

All primary data models extend from:

```python
class BaseModel:
    def to_dict(self) -> dict:
        ...
```

This ensures easy serialization across the project.

Located in:

```
primerlab/core/data_models.py
```

---

# **4. Primer Models**

## **4.1 Primer**

Represents a single primer.

```python
class Primer(BaseModel):
    sequence: str
    length: int
    tm: float
    gc_content: float
    hairpin_dg: float | None
    self_dimer_dg: float | None
    position_start: int
    position_end: int
    strand: str ("forward" or "reverse")
    notes: str | None
```

### Required fields:

* sequence
* strand
* tm
* gc_content

### Optional:

* structure-based energies
* additional QC flags

---

## **4.2 PrimerPair**

Represents a matched primer pair.

```python
class PrimerPair(BaseModel):
    forward: Primer
    reverse: Primer
    product_size: int
    tm_delta: float
    dimer_dg: float | None
    qc_pass: bool
```

### Notes:

* `tm_delta` = |tm_forward - tm_reverse|
* `dimer_dg` = cross-dimer ΔG
* `qc_pass` determined by QC layer

---

# **5. Probe Models (qPCR)**

## **5.1 Probe**

For qPCR hydrolysis or hybridization probes.

```python
class Probe(BaseModel):
    sequence: str
    length: int
    tm: float
    gc_content: float
    position_start: int
    position_end: int
    dye: str | None
    quencher: str | None
    notes: str | None
```

### Required for qPCR:

* sequence
* tm
* dye/quencher optional at early versions

---

# **6. CRISPR Models**

## **6.1 GuideRNA**

Represents a CRISPR guide RNA candidate.

```python
class GuideRNA(BaseModel):
    sequence: str
    pam: str
    position_start: int
    position_end: int
    gc_content: float
    score_simple: float | None
    score_offtarget: float | None
```

---

# **7. QC Models**

## **7.1 QCResult**

Stores QC outcomes for a primer or pair.

```python
class QCResult(BaseModel):
    hairpin_dg: float | None
    self_dimer_dg: float | None
    cross_dimer_dg: float | None
    tm_delta: float | None
    passes_all: bool
    warnings: list[str]
    errors: list[str]
```

### Notes:

* Used by both PCR and qPCR
* For CRISPR only relevant fields apply

---

# **8. Off-Target Models**

## **8.1 OffTargetHit**

Represents a single off-target alignment.

```python
class OffTargetHit(BaseModel):
    target_name: str
    mismatch_count: int
    score: float
    position: int
    strand: str
```

---

## **8.2 OffTargetResult**

Container for all hits.

```python
class OffTargetResult(BaseModel):
    hits: list[OffTargetHit]
    total_hits: int
    warnings: list[str]
```

---

# **9. Amplicon Models**

For PCR and qPCR.

## **9.1 Amplicon**

Represents the amplified region.

```python
class Amplicon(BaseModel):
    sequence: str
    length: int
    start: int
    end: int
    melting_profile: list[float] | None
    structure: str | None     # reserved for future modeling
```

---

# **10. Workflow Result Model**

This is the **output contract** for every workflow in PrimerLab.

Each workflow returns **one** `WorkflowResult`.

Located in:

```
primerlab/core/data_models.py
```

## **10.1 WorkflowResult**

```python
class WorkflowResult(BaseModel):
    meta: dict
    input: dict
    primers: list[PrimerPair] | list[Primer] | list[Probe] | list[GuideRNA]
    qc: dict
    offtarget: OffTargetResult | None
    amplicon: Amplicon | None
    report_path: str
    debug_paths: dict | None
```

### **meta:**

```yaml
workflow: "PCR"
version: "0.1.0"
runtime_sec: 1.53
timestamp: "2025-02-20 03:11:14"
```

### **input:**

Canonical representation of user config + loaded sequence.

### **primers:**

* PCR → list of PrimerPair
* qPCR → list of Primer+Probe bundle
* CRISPR → list of GuideRNA

### **qc:**

* global QC summary
* aggregated primer QC
* warnings/errors

### **offtarget:**

* list of hits or `None`

### **amplicon:**

* PCR only (None for CRISPR)

### **report_path:**

* relative path to markdown report

### **debug_paths:**

* optional list of debug dump filepaths
* includes Primer3 raw output, BLAST output, etc.

---

# **11. Serialization Rules**

All models must expose:

```python
to_dict()
```

which guarantees:

* JSON-safe
* no Python objects
* no numpy types
* no bytes

The CLI uses this to write:

* `result.json`
* `primers.txt`
* `qc_summary.json`

---

# **12. Data Model Validation**

Before returning a `WorkflowResult`, workflows must:

* confirm all required fields exist
* validate object types
* check primers have required QC fields
* check amplicon length matches primer positions
* ensure off-target results follow correct schema

If invalid → raise:

```
ERR_VALIDATION_004
```

---

# **13. Extending Data Models**

When introducing a new workflow (e.g., cloning, mutagenesis):

1. Add new fields to a workflow-specific model
2. Maintain backward compatibility
3. Update serialization
4. Document the extension here
5. Expand workflow blueprints

Never remove required fields from existing models.

---

# **14. Summary**

The PrimerLab data model is:

* stable
* modular
* workflow-agnostic
* serialization-friendly
* future-proof

These models guarantee consistency across the entire system and serve as the foundation for all workflows, reports, and outputs.
