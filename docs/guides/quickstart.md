# Quick Start

Design your first PCR primers in 5 minutes.

## Step 1: Verify Installation

```bash
primerlab health
```

You should see:

```
✅ Primer3 core found
✅ Python 3.10+
⚠️ BLAST+ not found (optional)
⚠️ ViennaRNA not found (optional)
```

> **Note:** BLAST+ and ViennaRNA are optional. You can still design primers without them.

---

## Step 2: Create Configuration

Create a file called `my_first_design.yaml`:

```yaml
# my_first_design.yaml
input:
  sequence: >
    ATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGGTGCCCATCCTGGTCGAGCTGGAC
    GGCGACGTAAACGGCCACAAGTTCAGCGTGTCCGGCGAGGGCGAGGGCGATGCCACCTAC
    GGCAAGCTGACCCTGAAGTTCATCTGCACCACCGGCAAGCTGCCCGTGCCCTGGCCCACC
    CTCGTGACCACCCTGACCTACGGCGTGCAGTGCTTCAGCCGCTACCCCGACCACATGAAG
    CAGCACGACTTCTTCAAGTCCGCCATGCCCGAAGGCTACGTCCAGGAGCGCACCATCTTC
    TTCAAGGACGACGGCAACTACAAGACCCGCGCCGAGGTGAAGTTCGAGGGCGACACCCTG
    GTGAACCGCATCGAGCTGAAGGGCATCGACTTCAAGGAGGACGGCAACATCCTGGGGCAC

parameters:
  tm:
    opt: 60.0
  product_size:
    min: 150
    max: 300
```

---

## Step 3: Run Design

```bash
primerlab run pcr --config my_first_design.yaml
```

Expected output:

```
🧬 PrimerLab PCR Design
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 5 primer pairs designed

Pair 1 (Score: 92.5)
  Forward: ATGGTGAGCAAGGGCGAGGAG (Tm: 60.2°C)
  Reverse: CCCAGGCATCCTTGAAGAA (Tm: 59.8°C)
  Product: 245 bp

📁 Output: primerlab_output/
```

---

## Step 4: Review Results

Check the output directory:

```bash
ls primerlab_output/
```

Files generated:

- `primers.json` — Machine-readable results
- `report.md` — Human-readable report
- `primers_idt.csv` — Ready for IDT ordering

---

## Next Steps

- [Full PCR Tutorial](pcr-design) — Learn all PCR options
- [qPCR Design](qpcr-design) — Design TaqMan probes
- [CLI Reference](/docs/reference/cli) — All command options

---

## Common Issues

**"Primer3 not found"**

```bash
# Install via conda
conda install -c bioconda primer3

# Or build from source
# See: https://github.com/primer3-org/primer3
```

**"No primers found"**

- Your sequence may be too short (min ~100 bp recommended)
- Try relaxing constraints (lower min Tm, larger product range)
