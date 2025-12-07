import os
from typing import Union
from primerlab.core.exceptions import SequenceError
from primerlab.core.logger import get_logger

logger = get_logger()

class SequenceLoader:
    """
    Handles loading and validation of DNA sequences from strings or files.
    """
    
    @staticmethod
    def load(input_data: str) -> str:
        """
        Loads sequence from a raw string or a file path.
        
        Args:
            input_data: Raw DNA string or path to a FASTA/text file.
            
        Returns:
            Cleaned uppercase DNA sequence.
        """
        sequence = ""
        
        # Check if input is a file path
        if os.path.exists(input_data) and os.path.isfile(input_data):
            logger.info(f"Loading sequence from file: {input_data}")
            try:
                with open(input_data, 'r') as f:
                    content = f.read().strip()
                    if content.startswith(">"):
                        # Simple FASTA parser: ignore header, join lines
                        lines = content.splitlines()
                        # Skip header(s)
                        seq_lines = [line.strip() for line in lines if not line.startswith(">")]
                        sequence = "".join(seq_lines)
                    else:
                        # Raw text file
                        sequence = content.replace("\n", "").replace(" ", "")
            except Exception as e:
                raise SequenceError(f"Failed to read sequence file: {e}", "ERR_SEQ_READ")
        else:
            # Assume raw string
            if len(input_data) > 1000:
                logger.debug("Loading sequence from raw string input")
            sequence = input_data.strip()

        # Clean and Validate
        cleaned_seq = SequenceLoader._clean_and_validate(sequence)
        return cleaned_seq

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
