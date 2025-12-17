# PrimerLab Troubleshooting Guide

Common issues and solutions for PrimerLab v0.1.3+.

---

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Primer3 Errors](#primer3-errors)
3. [ViennaRNA Issues](#viennarna-issues)
4. [Configuration Errors](#configuration-errors)
5. [QC Failures](#qc-failures)
6. [Performance Issues](#performance-issues)

---

## Installation Issues

### `ModuleNotFoundError: No module named 'primer3'`

**Cause:** primer3-py not installed.

**Solution:**
```bash
pip install primer3-py
```

**Note:** primer3-py requires C compiler on some systems:
```bash
# Ubuntu/Debian
sudo apt install build-essential

# macOS
xcode-select --install
```

---

### `primerlab: command not found`

**Cause:** Package not installed in editable mode or not in PATH.

**Solution:**
```bash
# Install in editable mode
pip install -e .

# Or install from source
pip install .
```

---

## Primer3 Errors

### `No primers returned` or `0 candidates generated`

**Cause:** Constraints too strict for the input sequence.

**Solutions:**
1. **Relax Tm range:**
   ```yaml
   parameters:
     tm:
       min: 55.0  # Was 58.0
       max: 65.0  # Was 62.0
   ```

2. **Widen product size:**
   ```yaml
   parameters:
     product_size:
       min: 100
       max: 500  # Increase this
   ```

3. **Use relaxed QC mode:**
   ```yaml
   qc:
     mode: relaxed
   ```

---

### Timeout during primer design

**Cause:** Complex sequence or very strict constraints.

**Solutions:**
1. Increase timeout:
   ```yaml
   advanced:
     timeout: 120  # seconds
   ```

2. Reduce number of candidates:
   ```yaml
   advanced:
     num_candidates: 20  # Was 50
   ```

---

## ViennaRNA Issues

### `ViennaRNA not found. Secondary structure QC will be skipped.`

**Cause:** ViennaRNA not installed.

**Solutions:**

```bash
# Ubuntu/Debian
sudo apt install vienna-rna

# macOS
brew install viennarna

# Conda (recommended)
conda install -c bioconda viennarna
```

**Verification:**
```bash
which RNAfold
# Should return path like /usr/bin/RNAfold
```

---

### ViennaRNA installed but not detected

**Cause:** Not in PATH.

**Solution:**
```bash
# Add to PATH temporarily
export PATH=$PATH:/path/to/viennarna/bin

# Or permanently in ~/.bashrc
echo 'export PATH=$PATH:/path/to/viennarna/bin' >> ~/.bashrc
source ~/.bashrc
```

---

## Configuration Errors

### `ERR_CONFIG_003: Missing required config section(s)`

**Required sections:**
- `workflow`
- `input`
- `parameters`
- `output`

**Solution:** Use template:
```bash
primerlab init --workflow pcr --output config.yaml
```

---

### `ERR_CONFIG_009: Invalid Tm range`

**Cause:** min Tm >= max Tm.

**Fix:**
```yaml
parameters:
  tm:
    min: 55.0
    opt: 60.0
    max: 65.0  # Must be > min
```

---

### Wide range warnings

These are **soft warnings**, not errors:
- "Wide Tm range may produce suboptimal primers"
- "Large product size may require specialized long-range PCR conditions"
- "Wide GC range may reduce primer specificity"

**Solution:** Tighten ranges if possible, or ignore if intentional.

---

## QC Failures

### `Weak 3' GC Clamp` (0-1 G/C in last 5 bases)

**Cause:** Primer 3' end lacks stability.

**Impact:** Reduced binding efficiency.

**Solution:** PrimerLab automatically rejects these candidates and tries alternatives.

---

### `Strong GC Clamp Warning` (4-5 G/C in last 5 bases)

**Note:** This is a **warning**, not failure. Primers still selected.

**Impact:** May cause non-specific binding.

---

### Poly-X Run Detected

**Cause:** Consecutive identical bases (e.g., AAAAA).

**Impact:** Primer instability.

**Solution:** Use default QC (max 4 consecutive allowed).

---

### Hairpin/Dimer ΔG too strong

**Cause:** Secondary structure formation.

**Solutions:**
1. Use relaxed mode:
   ```yaml
   qc:
     mode: relaxed  # -12.0 kcal/mol threshold
   ```

2. Or custom thresholds:
   ```yaml
   qc:
     hairpin_dg_max: -12.0
     homodimer_dg_max: -12.0
   ```

---

## Performance Issues

### Slow primer design

**Causes:**
1. Too many candidates requested
2. ViennaRNA overhead
3. Large sequence

**Solutions:**
```yaml
advanced:
  num_candidates: 20  # Reduce from 50
  timeout: 60
```

---

### Memory issues with large sequences

**Solution:** Target specific region:
```yaml
input:
  sequence: path/to/sequence.fasta
  target_region:
    start: 1000
    end: 2000
```

---

## Getting Help

### Run health check:
```bash
primerlab health
```

### Enable debug mode:
```bash
primerlab run pcr --config config.yaml --debug
```

### Check logs:
Debug files are saved in `output_dir/debug/`.

---

## Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| ERR_CONFIG_003 | Missing config section | Use `primerlab init` |
| ERR_CONFIG_009 | Invalid Tm range | Fix min/max values |
| ERR_TOOL_001 | Primer3 not found | Install primer3-py |
| ERR_TOOL_008 | ViennaRNA missing | Install ViennaRNA |
| ERR_SEQ_001 | Invalid sequence | Check for non-ATCG chars |
| ERR_QC_004 | Hairpin too stable | Use relaxed mode |

---

*Last updated: v0.1.3*
