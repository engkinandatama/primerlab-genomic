# 🧬 PrimerLab v1.1.0 — Development Plan: Primer3 Full Coverage

> **Goal**: Wrap semua fungsi Primer3 yang relevan, perbaiki arsitektur QC, dan tambah fitur baru.
> **Estimated Total**: ~40 tasks across 4 phases
> **Branch**: `feat/primer3-full-coverage`

---

## Overview Fase

| Fase | Fokus | Tasks | Priority |
|------|-------|-------|----------|
| **1** | Foundation — ThermocalcWrapper + Salt Config | 8 | 🔴 Critical |
| **2** | QC Migration — ViennaRNA → Primer3 untuk primer | 7 | 🔴 Critical |
| **3** | Parameter Expansion — Expose missing Primer3 params | 12 | 🟡 Important |
| **4** | New Features — TASK variants, mispriming, degenerate | 13 | 🟢 Feature |

---

## FASE 1: Foundation (ThermocalcWrapper + Salt/Buffer Config)

**Goal**: Buat wrapper native Primer3 ThermoAnalysis dan ekspose salt/buffer config ke user.

### Task 1.1 — Create `ThermocalcWrapper` class
- **File**: `primerlab/core/tools/thermocalc_wrapper.py` (NEW)
- **What**: Wrapper class untuk `primer3.thermoanalysis.ThermoAnalysis`
- **Methods**:
  - `calc_tm(seq) → float`
  - `calc_hairpin(seq) → ThermoResult`
  - `calc_homodimer(seq) → ThermoResult`
  - `calc_heterodimer(seq1, seq2) → ThermoResult`
  - `calc_end_stability(seq) → ThermoResult`
- **Constructor params**: `mv_conc, dv_conc, dntp_conc, dna_conc, tm_method, salt_corrections`
- **Tests**: `tests/test_thermocalc_wrapper.py` — 15+ tests
- **Depends on**: Nothing

### Task 1.2 — Create `ThermoResult` dataclass
- **File**: `primerlab/core/tools/thermocalc_wrapper.py`
- **What**: Standardized result from thermo calculations
- **Fields**: `tm, dg, dh, ds, structure_found, ascii_structure`
- **Methods**: `to_dict()`
- **Tests**: Included in 1.1

### Task 1.3 — Add `thermodynamics` section to YAML config schema
- **File**: `primerlab/core/config_loader.py` + `primerlab/core/config_validator.py`
- **What**: Parse and validate new thermodynamics config section
- **Schema**:
  ```yaml
  parameters:
    thermodynamics:
      salt_monovalent: 50.0     # mM Na+, default 50
      salt_divalent: 1.5        # mM Mg²⁺, default 1.5
      dntp_conc: 0.6            # mM, default 0.6
      dna_conc: 50.0            # nM oligo, default 50
      tm_method: santalucia     # santalucia | breslauer
      salt_corrections: santalucia  # santalucia | schildkraut | owczarzy
  ```
- **Tests**: `tests/test_config_thermo.py` — 8 tests
- **Depends on**: Nothing

### Task 1.4 — Pass salt/buffer to `primer3_wrapper.py`
- **File**: `primerlab/core/tools/primer3_wrapper.py`
- **What**: Map thermodynamics config to Primer3 global_args
- **Parameters to add**:
  - `PRIMER_SALT_MONOVALENT`
  - `PRIMER_SALT_DIVALENT`
  - `PRIMER_DNTP_CONC`
  - `PRIMER_DNA_CONC`
  - `PRIMER_TM_FORMULA` (0=Breslauer, 1=SantaLucia)
  - `PRIMER_SALT_CORRECTIONS` (0=Schildkraut, 1=SantaLucia, 2=Owczarzy)
- **Tests**: Update `tests/test_primer3_wrapper.py`
- **Depends on**: 1.3

### Task 1.5 — Pass salt/buffer for probe (Internal Oligo)
- **File**: `primerlab/core/tools/primer3_wrapper.py`
- **What**: Map probe-specific salt params
- **Parameters**: `PRIMER_INTERNAL_SALT_MONOVALENT`, `PRIMER_INTERNAL_SALT_DIVALENT`, etc.
- **Depends on**: 1.4

### Task 1.6 — Add default thermodynamics presets
- **Files**: `primerlab/config/presets/` — update existing presets
- **What**: Add thermodynamics defaults to each preset
  - `standard_pcr`: default salt (50mM Na+, 1.5mM Mg²⁺)
  - `diagnostic_pcr`: clinical buffer (50mM Na+, 2.0mM Mg²⁺)
  - `sybr_qpcr`: SYBR buffer (50mM Na+, 3.0mM Mg²⁺)
  - `taqman_qpcr`: TaqMan buffer (50mM Na+, 4.0mM Mg²⁺)
- **Tests**: Update preset tests
- **Depends on**: 1.3

### Task 1.7 — Update `ThermocalcWrapper` integration with cache.py
- **File**: `primerlab/core/cache.py`
- **What**: `cached_calc_tm()` should use ThermocalcWrapper instead of custom calc
- **Depends on**: 1.1

### Task 1.8 — Documentation: thermodynamics config
- **File**: `docs/reference/config.md` — add thermodynamics section
- **Depends on**: 1.3, 1.4

**Fase 1 Checkpoint**: Run all existing 1286 tests — must pass (backward compatible).

---

## FASE 2: QC Migration (ViennaRNA → Primer3 ThermoAnalysis untuk Primer)

**Goal**: Ganti ViennaRNA di `base_qc.py` dengan Primer3 ThermoAnalysis untuk primer/probe QC. ViennaRNA tetap untuk amplicon.

### Task 2.1 — Refactor `BaseQC.__init__` — dual engine
- **File**: `primerlab/core/qc/base_qc.py`
- **What**: Initialize both ThermocalcWrapper (primer QC) and ViennaWrapper (amplicon QC)
- **Change**:
  ```python
  # BEFORE
  self.vienna = ViennaWrapper()
  
  # AFTER
  self.thermo = ThermocalcWrapper(
      mv_conc=thermo_config.get('salt_monovalent', 50.0),
      dv_conc=thermo_config.get('salt_divalent', 1.5),
      ...
  )
  self.vienna = ViennaWrapper()  # Keep for amplicon analysis
  ```
- **Depends on**: 1.1, 1.3

### Task 2.2 — Migrate `check_hairpin()` → Primer3
- **File**: `primerlab/core/qc/base_qc.py`
- **Change**:
  ```python
  # BEFORE
  fwd_fold = self.vienna.fold(fwd.sequence)
  
  # AFTER  
  fwd_result = self.thermo.calc_hairpin(fwd.sequence)
  fwd_dg = fwd_result.dg
  ```
- **Fallback**: If primer3 ThermoAnalysis not available, fall back to ViennaRNA
- **Tests**: Update `tests/test_qc.py`
- **Depends on**: 2.1

### Task 2.3 — Migrate `check_homodimer()` → Primer3
- **File**: `primerlab/core/qc/base_qc.py`
- **Change**: `self.vienna.cofold(seq, seq)` → `self.thermo.calc_homodimer(seq)`
- **Tests**: Update tests
- **Depends on**: 2.1

### Task 2.4 — Migrate `check_heterodimer()` → Primer3
- **File**: `primerlab/core/qc/base_qc.py`
- **Change**: `self.vienna.cofold(fwd, rev)` → `self.thermo.calc_heterodimer(fwd, rev)`
- **Tests**: Update tests
- **Depends on**: 2.1

### Task 2.5 — Add `check_end_stability()` — NEW
- **File**: `primerlab/core/qc/base_qc.py`
- **What**: New QC check using `calc_end_stability()` — evaluates 3' binding strength
- **Integration**: Add to `evaluate_pair()` flow
- **Scoring**: Add penalty to `scoring.py` if ΔG too weak (>-3) or too stable (<-9)
- **Tests**: 5+ tests
- **Depends on**: 2.1

### Task 2.6 — Update `scoring.py` for new thermo engine
- **File**: `primerlab/core/scoring.py`
- **What**:
  - Add `end_stability_penalty` to PENALTY_CONFIG
  - Update docstrings: "ViennaRNA QC" → "Primer3 ThermoAnalysis"
  - Ensure score calculation is compatible with new ΔG values
- **Tests**: Update `tests/test_scoring.py`
- **Depends on**: 2.5

### Task 2.7 — Update `reranking.py` — use ThermocalcWrapper
- **File**: `primerlab/core/reranking.py`
- **What**: Replace ViennaWrapper with ThermocalcWrapper for re-ranking candidates
- **Depends on**: 2.1

**Fase 2 Checkpoint**:
- All 1286+ tests pass
- QC results use Primer3 ThermoAnalysis for primers
- ViennaRNA still used for amplicon analysis only
- Benchmark: QC should be 3-10x faster (no subprocess calls)

---

## FASE 3: Parameter Expansion

**Goal**: Expose missing Primer3 parameters ke user config dan CLI.

### Task 3.1 — `PRIMER_MAX_POLY_X` config
- **File**: `primer3_wrapper.py`, `config_loader.py`
- **YAML**: `parameters.max_poly_x: 4` (default 4, current Primer3 default=100=disabled)
- **CLI**: `--max-poly-x 4`
- **Tests**: 3 tests

### Task 3.2 — `PRIMER_MAX_NS_ACCEPTED` config
- **File**: `primer3_wrapper.py`, `config_loader.py`
- **YAML**: `parameters.max_ns: 0` (default 0)
- **CLI**: `--max-ns 1` (allow 1 ambiguous base)
- **Tests**: 3 tests

### Task 3.3 — `PRIMER_PAIR_MAX_DIFF_TM` via Primer3
- **File**: `primer3_wrapper.py`
- **YAML**: `parameters.max_tm_diff: 5.0`
- **What**: Let Primer3 filter Tm-imbalanced pairs at design time (before QC)
- **Tests**: 3 tests

### Task 3.4 — `PRIMER_OPT_GC_PERCENT` config
- **File**: `primer3_wrapper.py`
- **YAML**: `parameters.gc.opt: 50.0`
- **Tests**: 2 tests

### Task 3.5 — `SEQUENCE_INCLUDED_REGION` support
- **File**: `primer3_wrapper.py`
- **YAML**: `parameters.included_region: {start: 100, length: 500}`
- **What**: Different from `target_region` — primer must be WITHIN this region
- **Tests**: 3 tests

### Task 3.6 — Forced primer position support
- **File**: `primer3_wrapper.py`
- **YAML**:
  ```yaml
  parameters:
    force_left_start: 50
    force_left_end: 70
    force_right_start: 450
    force_right_end: 470
  ```
- **Maps to**: `SEQUENCE_FORCE_LEFT_START`, etc.
- **Use case**: Cloning, restriction site design
- **Tests**: 4 tests

### Task 3.7 — Nucleotide constraints at primer ends
- **File**: `primer3_wrapper.py`
- **YAML**:
  ```yaml
  parameters:
    must_match_five_prime: "NNANN"   # A at position 3 from 5'
    must_match_three_prime: "NNNNG"  # G at 3' end
  ```
- **Maps to**: `PRIMER_MUST_MATCH_FIVE_PRIME`, `PRIMER_MUST_MATCH_THREE_PRIME`
- **Use case**: Allele-specific primer, degenerate design
- **Tests**: 4 tests

### Task 3.8 — Threshold method params (TH vs ANY)
- **File**: `primer3_wrapper.py`
- **What**: Add `PRIMER_MAX_SELF_ANY_TH`, `PRIMER_MAX_SELF_END_TH`, `PRIMER_PAIR_MAX_COMPL_ANY_TH`, `PRIMER_PAIR_MAX_COMPL_END_TH`, `PRIMER_MAX_HAIRPIN_TH`
- **YAML**: `parameters.qc_method: threshold` (default) vs `any`
- **Tests**: 5 tests

### Task 3.9 — `PRIMER_NUM_RETURN` user-configurable
- **File**: `primer3_wrapper.py`
- **YAML**: `parameters.num_candidates: 50` (currently hardcoded 30/50)
- **CLI**: `--num-candidates 100`
- **Tests**: 2 tests

### Task 3.10 — Primer weight fine-tuning
- **File**: `primer3_wrapper.py`
- **YAML**:
  ```yaml
  parameters:
    weights:
      tm_gt: 1.0       # PRIMER_WT_TM_GT
      tm_lt: 1.0       # PRIMER_WT_TM_LT
      size_gt: 1.0      # PRIMER_WT_SIZE_GT
      size_lt: 1.0      # PRIMER_WT_SIZE_LT
      gc_percent_gt: 0.0
      gc_percent_lt: 0.0
      end_stability: 0.25
  ```
- **Tests**: 3 tests

### Task 3.11 — Config validator update for all new params
- **File**: `primerlab/core/config_validator.py`
- **What**: Add validation + helpful suggestions for all new params
- **Tests**: Update existing config validator tests

### Task 3.12 — Documentation: all new parameters
- **File**: `docs/reference/config.md`
- **What**: Document every new parameter with examples and defaults

**Fase 3 Checkpoint**: All tests pass. New parameters backward compatible (defaults match current behavior).

---

## FASE 4: New Features

**Goal**: PRIMER_TASK variants, mispriming library, IUPAC/degenerate support improvements.

### Task 4.1 — IUPAC template handling fix
- **File**: `primerlab/core/sequence.py`
- **What**: **STOP converting IUPAC → N** in template sequences
  ```python
  # BEFORE: IUPAC codes → N (info loss!)
  # AFTER:  Keep IUPAC codes, let Primer3 handle via PRIMER_MAX_NS_ACCEPTED
  ```
- **Add config**: `input.preserve_iupac: true` (default true)
- **Backward compat**: Add `input.preserve_iupac: false` for legacy behavior
- **Tests**: Update `tests/test_sequence.py` — 5 new tests
- **Depends on**: 3.2 (MAX_NS_ACCEPTED must be configurable first)

### Task 4.2 — RNA input mode enhancement
- **File**: `primerlab/core/sequence.py`, `cli/main.py`
- **What**: Better RNA → cDNA handling
  - Detect U and auto-convert with clear warning
  - CLI flag: `--input-type dna|rna|auto`
  - If `rna` → suggest RT-qPCR workflow
- **Tests**: 4 tests

### Task 4.3 — `check_primers` TASK
- **File**: `primer3_wrapper.py`, `cli/main.py`, `api/public.py`
- **What**: Validate existing primers via Primer3 (not design new ones)
- **PRIMER_TASK**: `check_primers`
- **CLI**: `primerlab check-primers --forward "ATGC..." --reverse "GCTA..." --template seq.fasta`
- **API**: `check_existing_primers(fwd, rev, template)`
- **Tests**: 6 tests

### Task 4.4 — `pick_left_only` / `pick_right_only` TASK
- **File**: `primer3_wrapper.py`, `cli/main.py`
- **What**: Design only forward OR only reverse primer
- **CLI**: `primerlab run pcr --config x.yaml --pick-only left`
- **Use case**: When user already has one primer, needs the other
- **Tests**: 4 tests

### Task 4.5 — `pick_hyb_probe_only` TASK
- **File**: `primer3_wrapper.py`, `cli/main.py`
- **What**: Design TaqMan probe for existing primer pair
- **CLI**: `primerlab design-probe --primers primers.json --template seq.fasta`
- **Use case**: User has validated primers, needs probe
- **Tests**: 4 tests

### Task 4.6 — Mispriming library support
- **File**: `primer3_wrapper.py`, `config_loader.py`
- **What**: Pass `misprime_lib` dict to `design_primers()`
- **YAML**:
  ```yaml
  parameters:
    mispriming:
      library_path: "repeats.fasta"   # FASTA of unwanted sequences
      # OR built-in:
      library: human_repeat           # Built-in human repeat library
  ```
- **Built-in libraries**: `human_repeat` (Alu, LINE-1), `rodent_repeat`
- **File**: `primerlab/config/mispriming/` (NEW dir with FASTA files)
- **Tests**: 5 tests

### Task 4.7 — Mishybridization library for probes
- **File**: `primer3_wrapper.py`
- **What**: Pass `mishyb_lib` dict for probe design
- **YAML**: `parameters.probe.mishyb_library_path: "pseudogenes.fasta"`
- **Tests**: 3 tests

### Task 4.8 — Degenerate primer output mode
- **File**: `primerlab/core/models/primer.py`, report modules
- **What**: When primer contains IUPAC, calculate degeneracy info
  - `degeneracy_multiplier` (e.g., R in primer = 2x, RY = 4x)
  - Warning if degeneracy > 256
  - Report shows all possible sequences
- **Tests**: 4 tests

### Task 4.9 — Sequencing primer TASK
- **File**: `primer3_wrapper.py`, `cli/main.py`
- **What**: New PRIMER_TASK for Sanger sequencing
- **Params**: `PRIMER_SEQUENCING_LEAD`, `PRIMER_SEQUENCING_SPACING`, `PRIMER_SEQUENCING_ACCURACY`
- **CLI**: `primerlab run sequencing --config seq.yaml`
- **Preset**: `primerlab/config/presets/sequencing.yaml`
- **Tests**: 4 tests

### Task 4.10 — Cloning primer design support
- **File**: `primer3_wrapper.py`, `cli/main.py`
- **What**: Force positions + restriction site overhang addition
- **CLI**: `primerlab run cloning --add-sites EcoRI,BamHI`
- **Tests**: 4 tests

### Task 4.11 — `pick_discriminative_primers` TASK
- **File**: `primer3_wrapper.py`
- **What**: Primer3 native discriminative primer design
- **Integration**: Link with existing `genotyping/` module
- **Tests**: 3 tests

### Task 4.12 — Update FEATURE_COMPARISON.md
- **File**: `benchmark/FEATURE_COMPARISON.md`
- **What**: Update comparison table — many ❌ should become ✅

### Task 4.13 — Version bump + CHANGELOG
- **Files**: `pyproject.toml`, `CHANGELOG.md`, `RELEASE_NOTES.md`
- **Version**: 1.0.1 → 1.1.0

**Fase 4 Checkpoint**: All tests pass. New features documented. Benchmark updated.

---

## Dependency Graph

```
FASE 1 (Foundation)
  1.1 ThermocalcWrapper ──┐
  1.2 ThermoResult ───────┤
  1.3 YAML config ────────┤──→ FASE 2 (QC Migration)
  1.4 Salt → Primer3 ─────┤      2.1 Dual engine init
  1.5 Salt → Probe ───────┘      2.2 Hairpin migration
  1.6 Presets                     2.3 Homodimer migration
  1.7 Cache integration           2.4 Heterodimer migration
  1.8 Docs                        2.5 End stability (NEW)
                                  2.6 Scoring update
                                  2.7 Reranking update
                                       │
                                       ▼
                              FASE 3 (Params)
                                3.1-3.12 All independent
                                       │
                                       ▼
                              FASE 4 (Features)
                                4.1 IUPAC fix (needs 3.2)
                                4.3-4.11 Mostly independent
```

---

## Testing Strategy

| Level | What | Count (estimated) |
|-------|------|-------------------|
| Unit | ThermocalcWrapper methods | 20 |
| Unit | Config parsing new params | 15 |
| Unit | Updated QC (base_qc.py) | 20 |
| Unit | New TASK variants | 25 |
| Unit | Mispriming/IUPAC | 15 |
| Integration | Full workflow with new params | 10 |
| Regression | Existing 1286 tests | 1286 |
| **Total new** | | **~105 tests** |
| **Total after** | | **~1391 tests** |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Primer3 ThermoAnalysis ΔG differs from ViennaRNA | Score thresholds need recalibration | Task 2.6: recalibrate PENALTY_CONFIG |
| IUPAC fix breaks existing behavior | Users who relied on N-conversion | Backward compat flag `preserve_iupac` |
| Salt config changes default Tm values | Existing presets produce different results | Ensure defaults match current behavior |
| Mispriming library files too large | Docker image size increase | Keep built-in libraries small, support external paths |

---

## Git Strategy

```
main
  └── feat/primer3-full-coverage
        ├── feat/p3-phase1-foundation      (Tasks 1.1-1.8)
        ├── feat/p3-phase2-qc-migration    (Tasks 2.1-2.7)
        ├── feat/p3-phase3-params          (Tasks 3.1-3.12)
        └── feat/p3-phase4-features        (Tasks 4.1-4.13)
```

Each phase = PR → review → merge to `feat/primer3-full-coverage` → final PR to `main`.

---

## Milestones

| Milestone | Deadline | Deliverable |
|-----------|----------|-------------|
| Fase 1 Complete | TBD | ThermocalcWrapper + Salt config working |
| Fase 2 Complete | TBD | QC uses Primer3 natively, ViennaRNA for amplicon only |
| Fase 3 Complete | TBD | All relevant Primer3 params configurable |
| Fase 4 Complete | TBD | v1.1.0 release with full Primer3 coverage |
