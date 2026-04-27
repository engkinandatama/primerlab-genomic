import pytest
import os
import tempfile
from unittest.mock import patch
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.exceptions import PrimerLabException

class TestPrimer3Libraries:
    """Tests for Phase 4 mispriming and repeat library features."""
    
    def test_mispriming_library_valid(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b">seq1\nATGC\n")
            tmp_name = tmp.name
            
        try:
            wrapper = Primer3Wrapper()
            params = {"mispriming_library": tmp_name}
            p3_settings = wrapper._build_p3_settings(params)
            
            assert "PRIMER_MISPRIMING_LIBRARY" in p3_settings
            assert p3_settings["PRIMER_MISPRIMING_LIBRARY"] == tmp_name
        finally:
            os.unlink(tmp_name)

    def test_mispriming_library_not_found(self):
        wrapper = Primer3Wrapper()
        params = {"mispriming_library": "/path/that/does/not/exist.fasta"}
        
        with pytest.raises(PrimerLabException) as excinfo:
            wrapper._build_p3_settings(params)
            
        assert "ERR_P3_LIB_NOT_FOUND" in str(excinfo.value.error_code)

    def test_repeat_library_valid(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b">seq1\nATGC\n")
            tmp_name = tmp.name
            
        try:
            wrapper = Primer3Wrapper()
            params = {"repeat_library": tmp_name}
            p3_settings = wrapper._build_p3_settings(params)
            
            assert "PRIMER_INTERNAL_MIPO_LIBRARY" in p3_settings
            assert p3_settings["PRIMER_INTERNAL_MIPO_LIBRARY"] == tmp_name
        finally:
            os.unlink(tmp_name)

    def test_repeat_library_not_found(self):
        wrapper = Primer3Wrapper()
        params = {"repeat_library": "/path/that/does/not/exist.fasta"}
        
        with pytest.raises(PrimerLabException) as excinfo:
            wrapper._build_p3_settings(params)
            
        assert "ERR_P3_LIB_NOT_FOUND" in str(excinfo.value.error_code)
