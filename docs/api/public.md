# Public API

Main entry points for programmatic primer design.

## Module

```python
from primerlab.api import design_pcr_primers, design_qpcr_assays
```

---

## design_pcr_primers()

Design PCR primers for a DNA sequence.

### Signature

```python
def design_pcr_primers(
    sequence: str = None,
    sequence_path: Path = None,
    tm_range: tuple = (58, 62),
    product_size: tuple = (200, 600),
    gc_range: tuple = (40, 60),
    primer_size: tuple = (18, 20, 24),  # min, opt, max
    output_dir: str = "output",
    config_path: Path = None,
    qc_mode: str = "standard"
) -> WorkflowResult
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sequence` | str | None | DNA sequence (A/T/C/G). Either this or `sequence_path` required |
| `sequence_path` | Path | None | Path to FASTA file |
| `tm_range` | tuple | (58, 62) | (min, max) melting temperature °C |
| `product_size` | tuple | (200, 600) | (min, max) amplicon size bp |
| `gc_range` | tuple | (40, 60) | (min, max) GC percentage |
| `primer_size` | tuple | (18, 20, 24) | (min, opt, max) primer length |
| `output_dir` | str | "output" | Output directory path |
| `config_path` | Path | None | Optional YAML config override |
| `qc_mode` | str | "standard" | QC stringency: relaxed/standard/strict |

### Returns

`WorkflowResult` containing:

- `primers`: List of designed primer pairs
- `scores`: QC scores for each pair
- `report_path`: Path to generated report
- `success`: Boolean indicating completion

### Example: Basic Usage

```python
from primerlab.api import design_pcr_primers

# Design primers for GFP sequence
result = design_pcr_primers(
    sequence="ATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGGTGCCC...",
    tm_range=(58, 62),
    product_size=(200, 500),
    output_dir="gfp_primers/"
)

# Check result
if result.success:
    print(f"Designed {len(result.primers)} primer pairs")
    for pair in result.primers[:3]:
        print(f"  Fwd: {pair.forward.sequence}")
        print(f"  Rev: {pair.reverse.sequence}")
        print(f"  Amplicon: {pair.amplicon_size} bp")
```

### Example: From FASTA File

```python
from primerlab.api import design_pcr_primers
from pathlib import Path

result = design_pcr_primers(
    sequence_path=Path("my_gene.fasta"),
    tm_range=(60, 65),
    qc_mode="strict",
    output_dir="strict_output/"
)
```

### Example: Custom Config

```python
from primerlab.api import design_pcr_primers

result = design_pcr_primers(
    sequence="ATGAGTAAAGGAGAAGAACTTTTC...",
    config_path=Path("custom_config.yaml")  # Override defaults
)
```

---

## design_qpcr_assays()

Design qPCR primers and probes (TaqMan or SYBR).

### Signature

```python
def design_qpcr_assays(
    sequence: str = None,
    sequence_path: Path = None,
    mode: str = "taqman",  # or "sybr"
    tm_range: tuple = (58, 62),
    probe_tm_range: tuple = (68, 72),
    product_size: tuple = (70, 150),
    output_dir: str = "output",
    qc_mode: str = "strict"
) -> WorkflowResult
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | str | "taqman" | Assay type: "taqman" or "sybr" |
| `probe_tm_range` | tuple | (68, 72) | Probe Tm range (TaqMan only) |
| `product_size` | tuple | (70, 150) | Shorter amplicons for qPCR |

### Example: TaqMan Assay

```python
from primerlab.api import design_qpcr_assays

result = design_qpcr_assays(
    sequence="ATGGTGAGCAAGGGCGAGGAG...",
    mode="taqman",
    product_size=(80, 120),
    output_dir="qpcr_taqman/"
)

if result.success:
    assay = result.primers[0]
    print(f"Fwd: {assay.forward.sequence}")
    print(f"Rev: {assay.reverse.sequence}")
    print(f"Probe: {assay.probe.sequence}")
```

### Example: SYBR Green

```python
result = design_qpcr_assays(
    sequence_path=Path("target.fasta"),
    mode="sybr",  # No probe needed
    output_dir="qpcr_sybr/"
)
```

---

## Error Handling

```python
from primerlab.api import design_pcr_primers
from primerlab.core.exceptions import PrimerLabException

try:
    result = design_pcr_primers(
        sequence="ATGC...",
        tm_range=(58, 62)
    )
except PrimerLabException as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
```

---

## See Also

- [In-silico API](insilico.md)
- [Report API](report.md)
- [Models Reference](models.md)
