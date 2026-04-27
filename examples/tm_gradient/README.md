# Tm Gradient Example

This example demonstrates how to use Tm gradient simulation to find optimal annealing temperatures.

## Files

- `primers.json` - Sample primers for simulation

## Quick Start

### 1. Run Simulation

```bash
cd examples/tm_gradient
primerlab tm-gradient --primers primers.json --output results/
```

### 2. View Results

```bash
cat results/tm_gradient.json
```

### 3. With Custom Range

```bash
# For high-GC primers
primerlab tm-gradient --primers primers.json --min-temp 55 --max-temp 75 --step 0.5
```

## Expected Output

```
🌡️ Tm Gradient Simulation (v0.4.3)
==================================================
📂 Loading primers: primers.json
🔬 Temperature range: 50.0°C - 72.0°C (step 0.5°C)

⏳ Simulating Tm gradient for 3 primers...

==================================================
🎯 Optimal Annealing Temperature: 58.2°C
   Recommended Range: 54.5°C - 62.0°C

📊 Per-Primer Results:
   BRCA1_Exon10_fwd: Tm=62.3°C, Optimal=57.3°C (Grade A)
   BRCA1_Exon10_rev: Tm=60.8°C, Optimal=55.8°C (Grade A)
   TP53_Exon5_fwd: Tm=61.5°C, Optimal=56.5°C (Grade A)
   TP53_Exon5_rev: Tm=58.2°C, Optimal=53.2°C (Grade B)
   KRAS_Exon2_fwd: Tm=59.7°C, Optimal=54.7°C (Grade A)
   KRAS_Exon2_rev: Tm=60.1°C, Optimal=55.1°C (Grade A)

📁 Report saved to: results/tm_gradient.json
```

## JSON Output Structure

```json
{
  "config": {
    "min_temp": 50.0,
    "max_temp": 72.0,
    "step_size": 0.5
  },
  "optimal": {
    "optimal": 58.2,
    "range_min": 54.5,
    "range_max": 62.0
  },
  "primers": [
    {
      "primer_name": "BRCA1_Exon10_fwd",
      "calculated_tm": 62.3,
      "optimal_annealing_temp": 57.3,
      "grade": "A",
      "data_points": [...]
    }
  ]
}
```

## See Also

- [Feature Documentation](../../docs/features/tm-gradient.md)
- [Tutorial](../../docs/tutorials/tm-gradient.md)
