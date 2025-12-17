# 🔶 **MID-TERM SCOPE SUMMARY (v0.5 – v0.6)**

Mid-term phase focuses on implementing **two major advanced workflows**:

1. **v0.5 — CRISPR Guide Design Workflow**
2. **v0.6 — Multiplex PCR Workflow**

These modules sit on top of all short-term components (PCR Basic, QC Extended, qPCR) and introduce more complex sequence analysis logic.

Total: **2 main milestones**.

---

# 🧬 **MID-TERM MILESTONE 1 — v0.5 CRISPR WORKFLOW**

📌 *This milestone introduces a new workflow type: CRISPR guide RNA design with off-target analysis and PAM detection.*

CRISPR is the first workflow in PrimerLab that requires **genome-wide specificity checking**, making it one of the most important mid-term components.

---

## ✅ **Components to Build**

### **1. PAM Finder Module**

* Detect PAM sequences (e.g., NGG for SpCas9)
* Configurable PAM rules
* Scan input sequence for possible guide sites
* Output guide candidates (20bp + PAM)

### **2. Guide Extraction & Orientation**

* Extract target sequence
* Handle reverse-complement guides
* Normalize guide orientation
* Provide correct genomic coordinates

### **3. Off-Target Scoring Engine (Local)**

Mid-term implementation should be **deterministic**, so we use a simple scoring model:

* Hamming distance mismatches
* Weighted penalty system
* Mismatch at 3’ end → stronger penalty
* Allowed mismatches configurable (default ≤ 3)

**No BLAST or Bowtie yet**
(BLAST introduced in long-term as optional).

### **4. CRISPR Rule Engine**

Rules include:

* GC balance (optimal 40–60%)
* Avoid poly-T (TTTT)
* Avoid high repetition
* Avoid unstable 3’ ends
* Minimum distance between multiple guides

### **5. Scoring v3 (CRISPR-specific)**

* On-target rule score
* Off-target mismatch score
* PAM proximity score
* Overall ranking formula

### **6. CRISPR Workflow Engine**

Implements full flow:

```
PAM Detection → Guide Extraction → QC → Off-Target Scoring → Ranking → Report
```

### **7. CRISPR Report v1**

Includes:

* guide sequence
* PAM type
* genomic coordinates
* GC%
* off-target score
* mismatch distribution
* QC flags

---

## 🎯 **Expected Output of v0.5**

You will be able to run:

```
primerlab run crispr --config crispr.yml
```

Result:

* list of ranked CRISPR guides
* PAM positions
* mismatch-based off-target scores
* QC flags
* CRISPR-specific JSON + Markdown report

⚠ No BLAST or genome alignment yet
⚠ No off-target genome-wide search (future milestone)
⚠ No CRISPR-Cas variants (future)

This milestone provides **functional, light-mode CRISPR design** suitable for most simple use cases.

---

# 🟠 **MID-TERM MILESTONE 2 — v0.6 MULTIPLEX PCR WORKFLOW**

📌 *Multiplex PCR involves designing multiple primer pairs that work simultaneously in the same tube.*
This is significantly more complex due to **cross-dimer interactions** and combined QC logic.

---

## ✅ **Components to Build**

### **1. Multiplex Candidate Generator**

* reuse PCR workflow to generate primer pairs
* produce 5–20 candidate primer sets
* each primer set stored with metadata

### **2. Cross-Dimer Matrix Engine**

For N primers, generate NxN matrix:

* homodimer check
* heterodimer check
* ΔG for each pairing
* penalty matrix

E.g., for 10 primers → 100 matrix entries.

### **3. Amplicon Separation Logic**

Multiplex requires:

* non-overlapping amplicons
* product size spacing
* minimum distance thresholds

### **4. Multiplex QC Rules**

Rules include:

* avoid primer interference
* avoid shared motifs
* ensure GC uniformity across primer sets
* ensure Tm similarity (tight threshold)

### **5. Multiplex Scoring Engine**

Score each primer combination based on:

* cross-dimer matrix
* Tm differences
* GC uniformity
* amplicon spacing
* distance penalties

### **6. Multiplex Workflow Engine**

Full process:

```
PCR Candidate Generation → Matrix QC → Rule Filtering → Scoring → Ranking
```

### **7. Multiplex Report v1**

Includes:

* list of primer sets
* cross-dimer heatmap (optional)
* QC fail reasons
* score breakdown
* selected multiplex panel

---

## 🎯 **Expected Output of v0.6**

You will be able to run:

```
primerlab run multiplex --config multiplex.yml
```

Result:

* multiple primer sets evaluated simultaneously
* ranked multiplex panel
* matrix QC summary
* JSON + detailed report
* consistent and deterministic scoring

⚠ No machine-learning prediction yet
⚠ No amplicon secondary structure modeling yet (future)

This milestone transforms PrimerLab into a **multi-target primer design system**.

---

# 🟧 **DEPENDENCIES**

### Mid-Term depends on:

### **Core Layer**

* config loader
* logging
* error system
* deterministic output

### **Short-Term Workflows**

* PCR Basic Workflow (v0.2)
* QC Extended (v0.3)
* qPCR Workflow (v0.4)

### **Tools**

* primer3_wrapper
* vienna_wrapper (for ΔG calculations)

No new heavy dependencies should be introduced.

---

# 🟩 **LIMITATIONS (Mid-Term)**

* No real BLAST-based off-target search
* No genome indexing
* No CRISPR variants beyond SpCas9 NGG
* No GPU acceleration
* No dynamic machine-learning scoring
* Multiplex remains deterministic (no stochastic optimization)

These belong to **long-term and future milestones**.

---

# 🟦 **MILESTONE SUMMARY TABLE**

| Milestone | Version       | Focus                                         | Deliverables                |
| --------- | ------------- | --------------------------------------------- | --------------------------- |
| v0.5      | CRISPR        | Guide design, PAM detection, mismatch scoring | CRISPR workflow + report    |
| v0.6      | Multiplex PCR | Multi-primer QC + cross-dimer matrix          | Multiplex workflow + report |

