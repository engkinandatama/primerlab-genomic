# Advanced Workflows

Specialized primer design techniques.

## Nested PCR

Two-round PCR for increased specificity.

### Configuration

```yaml
# outer_primers.yaml
input:
  sequence_path: ./target.fasta

parameters:
  tm:
    opt: 58.0
  product_size:
    min: 400
    max: 600

nested:
  enabled: true
  inner_product_size:
    min: 150
    max: 250
  inner_tm_opt: 60.0
```

### Run Design

```bash
primerlab run pcr --config nested_config.yaml --nested
```

### Output

```
Outer Primers (First Round)
  Forward: ATGCGATCGATCGATCG (Tm: 58.2°C)
  Reverse: GCTAGCTAGCTAGCTAG (Tm: 58.0°C)
  Product: 520 bp

Inner Primers (Second Round)
  Forward: TCGATCGATCGATCGAT (Tm: 60.1°C)
  Reverse: AGCTAGCTAGCTAGCTA (Tm: 60.3°C)
  Product: 185 bp
```

---

## Semi-Nested PCR

Use one outer primer with one new inner primer:

```yaml
nested:
  mode: semi  # or "full" for fully nested
```

---

## Multiplex PCR

Design primers for multiple targets in one reaction.

### Check Cross-Reactivity

```bash
# Design individual primer pairs first
primerlab run pcr -c target1.yaml -o target1/
primerlab run pcr -c target2.yaml -o target2/
primerlab run pcr -c target3.yaml -o target3/

# Check compatibility across all pairs
primerlab check-compat \
  -p target1/primers.json \
  -p target2/primers.json \
  -p target3/primers.json \
  --multiplex
```

### Tm Matching

Ensure all primers have similar Tm (within 2°C) for multiplex:

```yaml
parameters:
  tm:
    min: 59.0
    opt: 60.0
    max: 61.0  # Narrow range for multiplex
```

---

## Species Specificity

Design primers specific to target organism.

### Use Case

- Pathogen detection (e.g., detect Salmonella, not human DNA)
- GMO testing
- Environmental monitoring

### Configuration

```yaml
specificity:
  target_database: ./salmonella_genome.fasta
  background_database: ./human_genome.fasta
  min_specificity_score: 90
```

### Run with Species Check

```bash
primerlab run pcr -c config.yaml --species-check
```

### Standalone Species Check

```bash
primerlab species-check \
  -p primers.json \
  --target-db salmonella.fasta \
  --background-db human.fasta
```

---

## Allele-Specific PCR (AS-PCR)

Design primers for SNP genotyping.

### Principle

3' end of primer overlaps SNP position. Only perfect match amplifies.

### Configuration

```yaml
genotyping:
  enabled: true
  snp_position: 150  # Position in sequence
  alleles: ["A", "G"]  # Wild-type and variant
```

### Output

Generates separate primer pairs for each allele:

- `primers_allele_A.json` — Amplifies wild-type
- `primers_allele_G.json` — Amplifies variant

---

## Degenerate Primers

For conserved regions across related sequences.

### Input

Provide alignment with IUPAC ambiguity codes:

```fasta
>consensus
ATGRYSWKMBDHVN...
```

Where:

- R = A or G
- Y = C or T
- S = G or C
- etc.

PrimerLab will minimize degeneracy while maintaining coverage.

---

## Long-Range PCR

Amplify fragments >3 kb.

### Recommendations

```yaml
parameters:
  tm:
    opt: 65.0      # Higher Tm
  primer_size:
    opt: 25        # Longer primers
    max: 30
  product_size:
    min: 3000
    max: 10000
```

### Tips

- Use proofreading polymerase
- Longer extension time
- Higher primer Tm for stability

---

## See Also

- [PCR Design](pcr-design.md) — Standard workflow
- [qPCR Design](qpcr-design.md) — Probe design
- [Configuration Reference](../reference/config.md) — All options
