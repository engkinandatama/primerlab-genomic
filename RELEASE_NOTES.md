# v0.6.2 - Advanced Features & Complete Documentation

**Release Date:** 2026-01-01

## ✨ Highlights

This release brings **advanced qPCR and molecular biology features** along with comprehensive documentation update.

- 🧬 Allele Discrimination / SNP Genotyping
- 🔬 RT-qPCR Exon Junction Detection
- 📊 Melt Curve SVG/PNG Visualization
- 🖥️ New CLI Commands: `probe-check`, `melt-curve`, `amplicon-qc`
- ✅ 613 tests passing

---

## 🆕 New in v0.6.x

### v0.6.2 - Final Polish

- CLI tests for new qPCR commands
- Comprehensive README update
- Documentation indices update

### v0.6.1 - Documentation & Integration

- CLI documentation for 3 new commands
- API documentation update
- `--plot-melt` option for run command

### v0.6.0 - Advanced Features

- **Allele Discrimination** (`core/genotyping/`)
  - SNP genotyping primer scoring
  - 3' end position analysis
  - Mismatch Tm calculation

- **RT-qPCR Validation** (`core/rtpcr/`)
  - Exon junction detection
  - gDNA contamination risk assessment

- **Melt Curve Visualization** (`core/qpcr/melt_plot.py`)
  - SVG melt curve generation
  - PNG export with matplotlib
  - Multi-peak annotation

- **New CLI Commands**
  - `primerlab probe-check` - TaqMan probe binding
  - `primerlab melt-curve` - SYBR melt curve
  - `primerlab amplicon-qc` - Amplicon quality

---

## 📦 Installation

```bash
pip install git+https://github.com/engkinandatama/primerlab-genomic.git@v0.6.2
```

Or upgrade:

```bash
pip install --upgrade git+https://github.com/engkinandatama/primerlab-genomic.git@v0.6.2
```

---

## 📊 Test Coverage

- **613 tests passing**
- Python 3.10, 3.11, 3.12 supported
- CI/CD via GitHub Actions

---

## 📚 Documentation

- [Getting Started](docs/getting-started.md)
- [CLI Reference](docs/cli/README.md) - 19 commands
- [API Reference](docs/api/README.md) - 10+ functions
- [Features](docs/features/README.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 🔗 Links

- **Full Changelog:** [v0.5.0...v0.6.2](https://github.com/engkinandatama/primerlab-genomic/compare/v0.5.0...v0.6.2)
- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/engkinandatama/primerlab-genomic/issues)
