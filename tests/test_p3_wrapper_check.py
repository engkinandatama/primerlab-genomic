import pytest
from unittest.mock import patch, MagicMock
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper

class TestPrimer3WrapperCheck:
    """Tests for Phase 4 check_existing_primers feature."""
    
    @patch('primer3.bindings.design_primers')
    def test_check_existing_primers(self, mock_design):
        # Setup mock return value
        mock_design.return_value = {
            'PRIMER_LEFT_0_PENALTY': 0.0,
            'PRIMER_RIGHT_0_PENALTY': 0.0,
            'PRIMER_PAIR_0_PENALTY': 0.0,
            'PRIMER_WARNING': ''
        }
        
        wrapper = Primer3Wrapper()
        
        fwd = "ATGCATGCATGCATGC"
        rev = "GCATGCATGCATGCAT"
        target = "ATGCATGCATGCATGC" * 5
        
        settings = {
            "PRIMER_OPT_TM": 60.0
        }
        
        result = wrapper.check_existing_primers(fwd, rev, target, settings)
        
        # Verify bindings.design_primers was called with check_primers
        mock_design.assert_called_once()
        args, kwargs = mock_design.call_args
        
        seq_args = args[0]
        p3_settings = args[1]
        
        assert seq_args['SEQUENCE_PRIMER'] == fwd
        assert seq_args['SEQUENCE_PRIMER_REVCOMP'] == rev
        assert seq_args['SEQUENCE_TEMPLATE'] == target
        assert p3_settings['PRIMER_TASK'] == 'check_primers'
        assert p3_settings['PRIMER_OPT_TM'] == 60.0
        
        assert result['PRIMER_WARNING'] == ''
