# Multi-Candidate Re-ranking Algorithm

Documentation of PrimerLab's primer selection algorithm (v0.1.3+).

---

## Overview

The Multi-Candidate Re-ranking Engine solves a common problem: **Primer3's top candidate may fail ViennaRNA QC checks.**

Instead of failing, PrimerLab:
1. Requests multiple candidates from Primer3
2. Evaluates each with ViennaRNA
3. Selects the best that passes all QC

---

## Algorithm Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT SEQUENCE                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  PRIMER3 DESIGN                             │
│        Request N candidates (default: 50 for PCR)           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               FOR EACH CANDIDATE:                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Sequence QC (GC clamp, Poly-X)                  │   │
│  │  2. ViennaRNA QC (hairpin, homodimer, heterodimer)  │   │
│  │  3. Record: passes_qc, rejection_reason, scores     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FILTER                                    │
│        Keep only candidates with passes_qc = true            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     RANK                                     │
│     Sort by Primer3 penalty (lower = better)                │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    SELECT                                    │
│     Best = lowest penalty among QC-passing                  │
│     Alternatives = next N-1 (configurable)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

```yaml
advanced:
  num_candidates: 50      # PCR default, 30 for qPCR
  
parameters:
  show_alternatives: 5    # How many alternatives to include
  
qc:
  mode: standard          # strict, standard, relaxed
```

---

## Evaluation Criteria

### Per-Candidate Scores:

| Metric | Source | Purpose |
|--------|--------|---------|
| `primer3_penalty` | Primer3 | Lower = better fit to constraints |
| `hairpin_fwd_dg` | ViennaRNA | Forward primer self-folding |
| `hairpin_rev_dg` | ViennaRNA | Reverse primer self-folding |
| `homodimer_fwd_dg` | ViennaRNA | Forward self-dimerization |
| `homodimer_rev_dg` | ViennaRNA | Reverse self-dimerization |
| `heterodimer_dg` | ViennaRNA | Forward-reverse dimerization |

### Pass/Fail Logic:

```python
passes_qc = (
    gc_clamp_ok AND           # 2-3 G/C in last 5 bases
    no_poly_x AND             # No runs > 4
    hairpin_dg > threshold AND
    homodimer_dg > threshold AND
    heterodimer_dg > threshold
)
```

---

## Threshold Values

### By QC Mode:

| Mode | Hairpin | Homodimer | Heterodimer |
|------|---------|-----------|-------------|
| strict | > -6.0 | > -6.0 | > -6.0 |
| standard | > -9.0 | > -9.0 | > -9.0 |
| relaxed | > -12.0 | > -12.0 | > -12.0 |

*Units: kcal/mol. More negative = more stable (worse)*

---

## Selection Strategy

### Primary Selection:
```
best_candidate = min(passing_candidates, key=primer3_penalty)
```

### Alternative Selection:
```
alternatives = sorted(passing_candidates, key=primer3_penalty)[1:show_alternatives+1]
```

---

## Output Structure

```json
{
  "primers": {
    "forward": { ... },
    "reverse": { ... }
  },
  "alternatives": [
    {
      "rank": 1,
      "reason": "Second lowest penalty, all QC passed",
      "forward": { ... },
      "reverse": { ... }
    }
  ],
  "rejected_candidates": [
    {
      "index": 3,
      "reason": "Hairpin ΔG too stable (-10.5 kcal/mol)"
    }
  ]
}
```

---

## Edge Cases

### No candidates pass QC:
- Return `null` for primers
- Include all rejected candidates with reasons
- Suggest relaxing constraints

### ViennaRNA not available:
- Skip thermodynamic QC
- Use Primer3 ranking only
- Log warning

### Seed parameter:
```yaml
advanced:
  seed: 42  # For reproducible selection
```

When set, `random.seed(seed)` is called for deterministic tiebreakers.

---

## Implementation Files

| Module | Purpose |
|--------|---------|
| `primerlab/core/reranking.py` | Main re-ranking engine |
| `primerlab/core/sequence_qc.py` | GC clamp, Poly-X checks |
| `primerlab/core/tools/vienna_wrapper.py` | ViennaRNA interface |

---

## Performance Notes

Processing time depends on:
- Number of candidates requested
- Sequence complexity
- Whether ViennaRNA is installed
- System hardware

**Tips for faster runs:**
- Reduce `num_candidates` if acceptable
- Use `qc.mode: relaxed` for fewer rejections
- Consider skipping ViennaRNA for initial design

---

*Last updated: v0.1.3*
