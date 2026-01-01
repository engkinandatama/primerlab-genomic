# API Reference

Programmatic interface for PrimerLab.

## Modules

| Module | Description |
|--------|-------------|
| [Public API](public.md) | Main entry points: `design_pcr_primers()`, `design_qpcr_assays()` |
| [In-silico API](insilico.md) | Virtual PCR: `run_insilico_pcr()`, binding analysis |
| [Report API](report.md) | Report generation and export |
| [Models](models.md) | Data classes: `Primer`, `PrimerPair`, `BlastResult`, etc. |

## v0.6.x API Functions

| Function | Description |
|----------|-------------|
| `score_genotyping_primer_api()` | SNP genotyping primer scoring |
| `validate_rtpcr_primers_api()` | RT-qPCR exon junction validation |

## v0.5.0 API Functions

| Function | Description |
|----------|-------------|
| `simulate_probe_binding_api()` | TaqMan probe binding simulation |
| `predict_melt_curve_api()` | SYBR melt curve prediction |
| `validate_qpcr_amplicon_api()` | qPCR amplicon validation |

## Quick Start

```python
from primerlab.api import design_pcr_primers

result = design_pcr_primers(
    sequence="ATGAGTAAAGGAGAAGAACTTTTC...",
    tm_range=(58, 62),
    output_dir="output/"
)

for pair in result.primers[:3]:
    print(f"Fwd: {pair.forward.sequence}")
    print(f"Rev: {pair.reverse.sequence}")
```

## Import Patterns

```python
# Public API
from primerlab.api import design_pcr_primers, design_qpcr_assays

# v0.6.x API
from primerlab.api import score_genotyping_primer_api, validate_rtpcr_primers_api

# v0.5.x API
from primerlab.api import simulate_probe_binding_api, predict_melt_curve_api

# In-silico
from primerlab.core.insilico import run_insilico_pcr, analyze_binding

# Report
from primerlab.core.report import ReportGenerator, ReportExporter

# Models
from primerlab.core.models import Primer, PrimerPair
```

## See Also

- [CLI Reference](../cli/README.md) - Command-line usage
- [Configuration](../configuration/README.md) - YAML config reference
