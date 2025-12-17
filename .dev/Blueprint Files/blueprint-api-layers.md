# **PrimerLab — API Layers Blueprint**

This blueprint defines the **full API architecture** of PrimerLab.
It establishes:

* how users interact with PrimerLab programmatically
* how workflows expose a stable Python API
* how internal modules are protected
* how extension and integration are supported
* how forward compatibility is guaranteed

This doc translates the conceptual guidelines into an explicit, strict technical specification.

---

# **1. Purpose of This Blueprint**

PrimerLab’s API must be:

* clean
* stable
* minimal
* safe
* layered
* predictable
* easily usable by external developers

This blueprint describes the **public API**, the **internal API**, and how modules interact in a layered structure.

---

# **2. Overview of API Layers**

PrimerLab uses a **3-Layer API Model**:

```
Top:     Public API (primerlab.api)
Middle:  Workflow API (primerlab.workflows)
Bottom:  Core API (primerlab.core)
```

### Enforcement:

| Layer      | Allowed to import ↓ | Forbidden to import ↑ |
| ---------- | ------------------- | --------------------- |
| Public API | workflows, core     | N/A                   |
| Workflows  | core                | public API            |
| Core       | core-only           | workflows, public API |

These rules prevent circular dependencies and preserve modularity.

---

# **3. Public API Blueprint (`primerlab/api/`)**

This layer defines everything users can import.

File:

```
primerlab/api/__init__.py
```

Public API must expose **only these categories**:

### **3.1 High-level workflow runners**

```python
from primerlab.api import run_pcr
from primerlab.api import run_qpcr
from primerlab.api import run_crispr
```

### **3.2 Loading configs**

```python
from primerlab.api import load_config
```

### **3.3 Data models (selected non-internal fields)**

```python
from primerlab.api import Primer, Amplicon, WorkflowResult
```

### **3.4 Version information**

```python
from primerlab.api import __version__
```

### **3.5 Public exceptions**

```python
from primerlab.api import PrimerLabException
```

### **3.6 Allowed utility helpers**

Safe utilities only:

```python
from primerlab.api import reverse_complement
```

---

# **4. Public API Rules**

### **4.1 Only explicitly declared functions/classes are public**

Nothing is implicitly exposed.

### **4.2 Public functions must be:**

* stable
* documented
* version-controlled
* backward compatible

### **4.3 Public API must never expose:**

* workflow internal helpers
* raw Primer3 structures
* debug utilities
* CLI components
* file system internals

### **4.4 Public API must not accept raw YAML paths**

Instead, use:

```python
run_pcr(sequence="ATGCC...", config=config_dict)
```

or:

```python
cfg = load_config("myconfig.yaml")
```

### **4.5 Public API must return WorkflowResult only**

Never:

* dicts
* tuples
* raw objects

---

# **5. Workflow API Blueprint (`primerlab/workflows/`)**

The workflow layer contains the core pipeline logic.

Each workflow has:

```
primerlab/workflows/<workflow_name>/workflow.py
primerlab/workflows/<workflow_name>/utils.py
```

### **Workflow Entry Point Signature**

```python
def run_pcr_workflow(config: dict) -> WorkflowResult:
```

Rules:

* config MUST be fully merged + validated (from config_loader)
* workflows must NOT mutate config
* workflows must NOT produce prints
* workflows must use central logger + progress system

### **Workflows may import:**

* core utilities
* core exceptions
* other local workflow utilities

Workflows MUST NOT import:

* CLI
* public API
* other workflows

---

# **6. Core API Blueprint (`primerlab/core/`)**

The core layer contains:

* sequence utilities
* thermodynamic models
* config loader
* error handling
* data models
* logging system
* output system
* tool wrappers

Core modules must:

* be pure logic
* avoid side effects
* avoid workflow context
* avoid filesystem except output utilities
* be usable independently

Allowed imports: core-only and third-party libs.

Forbidden imports: workflows, CLI, public API.

---

# **7. External Tool API Blueprint**

External tools like Primer3, BLAST, ViennaRNA are wrapped in:

```
primerlab/core/tools/primer3_wrapper.py
primerlab/core/tools/blast_wrapper.py
```

Rules:

* wrappers return Python dicts
* errors raised as ToolExecutionError
* raw output captured separately for debug folder
* workflows never see “tool-level” objects

Tools must expose:

```python
run_primer3(params) -> dict
run_blast(seq, db) -> dict
```

These functions are stable internal APIs.

---

# **8. Internal API Boundaries**

Not exposed publicly:

* QC engines
* scoring systems
* workflow-level utils
* raw tool wrappers
* debug infrastructure
* logger internals
* output path builders

These are for internal use only.

---

# **9. Public API Stability Rules**

Once a function/class is public:

* MUST remain stable
* MUST keep the same function signature
* MUST remain importable from the same namespace
* MUST remain backward compatible for at least 3 versions
* deprecation requires a clear warning

Breaking changes are NOT allowed without version major bump (>= 2.0).

---

# **10. Internal API Flexibility**

Internal APIs:

* may change structure
* may change naming
* may relocate between modules

BUT must:

* avoid breaking workflows
* preserve testing coverage
* remain compatible with existing automated contributors

---

# **11. API Versioning Blueprint**

Public API version exposed via:

```
primerlab/api/__init__.py
```

Field:

```python
__version__ = "0.1.0"
```

Used by:

* CLI
* Workflow metadata
* output system
* reports

Version must follow:

```
MAJOR.MINOR.PATCH
```

---

# **12. API Testing Blueprint**

Tests for public API MUST verify:

* each public function is importable
* each public function maintains signature
* public functions produce correct results
* workflows callable through public API
* no private functions leak into `primerlab.api`
* internal errors propagate as PrimerLabException

Dedicated test:

```
tests/integration/test_public_api.py
```

---

# **13. API Documentation Blueprint**

Documentation will eventually include:

* API reference for each public function
* workflow parameter descriptions
* examples of PCR/qPCR/CRISPR API usage
* guidance for advanced researchers
* programmatic integration guide

This is not part of the internal project but must be planned.

---

# **14. Future API Extension Blueprint**

Potential future extensions:

* Multi-target batch API
* Streaming workflows
* Long-read sequencing primer design workflows
* CRISPR multiplex design API
* Plugin system for assay design
* REST API mode for server deployment
* Cloud execution API

All extensions must preserve backward compatibility of existing public API.

---

# **15. Summary**

This blueprint defines:

* three-layer API architecture
* strict import rules
* clear boundaries between public, workflow, and core API
* stable function signatures
* strict backward compatibility
* testing requirements
* future-proof expansion plans

Following this blueprint ensures PrimerLab provides a clean, robust, and scalable API surface for programmatic primer design and molecular pipeline development.

