# PrimerLab QC Metrics & Thresholds

Documentation of quality control checks in PrimerLab v0.1.3+.

---

## Overview

PrimerLab performs multi-level quality control:

1. **Sequence QC** - GC clamp, Poly-X detection
2. **Thermodynamic QC** - Hairpin, homodimer, heterodimer (via ViennaRNA)
3. **Parameter QC** - Tm balance, GC content, length

---

## QC Modes

Three preset modes control threshold stringency:

| Mode | Hairpin ΔG | Homodimer ΔG | Heterodimer ΔG | Use Case |
|------|------------|--------------|----------------|----------|
| **strict** | -6.0 | -6.0 | -6.0 | High-specificity assays |
| **standard** | -9.0 | -9.0 | -9.0 | General PCR (default) |
| **relaxed** | -12.0 | -12.0 | -12.0 | Difficult templates |

### Configuration:
```yaml
qc:
  mode: standard  # or strict, relaxed
```

### Custom Thresholds:
```yaml
qc:
  mode: standard
  hairpin_dg_max: -8.0    # Override preset
  homodimer_dg_max: -10.0
  heterodimer_dg_max: -10.0
```

---

## Sequence QC Checks

### 1. GC Clamp (3' End Stability)

Evaluates the last 5 bases of each primer.

**PrimerLab Behavior:**
| G/C Count | Status | Reason |
|-----------|--------|--------|
| 2-3 | ✅ PASS | Optimal stability |
| 0-1 | ❌ FAIL (Weak) | Poor 3' binding |
| 4-5 | ⚠️ WARNING (Strong) | May cause non-specific binding |

**Scientific Rationale:**
The 3' end is critical for extension initiation. A GC clamp (2-3 G/C in last 5 bases) promotes stable priming without excessive secondary structure [1][2].

**Reference:** [1] Dieffenbach et al., PCR Primer: A Laboratory Manual, 2003

---

### 2. Poly-X Run Detection

Detects consecutive identical nucleotides.

**PrimerLab Threshold:**
| Run Length | Status |
|------------|--------|
| ≤ 4 | ✅ PASS |
| > 4 | ❌ FAIL |

**Scientific Rationale:**
Mononucleotide runs >4 bases:
- Cause primer slippage during synthesis
- Form secondary structures (poly-G quadruplexes)
- Reduce binding specificity [2]

**Reference:** [2] Abd-Elsalam, K.A. "Bioinformatic tools in primer design", 2003

---

## Thermodynamic QC Checks

Requires ViennaRNA installation.

### 3. Hairpin Formation

Self-complementary folding of single primer.

**Interpretation Guidelines:**
| ΔG (kcal/mol) | Interpretation | Recommendation |
|---------------|----------------|----------------|
| > 0 | No hairpin | ✅ Ideal |
| -3 to 0 | Weak hairpin | ✅ Acceptable |
| -6 to -3 | Moderate hairpin | ⚠️ Use with caution |
| < -6 | Strong hairpin | ❌ Avoid for standard PCR |
| < -9 | Very stable | ❌ Avoid completely |

**Scientific Rationale:**
Hairpins with ΔG < -9 kcal/mol are stable at annealing temperatures (50-65°C), reducing available primer for target binding [3].

**Reference:** [3] SantaLucia, J. "A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics", PNAS 1998

---

### 4. Homodimer / Heterodimer Formation

Self-dimerization and primer-primer interactions.

**PrimerLab Thresholds:**
| Mode | ΔG Threshold | Use Case |
|------|--------------|----------|
| strict | > -6.0 kcal/mol | Multiplex, qPCR |
| standard | > -9.0 kcal/mol | Standard PCR |
| relaxed | > -12.0 kcal/mol | Difficult templates |

**Scientific Rationale:**
Primer dimers compete with target amplification. For qPCR/multiplex, stricter thresholds prevent artifact bands [4].

**Reference:** [4] Primer3 documentation, https://primer3.org/manual.html

---

## Parameter QC Checks

### 5. Tm Balance

Forward/reverse primer melting temperature difference.

**PrimerLab Defaults:**
| Preset | tm_diff_max |
|--------|-------------|
| PCR (standard) | 3.0°C |
| qPCR | 2.0°C |
| Long Range | 2.0°C |
| DNA Barcoding | 5.0°C |

**Recommended Ranges (Literature):**
| Tm Difference | Status | Rationale |
|---------------|--------|-----------|
| ≤ 2°C | ✅ Ideal | Equal annealing efficiency |
| 2-5°C | ⚠️ Acceptable | May require optimization |
| > 5°C | ❌ Suboptimal | Unequal annealing, strand bias |

**Reference:** [5] Rychlik et al., "Optimization of Annealing Temperature", Nucleic Acids Research 1990

---

### 6. GC Content

Percentage of G and C bases.

**PrimerLab Defaults:**
```yaml
parameters:
  gc:
    min: 40.0
    max: 60.0
```

**Recommended Ranges (Literature):**
| GC % | Status | Rationale |
|------|--------|-----------|
| 40-60% | ✅ Optimal | Balanced Tm and specificity [5] |
| 30-40% | ⚠️ Acceptable | Lower Tm, may need optimization |
| 60-70% | ⚠️ Acceptable | Higher Tm, secondary structure risk |
| < 30% | ❌ Not recommended | Unstable binding |
| > 70% | ❌ Not recommended | G-quadruplex formation risk [6] |

**Reference:** [6] Burge et al., "Quadruplex DNA", Nucleic Acids Research 2006

---

### 7. Primer Length

**PrimerLab Defaults:**
| Preset | Min | Opt | Max |
|--------|-----|-----|-----|
| PCR | 18 | 20 | 25 |
| Long Range | 25 | 28 | 35 |
| qPCR | 18 | 20 | 25 |

**Recommended Ranges (Literature):**
| Length | Status | Rationale |
|--------|--------|-----------|
| 18-25 bp | ✅ Optimal | Standard specificity, manageable Tm [1] |
| 15-17 bp | ⚠️ Short | May lack specificity for complex genomes |
| 26-35 bp | ⚠️ Long | Higher Tm, needed for long-range PCR |
| < 15 bp | ❌ Too short | Insufficient specificity |
| > 35 bp | ❌ Too long | Synthesis issues, high cost |

**Reference:** [1] Dieffenbach et al., PCR Primer: A Laboratory Manual, 2003

---

## QC in Re-ranking Engine

The re-ranking engine (`primerlab/core/reranking.py`) evaluates candidates:

1. **Generate** - Request N candidates from Primer3
2. **Filter** - Apply QC thresholds to each
3. **Rank** - Sort passing candidates by Primer3 penalty
4. **Select** - Choose best + alternatives

### Candidate Status:
- `passes_qc: true` → Available for selection
- `passes_qc: false` → Rejected with reason

---

## QC Result Fields

Output JSON includes:

```json
{
  "qc": {
    "hairpin_ok": true,
    "homodimer_ok": true,
    "heterodimer_ok": true,
    "tm_balance_ok": true,
    "hairpin_dg": -2.5,
    "homodimer_dg": -1.8,
    "heterodimer_dg": -3.2,
    "tm_diff": 1.5,
    "warnings": [],
    "errors": []
  }
}
```

---

## Fallback Behavior

When ViennaRNA is not installed:
- ✅ Sequence QC still runs (GC clamp, Poly-X)
- ⚠️ Thermodynamic QC skipped
- ⚠️ Warning logged

```
⚠️ ViennaRNA not found. Secondary structure QC will be skipped.
```

---

## References

1. Dieffenbach, C.W., Dveksler, G.S. (2003). *PCR Primer: A Laboratory Manual*. Cold Spring Harbor Laboratory Press.
2. Abd-Elsalam, K.A. (2003). "Bioinformatic tools and guideline for PCR primer design". *African Journal of Biotechnology*.
3. SantaLucia, J. (1998). "A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics". *PNAS* 95(4):1460-1465.
4. Untergasser A. et al. (2012). "Primer3—new capabilities and interfaces". *Nucleic Acids Research*. https://primer3.org/manual.html
5. Rychlik, W. et al. (1990). "Optimization of the annealing temperature for DNA amplification in vitro". *Nucleic Acids Research* 18(21):6409-6412.
6. Burge, S. et al. (2006). "Quadruplex DNA: sequence, topology and structure". *Nucleic Acids Research* 34(19):5402-5415.

---

*Last updated: v0.1.3*
