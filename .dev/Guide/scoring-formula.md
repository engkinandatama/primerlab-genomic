# Primer Quality Score

PrimerLab uses a combined quality scoring system to rank primer pairs and provide an intuitive 0-100 score indicating the likelihood of successful amplification.

## Scoring Formula

```
PrimerLab Score = 100 - (Primer3 Penalty × 10) - Σ(QC Penalties)
```

The score combines:
1. **Primer3 Penalty** - Sequence-based quality from Primer3
2. **ViennaRNA QC** - Thermodynamic secondary structure analysis
3. **Sequence QC** - GC clamp and poly-nucleotide checks

## Score Categories

| Score | Category | Display | Interpretation |
|-------|----------|---------|----------------|
| 85-100 | Excellent | ✅ | High probability of successful amplification |
| 70-84 | Good | ✅ | Likely successful with standard conditions |
| 50-69 | Fair | ⚠️ | May require optimization |
| 0-49 | Poor | ❌ | Low probability of success |

## Penalty Weights by QC Mode

PrimerLab applies different penalty weights depending on the QC mode:

### Strict Mode (High-Specificity Assays)

| Check | Threshold | Penalty |
|-------|-----------|---------|
| Hairpin (3' end) | ΔG < -2 kcal/mol | -20 |
| Hairpin (internal) | ΔG < -3 kcal/mol | -15 |
| Self-dimer | ΔG < -5 kcal/mol | -20 |
| Heterodimer | ΔG < -5 kcal/mol | -15 |
| GC clamp (weak) | 0-1 G/C in last 5 bases | -20 |
| GC clamp (strong) | 4-5 G/C in last 5 bases | -10 |
| Poly-X | >4 consecutive nucleotides | -15 |

### Standard Mode (Default)

| Check | Threshold | Penalty |
|-------|-----------|---------|
| Hairpin (3' end) | ΔG < -3 kcal/mol | -15 |
| Hairpin (internal) | ΔG < -6 kcal/mol | -10 |
| Self-dimer | ΔG < -6 kcal/mol | -15 |
| Heterodimer | ΔG < -6 kcal/mol | -10 |
| GC clamp (weak) | 0-1 G/C in last 5 bases | -15 |
| GC clamp (strong) | 4-5 G/C in last 5 bases | -5 |
| Poly-X | >4 consecutive nucleotides | -10 |

### Relaxed Mode (Difficult Templates)

| Check | Threshold | Penalty |
|-------|-----------|---------|
| Hairpin (3' end) | ΔG < -6 kcal/mol | -10 |
| Hairpin (internal) | ΔG < -9 kcal/mol | -5 |
| Self-dimer | ΔG < -9 kcal/mol | -10 |
| Heterodimer | ΔG < -9 kcal/mol | -5 |
| GC clamp (weak) | 0-1 G/C in last 5 bases | -10 |
| GC clamp (strong) | 4-5 G/C in last 5 bases | 0 |
| Poly-X | >4 consecutive nucleotides | -5 |

## Example Calculation

For a primer pair with:
- Primer3 penalty: 0.5
- No hairpin issues
- Weak heterodimer (ΔG = -7.0)
- Strong GC clamp on forward primer

**Standard Mode Calculation:**
```
Score = 100 - (0.5 × 10) - 10 (heterodimer) - 5 (strong GC)
Score = 100 - 5 - 10 - 5 = 80
Category: Good ✅
```

## Scientific References

The thresholds and penalties are based on established primer design literature:

1. **Benchling (2024)**. "PCR Primer Design Guidelines"
   - Hairpin 3' end: ΔG ≥ -2 kcal/mol
   - Self-dimer: ΔG ≥ -5 kcal/mol

2. **IDT (2024)**. "Primer & Probe Design Guidelines"
   - General cutoff: ΔG ≥ -9.0 kcal/mol

3. **Untergasser et al. (2023)**. "DeGenPrime: Degenerate Primer Design"
   - Nearest-Neighbor thermodynamic model
   - Penalty scoring for secondary structures

4. **ThermoPlex (2024)**. "Multiplex PCR design based on DNA Thermodynamics"
   - DNA-DNA interaction prediction

5. **SantaLucia J. (1998)**. "Nearest-Neighbor Thermodynamics"
   - PNAS 95:1460-1465
   - Foundation for thermodynamic calculations

## Limitations

- The score is a **heuristic** and does not guarantee experimental success
- Actual PCR performance depends on reaction conditions, template quality, and polymerase
- Use the score as a **relative ranking** tool, not an absolute predictor
- When comparing primers, focus on scores within the same QC mode
