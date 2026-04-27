# 🧬 PrimerLab v1.1.0 — Thermodynamic Engine Release

**The largest feature update since v1.0.0 — completing the four-phase Thermodynamic Engine initiative.**

This release exposes the full power of Primer3's advanced capabilities through an intuitive YAML configuration
and ergonomic CLI, bringing PrimerLab to feature parity with commercial primer design tools.

---

## What's New in v1.1.0

### 🔬 Advanced Primer3 Task Support
- `check-primers` CLI — validate existing primers against a template (no new design)
- `design-probe` CLI — design TaqMan probe for an existing validated primer pair
- `--pick-only left|right` — design only one side of a primer pair (RACE, extension assays)
- `workflow: sequencing` → Sanger sequencing primer design (`pick_sequencing_primers`)
- `workflow: discriminative` → allele-discriminative primer design

### 🧪 Restriction Cloning Support
- `--add-sites EcoRI,BamHI` adds recognition site overhangs to 5' ends of primers
- 24 built-in enzymes (EcoRI, BamHI, HindIII, NotI, XhoI, NdeI, SalI, ...)
- Correct sense-strand orientation: reverse complement applied automatically to right primer
- GC clamp (GC) added for reliable cutting efficiency

### 🔠 IUPAC & Degenerate Primer Analysis
- Template IUPAC codes now preserved by default (`preserve_iupac: true`)
- `Primer.degeneracy_multiplier` and `Primer.possible_sequences` auto-calculated
- Automatic warning when degeneracy exceeds 256 combinations

### 📚 Library Support for Specificity
- `parameters.mispriming_library` → FASTA file of unwanted sequences (repetitive elements)
- `parameters.probe.mishyb_library_path` → FASTA file for probe mishybridization exclusion
- Path validation with clear error messages (`ERR_P3_LIB_NOT_FOUND`)

### 🔧 Full Thermodynamics Configuration
- `thermodynamics.tm_method` — SantaLucia or Breslauer
- `thermodynamics.salt_corrections` — SantaLucia or Owczarzy
- Salt concentration, dNTP concentration, DNA concentration all configurable
- `qc_method: threshold` (ΔG thresholds) or `qc_method: any` (non-thermodynamic)
- Penalty weight tuning via `parameters.weights.*`

### 🐛 Critical Bug Fixes
- **`UnboundLocalError`** in `run` and `compat-check` CLI commands — caused by Python scoping issue with local imports inside `main()`
- **Windows multiprocessing** — `_run_p3_process` moved to module level to fix `pickle` errors
- **Unicode errors** on Windows cp1252 terminals — emoji characters removed from print statements

---

## Installation

```bash
pip install primerlab-genomic==1.1.0
```

## Quick Start — New Features

```bash
# Check existing primers from literature
primerlab check-primers \
  --forward "ATGCGATCGAT" \
  --reverse "CGTAGCTAGCT" \
  --template sequence.fasta

# Design probe for validated primers
primerlab design-probe \
  --primers results/primers.json \
  --template sequence.fasta

# Cloning primers with EcoRI/BamHI overhangs
primerlab run cloning \
  --config cloning.yaml \
  --add-sites EcoRI,BamHI

# Sanger sequencing primer design
primerlab run sequencing --config seq.yaml

# Design only forward primer (have reverse already)
primerlab run pcr --config pcr.yaml --pick-only left
```

---

## Previous Release: [v1.0.0](CHANGELOG.md#100---2026-01-11---stable-release-)


## Highlights

- ✅ **1286+ passing tests** with comprehensive coverage
- ✅ **Full PCR Workflows**: Standard PCR, qPCR, Nested PCR, Semi-Nested PCR
- ✅ **Complete Analysis Suite**: BLAST off-target, In-silico PCR, Dimer matrix
- ✅ **Multiple Installation Options**: Docker, Conda, Pip
- ✅ **Comprehensive Documentation**: API reference, CLI guide, tutorials

## Installation

### PyPI (Recommended)

```bash
pip install primerlab-genomic
```

### Docker

```bash
docker pull ghcr.io/engkinandatama/primerlab-genomic:1.0.0
docker run ghcr.io/engkinandatama/primerlab-genomic:1.0.0 --version
```

### Conda

```bash
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic
conda env create -f environment.yml
conda activate primerlab
pip install -e .
```

## Quick Start

```bash
# PCR primer design
primerlab run pcr --config your_config.yaml

# qPCR with TaqMan probe
primerlab run qpcr --config qpcr_config.yaml

# Nested PCR
primerlab run nested --config nested_config.yaml
```

## What's New in v1.0.0

### Added

- **Production Status**: Changed from Beta to Production/Stable
- **Report Standardization**: Unified report format across all workflows
- **Documentation**: Complete tutorials, API reference, configuration guide
- **Docker Support**: Multi-stage build with ViennaRNA and BLAST+ included
- **PyPI Publishing**: Automated release via GitHub Actions

### Changed  

- Version bump from 0.9.x to 1.0.0
- Updated all badges and documentation to reflect stable release

## Documentation

- 📚 [Full Documentation](https://engkinandatama.github.io/primerlab-genomic/)
- 🚀 [Getting Started](https://engkinandatama.github.io/primerlab-genomic/getting-started/)
- 📖 [CLI Reference](https://engkinandatama.github.io/primerlab-genomic/cli/README/)
- 🔧 [API Reference](https://engkinandatama.github.io/primerlab-genomic/api/README/)
- 📝 [Tutorials](https://engkinandatama.github.io/primerlab-genomic/tutorials/README/)

## Requirements

- Python 3.10+
- primer3-py >= 2.0.0
- biopython >= 1.80
- Optional: ViennaRNA, BLAST+ (included in Docker)

## Full Changelog

See [CHANGELOG.md](https://github.com/engkinandatama/primerlab-genomic/blob/main/CHANGELOG.md)
