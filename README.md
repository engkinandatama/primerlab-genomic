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
Download the release files (`.whl` or `.tar.gz`) from the [GitHub Releases page](https://github.com/engkinandatama/primerlab-genomic/releases), then:

**Using the Wheel (.whl) - Recommended:**
```bash
# Navigate to the directory where you downloaded the file, or use the full path
cd ~/Downloads  # Example: where browser downloads files

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

Once installed, you can run PrimerLab from anywhere:
```bash
primerlab --version
```

---

## 🔧 Usage

### Command-Line Interface (CLI)

**PCR Workflow:**
```bash
primerlab run pcr --config test_pcr.yaml
```

**qPCR Workflow:**
```bash
primerlab run qpcr --config test_qpcr.yaml
```

### Programmatic API (Python)

For integration into your own Python scripts:

```python
from primerlab.api.public import design_pcr_primers, design_qpcr_assays

# PCR primer design
sequence = "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGT..."
result = design_pcr_primers(sequence)

print(f"Forward: {result.primers['forward'].sequence}")
print(f"Reverse: {result.primers['reverse'].sequence}")
print(f"Amplicon: {result.amplicons[0].length} bp")

# qPCR assay design (with custom parameters)
config = {
    "parameters": {
        "product_size_range": [[70, 200]],
        "probe": {"tm": {"min": 68.0, "opt": 70.0, "max": 72.0}}
    }
}
result = design_qpcr_assays(sequence, config)

print(f"Probe: {result.primers['probe'].sequence}")
print(f"Efficiency: {result.efficiency}%")
```

---

## 📖 Documentation

Full documentation is available in the [`Docs/`](Docs/) directory:

* **[Project Overview](Docs/High-Level%20Documentation/project-overview.md)** — Vision, scope, and future development
* **[Development Rules](Docs/Development%20Rules/rules-development.md)** — Architecture constraints and coding standards
* **[System Architecture](Docs/Manual%20Plan/)** — Workflow structure, data flow, and roadmap
* **[WSL Quickstart](Docs/Guide/wsl_quickstart.md)** — Setup guide for Windows environments
* **[CHANGELOG](CHANGELOG.md)** — Version history and release notes

---

## 🧪 Example Configurations

### PCR Configuration (`test_pcr.yaml`)

```yaml
workflow: pcr

input:
  sequence: "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGT..."  # Or use sequence_path: "input.fasta"

parameters:
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 58.0, opt: 60.0, max: 62.0}
  product_size: {min: 200, opt: 400, max: 600}  # New in v0.1.1: Simple min/opt/max

output:
  directory: "test_output"
```

### qPCR Configuration (TaqMan - Default)

```yaml
workflow: qpcr
# mode: taqman (default)

input:
  sequence: "ATGGGGAAGGTGAAGGTCGGAGT..."

parameters:
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 55.0, opt: 60.0, max: 65.0}
  
  probe:
    size: {min: 18, opt: 24, max: 30}
    tm: {min: 68.0, opt: 70.0, max: 72.0}

output:
  directory: "test_output"
```

### qPCR Configuration (SYBR Green)

```yaml
workflow: qpcr

parameters:
  mode: sybr  # New in v0.1.1: Disables probe design automatically
  
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 58.0, opt: 60.0, max: 62.0}
  product_size: {min: 70, opt: 100, max: 150}

output:
  directory: "test_output_sybr"
```

Sample config files are included in the repository root for immediate testing.

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
➡️ Open an issue on GitHub:
[Github Issues](https://github.com/engkinandatama/primerlab-genomic/issues)

