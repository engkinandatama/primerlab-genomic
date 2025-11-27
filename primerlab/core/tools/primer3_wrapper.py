import primer3
from typing import Dict, Any, List
from primerlab.core.exceptions import ToolExecutionError
from primerlab.core.logger import get_logger

logger = get_logger()

class Primer3Wrapper:
    """
    Wrapper for primer3-py bindings.
    """
    
    def design_primers(self, sequence: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs primer3 design with provided configuration.
        
        Args:
            sequence: The template DNA sequence.
            config: The full workflow configuration dictionary.
            
        Returns:
            Raw dictionary output from primer3.
        """
        # Extract parameters from config
        params = config.get("parameters", {})
        
        # Map PrimerLab config to Primer3 parameters
        p3_settings = {
            'SEQUENCE_TEMPLATE': sequence,
            'PRIMER_TASK': 'generic',
            'PRIMER_PICK_LEFT_PRIMER': 1,
            'PRIMER_PICK_RIGHT_PRIMER': 1,
            'PRIMER_NUM_RETURN': 1,
            
            # Size
            'PRIMER_OPT_SIZE': params.get('primer_size', {}).get('opt', 20),
            'PRIMER_MIN_SIZE': params.get('primer_size', {}).get('min', 18),
            'PRIMER_MAX_SIZE': params.get('primer_size', {}).get('max', 27),
            
            # Tm
            'PRIMER_OPT_TM': params.get('tm', {}).get('opt', 60.0),
            'PRIMER_MIN_TM': params.get('tm', {}).get('min', 57.0),
            'PRIMER_MAX_TM': params.get('tm', {}).get('max', 63.0),
            
            # GC
            'PRIMER_MIN_GC': params.get('gc', {}).get('min', 20.0),
            'PRIMER_MAX_GC': params.get('gc', {}).get('max', 80.0),
            
            # Product Size Range (default if not specified)
            'PRIMER_PRODUCT_SIZE_RANGE': [[75, 300]],
        }

        # Handle Probe Design (qPCR)
        probe_params = params.get('probe')
        if probe_params:
            p3_settings.update({
                'PRIMER_PICK_INTERNAL_OLIGO': 1,
                'PRIMER_INTERNAL_OPT_SIZE': probe_params.get('size', {}).get('opt', 20),
                'PRIMER_INTERNAL_MIN_SIZE': probe_params.get('size', {}).get('min', 18),
                'PRIMER_INTERNAL_MAX_SIZE': probe_params.get('size', {}).get('max', 27),
                'PRIMER_INTERNAL_OPT_TM': probe_params.get('tm', {}).get('opt', 70.0),
                'PRIMER_INTERNAL_MIN_TM': probe_params.get('tm', {}).get('min', 68.0),
                'PRIMER_INTERNAL_MAX_TM': probe_params.get('tm', {}).get('max', 72.0),
                'PRIMER_INTERNAL_MIN_GC': probe_params.get('gc', {}).get('min', 30.0),
                'PRIMER_INTERNAL_MAX_GC': probe_params.get('gc', {}).get('max', 80.0),
            })
            
        # ...

        # Split into seq_args and global_args
        seq_args = {
            'SEQUENCE_TEMPLATE': sequence
        }
        
        # Remove sequence from global settings to avoid duplication/confusion
        if 'SEQUENCE_TEMPLATE' in p3_settings:
            del p3_settings['SEQUENCE_TEMPLATE']

        logger.info(f"Calling Primer3 binding with {len(p3_settings)} settings...")
        # logger.debug(f"Settings: {p3_settings}")

        try:
            # Use the new snake_case API as requested by the warning
            results = primer3.bindings.design_primers(
                seq_args=seq_args,
                global_args=p3_settings
            )
            logger.info("Primer3 returned results.")
            return results
            return results
        except Exception as e:
            logger.error(f"Primer3 execution failed: {e}")
            raise ToolExecutionError(f"Primer3 failed: {e}", "ERR_TOOL_P3_001")
