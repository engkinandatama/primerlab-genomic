"""Tests for Sequence Loading and Validation (v0.1.6)."""
import pytest


class TestSequenceValidation:
    """Tests for sequence validation including IUPAC and RNA handling."""
    
    def test_valid_dna_sequence(self):
        """Test valid DNA sequence is accepted."""
        from primerlab.core.sequence import SequenceLoader
        
        sequence = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"  # 52bp
        result = SequenceLoader._clean_and_validate(sequence)
        
        assert result == sequence.upper()
        assert len(result) == 52
    
    def test_lowercase_converted(self):
        """Test lowercase is converted to uppercase."""
        from primerlab.core.sequence import SequenceLoader
        
        sequence = "atgcatgcatgcatgcatgcatgcatgcatgcatgcatgcatgcatgcatgc"
        result = SequenceLoader._clean_and_validate(sequence)
        
        assert result == sequence.upper()
    
    def test_whitespace_removed(self):
        """Test whitespace and newlines are removed."""
        from primerlab.core.sequence import SequenceLoader
        
        # 52 characters of ATGC with whitespace/newlines
        sequence = "ATGC ATGC\nATGC ATGC\rATGC ATGC ATGC ATGC ATGC ATGC ATGC ATGC ATGC"
        result = SequenceLoader._clean_and_validate(sequence)
        
        assert " " not in result
        assert "\n" not in result
        assert len(result) >= 50
    
    def test_empty_sequence_raises(self):
        """Test empty sequence raises error."""
        from primerlab.core.sequence import SequenceLoader
        from primerlab.core.exceptions import SequenceError
        
        with pytest.raises(SequenceError) as exc_info:
            SequenceLoader._clean_and_validate("")
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_too_short_sequence_raises(self):
        """Test sequence < 50bp raises error."""
        from primerlab.core.sequence import SequenceLoader
        from primerlab.core.exceptions import SequenceError
        
        with pytest.raises(SequenceError) as exc_info:
            SequenceLoader._clean_and_validate("ATGCATGC")  # 8bp
        
        assert "too short" in str(exc_info.value).lower()
    

class TestRNAConversion:
    """Tests for RNA (U) to DNA (T) conversion."""
    
    def test_rna_converted_to_dna(self):
        """Test RNA sequence (U) is converted to DNA (T)."""
        from primerlab.core.sequence import SequenceLoader
        
        # RNA sequence with U
        rna = "AUGCAUGCAUGCAUGCAUGCAUGCAUGCAUGCAUGCAUGCAUGCAUGCAUGC"  # 52bp
        result = SequenceLoader._clean_and_validate(rna)
        
        assert 'U' not in result
        assert 'T' in result
        assert result == "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
    
    def test_lowercase_rna_converted(self):
        """Test lowercase RNA (u) is also converted."""
        from primerlab.core.sequence import SequenceLoader
        
        rna = "augcaugcaugcaugcaugcaugcaugcaugcaugcaugcaugcaugcaugc"
        result = SequenceLoader._clean_and_validate(rna)
        
        assert 'u' not in result
        assert 'T' in result


class TestIUPACCodes:
    """Tests for IUPAC ambiguous code handling."""
    
    def test_iupac_codes_converted_to_n(self):
        """Test IUPAC codes (R,Y,W,S,K,M,B,D,H,V) are converted to N."""
        from primerlab.core.sequence import SequenceLoader
        
        # Sequence with IUPAC codes: R (A/G), Y (C/T)
        sequence = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCRYSWATGC"
        result = SequenceLoader._clean_and_validate(sequence)
        
        assert 'R' not in result
        assert 'Y' not in result
        assert 'S' not in result
        assert 'W' not in result
        # IUPAC codes should be replaced with N
        assert 'N' in result
    
    def test_all_iupac_codes(self):
        """Test all IUPAC ambiguous codes are handled."""
        from primerlab.core.sequence import SequenceLoader
        
        # Sequence with all IUPAC codes
        sequence = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCRYSWKMBDHVATGC"
        result = SequenceLoader._clean_and_validate(sequence)
        
        iupac_codes = set("RYSWKMBDHV")
        for code in iupac_codes:
            assert code not in result
    
    def test_n_preserved(self):
        """Test N characters are preserved (not rejected)."""
        from primerlab.core.sequence import SequenceLoader
        
        sequence = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCNNNNATGCATGC"
        result = SequenceLoader._clean_and_validate(sequence)
        
        assert result.count('N') == 4


class TestInvalidCharacters:
    """Tests for invalid character handling."""
    
    def test_invalid_char_raises(self):
        """Test truly invalid characters raise error."""
        from primerlab.core.sequence import SequenceLoader
        from primerlab.core.exceptions import SequenceError
        
        # 'X' and 'Z' are not valid
        sequence = "ATGCATGCATGCXZATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
        
        with pytest.raises(SequenceError) as exc_info:
            SequenceLoader._clean_and_validate(sequence)
        
        assert "Invalid characters" in str(exc_info.value)
    
    def test_numbers_rejected(self):
        """Test numeric characters are rejected."""
        from primerlab.core.sequence import SequenceLoader
        from primerlab.core.exceptions import SequenceError
        
        sequence = "ATGC123ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
        
        with pytest.raises(SequenceError):
            SequenceLoader._clean_and_validate(sequence)


class TestSequenceLoader:
    """Tests for SequenceLoader class."""
    
    def test_load_from_string(self):
        """Test loading sequence from raw string."""
        from primerlab.core.sequence import SequenceLoader
        
        sequence = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
        result = SequenceLoader.load(sequence)
        
        assert result == sequence.upper()
    
    def test_sequence_name_stored(self):
        """Test sequence name is stored for primer naming."""
        from primerlab.core.sequence import SequenceLoader
        
        sequence = "ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
        SequenceLoader.load(sequence)
        
        name = SequenceLoader.get_last_sequence_name()
        assert name is not None
