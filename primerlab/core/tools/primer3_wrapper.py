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
        
        # Determine default num_candidates based on workflow type
        # qPCR with probe design is slower, so use fewer candidates
        workflow_type = config.get('workflow', 'pcr')
        default_num_candidates = 30 if workflow_type == 'qpcr' else 50
        
        # Map PrimerLab config to Primer3 parameters
        p3_settings = {
            'SEQUENCE_TEMPLATE': sequence,
            'PRIMER_TASK': 'generic',
            'PRIMER_PICK_LEFT_PRIMER': 1,
            'PRIMER_PICK_RIGHT_PRIMER': 1,
            'PRIMER_NUM_RETURN': params.get('num_candidates', default_num_candidates),  # v0.1.3: Multi-candidate support
            
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
        }
        
        # Product Size Range - determine based on workflow type
        if workflow_type == 'qpcr':
            default_range = [[70, 150]]  # qPCR-optimal range
        else:
            default_range = [[75, 300]]  # Standard PCR range
        
        size_range = params.get('product_size_range', default_range)
        p3_settings['PRIMER_PRODUCT_SIZE_RANGE'] = size_range

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
        
        # v0.1.4: Target Region Specification
        target_region = params.get('target_region')
        if target_region:
            start = target_region.get('start', 0)
            length = target_region.get('length', 100)
            
            # Validate region is within sequence bounds
            if start < 0:
                start = 0
            if start + length > len(sequence):
                length = len(sequence) - start
                logger.warning(f"Target region adjusted to fit sequence: {start},{length}")
            
            seq_args['SEQUENCE_TARGET'] = [[start, length]]
            logger.info(f"Target region set: position {start}, length {length}")
        
        # v0.1.4: Excluded Regions (for avoiding specific areas)
        excluded_regions = params.get('excluded_regions', [])
        if excluded_regions:
            seq_args['SEQUENCE_EXCLUDED_REGION'] = [[r['start'], r['length']] for r in excluded_regions]
            logger.info(f"Excluded regions: {len(excluded_regions)}")
        
        # Remove sequence from global settings to avoid duplication/confusion
        if 'SEQUENCE_TEMPLATE' in p3_settings:
            del p3_settings['SEQUENCE_TEMPLATE']

        logger.info(f"Calling Primer3 binding with {len(p3_settings)} settings...")
        
        # Use multiprocessing to enforce timeout and allow killing stuck processes
        import multiprocessing
        
        timeout_seconds = config.get("advanced", {}).get("timeout", 30)
        
        # Helper function for the worker process
        def _run_p3(seq_args, global_args, queue):
            try:
                res = primer3.bindings.design_primers(
                    seq_args=seq_args,
                    global_args=global_args
                )
                queue.put({"success": True, "data": res})
            except Exception as e:
                queue.put({"success": False, "error": str(e)})

        # Create a Queue to get results
        queue = multiprocessing.Queue()
        
        # Create and start the process
        p = multiprocessing.Process(
            target=_run_p3, 
            args=(seq_args, p3_settings, queue)
        )
        p.start()
        
        # Wait for the process with timeout
        p.join(timeout_seconds)
        
        if p.is_alive():
            # If still alive after timeout, kill it!
            logger.error(f"Primer3 process timed out ({timeout_seconds}s). Terminating...")
            p.terminate()
            p.join() # Clean up
            
            raise ToolExecutionError(
                f"Primer3 execution timed out after {timeout_seconds} seconds. "
                "This usually means the constraint combination is too strict for your sequence. "
                "Try: (1) Using a longer target sequence, (2) Relaxing probe Tm constraints "
                "(e.g., min: 65.0 instead of 68.0), or (3) Increasing timeout in config (advanced.timeout).", 
                "ERR_TOOL_P3_TIMEOUT"
            )
        
        # Check result
        if not queue.empty():
            result_wrapper = queue.get()
            if result_wrapper["success"]:
                data = result_wrapper["data"]
                
                # Check if any primers were actually returned
                num_returned = data.get('PRIMER_LEFT_NUM_RETURNED', 0)
                if num_returned == 0:
                    # Extract explanations
                    left_explain = data.get('PRIMER_LEFT_EXPLAIN', 'N/A')
                    right_explain = data.get('PRIMER_RIGHT_EXPLAIN', 'N/A')
                    pair_explain = data.get('PRIMER_PAIR_EXPLAIN', 'N/A')
                    
                    error_msg = (
                        "Primer3 failed to find any primers.\n"
                        "Reasons:\n"
                        f"- Left Primer: {left_explain}\n"
                        f"- Right Primer: {right_explain}\n"
                        f"- Pair: {pair_explain}\n\n"
                        "Suggestion: Try relaxing constraints (e.g., wider Tm range, lower GC content) or using a different region."
                    )
                    
                    # v0.1.5: Include structured details for Auto Parameter Suggestion
                    raise ToolExecutionError(
                        error_msg, 
                        "ERR_TOOL_P3_NO_PRIMERS",
                        details={
                            "left_explain": left_explain,
                            "right_explain": right_explain,
                            "pair_explain": pair_explain,
                            "config_params": p3_settings
                        }
                    )
                
                logger.info(f"Primer3 returned {num_returned} pairs.")
                return data
            else:
                raise ToolExecutionError(f"Primer3 failed: {result_wrapper['error']}", "ERR_TOOL_P3_001")
        else:
            # Should not happen if process exited cleanly without putting to queue
            raise ToolExecutionError("Primer3 process exited without returning result.", "ERR_TOOL_P3_CRASH")
