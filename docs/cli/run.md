# primerlab run

Run a primer design workflow.

## Synopsis

```bash
primerlab run <workflow> [options]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `workflow` | Yes | Workflow type: `pcr`, `qpcr`, or `crispr` |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Path to configuration YAML file |
| `--out` | `-o` | Override output directory |
| `--debug` | | Enable debug logging |
| `--dry-run` | | Validate config without running |
| `--export` | `-e` | Export formats (comma-separated) |
| `--mask` | `-m` | Region masking mode |
| `--quiet` | `-q` | Suppress warnings (v0.1.6) |

## Examples

### Basic PCR Design

```bash
primerlab run pcr --config my_pcr.yaml
```

### qPCR with TaqMan Probe

```bash
primerlab run qpcr --config my_qpcr.yaml
```

### With Masking

```bash
# Auto-detect lowercase and N-masked regions
primerlab run pcr --config my_pcr.yaml --mask auto
```

### Export to Multiple Formats

```bash
primerlab run pcr --config my_pcr.yaml --export idt,benchling
```

### Quiet Mode (v0.1.6)

```bash
# Suppress warnings for scripted pipelines
primerlab run pcr --config my_pcr.yaml --quiet
```

### Dry Run

```bash
# Validate config without running
primerlab run pcr --config my_pcr.yaml --dry-run
```

## Mask Modes

| Mode | Description |
|------|-------------|
| `auto` | Detect both lowercase and N-masked regions |
| `lowercase` | Only detect lowercase (RepeatMasker) regions |
| `n` | Only detect N-masked regions |
| `none` | No masking (default) |

## Export Formats

| Format | Description |
|--------|-------------|
| `idt` | IDT ordering format |
| `sigma` | Sigma-Aldrich format |
| `thermo` | Thermo Fisher format |
| `benchling` | Benchling CSV import |
| `xlsx` | Excel spreadsheet |
