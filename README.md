# 🧬 PrimerLab Genomic

A modular bioinformatics framework for automated **primer and probe design**, built with clean architecture and reproducible workflows.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-green.svg)](LICENSE)
[![Tests](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml/badge.svg)](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml)
[![Status](https://img.shields.io/badge/status-v0.1.0-orange.svg)]()

> 🔰 **Latest Release**: **v0.1.0 Technical Preview** is now available! 🎉  
> Download the [latest release](https://github.com/engkinandatama/primerlab-genomic/releases/tag/v0.1.0) or check out the [CHANGELOG](CHANGELOG.md) for details.

---

## 📋 Overview

**PrimerLab Genomic** is a Python-based toolkit for automated primer and probe design in molecular biology workflows.
It provides a structured and reproducible framework for:

* **PCR** — Standard primer design with quality control
* **qPCR** — Probe design with thermodynamic checks
* **(Future)** CRISPR guides, mutagenesis primers, cloning primers, and multiplex workflows

PrimerLab focuses on **deterministic, transparent bioinformatics**, following strict modularity and best practices.

### 🔑 Key Features

* **End-to-End Workflow**: Sequence input → Primer/Probe design → QC → Report
* **Thermodynamic Validation**: Secondary structure prediction via ViennaRNA
* **QC Framework**: Hairpins, dimers, GC%, Tm ranges, amplicon checks
* **qPCR Support**: TaqMan-style probe design with efficiency estimation
* **Safe Execution**: Timeout protection for complex sequences
* **Structured Output**: JSON + Markdown reports with interpretable metrics

---

## 🚀 Quick Start

### Installation

#### Option 1: For Developers (Source)
```bash
# Clone the repository
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic

# Create virtual environment (recommended)
python3 -m venv ~/primerlab_venv
source ~/primerlab_venv/bin/activate  # Linux/WSL
# or
# .\primerlab_venv\Scripts\activate   # Windows PowerShell

# Install dependencies & package in editable mode
pip install -e .
```

#### Option 2: For End Users (Using Release Files)
If you downloaded the release files (`.whl` or `.tar.gz`) from GitHub:

**Using the Wheel (.whl) - Recommended:**
```bash
# Create a virtual environment first
python3 -m venv ~/primerlab_venv
source ~/primerlab_venv/bin/activate

# Install directly from the file
pip install primerlab_genomic-0.1.0-py3-none-any.whl
```

**Using the Source Tarball (.tar.gz):**
```bash
pip install primerlab_genomic-0.1.0.tar.gz
```

Once installed, you can run PrimerLab from anywhere in your terminal:
```bash
primerlab --version
primerlab run pcr --config my_config.yaml
```

---

## 🔧 Basic Usage

### PCR Workflow

```bash
python3 -m primerlab.cli.main run pcr --config test_pcr.yaml
```

### qPCR Workflow

```bash
python3 -m primerlab.cli.main run qpcr --config test_qpcr.yaml
```

---

## 📖 Documentation

Full documentation is available in the [`Docs/`](Docs/) directory:

* **Project Overview** — Vision, scope, and future development
* **Development Rules** — Architecture constraints and coding standards
* **System Architecture** — Workflow structure and data flow
* **WSL Quickstart** — Setup guide for Windows environments

---

## 🧪 Example Configuration (qPCR)

```yaml
workflow: qpcr

input:
  sequence: "ATGGGGAAGGTGAAGGTCGGAGT..."

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
      min: 68.0
      opt: 70.0
      max: 72.0

output:
  directory: "output"
```

---

## 📊 Output Overview

PrimerLab generates a structured report containing:

* **Primer & Probe Details** — Sequences, GC%, Tm, positions
* **qPCR Metrics** — Estimated amplification efficiency
* **Amplicon Properties** — Length, GC%, suitability
* **QC Checks** — Dimers, hairpins, Tm balance
* **Warnings** — Optimization suggestions

Run a workflow to generate your own report!

---

## 🏗️ Project Structure

```
primerlab-genomic/
├── primerlab/
│   ├── cli/              # Command-line interface
│   ├── core/             # Reusable utilities (sequence, QC, tools)
│   │   ├── tools/        # Primer3, ViennaRNA wrappers
│   │   └── models/       # Data models and schema
│   ├── workflows/        # Workflow modules
│   │   ├── pcr/          # PCR workflow implementation
│   │   └── qpcr/         # qPCR workflow implementation
│   └── config/           # Default configurations
├── Docs/                 # High-level documentation
```

### 📌 Development Status

#### ✅ **v0.1.0 Technical Preview** (Released)
The current release includes:
* Core foundation (configuration, logging, output system)
* PCR workflow with Primer3 integration
* Extended QC (secondary structure, hairpin/dimer validation via ViennaRNA)
* qPCR workflow (TaqMan probe design + efficiency estimation)
* Public API (`design_pcr_primers`, `design_qpcr_assays`)
* Automated testing suite (pytest)
* CI/CD pipeline (GitHub Actions)

#### � **Upcoming Milestones**

* **v0.5** — CRISPR guide design (PAM finding, off-target filtering)
* **v0.6** — Multiplex PCR support
* **v0.7** — Genome-aware off-target search
* **v0.8** — Advanced thermodynamic modeling
* **v1.0** — Production-ready release with full documentation

---

## 🛠️ Requirements

* **Python 3.10+**
* **Primer3** (`primer3-py`)
* **ViennaRNA** for structure prediction
* **WSL recommended for Windows**

---

## 🤝 Contributing

PrimerLab follows strict architecture guidelines:

* No cross-layer imports
* Consistent naming conventions
* Explicit error handling
* Deterministic, reproducible outputs

See:
📄 [`rules-development.md`](Docs/Development%20Rules/rules-development.md)

---

## 📄 License

This project is licensed under the **BSD 3-Clause License**.
See the [LICENSE](LICENSE) file for details.

© 2025–present — **Engki Nandatama**

---

## 🙏 Acknowledgments

* **Primer3** — Primary primer design engine
* **ViennaRNA** — Thermodynamic folding & secondary structure analysis

---

## 📬 Contact

For issues, suggestions, or contributions:
➡️ Open an issue on GitHub:
[Github Issues](https://github.com/engkinandatama/primerlab-genomic/issues)

---

### **Built with scientific care for the molecular biology community.** 🧪💻

---

