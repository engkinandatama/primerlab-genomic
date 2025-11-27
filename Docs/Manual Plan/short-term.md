# 🚀 **SHORT-TERM SCOPE SUMMARY (v0.1 – v0.4)**

This document defines the **official deliverables** for the *PrimerLab short-term development phase*, covering versions:

* **v0.1 — Core Foundation Layer**
* **v0.2 — PCR Basic Workflow**
* **v0.3 — QC Extended**
* **v0.4 — qPCR Workflow**

Total: **4 major milestones**.

---

# 🧱 **SHORT-TERM MILESTONE 1 — v0.1 Core Foundation**

📌 *This milestone establishes the entire structural and architectural backbone of PrimerLab.*
No biological logic is implemented yet.

## ✅ **Components to Build**

### **1. Core System**

* `core/config_loader.py`
* `core/error.py`
* `core/logging.py`
* `core/output.py`
* `core/sequence.py`

### **2. API Layer**

* `api/__init__.py`
* Public API interface definitions (empty or minimal)

### **3. Tools Wrapper Skeleton**

* `core/tools/primer3_wrapper.py` *(skeleton only)*
* `core/tools/vienna_wrapper.py` *(skeleton only)*

### **4. CLI Skeleton**

* `cli/main.py`
* Commands:

  * `primerlab run <workflow>`
  * `primerlab version`

### **5. Deterministic Output System**

* canonical output folder structure
* stable JSON writer
* Markdown/PDF report placeholder

### **6. Logging System**

* log formatter
* multi-stage progress system
* debug-mode directory handling

### **7. Config System**

* YAML + CLI parsing
* config validation engine
* default required keys

---

## 🎯 **Expected Output of v0.1**

At the end of v0.1, you should be able to:

✔ Run the CLI without errors
✔ Execute a dummy workflow skeleton (PCR placeholder)
✔ Create deterministic output folders like:

```
runs/
   run_2025_11_26T/
      logs/
      debug/
      output.json
```

✔ Run a basic command:

```
primerlab run pcr --config pcr.yml
```

⚠ No primer design yet
⚠ No QC
⚠ No Primer3 execution
⚠ No modeling

This stage is **pure architecture and skeleton**.

---

# 🧪 **SHORT-TERM MILESTONE 2 — v0.2 PCR BASIC WORKFLOW**

📌 *This is the first milestone that produces actual biological results.*

## ✅ **Components to Build**

### **1. Functional Primer3 Wrapper**

* invoke Primer3 via CLI
* send FASTA sequence
* parse returned primers
* error handling + safety wrappers

### **2. Basic Primer Scoring**

* Tm calculation
* GC content
* primer length check
* product size check

### **3. Basic Hairpin/Dimer Predictors**

* simple ΔG thresholding
* penalty scoring placeholders

### **4. PCR Workflow Engine**

* sequence input → Primer3
* format + evaluate primers
* rank candidates
* produce structured JSON output

### **5. Output Report v1**

Includes:

* forward & reverse primer sequences
* Tm, GC
* product size
* QC penalties

---

## 🎯 **Expected Output of v0.2**

You should be able to run:

```
primerlab run pcr --config pcr_basic.yml
```

And obtain:

```
runs/run_xxxx/output.json
```

Example:

```json
{
  "status": "success",
  "primers": [
    {
      "name": "primer_1_f",
      "sequence": "ATGCGTTAC...",
      "tm": 58.2,
      "gc": 42.1,
      "hairpin_penalty": 0.3,
      "dimer_penalty": 0.1
    }
  ]
}
```

⚠ No extended QC yet
⚠ No secondary structure analysis

This milestone delivers a **functional minimal PCR designer**.

---

# 🔬 **SHORT-TERM MILESTONE 3 — v0.3 QC EXTENDED**

📌 *This milestone upgrades the PCR engine to a scientifically robust, high-quality system.*

## ✅ **Components to Build**

### **1. ViennaRNA Wrapper**

* CLI bindings for `RNAfold`
* compute secondary structure ΔG
* fold stability scoring

### **2. Extended QC Engine**

* cross-dimer matrix evaluation
* secondary-structure scanning
* repeat/homopolymer detection
* problematic 3' ends
* GC clamp evaluation

### **3. Scoring v2**

* weighted scoring system
* multi-factor QC scoring
* penalty matrix

### **4. Output Report v2**

* detailed QC metrics
* PASS/WARNING/FAIL flags
* ΔG tables
* extended validations

---

## 🎯 **Expected Output of v0.3**

You will obtain:

✔ more accurate primer scoring
✔ real ΔG folding QC (ViennaRNA)
✔ cross-dimer matrix stability checks
✔ detailed Markdown/PDF report

At this stage, PrimerLab becomes a **scientific-grade PCR primer design engine**.

---

# 📊 **SHORT-TERM MILESTONE 4 — v0.4 qPCR WORKFLOW**

📌 *qPCR builds directly on PCR + QC Extended, adding qPCR-specific constraints.*

## ✅ **Components to Build**

### **1. qPCR Rule Engine**

* amplicon size constraints
* primer efficiency rules
* detection heuristics

### **2. Efficiency Estimator**

* ΔG-based approximation
* logistic or regression placeholder model

### **3. qPCR Workflow Engine**

* invoke PCR workflow
* filter + re-score based on qPCR rules
* return qPCR-optimized primers

### **4. qPCR Report**

* efficiency predictions
* qPCR scoring
* qPCR-specific flags

---

## 🎯 **Expected Output of v0.4**

You will be able to run:

```
primerlab run qpcr --config qpcr.yml
```

And obtain:

* qPCR-optimized primer pairs
* predicted efficiencies
* validated qPCR constraints
* qPCR-specific structured report

---

# ✅ **FINAL NOTE**

This document is the **canonical short-term development plan** for PrimerLab.
It defines exactly what must be achieved before moving to mid-term modules (CRISPR, Multiplex PCR, etc.).
