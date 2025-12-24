# API Reference

Programmatic interface for PrimerLab.

## Public API

The main entry points are in `primerlab.api.public`:

```python
from primerlab.api import design_pcr_primers, design_qpcr_assays
```

### design_pcr_primers()

Design PCR primers for a given sequence.

```python
from primerlab.api import design_pcr_primers

result = design_pcr_primers(
    sequence="ATGAGTAAAGGAGAAGAACTTTTCACTGGAGT...",
    tm_range=(58, 62),
    product_size=(200, 600),
    output_dir="output/"
)

# Returns: WorkflowResult with primers, QC results, and report
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sequence` | str | required | DNA sequence |
| `sequence_path` | Path | None | Alternative: path to FASTA |
| `tm_range` | tuple | (58, 62) | Min/max Tm |
| `product_size` | tuple | (200, 600) | Amplicon size range |
| `output_dir` | str | "output" | Output directory |

---

### design_qpcr_assays()

Design qPCR primers and probes.

```python
from primerlab.api import design_qpcr_assays

result = design_qpcr_assays(
    sequence="ATGAGTAAAGGAGAAGAACTTTTCACTGGAGT...",
    mode="taqman",  # or "sybr"
    output_dir="output/"
)
```

---

## In-silico PCR

```python
from primerlab.core.insilico import run_insilico_pcr

result = run_insilico_pcr(
    forward="ATGGTGAGCAAGGGCGAGGAG",
    reverse="TTACTTGTACAGCTCGTCCATGCC",
    template_path="template.fasta"
)
```

---

## Report Generation

```python
from primerlab.core.report import ReportGenerator, ReportExporter

# Generate report
generator = ReportGenerator()
generator.set_design_data(primers, scores)
report = generator.generate()

# Export
exporter = ReportExporter(report)
exporter.export("report.html", format="html")
```

---

## Models

Key data classes:

| Class | Location | Description |
|-------|----------|-------------|
| `Primer` | `core.models` | Single primer |
| `PrimerPair` | `core.models` | Fwd + Rev pair |
| `Amplicon` | `core.models` | Predicted product |
| `BlastResult` | `core.models.blast` | Off-target result |
| `BindingSite` | `core.insilico` | Binding analysis |

---

## See Also

- [CLI Reference](../cli/README.md)
- [Configuration](../configuration/README.md)
