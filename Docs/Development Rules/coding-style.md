# **PrimerLab — Coding Style Guide**

## **1. Purpose of This Document**

This document defines the coding style guidelines for all PrimerLab source code.
These rules ensure:

* consistent structure across the entire project
* readable and maintainable code
* predictable patterns for contributors
* a clean foundation for large-scale and long-term development

All contributors must adhere strictly to these standards.

---

# **2. Language and Version**

PrimerLab uses:

* **Python 3.11** (baseline version)
* UTF-8 encoding
* Standard library whenever possible

---

# **3. Style Framework**

PrimerLab follows:

* **PEP8** for formatting
* **PEP257** for docstrings
* Additional internal rules defined here

---

# **4. Formatting Rules**

## **4.1 Line Length**

* Maximum: **100 characters** per line
  (80 is preferred, but 100 is acceptable for clarity.)

## **4.2 Indentation**

* 4 spaces
* No tabs allowed

## **4.3 Blank Lines**

* 2 blank lines before top-level definitions
* 1 blank line between methods inside a class
* No trailing blank lines at end of file

---

# **5. Imports**

## **5.1 Order of Imports**

Imports must follow this structure:

```python
# 1. Standard library
import os
import sys
from pathlib import Path

# 2. Third-party libraries
import numpy as np

# 3. Local imports (primerlab modules)
from primerlab.core import seq_io, logger
```

## **5.2 Import Style**

* Use **absolute imports**
* No wildcard imports: `from X import *` (prohibited)
* Multi-line imports should use parentheses:

```python
from primerlab.core import (
    seq_io,
    tm_qc,
    structure_qc,
)
```

## **5.3 One Import Per Line**

Unless grouped in parentheses.

---

# **6. Naming Conventions**

All naming conventions are defined in `naming-convention.md`.
These rules must be followed without exception.

Summary:

| Type      | Style            |
| --------- | ---------------- |
| Variables | snake_case       |
| Functions | snake_case       |
| Classes   | PascalCase       |
| Modules   | snake_case       |
| Constants | UPPER_SNAKE_CASE |

---

# **7. Docstring Standards**

## **7.1 Docstring Format**

PrimerLab uses **Google-style docstrings**:

```python
def design_primers(sequence: str) -> list:
    """
    Designs primer candidates for a given DNA sequence.

    Args:
        sequence: Input DNA sequence (A/T/C/G).

    Returns:
        A list of Primer objects meeting preset criteria.
    """
```

## **7.2 Required Docstrings**

Every public function, class, and method must include a docstring.

Private helpers (`_helper_function()`) may include shorter docstrings.

## **7.3 Class Docstrings**

Describe:

* purpose
* attributes
* relationships

Example:

```python
class Primer:
    """
    Represents a single PCR primer.

    Attributes:
        sequence: Primer sequence (5'→3').
        tm: Melting temperature (°C).
        gc_content: GC percentage.
    """
```

---

# **8. Function Structure Guidelines**

## **8.1 Function Size**

* Prefer small, focused functions
* Single responsibility
* Avoid multi-page functions

## **8.2 Arguments**

Use explicit keyword arguments:

```python
design_primers(sequence=seq, tm_range=(58, 62))
```

Avoid *args unless necessary.

## **8.3 Return Values**

Always return structured, predictable objects:

* `Primer`, `PrimerPair`, `QCResult`, `WorkflowResult`
* or dictionaries with documented structure

Never return raw tuples with implicit meaning.

---

# **9. Error Handling**

## **9.1 Use Custom Exceptions**

All errors must come from `core/exceptions.py`.

Example:

```python
from primerlab.core.exceptions import ConfigError

raise ConfigError("Invalid Tm range", code="ERR_CONFIG_002")
```

## **9.2 No Silent Failures**

All problems must either:

* be logged explicitly using logger
  or
* raise a custom exception

## **9.3 No Bare `except:`**

Only catch explicit exceptions:

```python
except ValueError:
    ...
```

---

# **10. Logging Practices**

Use the unified logger:

```python
from primerlab.core.logger import log

log.info("Starting QC evaluation")
log.warning("Hairpin ΔG is borderline")
log.error("Primer3 process failed")
```

Never use:

* `print()`
* ad-hoc logging systems

Refer to `logging-progress.md`.

---

# **11. Comments**

### **11.1 Use Comments for Logic, Not Style**

Good comment:

```python
# Reject primer if hairpin ΔG is too stable (< -3.0 kcal/mol)
```

Bad comment:

```python
# loop
for i in x:
```

### **11.2 Avoid Redundant Comments**

The code must be self-explanatory.

---

# **12. Type Hints**

Type hints are **mandatory** for all functions:

```python
def calculate_tm(sequence: str) -> float:
```

Use typing for complex types:

```python
from typing import List, Dict

def parse_output(raw: str) -> List[Dict]:
```

This improves static analysis and automated code generation.

---

# **13. File Structure**

Each file should follow:

```
1. Imports
2. Constants
3. Classes
4. Public functions
5. Private helper functions (_name)
```

Avoid mixing classes and functions randomly.

---

# **14. Testing Style**

Testing rules (expanded in `test-guidelines.md`):

* deterministic tests only
* no network calls
* minimum 1 test per core function
* workflow tests must validate JSON output

Tests should mimic standard unittest or pytest style.

---

# **15. Performance Rules**

### **15.1 No Premature Optimization**

Only optimize after profiling.

### **15.2 Avoid Heavy Loops**

Prefer vectorized logic or helper functions.

### **15.3 Avoid Recomputing**

Cache intermediate QC values where appropriate.

---

# **16. Prohibited Coding Practices**

❌ No global mutable state
❌ No circular imports
❌ No hardcoded paths
❌ No bare exceptions
❌ No embedded config in code
❌ No code duplication
❌ No direct filesystem writes except in CLI/output handlers

---

# **17. Summary**

These coding style rules provide a strong, consistent foundation for all PrimerLab development.
Every contributor must follow these rules to ensure long-term sustainability, clarity, and correctness across the project.
