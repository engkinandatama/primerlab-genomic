# Species Check Example

This example demonstrates how to use `primerlab species-check` to validate primer specificity across multiple species.

## Files

| File | Description |
|------|-------------|
| `primers.json` | 3 primer pairs for BRCA1/TP53 regions |
| `target_human.fasta` | Human BRCA1 target sequence |
| `offtargets_mouse_rat.fasta` | Mouse and Rat orthologs |

## Usage

### Basic Check (Target Only)

```bash
primerlab species-check \
  --primers primers.json \
  --target target_human.fasta \
  --output ./results
```

### With Off-targets

```bash
primerlab species-check \
  --primers primers.json \
  --target target_human.fasta \
  --offtargets offtargets_mouse_rat.fasta \
  --output ./results
```

### Excel Output

```bash
primerlab species-check \
  --primers primers.json \
  --target target_human.fasta \
  --offtargets offtargets_mouse_rat.fasta \
  --format excel \
  --output ./results
```

## Expected Output

```
🧬 Species Specificity Check (v0.4.2)
==================================================
📂 Loading primers: primers.json
🎯 Loading target: target_human.fasta
🔬 Loaded off-target: Mouse_Brca1_Ortholog
🔬 Loaded off-target: Rat_Brca1_Related

⏳ Analyzing species specificity...

==================================================
🏁 Specificity Score: 85.0/100 (Grade B)
   Status: ✅ SPECIFIC
   Primers: 3 | Species: 3

📁 Reports saved to: ./results
   • species_analysis.json
   • species_report.md
```

## API Usage

```python
from primerlab.api.public import check_species_specificity_api

result = check_species_specificity_api(
    primers=[
        {"name": "BRCA1_F1", "forward": "ATGATTTTGAAATCAGACAACTG", "reverse": "CTCTTAAGGGCAGTTGTGAG"},
    ],
    target_template="ATGATTTTGAAATCAGACAACTG...",
    target_name="Human",
    offtarget_templates={
        "Mouse": "ATGACTTTGAAATCGGAC...",
        "Rat": "ATGACTTTGAAATCGGAC...",
    }
)

print(f"Score: {result['overall_score']}/100")
print(f"Grade: {result['grade']}")
```
