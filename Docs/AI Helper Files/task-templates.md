# **PrimerLab — AI Task Templates**

This document provides **standard task templates** that automated contributors must follow when performing any development or documentation work inside the PrimerLab project.

These templates enforce:

* architectural correctness
* deterministic code
* strict testing patterns
* reproducible updates
* compliance with AI helper rules

---

# **1. Purpose of This Document**

The goal of these templates is to:

* give AI contributors a predictable structure
* eliminate ambiguity
* reduce risk of violating core architecture
* unify thinking patterns across different tasks
* ensure incremental, safe contributions

Each template must be followed exactly (unless instructed otherwise).

---

# **2. Task Types Supported**

This document defines templates for the following categories:

1. Code Implementation
2. Workflow Modification
3. Utility Module Creation
4. Test Creation (Unit & Integration)
5. Bug Fixes
6. Documentation Updates
7. Refactoring
8. Config Schema Updates
9. Report Template Modifications
10. Tool Wrapper Improvements
11. Output System Extensions

---

# **3. Template: Code Implementation Task**

Use when AI needs to implement a function, class, or module.

```
## Task: <short description>

### 1. Read These Files Before Coding
- architecture.md
- module-plan.md
- relevant blueprint (e.g., blueprint-data-model.md)
- naming-convention.md
- coding-style.md

### 2. Requirements
- function signature:
- allowed imports:
- expected behavior:
- deterministic result required? (yes/no)
- test coverage needed? (yes/no)
- logging required? (yes/no)

### 3. Constraints
- do not modify public API
- do not add dependencies
- do not break determinism
- must follow PRIMERLAB_* error code rules

### 4. Implementation Plan
- step-by-step outline of what to implement

### 5. Final Output
- full code block only, no explanations
```

---

# **4. Template: Workflow Modification Task**

Use when modifying a workflow (`workflow.py`).

```
## Task: Modify workflow <name>

### 1. Read First
- blueprint-output-system.md
- blueprint-logging-system.md
- blueprint-config-system.md
- blueprint-error-handling.md

### 2. Required Changes
(list items)

### 3. Constraints
- must not change workflow entrypoint signature
- must follow progress system templates
- must use logger (no prints)
- must update WorkflowResult if needed
- must not mutate config

### 4. Implementation Plan
(step-by-step)

### 5. Final Output
(code changes or patch)
```

---

# **5. Template: Utility Module Creation**

For creating something like:

```
primerlab/core/utils/sequence_math.py
```

Use this template:

```
## Task: Create Utility Module

### 1. Requirements
- module path:
- allowed imports:
- functions to implement:
- required helpers:

### 2. Constraints
- no side effects
- deterministic output
- no logging inside utility functions
- must follow naming conventions

### 3. Implementation Outline
(step-by-step)

### 4. Final Output
(code block only)
```

---

# **6. Template: Unit Test Creation**

```
## Task: Create Unit Tests for <module>

### 1. Files Under Test
(list module paths)

### 2. What Must Be Tested
- function behavior
- edge cases
- invalid inputs
- error codes
- deterministic output

### 3. Tools
- pytest
- pytest-mock

### 4. Constraints
- tests must run < 200ms
- tests must use mocks when external tools involved
- do not access real filesystem except tmp_path
- no random data

### 5. Final Output
- code block with full test file
```

---

# **7. Template: Integration Test Creation**

```
## Task: Integration Test — <workflow>

### 1. Workflow Under Test
- pcr / qpcr / crispr / multiplex

### 2. Input Files Needed
- YAML config path under tests/resources
- sequence file

### 3. What to Validate
- CLI execution success
- output folder structure
- logs creation
- debug folder behavior
- JSON output validity (golden tests)
- deterministic metadata

### 4. Constraints
- mock all external tools
- test must run < 700ms
- follow integration-tests.md rules

### 5. Final Output
(test file code block)
```

---

# **8. Template: Bug Fix Task**

```
## Task: Fix Bug <bug description>

### 1. Reproduce
- how to reproduce the issue
- expected vs actual

### 2. Root Cause Analysis
- module involved
- exact function responsible

### 3. Constraints
- fix must not alter public API
- fix must not introduce new dependencies
- fix must not break determinism

### 4. Patch Plan
- list code changes needed

### 5. Final Output
(patch or code block)
```

---

# **9. Template: Documentation Update Task**

```
## Task: Update Documentation

### 1. Affected Docs
(list docs)

### 2. Required Updates
- clarity improvements
- new sections needed
- outdated content removal

### 3. Constraints
- English only
- Markdown only
- follow naming & style conventions
- no architectural changes

### 4. Final Output
(markdown patch)
```

---

# **10. Template: Refactor Task**

```
## Task: Refactor <module>

### 1. Goal
- performance?
- readability?
- code removal?
- cleanup?

### 2. Constraints
- must not change public API
- must not change behavior
- must not break tests
- must not reorder output JSON fields

### 3. Implementation Plan
(step-by-step)

### 4. Final Output
(patch)
```

---

# **11. Template: Config Schema Update Task**

```
## Task: Update Config Schema

### 1. Config Section
(name)

### 2. Change Required
(add/remove/modify keys)

### 3. Constraints
- must not break backward compatibility
- must update config-design.md
- must update related tests
- must update workflow validation logic
- must update sample configs

### 4. Implementation Plan

### 5. Final Output
(patch)
```

---

# **12. Template: Report Generator Modification**

```
## Task: Modify Report Generator

### 1. Update Target
(report.py)

### 2. Requirements
- new sections?
- formatting updates?

### 3. Constraints
- output must remain deterministic
- must not change folder structure
- must not print sensitive data
- must not change JSON schema

### 4. Implementation Plan

### 5. Final Output
(code block)
```

---

# **13. Template: External Tool Wrapper Update**

```
## Task: Update <tool> Wrapper

### 1. Tool Wrapper
- primer3_wrapper / blast_wrapper / vienna_wrapper

### 2. Required Modifications
(list)

### 3. Constraints
- must not call tools directly in tests
- must maintain safe subprocess invocation
- must not introduce shell=True
- must update mocks accordingly

### 4. Implementation Plan

### 5. Final Output
(code block)
```

---

# **14. Template: Output System Extension**

```
## Task: Extend Output System

### 1. New Output Behavior
- add JSON? modify report? extend metadata?

### 2. Required Updates
- output manager
- workflow integration

### 3. Constraints
- deterministic paths
- backward compatibility
- no sensitive data in outputs

### 4. Implementation Plan

### 5. Final Output
(patch)
```

---

# **15. Summary**

This document provides a **complete structured toolkit** for automated contributors.
Every task must follow the relevant template, ensuring:

* safe
* deterministic
* architecture-compliant
* maintainable
* testable

contributions.

Templates help prevent common agent mistakes and keep PrimerLab consistent as it evolves.
