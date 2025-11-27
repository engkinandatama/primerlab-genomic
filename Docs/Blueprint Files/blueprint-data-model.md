# **PrimerLab — Data Model Blueprint**

This blueprint defines the complete internal data model architecture for PrimerLab.
It converts the conceptual model from `data-model.md` into a **precise technical specification** describing:

* classes
* objects
* field structure
* JSON export contracts
* internal vs external fields
* validation rules
* extensibility constraints

The data model is one of the core foundations that ensures **reproducible, interpretable, and machine-readable results**.

---

# **1. Purpose of This Blueprint**

This blueprint explains:

* how PrimerLab represents primers, QC metrics, amplicons, workflow results
* the relationship between internal objects and JSON output
* field definitions, types, constraints
* versioning and backward-compatibility strategy
* rules for internal-only fields vs public fields
* how to guarantee stable output for automated contributors

The data model must remain **stable and predictable** across versions.

---

# **2. Data Model Architecture Overview**

PrimerLab uses **typed data objects**, implemented as Python `@dataclass` instances:

```
Primer          → represents a specific primer
Amplicon        → PCR product structure
QCResult        → thermodynamic & structural QC metrics
WorkflowResult  → top-level result object for workflows
Metadata        → run metadata
```

All classes live under:

```
primerlab/core/models/
```

This folder contains:

```
primer.py
amplicon.py
qc.py
workflow_result.py
metadata.py
```

---

# **3. Primer Data Model Blueprint**

File: `primerlab/core/models/primer.py`

```python
@dataclass
class Primer:
    id: str
    sequence: str
    tm: float
    gc: float
    length: int

    hairpin_dg: float
    homodimer_dg: float
    heterodimer_dg: Optional[float] = None

    start: Optional[int] = None
    end: Optional[int] = None

    warnings: List[str] = field(default_factory=list)

    raw: Optional[dict] = None  # internal (primer3 raw output)
```

### **3.1 Field Rules**

* `id` is human-friendly (e.g., `"forward"`, `"reverse"`).
* `sequence` MUST be uppercase, ATGC only.
* `tm` uses unified Tm engine, deterministic across tools.
* `raw` contains raw Primer3 output and must **never** be included in reports.

### **3.2 JSON Export**

When exporting to JSON:

* include all fields *except* `raw`
* None → null
* keys sorted

---

# **4. Amplicon Data Model Blueprint**

File: `primerlab/core/models/amplicon.py`

```python
@dataclass
class Amplicon:
    start: int
    end: int
    length: int
    sequence: str
    gc: float

    tm_forward: float
    tm_reverse: float

    warnings: List[str] = field(default_factory=list)
```

Field notes:

* start/end positions are 0-based indexing
* sequence stored in uppercase
* GC must be precomputed by core utilities

---

# **5. QCResult Data Model Blueprint**

File: `primerlab/core/models/qc.py`

```python
@dataclass
class QCResult:
    hairpin_ok: bool
    homodimer_ok: bool
    heterodimer_ok: bool
    tm_balance_ok: bool

    hairpin_dg: float
    homodimer_dg: float
    heterodimer_dg: Optional[float]

    tm_diff: float

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
```

QC behavior rules:

* QCResult does NOT raise exceptions
* workflows check `qc.errors` and decide to fail workflow
* QC warnings are environmental, not fatal

---

# **6. Metadata Model Blueprint**

File: `primerlab/core/models/metadata.py`

```python
@dataclass
class RunMetadata:
    workflow: str
    timestamp: str
    version: str

    input_hash: str
    config_hash: str

    parameters: Dict[str, Any]
```

Rules:

* timestamp: ISO 8601 (`2025-03-14T15:09:26Z`)
* version auto-inserted from package version
* parameters must be a **deep copy of final merged config** (public fields only)
* must be saved to `run_metadata.json`

---

# **7. WorkflowResult Data Model Blueprint**

File: `primerlab/core/models/workflow_result.py`

This is the **top-level result container** returned by every workflow.

```python
@dataclass
class WorkflowResult:
    workflow: str
    primers: Dict[str, Primer]
    amplicons: List[Amplicon]
    qc: Optional[QCResult]

    metadata: RunMetadata
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    raw: Dict[str, Any] = field(default_factory=dict)  # internal diagnostics
```

### **7.1 Requirements**

* All workflows must return this object
* QC may be None for workflows that do not use thermodynamic QC
* `raw` contains internal debugging structures
* Errors stored in `errors` must NOT be full Python tracebacks
* Workflows must not modify this object after creation

---

# **8. JSON Export Contract**

The JSON export contract defines how WorkflowResults map to the output files in:

```
results/workflow_result.json
```

Rules:

* Must serialize via `to_dict()` method
* Must not include internal fields (`raw` values only in debug folder)
* Must be readable by other programming languages
* Must be version-stable
* Must never change key names once defined

Example output:

```json
{
  "workflow": "PCR",
  "primers": {
    "forward": { ... },
    "reverse": { ... }
  },
  "amplicons": [ ... ],
  "qc": { ... },
  "metadata": { ... },
  "warnings": [],
  "errors": []
}
```

---

# **9. Internal vs Public Fields**

PrimerLab allows internal-only fields for debugging:

### Internal-only fields:

* Primer.raw
* WorkflowResult.raw
* internal Primer3 structures
* intermediate scoring

Internal fields:

* MUST NOT appear in reports
* MUST NOT appear in public JSON
* MUST appear in debug dumps if relevant

---

# **10. Validation Rules for Data Model**

### Prime rules:

* sequence fields must be uppercase
* GC values must be float in [0, 1]
* Tm values must be float > 0
* lists must not contain None values
* numeric ranges must be defined

### Amplicon-specific:

* `end >= start`
* `length == end - start + 1`

### WorkflowResult:

* `workflow` must match config.workflow
* primers must use keys (`forward`, `reverse`, etc.)

---

# **11. to_dict() Blueprint**

Every data class MUST implement:

```python
def to_dict(self) -> dict:
    ...
```

Rules:

* must use primitive Python types
* must NOT embed Python objects
* must sort keys deterministically
* must exclude internal fields
* must be reversible (dict → object is possible)

---

# **12. Interactions With Other Systems**

### 12.1 With Output System

WorkflowResult drives:

* results/*.json
* report generation
* warnings printed in CLI

### 12.2 With Logging System

Data model itself does not log anything.

### 12.3 With Error Handling

WorkflowResult.errors are non-fatal results
Exceptions are fatal *before* WorkflowResult is returned.

### 12.4 With Config System

Metadata.parameters must reflect final merged config.

---

# **13. Versioning and Stability Blueprint**

Once a field name is published:

* it MUST NOT be renamed
* it MUST NOT be removed
* new fields must be optional
* removing internal fields is allowed

This ensures backward compatibility for automated contributors.

---

# **14. Extension Blueprint**

Future extensions may include:

* multiplex primer sets
* probe structures (qPCR)
* CRISPR multi-guide models
* RNA structure annotations
* plasmid design models
* target scoring models
* epitope-focused primer design

These must extend the data model without breaking existing workflows.

---

# **15. Summary**

This blueprint defines the full data model architecture:

* Primer
* Amplicon
* QCResult
* Metadata
* WorkflowResult

and describes:

* JSON export contracts
* internal vs public fields
* validation rules
* interactions with other systems
* versioning constraints
* extensibility

Following this blueprint ensures PrimerLab’s data representation remains consistent, safe, interpretable, and future-proof.

