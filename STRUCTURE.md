# PrimerLab Project Structure

> **Version**: 0.8.2 - Architecture Polish
>
> **Last updated**: 2026-01-09

```
primerlab-genomic/
├── primerlab/                      # Main package (132 Python files)
│   ├── __init__.py                 # Package version (0.8.2)
│   │
│   ├── cli/                        # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py                 # CLI entry point (~3000 lines)
│   │
│   ├── api/                        # Public API
│   │   ├── __init__.py
│   │   └── public.py               # design_pcr_primers(), design_qpcr_assays(), validate_primers()
│   │
│   ├── core/                       # Core utilities (17 modules + 17 subdirectories)
│   │   ├── __init__.py
│   │   ├── audit.py                # Audit logging for reproducibility
│   │   ├── batch_summary.py        # Batch run summaries
│   │   ├── comparison.py           # Primer comparison tools
│   │   ├── config_loader.py        # YAML config loading & validation
│   │   ├── config_validator.py     # v0.3.2: Config validation with suggestions
│   │   ├── database.py             # Primer design history (SQLite)
│   │   ├── exceptions.py           # Custom exceptions & error codes
│   │   ├── html_report.py          # HTML report generation
│   │   ├── logger.py               # Logging system
│   │   ├── masking.py              # Region masking (BED, lowercase, N)
│   │   ├── output.py               # Output manager (JSON, reports)
│   │   ├── rationale.py            # Selection rationale tracking
│   │   ├── reranking.py            # Multi-candidate re-ranking engine
│   │   ├── scoring.py              # Quality scoring system
│   │   ├── sequence.py             # Sequence loading & validation (IUPAC)
│   │   ├── sequence_qc.py          # Sequence QC (GC clamp, poly-X)
│   │   ├── suggestion.py           # Auto-parameter suggestion engine
│   │   │
│   │   ├── amplicon/               # v0.4.1+: Amplicon analysis
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py         # Main amplicon analyzer
│   │   │   ├── gc_profile.py       # GC profile analysis
│   │   │   ├── models.py           # AmpliconAnalysisResult, etc.
│   │   │   ├── restriction.py      # Restriction site detection
│   │   │   └── secondary.py        # Secondary structure analysis
│   │   │
│   │   ├── analysis/               # v0.7.1: Batch analysis tools
│   │   │   ├── batch_compare.py    # Batch comparison
│   │   │   └── dimer_matrix.py     # Primer dimer NxN matrix
│   │   │
│   │   ├── compat_check/           # v0.4.0: Multiplex compatibility
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # MultiplexPair, DimerResult, etc.
│   │   │   ├── overlap_detection.py # Amplicon overlap detection
│   │   │   ├── scoring.py          # Compatibility scoring
│   │   │   └── validator.py        # MultiplexValidator
│   │   │
│   │   ├── genotyping/             # v0.5.0: Genotyping support
│   │   │   ├── __init__.py
│   │   │   ├── allele_scoring.py   # Allele-specific scoring
│   │   │   └── snp_position.py     # SNP position analysis
│   │   │
│   │   ├── insilico/               # v0.2.0+: In-silico PCR
│   │   │   ├── __init__.py         # run_insilico_pcr()
│   │   │   ├── engine.py           # Virtual PCR engine
│   │   │   ├── binding.py          # Binding analysis, Tm correction
│   │   │   └── report.py           # In-silico report generation
│   │   │
│   │   ├── models/                 # Data models
│   │   │   ├── amplicon.py         # Amplicon model
│   │   │   ├── blast.py            # BlastResult, BlastHit
│   │   │   ├── metadata.py         # Metadata model
│   │   │   ├── primer.py           # Primer model
│   │   │   ├── qc.py               # QC result models
│   │   │   ├── variant.py          # Variant, VariantOverlap
│   │   │   └── workflow_result.py  # WorkflowResult
│   │   │
│   │   ├── offtarget/              # v0.3.0+: Off-target detection
│   │   │   ├── __init__.py
│   │   │   ├── finder.py           # OfftargetFinder
│   │   │   ├── integration.py      # Integration with workflows
│   │   │   └── variant_check.py    # Primer-SNP overlap detection
│   │   │
│   │   ├── qpcr/                   # v0.6.0+: qPCR-specific
│   │   │   ├── __init__.py
│   │   │   ├── advanced.py         # HRM, dPCR compatibility
│   │   │   ├── amplicon_qc.py      # Amplicon QC for qPCR
│   │   │   ├── efficiency.py       # Efficiency calculator
│   │   │   ├── melt_curve.py       # Melt curve analysis
│   │   │   ├── probe_binding.py    # Probe binding analysis
│   │   │   └── probe_position.py   # Probe positioning
│   │   │
│   │   ├── report/                 # v0.3.3: Report generation
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # PrimerReport, DesignSummary
│   │   │   ├── generator.py        # Markdown/JSON generator
│   │   │   ├── alignment_view.py   # ASCII alignment visualization
│   │   │   ├── html_export.py      # HTML report (dark mode)
│   │   │   └── json_export.py      # JSON report
│   │   │
│   │   ├── rtpcr/                  # v0.6.0: RT-PCR support
│   │   │   ├── __init__.py
│   │   │   ├── exon_junction.py    # Exon-junction spanning
│   │   │   ├── gdna_check.py       # gDNA contamination check
│   │   │   └── transcript_loader.py # Transcript loading
│   │   │
│   │   ├── species/                # v0.5.1: Species-specific design
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SpeciesConfig, ConsensusResult
│   │   │   ├── scoring.py          # Species specificity scoring
│   │   │   └── batch/              # Batch processing
│   │   │
│   │   ├── tm_gradient/            # v0.5.2: Tm gradient optimization
│   │   │   ├── __init__.py
│   │   │   ├── engine.py           # Gradient optimization
│   │   │   └── models.py           # GradientResult
│   │   │
│   │   ├── tools/                  # External tool wrappers
│   │   │   ├── __init__.py
│   │   │   ├── primer3_wrapper.py  # Primer3 interface
│   │   │   ├── vienna_wrapper.py   # ViennaRNA interface
│   │   │   ├── blast_cache.py      # SQLite BLAST cache
│   │   │   ├── parallel_blast.py   # Multi-threaded BLAST
│   │   │   ├── ncbi_blast.py       # NCBI Web BLAST
│   │   │   ├── primer_aligner.py   # Primer alignment
│   │   │   └── vcf_parser.py       # VCF/variant parser
│   │   │
│   │   ├── variants/               # v0.3.1: Variant handling
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # Variant models
│   │   │   └── checker.py          # Variant overlap checker
│   │   │
│   │   └── visualization/          # v0.1.5+: Visualization
│   │       ├── __init__.py
│   │       ├── gc_profile.py       # GC profile plots
│   │       └── coverage_map.py     # Amplicon coverage map
│   │
│   ├── workflows/                  # Workflow modules
│   │   ├── __init__.py
│   │   │
│   │   ├── nested/                 # v0.7.0: Nested PCR
│   │   │   └── workflow.py
│   │   │
│   │   ├── pcr/                    # PCR workflow
│   │   │   ├── __init__.py
│   │   │   ├── workflow.py         # Main PCR workflow
│   │   │   ├── qc.py               # PCR QC logic
│   │   │   └── report.py           # PCR report generator
│   │   │
│   │   └── qpcr/                   # qPCR workflow
│   │       ├── __init__.py
│   │       ├── workflow.py         # Main qPCR workflow
│   │       ├── design.py           # Primer/probe parsing
│   │       ├── qc.py               # qPCR QC + efficiency
│   │       ├── report.py           # qPCR report generator
│   │       └── progress.py         # Progress tracking
│   │
│   └── config/                     # Default configurations
│       ├── presets/                # Built-in presets (12+)
│       ├── pcr_default.yaml
│       └── qpcr_default.yaml
│
├── tests/                          # Test suite (87 files, 1273+ tests)
│   ├── conftest.py                 # Shared fixtures
│   ├── fixtures/                   # Test data files
│   ├── test_model_serialization.py # v0.8.2: Serialization tests
│   ├── test_report.py              # Report tests
│   ├── test_insilico.py            # In-silico tests
│   └── ...
│
├── examples/                       # Example files
│   ├── insilico/                   # In-silico examples
│   ├── multi_sequences.fasta
│   ├── variants.vcf
│   └── ...
│
├── docs/                           # User documentation
│   ├── cli/                        # CLI reference
│   ├── features/                   # Feature documentation
│   └── ...
│
├── .github/                        # CI/CD
│   └── workflows/
│       └── test.yml
│
├── CHANGELOG.md
├── README.md
├── STRUCTURE.md                    # This file
├── pyproject.toml
├── mypy.ini                        # v0.8.0: Type checking config
├── py.typed                        # v0.8.0: PEP 561 marker
└── LICENSE

```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           CLI Layer                              │
│   primerlab run/insilico/stats/health/validate/preset/...        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Workflow Layer                           │
│   PCR, qPCR, Nested (modular, isolated)                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                           Core Layer                             │
│   Tools, Models, Utilities, In-silico, Off-target, Reports      │
└─────────────────────────────────────────────────────────────────┘
```

## Module Summary

| Module | Purpose | Since |
|--------|---------|-------|
| `cli/` | Command-line interface | v0.1.0 |
| `api/` | Public Python API | v0.1.0 |
| `core/` | Shared utilities | v0.1.0 |
| `core/amplicon/` | Amplicon quality analysis | v0.4.1 |
| `core/analysis/` | Batch analysis tools | v0.7.1 |
| `core/compat_check/` | Multiplex compatibility | v0.4.0 |
| `core/genotyping/` | Genotyping support | v0.5.0 |
| `core/insilico/` | In-silico PCR simulation | v0.2.0 |
| `core/offtarget/` | Off-target detection | v0.3.0 |
| `core/qpcr/` | qPCR-specific tools | v0.6.0 |
| `core/report/` | Report generation | v0.3.3 |
| `core/rtpcr/` | RT-PCR support | v0.6.0 |
| `core/species/` | Species-specific design | v0.5.1 |
| `core/tm_gradient/` | Tm gradient optimization | v0.5.2 |
| `core/tools/` | External tool wrappers | v0.1.0 |
| `core/variants/` | Variant handling | v0.3.1 |
| `core/visualization/` | Visualization tools | v0.1.5 |
| `workflows/nested/` | Nested PCR workflow | v0.7.0 |
| `workflows/pcr/` | PCR primer design | v0.1.0 |
| `workflows/qpcr/` | qPCR assay design | v0.4.0 |

## Statistics

| Metric | Count |
|--------|-------|
| Python files (package) | 132 |
| Test files | 87 |
| Total tests | 1273+ |
| Config presets | 12+ |
| CLI commands | 20+ |

## Key Dataclasses (v0.8.2)

All dataclasses now have `to_dict()` methods for JSON serialization:

| File | Dataclasses |
|------|-------------|
| `compat_check/models.py` | `MultiplexPair`, `DimerResult`, `CompatibilityMatrix`, `MultiplexResult` |
| `amplicon/models.py` | `SecondaryStructure`, `GCProfile`, `AmpliconQuality`, etc. |
| `offtarget/finder.py` | `OfftargetHit`, `OfftargetResult`, `PrimerPairOfftargetResult` |
| `insilico/engine.py` | `PrimerBinding`, `AmpliconPrediction`, `InsilicoPCRResult` |
| `insilico/binding.py` | `BindingSite` |

---

*Updated for v0.8.2 - Architecture Polish*
