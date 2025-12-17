# 🤖 Agent Session Log

Format: `[TIMESTAMP] [TYPE] message`
Types: `INFO`, `CHANGE`, `FIX`, `TODO`, `WARN`, `ERR`

---

## Quick Reference

- **Current Version**: v0.1.6 (in progress)
- **Dev Environment**: Requires WSL (primer3-py doesn't work on Windows native)
- **Test Status**: 196 passed, 0 warnings

---

## Log

```
# ===== v0.1.0 Release (2025-11-27) =====
[2025-11-27] INFO    Project initialized - 3-layer architecture (CLI → Workflows → Core)
[2025-11-27] CHANGE  Created core modules: config_loader.py, logger.py, exceptions.py
[2025-11-27] CHANGE  Created PCR workflow: workflow.py, qc.py, report.py
[2025-11-27] CHANGE  Created qPCR workflow with TaqMan probe support
[2025-11-27] CHANGE  Created Primer3 wrapper with primer3-py bindings
[2025-11-27] CHANGE  Created ViennaRNA wrapper for secondary structure QC
[2025-11-27] CHANGE  Created API layer: api/__init__.py, api/public.py
[2025-11-27] CHANGE  Created test suite: test_pcr.py, test_qpcr.py, test_api.py
[2025-11-27] FIX     Fixed reverse primer coordinate calculation (3' vs 5' index)
[2025-11-27] FIX     Fixed QC silent pass when ViennaRNA missing

# ===== v0.1.1 Patch (2025-11-30) =====
[2025-11-30] CHANGE  Added product_size simplified syntax (min/opt/max)
[2025-11-30] CHANGE  Added preset configuration support (long_range, standard_pcr)
[2025-11-30] CHANGE  Added qPCR mode parameter (sybr/taqman)
[2025-11-30] FIX     Fixed SetuptoolsDeprecationWarning in pyproject.toml

# ===== v0.1.2 Release (2025-12-07) =====
[2025-12-07] CHANGE  Added 4 example configs (pcr_standard, pcr_long_range, qpcr_taqman, qpcr_sybr)
[2025-12-07] CHANGE  Added CSV export for primers
[2025-12-07] CHANGE  Added vendor ordering formats (IDT, Sigma, Thermo)
[2025-12-07] CHANGE  Added --dry-run CLI flag
[2025-12-07] CHANGE  Added batch-generate command
[2025-12-07] FIX     Added minimum sequence length validation (50bp)
[2025-12-07] FIX     Added detailed Primer3 failure reasons

# ===== v0.1.3 Release (2025-12-08) =====
[2025-12-08] CHANGE  Added multi-candidate reranking engine (core/reranking.py)
[2025-12-08] CHANGE  Added GC clamp check and poly-X detection (sequence_qc.py)
[2025-12-08] CHANGE  Added presets: dna_barcoding, rt_pcr, long_range
[2025-12-08] CHANGE  Added CLI commands: init, health
[2025-12-08] CHANGE  Added --export flag for vendor format selection
[2025-12-08] CHANGE  Added Rich colorized output and tqdm progress bars
[2025-12-08] CHANGE  Added advanced.seed for reproducibility
[2025-12-08] CHANGE  Added Docs/Guide: troubleshooting.md, qc-metrics.md, reranking-algorithm.md

# ===== v0.1.4 Release (2025-12-10) =====
[2025-12-10] CHANGE  Added Primer Quality Score (0-100) in scoring.py
[2025-12-10] CHANGE  Added "Why This Primer?" rationale in rationale.py
[2025-12-10] CHANGE  Added audit.json logging in audit.py
[2025-12-10] CHANGE  Added Excel export (.xlsx) with openpyxl
[2025-12-10] CHANGE  Added IDT bulk ordering template
[2025-12-10] CHANGE  Added HTML report generator (html_report.py)
[2025-12-10] CHANGE  Added target_region and excluded_regions in Primer3 wrapper
[2025-12-10] CHANGE  Added --export xlsx, html, idt_bulk options

# ===== v0.1.5 Release (2025-12-17) =====
[2025-12-17] CHANGE  Added Auto Parameter Suggestion (core/suggestion.py)
[2025-12-17] CHANGE  Added Primer Comparison Tool (core/comparison.py, CLI compare)
[2025-12-17] CHANGE  Added Benchling CSV Export (--export benchling)
[2025-12-17] CHANGE  Added Batch Run Command (primerlab batch-run)
[2025-12-17] CHANGE  Added GC Profile Plot (primerlab plot, requires matplotlib)
[2025-12-17] CHANGE  Added Primer Database (primerlab history, SQLite)
[2025-12-17] CHANGE  Added Region Masking (--mask auto/lowercase/n)
[2025-12-17] CHANGE  Added JSON Schema for config validation

# ===== v0.1.6 Development (2025-12-17 - 2025-12-18) =====
[2025-12-17 22:48] INFO    Session start - v0.1.6 Stabilization & Testing
[2025-12-17 23:00] CHANGE  Created test fixtures (multi_sequences.fasta, masked_sequence.fasta, etc.)
[2025-12-17 23:15] CHANGE  Created test_visualization.py (13 tests)
[2025-12-17 23:20] CHANGE  Created test_database.py (9 tests)
[2025-12-17 23:25] CHANGE  Created test_masking.py (9 tests)
[2025-12-17 23:30] CHANGE  Added matplotlib to required dependencies
[2025-12-17 23:45] CHANGE  Created test_integration.py (10 E2E tests)
[2025-12-18 00:00] CHANGE  Added IUPAC ambiguous codes handling (R,Y,W,S,K,M,B,D,H,V → N)
[2025-12-18 00:05] CHANGE  Added RNA sequence detection (U → T conversion)
[2025-12-18 00:15] CHANGE  Created test_sequence.py (14 tests)
[2025-12-18 00:30] CHANGE  Added primerlab stats command
[2025-12-18 00:35] CHANGE  Added version check in primerlab health
[2025-12-18 00:45] CHANGE  Added --quiet flag for run command
[2025-12-18 00:50] CHANGE  Created test_stats.py (8 tests)
[2025-12-18 01:00] FIX     Fixed datetime.utcnow() deprecation warning
[2025-12-18 01:45] CHANGE  Bumped version to 0.1.6
[2025-12-18 01:50] CHANGE  Updated CHANGELOG.md with v0.1.6 entries
[2025-12-18 02:00] CHANGE  Updated README.md with v0.1.6 features
[2025-12-18 02:10] CHANGE  Created comprehensive docs (20 files in Docs/)
[2025-12-18 02:20] CHANGE  Reorganized docs - moved internal to .dev/
[2025-12-18 02:25] INFO    Total: 196 tests passing, 0 warnings
```

---

## Context Notes (Update when major state changes)

Last updated: 2025-12-18

### Release Status

| Version | Status | Highlights |
|---------|--------|------------|
| v0.1.0 - v0.1.4 | ✅ COMPLETE | Core functionality |
| v0.1.5 | ✅ RELEASED | Smart features, batch, database |
| v0.1.6 | 🔄 IN PROGRESS | Stabilization, testing, docs |

### v0.1.6 Checklist

- [x] Test Fixtures & Examples
- [x] Unit Tests (70+ new tests)
- [x] Integration Tests (10 E2E)
- [x] IUPAC & RNA Handling
- [x] `primerlab stats` command
- [x] Version check in health
- [x] `--quiet` flag
- [x] Comprehensive documentation (20 files)
- [x] Docs reorganization (.dev/ for internal)
- [ ] Git tag v0.1.6
- [ ] Push to GitHub

### Test Coverage

- **Total Tests**: 196
- **Warnings**: 0
- **Files**: test_cli, test_pcr, test_qpcr, test_visualization, test_database, test_masking, test_suggestion, test_sequence, test_integration, test_stats

### Next Steps

1. Create git tag v0.1.6
2. Push to GitHub (manual)
3. Start v0.2.0 planning (In-silico PCR Validation)
