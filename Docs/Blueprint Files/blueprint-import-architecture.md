# **PrimerLab — Import Architecture Blueprint**

This blueprint defines the complete strategy for managing imports inside PrimerLab.
It ensures:

* consistent import patterns
* strict layering separation
* no circular dependencies
* deterministic import order
* clean namespace exposure
* safe API surfaces
* clarity for contributors and automated tool extensions

Import design is critical for a modular molecular workflow framework, and this document standardizes every aspect of it.

---

# **1. Purpose of This Blueprint**

The goals:

* enforce predictable imports
* prevent circular dependencies between core/workflows/CLI
* provide rule-based import usage
* ensure clean public/private API boundaries
* guide contributors to follow the architectural layers
* make the project scalable as workflows expand

Import design directly affects stability of the entire codebase.

---

# **2. PrimerLab Layered Import Model**

PrimerLab uses a **strict 3-layer import architecture**:

```
CLI Layer
   ↓
Workflow Layer
   ↓
Core Layer
```

### Import rules:

| Layer    | Allowed to import from | Forbidden to import from |
| -------- | ---------------------- | ------------------------ |
| CLI      | Workflow + Core        | none                     |
| Workflow | Core only              | CLI                      |
| Core     | Core/internal only     | Workflow or CLI          |

This prevents dependency inversion and circular imports.

---

# **3. Explicit Rules**

### **3.1 CLI Layer Import Rules**

The CLI (`primerlab/cli/main.py`) MAY import from:

✔ workflow dispatch
✔ core.config_loader
✔ core.logger
✔ core.exceptions

CLI MUST NOT import:

✘ workflow utilities (pcr/design.py)
✘ data models directly (only through workflow results)
✘ any module that would break layering

CLI's role is orchestration only.

---

### **3.2 Workflow Layer Import Rules**

Workflows (e.g., `primerlab/workflows/pcr/workflow.py`) MAY import:

✔ core utilities
✔ core exceptions
✔ core sequence tools
✔ core data models
✔ internal workflow helpers

Workflows MUST NOT import:

✘ CLI modules
✘ other workflows
✘ other workflow configs
✘ workflow UI/printing functions
✘ anything from primerlab/config except default YAML loader already handled by core

Reason: workflows must remain portable.

---

### **3.3 Core Layer Import Rules**

Core modules MAY import:

✔ other core modules (lower or equal layer)
✔ Python standard library
✔ third-party libraries

Core MUST NOT import:

✘ workflow modules
✘ CLI modules
✘ any config YAML directly
✘ functions that produce workflow output

Core stays "pure", reusable, and stable.

---

# **4. File-System Based Layer Enforcement**

Folder structure enforces import order:

```
primerlab/
 ├─ cli/                ← Top layer
 ├─ workflows/          ← Middle layer
 └─ core/               ← Base layer
```

Meaning:

* Core never reaches up to workflows/ or cli/
* Workflows cannot reach up to cli/
* CLI can reach anywhere downward

This prevents bidirectional dependencies.

---

# **5. Public vs Private Import Rules**

### **5.1 Public imports (exposed to users)**

Only modules inside:

```
primerlab/api/
```

can expose a public API.

Users must only import via:

```python
import primerlab as pl
pl.run_pcr(...)
```

Unless they are contributing to the codebase.

---

### **5.2 Private imports**

All imports inside:

* core
* workflows
* cli

must be done using **relative imports**:

```
from ..core.tm_qc import calculate_tm
```

or

```
from .design import run_primer3
```

---

# **6. Relative Import Rules**

### When inside core/

Use **relative imports only** to avoid accidental upward imports.

Allowed:

```python
from .tm_qc import calculate_tm
from .seq_utils import reverse_complement
```

Forbidden:

```python
from primerlab.workflows.pcr.workflow import run_pcr_workflow  # ❌
```

---

### When inside workflows/

Allowed:

```python
from primerlab.core.seq_utils import load_sequence
from primerlab.core.exceptions import QCError
```

Not allowed:

```python
from primerlab.cli.main import dispatch_workflow  # ❌
```

---

### When inside CLI

Allowed:

```python
from primerlab.workflows.pcr.workflow import run_pcr_workflow
from primerlab.core.config_loader import load_and_merge_config
```

CLI is the only layer allowed to reach both downward layers.

---

# **7. Lazy Imports Blueprint**

To avoid heavy imports and cyclic dependencies:

Workflows may use **lazy imports** only when:

* importing large external tools
* importing expensive modules
* importing optional modules (e.g., secondary structure modeling)

Example:

```python
def run_advanced_structure(seq):
    from primerlab.core.structure import predict_mfe
    return predict_mfe(seq)
```

Lazy imports must never hide errors.

---

# **8. Circular Dependency Avoidance**

To prevent cycles:

* core functions must not depend on workflow logic
* workflows must remain isolated from each other
* CLI must not store global workflow state
* core must not import config YAML
* config loader must remain in core (not workflows)

Explicit anti-patterns:

❌ Workflow imports another workflow
❌ Core imports a workflow
❌ CLI stores state across workflows
❌ Tools write to CLI module

---

# **9. Import Ordering Rules**

Inside any file:

```
1. Standard library
2. Third-party libraries
3. PrimerLab core modules
4. PrimerLab workflow modules (if in CLI)
5. PrimerLab local modules (relative imports)
```

Example:

```python
import os
import subprocess

import yaml
import primer3

from primerlab.core.exceptions import QCError
from primerlab.core.seq_utils import load_sequence

from .design import design_primers
```

---

# **10. Naming Rules for Imports**

### 10.1 Function imports

Always explicit:

```python
from primerlab.core.tm_qc import calculate_tm
```

Avoid wildcard imports:

```python
from primerlab.core.tm_qc import *  # ❌ forbidden
```

### 10.2 Aliasing

Allowed only when meaningful:

```python
import primerlab.core.exceptions as exc
```

---

# **11. Public API Exposure Blueprint**

The public API lives in:

```
primerlab/api/__init__.py
```

This file may expose selected functions:

```python
from primerlab.workflows.pcr.workflow import run_pcr_workflow
```

Workflows must NOT import from api/.

---

# **12. Testing Import Architecture**

The following tests must exist:

* ensure no workflow imports CLI
* ensure no core imports workflows
* ensure no wildcard imports
* ensure relative imports used inside core
* ensure public API does not leak internal modules

A dedicated test exists:

```
tests/integration/test_import_architecture.py
```

---

# **13. Future Extension Blueprint**

Import architecture must be robust for:

* plugin-based workflows
* optional dependency injection
* multi-workflow pipelines
* cloud execution environment
* remote BLAST / Primer3 services

All future enhancements must preserve layering.

---

# **14. Summary**

This blueprint defines:

* strict layered import architecture
* public/private boundaries
* how imports must be structured
* how to prevent circular dependencies
* how to use lazy or relative imports
* rules for CLI, workflow, and core import behavior
* testing requirements
* future extension directions

Following this blueprint ensures PrimerLab remains stable, scalable, and maintainable as it grows.

