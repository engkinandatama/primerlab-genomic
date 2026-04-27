import pytest
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper

def test_sequencing_task_settings():
    wrapper = Primer3Wrapper()
    config = {
        "workflow": "sequencing",
        "parameters": {
            "sequencing_lead": 40,
            "sequencing_spacing": 400,
            "sequencing_accuracy": 15
        }
    }
    
    settings = wrapper._build_p3_settings(config["parameters"], config["workflow"])
    assert settings["PRIMER_TASK"] == "pick_sequencing_primers"
    assert settings["PRIMER_SEQUENCING_LEAD"] == 40
    assert settings["PRIMER_SEQUENCING_SPACING"] == 400
    assert settings["PRIMER_SEQUENCING_ACCURACY"] == 15

def test_discriminative_task_settings():
    wrapper = Primer3Wrapper()
    config = {
        "workflow": "discriminative",
        "parameters": {}
    }
    
    settings = wrapper._build_p3_settings(config["parameters"], config["workflow"])
    assert settings["PRIMER_TASK"] == "pick_discriminative_primers"
