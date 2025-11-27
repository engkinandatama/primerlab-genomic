# 🧬 PrimerLab

**A modular, AI-friendly bioinformatics framework for automated primer and probe design.**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-v0.1.0-orange.svg)]()

---

## 📋 Overview

PrimerLab is a Python-based toolkit designed to automate primer design, validation, and analysis for molecular biology workflows. Built with clean architecture and strict modularity, it supports:

- **PCR** - Standard primer design with comprehensive QC
- **qPCR** - Probe design with efficiency estimation
- **Future**: CRISPR, Cloning, Mutagenesis, and more

### Key Features

✅ **End-to-End Automation** - Sequence input → Primer design → QC → Report generation  
✅ **Scientific Accuracy** - ViennaRNA integration for secondary structure prediction  
✅ **Robust QC** - Hairpin, dimer, Tm validation with configurable thresholds  
✅ **qPCR Support** - TaqMan probe design with efficiency estimation  
✅ **Timeout Protection** - Prevents hanging on difficult sequences  
✅ **Structured Output** - JSON + Markdown reports with detailed metrics  

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic

# Create virtual environment (recommended in home directory for WSL users)
python3 -m venv ~/primerlab_venv
source ~/primerlab_venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install PrimerLab in editable mode
pip install -e .
```

### Basic Usage

#### PCR Workflow
```bash
python3 -m primerlab.cli.main run pcr --config test_pcr.yaml
```

#### qPCR Workflow
```bash
python3 -m primerlab.cli.main run qpcr --config test_qpcr.yaml
```

---

## 📖 Documentation

Comprehensive documentation is available in the [`Docs/`](Docs/) directory:

- **[Project Overview](Docs/High-Level%20Documentation/project-overview.md)** - Vision and goals
- **[Development Rules](Docs/Development%20Rules/rules-development.md)** - Coding standards
- **[Architecture](Docs/High-Level%20Documentation/architecture.md)** - System design
- **[WSL Quickstart](Docs/Guide/wsl_quickstart.md)** - Setup guide for Windows users

---

## 🧪 Example Configuration

### qPCR Configuration
```yaml
workflow: qpcr

input:
  sequence: "ATGGGGAAGGTGAAGGTCGGAGT..."  # Your target sequence

parameters:
  primer_size:
    min: 18
    opt: 20
    max: 24
  
  tm:
    min: 58.0
    opt: 60.0
    max: 62.0

  probe:
    tm:
      min: 68.0  # Probe Tm should be 8-10°C higher than primers
      opt: 70.0
      max: 72.0

output:
  directory: "output"
```

---

## 📊 Output Example

PrimerLab generates structured reports with:

- **Primers & Probe** - Sequences, Tm, GC%, positions
- **qPCR Metrics** - Estimated efficiency (e.g., 98.0%)
- **Amplicon Details** - Size, suitability for qPCR
- **Quality Control** - Hairpin, dimer, Tm balance checks
- **Warnings** - Specific QC flags for optimization

Example report: [`report.md`](test_qpcr_out/20251127_163137_QPCR/report.md)

---

## 🏗️ Project Structure

```
primerlab-genomic/
├── primerlab/
│   ├── cli/              # Command-line interface
│   ├── core/             # Reusable utilities (sequence, QC, tools)
│   │   ├── tools/        # Primer3, ViennaRNA wrappers
│   │   └── models/       # Data models
│   ├── workflows/        # Workflow modules
│   │   ├── pcr/          # PCR workflow
│   │   └── qpcr/         # qPCR workflow
│   └── config/           # Default configurations
├── Docs/                 # Comprehensive documentation
│   ├── Development Rules/
│   ├── High-Level Documentation/
│   └── Manual Plan/
└── tests/                # (Future) Test suite
```

**Architecture**: Clean 3-layer design (`CLI → Workflows → Core`)

---

## 🎯 Development Status

### ✅ Short-Term Milestones (Complete)

- **v0.1** - Core foundation (config, logging, output system)
- **v0.2** - PCR basic workflow (Primer3 integration)
- **v0.3** - QC extended (ViennaRNA, secondary structure)
- **v0.4** - qPCR workflow (probe design, efficiency estimation)

### 🔜 Upcoming (Mid-Term)

- CRISPR guide design
- Multiplex PCR support
- Docker environment
- Enhanced thermodynamic models

---

## 🛠️ Requirements

- **Python** 3.10+
- **Primer3** (via `primer3-py` package)
- **ViennaRNA** (for secondary structure prediction)
- **WSL** (recommended for Windows users)

---

## 🤝 Contributing

PrimerLab follows strict development guidelines to ensure:
- Clean architecture (no cross-layer imports)
- Consistent naming conventions
- Comprehensive error handling
- Deterministic outputs

See [Development Rules](Docs/Development%20Rules/rules-development.md) for details.

---

## 📄 License

This project is licensed under the **BSD 3-Clause License** - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025–present, Engki Nandatama

---

## 🙏 Acknowledgments

- **Primer3** - Primer design engine
- **ViennaRNA** - RNA secondary structure prediction

---

## 📬 Contact

For questions, issues, or suggestions:
- Open an issue on [GitHub](https://github.com/engkinandatama/primerlab-genomic/issues)

---

**Built with ❤️ for the bioinformatics community**
