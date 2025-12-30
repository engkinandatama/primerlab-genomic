"""
Batch Species-Check Module.

Provides batch processing, caching, and parallel analysis for species-check.
"""

from .batch_loader import (
    load_primers_from_directory,
    load_multi_fasta_templates,
    load_primer_files,
    BatchInput,
)
from .cache import (
    AlignmentCache,
    get_cache,
)
from .parallel import (
    run_parallel_species_check,
    BatchSpeciesResult,
    generate_batch_csv,
)

__all__ = [
    # Batch loader
    "load_primers_from_directory",
    "load_multi_fasta_templates",
    "load_primer_files",
    "BatchInput",
    # Cache
    "AlignmentCache",
    "get_cache",
    # Parallel
    "run_parallel_species_check",
    "BatchSpeciesResult",
    "generate_batch_csv",
]
