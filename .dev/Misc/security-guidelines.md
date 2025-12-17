# **PrimerLab — Security Guidelines**

This document defines all security practices required for developing, maintaining, and extending PrimerLab.
It covers protection of:

* API keys
* user data
* filesystem safety
* output sanitization
* external tool invocation
* dependency trust
* CLI behavior
* sandbox compliance for automated contributors

These rules apply to **all contributors**, including automation systems.

---

# **1. Purpose of This Document**

PrimerLab handles:

* biological sequences
* user-supplied file paths
* external tool invocation
* API keys for optional services

Thus, strict security rules are required to prevent:

* accidental key exposure
* malicious path traversal
* insecure subprocess execution
* leaking sensitive sequence data
* corruption of output directories
* remote code execution through config files

This document ensures safe operation and safe development.

---

# **2. Scope**

Security considerations apply to:

* all Python code
* all configs and YAML structures
* CLI input
* environment variables
* output generation
* external binaries (Primer3, BLAST)
* automated contributor interactions
* GitHub repository contents
* packaging and distribution

---

# **3. API Key Security**

PrimerLab may use optional external APIs in the future.
To prevent key leakage:

### **3.1 Never embed API keys in source code**

Forbidden:

```python
API_KEY = "mykey123"  # ❌
```

Allowed:

```python
key = os.getenv("PRIMERLAB_API_KEY")
```

---

### **3.2 Environment variables only**

Users provide keys via:

```
export PRIMERLAB_API_KEY="abc123"
```

---

### **3.3 Key validation rules**

Keys must:

* never be printed
* never appear in logs
* never appear in traceback
* never be written to output JSON
* never be included in metadata

---

### **3.4 Mask keys when needed**

If a key must be referenced:

```
log.info("Using API key: ****1234")
```

---

# **4. File System Safety**

Because PrimerLab writes output files and loads sequences:

### **4.1 Path sanitization**

No user-supplied path may:

* escape output folder
* contain “..”
* contain absolute root paths unless explicitly allowed
* start with `~` unless expanded safely

### **4.2 Never overwrite unrelated files**

All writing must occur in:

```
<run_folder>/
```

### **4.3 Do not follow symlinks**

When creating output:

* do NOT resolve user-provided symlinks
* do NOT allow output directories to be symbolic links

### **4.4 Safe directory creation**

Use:

```python
path.mkdir(parents=True, exist_ok=True)
```

Never:

```python
os.makedirs(user_input)  # ❌ dangerous
```

---

# **5. Input Sequence Safety**

PrimerLab must assume sequences may contain:

* malformed characters
* malicious escape patterns
* extremely long sequences

Rules:

### **5.1 Strict validation**

Reject sequences containing:

* non-ATGCN characters
* whitespace
* newline escapes
* module import attempts
* extremely long sequences (>5 MB default)

### **5.2 No dynamic execution**

Sequence content must never be executed, evaluated, or interpolated into code.

---

# **6. External Tool Execution Security**

PrimerLab uses optional tools (Primer3, BLAST).
To avoid command injection:

### **6.1 Never build shell commands using string concatenation**

Forbidden:

```python
cmd = "primer3_core " + args  # ❌
```

Allowed:

```python
subprocess.run(["primer3_core", "--arg", "value"])
```

### **6.2 Disable shell=True**

Always:

```
shell=False
```

### **6.3 Validate tool paths**

User-defined paths must:

* exist
* point to an executable
* not include spaces in unsafe locations
* not expand to shell commands

### **6.4 Timeout**

Every external tool call must include a timeout:

```python
subprocess.run(cmd, timeout=15)
```

---

# **7. YAML and Config File Security**

YAML is dangerous if loaded unsafely.

### **7.1 Always use safe loader**

Correct:

```python
yaml.safe_load(stream)
```

NEVER use:

```python
yaml.load(stream)  # ❌
```

### **7.2 Prevent arbitrary objects**

Config files may NOT contain:

* Python objects
* custom tags
* anchors referencing external files
* executable instructions

### **7.3 Validate every config key**

Before use, every config key must be checked against:

* allowed fields
* allowed types
* allowed ranges

---

# **8. Logging Security**

Logs must never contain:

* API keys
* entire biological sequences
* traceback with sensitive file paths
* raw tool output containing private data

### **8.1 Allowed logging:**

* step names
* QC summaries
* error codes

### **8.2 Not allowed:**

* raw sequence content
* private internal state
* user-provided paths
* raw external tool output (only in debug folder)

---

# **9. Debug Folder Security**

Debug folder contains sensitive info.
Rules:

### **9.1 Do not include:**

* API keys
* full sequence content (only short windows allowed)

### **9.2 Allowed internal dumps:**

* primer3_raw.txt
* blast_raw.txt
* traceback.txt

### **9.3 Debug folder must never be uploaded automatically**

Contributors must not commit debug/ contents.

---

# **10. CLI Security Rules**

The CLI must:

* sanitize all user inputs
* reject malicious file paths
* validate configuration before executing anything
* catch all exceptions and prevent raw tracebacks
* never echo sensitive content

The CLI must run in a safe, deterministic manner.

---

# **11. Dependency Security**

### **11.1 Pin trusted dependencies only**

Dependencies must:

* come from PyPI official
* be mature
* not be deprecated
* be pinned if needed for reproducibility

### **11.2 Avoid risky packages**

No package that:

* uses unsafe loaders
* uses dynamic evaluation
* downloads binaries automatically
* has questionable maintenance status

### **11.3 Review dependencies annually**

Security review:

* CVEs
* support status
* API stability

---

# **12. Packaging & Distribution Security**

When publishing PrimerLab:

### **12.1 Never include:**

* test data
* debug folders
* user sequences
* any credentials

### **12.2 Verify PyPI package contents**

Only required directories:

```
primerlab/
docs/ (optional)
```

### **12.3 PyPI long description must avoid exposing config examples with sensitive data**

---

# **13. Security in Automated Contributions**

Automated contributors must:

* never output API keys
* never insert unsafe imports
* never add logging of raw biological sequences
* follow all file I/O safety patterns
* never modify CLI to allow unsafe operations
* never introduce shell=True

AI contributions must be validated by unit tests covering safety.

---

# **14. Future Security Extensions**

Future versions may introduce:

* sandboxed execution mode
* remote execution mode
* encrypted metadata fields
* sequence redaction in logs
* secure temp directory isolation

All must remain backward-compatible.

---

# **15. Summary**

This security guideline defines:

* API key protection
* filesystem safety
* config/YAML safety
* CLI hardening
* external tool sanitization
* dependency safety
* debug output protection
* distribution security
* automated contributor restrictions

Following these rules ensures PrimerLab remains secure, trustworthy, and suitable for publication, collaboration, and open-source distribution.

