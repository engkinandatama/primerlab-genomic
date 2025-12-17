import os
from typing import Union, Tuple, Optional
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
        current_seq_lines = []
        
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
        """
        if not sequence:
            raise SequenceError("Input sequence is empty.", "ERR_SEQ_EMPTY")
            
        sequence = sequence.upper().replace(" ", "").replace("\n", "").replace("\r", "")
        
        allowed_chars = set("ATCGN")
        # Check for invalid characters
        # Note: For large sequences, set difference is faster than iterating
        unique_chars = set(sequence)
        invalid_chars = unique_chars - allowed_chars
        
        if invalid_chars:
            raise SequenceError(f"Invalid characters found in sequence: {invalid_chars}", "ERR_SEQ_INVALID_CHAR")
        
        # Check minimum length (50bp minimum for primer design)
        MIN_SEQUENCE_LENGTH = 50
        if len(sequence) < MIN_SEQUENCE_LENGTH:
            raise SequenceError(
                f"Sequence too short ({len(sequence)} bp). Minimum length is {MIN_SEQUENCE_LENGTH} bp for primer design.",
                "ERR_SEQ_TOO_SHORT"
            )
            
        return sequence
