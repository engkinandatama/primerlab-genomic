"""
Multi-Species FASTA Loader.

Load and parse FASTA files for multiple species templates.
"""

import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from .models import SpeciesTemplate

logger = logging.getLogger(__name__)


def parse_fasta(content: str) -> List[Tuple[str, str, str]]:
    """
    Parse FASTA content into list of (header, sequence, description).
    
    Returns:
        List of (name, sequence, description) tuples
    """
    sequences = []
    current_header = ""
    current_desc = ""
    current_seq = []
    
    for line in content.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('>'):
            # Save previous sequence
            if current_header:
                sequences.append((current_header, ''.join(current_seq), current_desc))
            
            # Parse new header
            header_parts = line[1:].split(None, 1)
            current_header = header_parts[0] if header_parts else "unknown"
            current_desc = header_parts[1] if len(header_parts) > 1 else ""
            current_seq = []
        else:
            current_seq.append(line.upper())
    
    # Save last sequence
    if current_header:
        sequences.append((current_header, ''.join(current_seq), current_desc))
    
    return sequences


def load_species_template(fasta_path: str, species_name: Optional[str] = None) -> SpeciesTemplate:
    """
    Load a single species template from a FASTA file.
    
    Args:
        fasta_path: Path to FASTA file
        species_name: Override species name (default: use filename)
        
    Returns:
        SpeciesTemplate object
    """
    path = Path(fasta_path)
    if not path.exists():
        raise FileNotFoundError(f"FASTA file not found: {fasta_path}")
    
    content = path.read_text()
    sequences = parse_fasta(content)
    
    if not sequences:
        raise ValueError(f"No sequences found in: {fasta_path}")
    
    # Use first sequence
    header, seq, desc = sequences[0]
    
    # Determine species name
    name = species_name or path.stem
    
    return SpeciesTemplate(
        species_name=name,
        sequence=seq,
        description=desc,
        accession=header
    )


def load_species_templates(
    fasta_paths: List[str],
    species_names: Optional[List[str]] = None
) -> Dict[str, SpeciesTemplate]:
    """
    Load multiple species templates from FASTA files.
    
    Args:
        fasta_paths: List of paths to FASTA files
        species_names: Optional list of species names (same order as paths)
        
    Returns:
        Dict mapping species_name -> SpeciesTemplate
    """
    templates = {}
    
    for i, path in enumerate(fasta_paths):
        name = species_names[i] if species_names and i < len(species_names) else None
        
        try:
            template = load_species_template(path, name)
            templates[template.species_name] = template
            logger.info(f"Loaded template: {template.species_name} ({template.length} bp)")
        except Exception as e:
            logger.warning(f"Failed to load {path}: {e}")
    
    return templates


def load_multi_fasta(fasta_path: str) -> Dict[str, SpeciesTemplate]:
    """
    Load multiple species from a single multi-FASTA file.
    Each sequence header is used as species name.
    
    Args:
        fasta_path: Path to multi-FASTA file
        
    Returns:
        Dict mapping species_name -> SpeciesTemplate
    """
    path = Path(fasta_path)
    if not path.exists():
        raise FileNotFoundError(f"FASTA file not found: {fasta_path}")
    
    content = path.read_text()
    sequences = parse_fasta(content)
    
    templates = {}
    for header, seq, desc in sequences:
        template = SpeciesTemplate(
            species_name=header,
            sequence=seq,
            description=desc,
            accession=header
        )
        templates[header] = template
    
    logger.info(f"Loaded {len(templates)} species from {path.name}")
    return templates
