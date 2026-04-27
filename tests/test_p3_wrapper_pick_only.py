import pytest
import os
import tempfile
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.exceptions import PrimerLabException

class TestPrimer3PickOnly:
    def test_pick_left_only(self):
        wrapper = Primer3Wrapper()
        params = {"pick_only": "left"}
        p3_settings = wrapper._build_p3_settings(params, "pcr")
        
        assert p3_settings["PRIMER_PICK_LEFT_PRIMER"] == 1
        assert p3_settings["PRIMER_PICK_RIGHT_PRIMER"] == 0
        assert p3_settings["PRIMER_PICK_INTERNAL_OLIGO"] == 0

    def test_pick_right_only(self):
        wrapper = Primer3Wrapper()
        params = {"pick_only": "right"}
        p3_settings = wrapper._build_p3_settings(params, "pcr")
        
        assert p3_settings["PRIMER_PICK_LEFT_PRIMER"] == 0
        assert p3_settings["PRIMER_PICK_RIGHT_PRIMER"] == 1
        assert p3_settings["PRIMER_PICK_INTERNAL_OLIGO"] == 0

    def test_pick_probe_only(self):
        wrapper = Primer3Wrapper()
        params = {"pick_only": "probe"}
        p3_settings = wrapper._build_p3_settings(params, "qpcr")
        
        assert p3_settings["PRIMER_PICK_LEFT_PRIMER"] == 0
        assert p3_settings["PRIMER_PICK_RIGHT_PRIMER"] == 0
        assert p3_settings["PRIMER_PICK_INTERNAL_OLIGO"] == 1

class TestProbeMishybLibrary:
    def test_probe_mishyb_library_valid(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b">seq1\nATGC\n")
            tmp_name = tmp.name
            
        try:
            wrapper = Primer3Wrapper()
            config = {
                "workflow": "qpcr",
                "parameters": {
                    "probe": {
                        "mishyb_library_path": tmp_name
                    }
                }
            }
            with pytest.MonkeyPatch.context() as m:
                import multiprocessing
                
                # Mock the process to just put a dummy result in the queue immediately
                class MockProcess:
                    def __init__(self, target, args):
                        self.target = target
                        self.args = args
                        # args[1] is p3_settings! We can just save it to wrapper
                        wrapper.captured_settings = args[1]
                        
                        # Put dummy result in queue
                        queue = args[2]
                        queue.put({"success": True, "data": {"PRIMER_PAIR_NUM_RETURNED": 1}})
                        
                    def start(self): pass
                    def join(self, *a, **kw): pass
                    def is_alive(self): return False
                    
                m.setattr(multiprocessing, "Process", MockProcess)
                try:
                    wrapper.design_primers("ATGC" * 50, config)
                except Exception:
                    pass
                
            p3_settings = wrapper.captured_settings
            assert "PRIMER_INTERNAL_MISHYB_LIBRARY" in p3_settings
            assert p3_settings["PRIMER_INTERNAL_MISHYB_LIBRARY"] == tmp_name
        finally:
            os.unlink(tmp_name)

    def test_probe_mishyb_library_not_found(self):
        wrapper = Primer3Wrapper()
        config = {
            "workflow": "qpcr",
            "parameters": {
                "probe": {
                    "mishyb_library_path": "/path/that/does/not/exist.fasta"
                }
            }
        }
        with pytest.raises(PrimerLabException) as excinfo:
            wrapper.design_primers("ATGC", config)
            
        assert "ERR_P3_LIB_NOT_FOUND" in str(excinfo.value.error_code)
