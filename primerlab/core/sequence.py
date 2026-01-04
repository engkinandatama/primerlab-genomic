import os
from typing import Union, Tuple, Optional, List
from primerlab.core.exceptions import SequenceError
from primerlab.core.logger import get_logger

logger = get_logger()

class SequenceLoader:
    """
    Handles loading and validation of DNA sequences from strings or files.
    """

    # v0.1.5: Store last loaded sequence name for primer naming
    _last_sequence_name: Optional[str] = None

    @classmethod
    def get_last_sequence_name(cls) -> Optional[str]:
        """Returns the name of the last loaded sequence (from FASTA header or filename)."""
        return cls._last_sequence_name

    @staticmethod
    def load(input_data: str) -> str:
        """
        Loads sequence from a raw string or a file path.
        
        v0.1.5: Enhanced FASTA support with multi-sequence handling.
        
        Args:
            input_data: Raw DNA string or path to a FASTA/text file.
            
        Returns:
            Cleaned uppercase DNA sequence.
        """
        sequence = ""
        sequence_name = None

        # Check if input is a file path
        if os.path.exists(input_data) and os.path.isfile(input_data):
            logger.info(f"Loading sequence from file: {input_data}")

            # v0.1.5: Extract gene name from filename
            base_name = os.path.splitext(os.path.basename(input_data))[0]

            try:
                with open(input_data, 'r') as f:
                    content = f.read().strip()

                    if content.startswith(">"):
                        # FASTA format
                        sequences = SequenceLoader._parse_fasta(content)

                        if not sequences:
                            raise SequenceError("No valid sequences found in FASTA file.", "ERR_SEQ_EMPTY")

                        # v0.1.5: Use first sequence, warn if multi-sequence
                        if len(sequences) > 1:
                            logger.warning(f"Multi-FASTA detected with {len(sequences)} sequences. Using first sequence only.")

                        sequence_name, sequence = sequences[0]
                        logger.info(f"Loaded sequence '{sequence_name}' ({len(sequence)} bp)")
                    else:
                        # Raw text file
                        sequence = content.replace("\n", "").replace(" ", "")
                        sequence_name = base_name

            except SequenceError:
                raise
            except Exception as e:
                raise SequenceError(f"Failed to read sequence file: {e}", "ERR_SEQ_READ")
        else:
            # Assume raw string
            if len(input_data) > 1000:
                logger.debug("Loading sequence from raw string input")
            sequence = input_data.strip()
            sequence_name = "input_sequence"

        # Store sequence name for primer naming
        SequenceLoader._last_sequence_name = sequence_name

        # Clean and Validate
        cleaned_seq = SequenceLoader._clean_and_validate(sequence)
        return cleaned_seq

    @staticmethod
    def _parse_fasta(content: str) -> list:
        """
        Parse FASTA content into list of (name, sequence) tuples.
        
        v0.1.5: Supports multi-FASTA files.
        """
        sequences = []
        current_name = None
        current_seq_lines: List[str] = []

        for line in content.splitlines():
            line = line.strip()
            if line.startswith(">"):
                # Save previous sequence if exists
                if current_name is not None:
                    sequences.append((current_name, "".join(current_seq_lines)))

                # Start new sequence
                # Extract name (first word after >, clean up)
                header = line[1:].strip()
                current_name = header.split()[0] if header else "unnamed"
                current_seq_lines = []
            else:
                current_seq_lines.append(line)

        # Don't forget the last sequence
        if current_name is not None:
            sequences.append((current_name, "".join(current_seq_lines)))

        return sequences

    @staticmethod
    def _clean_and_validate(sequence: str) -> str:
        """
        Validates DNA characters and converts to uppercase.
        
        v0.1.6 Enhancements:
        - Converts RNA (U) to DNA (T) with warning
        - Converts IUPAC ambiguous codes to N with warning
        """
        if not sequence:
            raise SequenceError("Input sequence is empty.", "ERR_SEQ_EMPTY")

        # v0.1.6: Convert to uppercase first, then handle special cases
        sequence = sequence.replace(" ", "").replace("\n", "").replace("\r", "")

        # v0.1.6: Check for RNA (U/u) and convert to DNA
        if 'U' in sequence or 'u' in sequence:
            logger.warning("RNA sequence detected (contains U). Converting to DNA (U→T).")
            sequence = sequence.replace('U', 'T').replace('u', 't')

        # Now convert to uppercase
        sequence = sequence.upper()

        # v0.1.6: IUPAC ambiguous codes
        IUPAC_AMBIGUOUS = set("RYSWKMBDHV")
        standard_chars = set("ATCGN")
        unique_chars = set(sequence)

        # Find any IUPAC codes in the sequence
        iupac_found = unique_chars & IUPAC_AMBIGUOUS
        if iupac_found:
            logger.warning(
                f"IUPAC ambiguous codes detected: {iupac_found}. "
                f"Converting to N (will be masked/excluded from primer placement)."
            )
            # Convert all IUPAC codes to N
            for code in IUPAC_AMBIGUOUS:
                sequence = sequence.replace(code, 'N')

        # Check for remaining invalid characters
        unique_chars = set(sequence)
        invalid_chars = unique_chars - standard_chars

        if invalid_chars:
            raise SequenceError(
                f"Invalid characters found in sequence: {invalid_chars}. "
                f"Allowed: A, T, G, C, N. IUPAC codes (R,Y,W,S,K,M,B,D,H,V) are converted to N.",
                "ERR_SEQ_INVALID_CHAR"
            )

        # Check minimum length (50bp minimum for primer design)
        MIN_SEQUENCE_LENGTH = 50
        if len(sequence) < MIN_SEQUENCE_LENGTH:
            raise SequenceError(
                f"Sequence too short ({len(sequence)} bp). Minimum length is {MIN_SEQUENCE_LENGTH} bp for primer design.",
                "ERR_SEQ_TOO_SHORT"
            )

        return sequence

    @staticmethod
    def get_iupac_map() -> dict:
        """Returns map of IUPAC codes to sets of possible bases."""
        return {
            'A': {'A'}, 'C': {'C'}, 'G': {'G'}, 'T': {'T'},
            'R': {'A', 'G'}, 'Y': {'C', 'T'}, 'S': {'G', 'C'}, 'W': {'A', 'T'},
            'K': {'G', 'T'}, 'M': {'A', 'C'}, 'B': {'C', 'G', 'T'},
            'D': {'A', 'G', 'T'}, 'H': {'A', 'C', 'T'}, 'V': {'A', 'C', 'G'},
            'N': {'A', 'C', 'G', 'T'}
        }


def reverse_complement(seq: str) -> str:
    """
    Return reverse complement of DNA sequence including IUPAC codes.
    
    v0.2.1: Centralized and supports all IUPAC codes.
    """
    complement = {
        'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
        'R': 'Y', 'Y': 'R', 'S': 'S', 'W': 'W',
        'K': 'M', 'M': 'K', 'B': 'V', 'V': 'B',
        'D': 'H', 'H': 'D', 'N': 'N',
        'a': 't', 't': 'a', 'g': 'c', 'c': 'g',
        'r': 'y', 'y': 'r', 's': 's', 'w': 'w',
        'k': 'm', 'm': 'k', 'b': 'v', 'v': 'b',
        'd': 'h', 'h': 'd', 'n': 'n'
    }
    return ''.join(complement.get(base, 'N') for base in reversed(seq))


def bases_match(b1: str, b2: str) -> bool:
    """
    Check if two bases match, accounting for IUPAC ambiguity.
    
    v0.2.1: Semantic matching.
    """
    # Quick exact match
    b1_up, b2_up = b1.upper(), b2.upper()
    if b1_up == b2_up:
        return True

    # IUPAC logic
    iupac = {
        'A': {'A'}, 'C': {'C'}, 'G': {'G'}, 'T': {'T'},
        'R': {'A', 'G'}, 'Y': {'C', 'T'}, 'S': {'G', 'C'}, 'W': {'A', 'T'},
        'K': {'G', 'T'}, 'M': {'A', 'C'}, 'B': {'C', 'G', 'T'},
        'D': {'A', 'G', 'T'}, 'H': {'A', 'C', 'T'}, 'V': {'A', 'C', 'G'},
        'N': {'A', 'C', 'G', 'T'}
    }

    s1 = iupac.get(b1_up, {b1_up})
    s2 = iupac.get(b2_up, {b2_up})

    return bool(s1 & s2)
