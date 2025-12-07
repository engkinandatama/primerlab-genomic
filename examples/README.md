# PrimerLab Examples

This directory contains example configuration files for various PrimerLab workflows.

## Usage

Run any example using the `primerlab run` command:

```bash
# Standard PCR
primerlab run pcr --config examples/pcr_standard.yaml

# Long-Range PCR (using presets)
primerlab run pcr --config examples/pcr_long_range.yaml

# qPCR (TaqMan Probe)
primerlab run qpcr --config examples/qpcr_taqman.yaml

# qPCR (SYBR Green)
primerlab run qpcr --config examples/qpcr_sybr.yaml
```

## Batch Processing

Generate multiple configs from a CSV file:

```bash
# Generate configs from CSV
primerlab batch-generate --input examples/batch_sequences.csv --output ./configs

# Run each generated config
primerlab run pcr --config configs/GAPDH.yaml
```

## Available Examples

| File | Workflow | Description |
|------|----------|-------------|
| `pcr_standard.yaml` | PCR | Basic primer design for ~400bp amplicon |
| `pcr_long_range.yaml` | PCR | Demonstrates `preset: long_range` for >1kb amplicons |
| `qpcr_taqman.yaml` | qPCR | Design primers + probe for TaqMan assays |
| `qpcr_sybr.yaml` | qPCR | Design primers only (no probe) for SYBR Green |
| `batch_sequences.csv` | Batch | Example CSV for batch config generation |
