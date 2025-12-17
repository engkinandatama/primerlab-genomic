# 🟦 **LONG-TERM SCOPE SUMMARY (v0.7 – v0.8)**

Long-term development focuses on **computational biology features** that go beyond classical primer/guide design:

1. **v0.7 — Genome-Aware Off-Target Search**
2. **v0.8 — Structural & Thermodynamic Modeling (3D + ΔG Deep QC)**

These milestones transform PrimerLab from a “primer-generator” into an actual **bioinformatics analysis suite** capable of deep QC, realistic modeling, and genome-scale computations.

---

# 🧬 **LONG-TERM MILESTONE 1 — v0.7 GENOME-AWARE OFF-TARGET WORKFLOW**

📌 *This milestone introduces full genomic specificity checking using local indexers (Bowtie/BWA) instead of simple mismatch-based scoring.*

This is the most important milestone for CRISPR & advanced PCR.

---

## ✅ **Components to Build**

### **1. Genome Indexer Integration**

Support 1–2 backend engines:

* **Bowtie2** (recommended for short guides/primers)
* **BWA** (longer sequences)

Tasks:

* build local genome index
* detect if index exists
* load index with minimal overhead
* provide API:

```
search(sequence, max_mismatch=3)
```

### **2. Genome Search Engine (Deterministic Wrapper)**

Deliverables:

* align primer/gRNA across whole genome
* return off-target locations
* produce mismatch maps
* strand-aware orientation
* penalty scoring based on mismatch positions

### **3. CRISPR Off-Target v2**

Upgrade CRISPR scoring:

* incorporate true genome hits
* score based on mismatch position
* PAM compatibility
* filter high-risk off-target sites

### **4. PCR Off-Target Workflow**

PCR primers also benefit:

* detect unintended genomic hits
* detect pseudogene binding
* identify multi-target risk

### **5. Genome-Aware Report v1**

Includes:

* genomic coordinates
* number of off-target sites
* mismatch distribution
* on-target/off-target score
* genome summary table

### **6. Optional Genome Downloader**

Low-complexity utility:

* download reference genomes (e.g., from NCBI)
* validate FASTA
* SHA256 checksum verification
* store in cache directory

**NOT required to automate, just provide helper.**

---

## 🎯 **Expected Output of v0.7**

You will be able to run:

```
primerlab run crispr --config crispr.yml --genome hg38
primerlab run pcr --config pcr.yml --genome hg19
```

and obtain:

* true genome-aware off-target scoring
* CRISPR results comparable to Benchling/CRISPOR (light version)
* PCR primer off-target validation
* accurate genomic coordinates

⚠ Requires external index databases
⚠ Slower but optional
⚠ Not used for deterministic unit tests

---

# 🧪 **LONG-TERM MILESTONE 2 — v0.8 STRUCTURAL & THERMODYNAMIC MODELING**

📌 *This milestone introduces higher-order modeling: 3D prediction, free-energy simulation, and realistic molecular QC.*

This is where PrimerLab becomes a **modern computational-biology toolkit**.

---

## ✅ **Components to Build**

### **1. Secondary Structure Modeling (Advanced)**

Improve over v0.3 (basic ViennaRNA):

* full ΔG folding model
* ensemble frequency prediction
* MFE + centroid structure
* stem-loop detection
* alternative conformations

Used for:

* RNA-based primers
* CRISPR gRNA stability
* hairpin hotspots

### **2. Amplicon Structure Modeling**

Using tools like:

* RNAfold (for amplified RNA)
* mfold-like heuristics
* coarse-grain polymer simulation

Deliverables:

* amplicon-level folding QC
* detection of stable intramolecular loops
* thermodynamic penalty scoring

### **3. Primer–Template Hybridization Energy**

Simulate:

* binding free energy
* replication efficiency estimate
* 3' end stability modeling
* salt & Mg2+ corrections

### **4. CRISPR Structural Modeling**

Light version:

* gRNA secondary structure QC
* 5'/3' overhang scoring
* structural penalties

Full 3D modeling for CRISPR is future milestone (v0.9+).

### **5. 3D Modeling Integration (Optional Stub)**

Light integration:

* ViennaRNA → *.ps* or *.dot* files
* convert to SVG
* visualize hairpins
* structure diagrams

NOT a full Rosetta or Alphafold integration.

### **6. Structural QC Report v1**

Include:

* ΔG distribution
* strongest hairpin regions
* dimerization hotspots
* 3D structure thumbnails (optional)
* thermodynamic flags

---

## 🎯 **Expected Output of v0.8**

PrimerLab can:

* model RNA/DNA secondary structure accurately
* provide realistic ΔG-based QC
* detect structural issues in amplicons
* generate diagrams for reports
* estimate primer binding strength more realistically

At this stage, PrimerLab is comparable to:

* Primer3 (QC)
* OligoAnalyzer
* CRISPOR (light)
* IDT tools (minus wet-lab optimization)

---

# 🟧 **DEPENDENCIES (LONG-TERM)**

### Requires:

* ViennaRNA (full usage)
* Bowtie2 or BWA
* optional genome files
* additional CPU time

### Reuses:

* PCR workflow
* CRISPR workflow
* QC extended
* scoring v2/v3
* deterministic output

### Does NOT introduce:

* machine learning
* GPU requirements
* heavy protein-folding models

---

# 🟥 **LIMITATIONS (LONG-TERM)**

* no real 3D tertiary structure (Rosetta/AlphaFold)
* no machine-learning predictions
* no off-target simulation with SNP awareness (future)
* no population variant modeling
* no enzyme kinetics simulation
* no expression-level model

Those belong to the **Future Phase** (v0.9 – v1.0+).

---

# 🟩 **MILESTONE SUMMARY TABLE**

| Milestone | Version                 | Focus                            | Deliverables                 |
| --------- | ----------------------- | -------------------------------- | ---------------------------- |
| v0.7      | Genome-Aware Off-Target | Bowtie/BWA-based specificity     | CRISPR + PCR genome-wide QC  |
| v0.8      | Structural Modeling     | Secondary/thermodynamic modeling | ΔG simulation + structure QC |

