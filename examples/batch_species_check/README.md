# Batch Species-Check Example

This example demonstrates batch processing of multiple primer files.

## Files

- `primers/` - Directory with sample primer JSON files
- `target.fasta` - Target species template
- `offtarget.fasta` - Off-target species template

## Quick Start

```bash
cd examples/batch_species_check

# Run batch analysis
primerlab species-check \
  --primers-dir primers/ \
  --target target.fasta \
  --offtargets offtarget.fasta \
  --parallel 2 \
  --output results/
```

## Expected Output

```
📦 Batch Species Specificity Check (v0.4.3)
==================================================
📂 Loading primers from directory: primers/
   Found 2 primer files

⏳ Processing 2 files in parallel (2 threads)...

==================================================
📊 Batch Analysis Complete
   Total Files: 2
   Passed: 2 (100%)
   Failed: 0 (0%)
   Avg Score: 95.0

📁 Reports saved to: results/
   • batch_summary.csv
   • gene1_primers.json
   • gene2_primers.json
```

## Python API

```python
from primerlab.api import batch_species_check_api

result = batch_species_check_api(
    primer_dir="primers/",
    target_name="Human",
    target_template=open("target.fasta").read(),
    max_workers=2
)

print(f"Pass rate: {result['pass_rate']}%")
```

## See Also

- [Batch Tutorial](../../docs/tutorials/batch-species-check.md)
- [Species Check Example](../species_check/)
