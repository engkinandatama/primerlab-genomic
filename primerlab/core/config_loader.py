import yaml
import copy
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import ConfigError
from .logger import get_logger

logger = get_logger()

def load_yaml(path: str) -> Dict[str, Any]:
    """Loads a YAML file safely."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}", "ERR_CONFIG_001")
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML syntax in {path}: {e}", "ERR_CONFIG_002")

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges two dictionaries.
    - Dicts are merged.
    - Lists and scalars in 'override' replace 'base'.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result

def validate_config(config: Dict[str, Any]):
    """
    Validates the merged configuration against required schema.
    """
    required_keys = ["workflow", "input", "parameters", "output"]
    for key in required_keys:
        if key not in config:
            raise ConfigError(f"Missing required config section: '{key}'", "ERR_CONFIG_003")
            
    # Validate workflow name
    if not config.get("workflow"):
        raise ConfigError("Workflow name cannot be empty", "ERR_CONFIG_004")

    # Validate output directory
    if not config["output"].get("directory"):
        raise ConfigError("Output directory must be specified", "ERR_CONFIG_005")

def load_and_merge_config(workflow: str, user_config_path: Optional[str] = None, cli_overrides: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Main entry point for config loading.
    1. Load default config for the workflow.
    2. Load user config (if provided).
    3. Apply CLI overrides.
    4. Validate.
    """
    # 1. Load Default Config
    # Assuming default configs are in primerlab/config/<workflow>_default.yaml
    base_path = Path(__file__).parent.parent / "config" / f"{workflow}_default.yaml"
    
    if not base_path.exists():
        raise ConfigError(f"Default config for workflow '{workflow}' not found at {base_path}", "ERR_CONFIG_006")
        
    logger.debug(f"Loading default config from {base_path}")
    final_config = load_yaml(str(base_path))

    # 2. Load User Config
    if user_config_path:
        logger.info(f"Loading user config from {user_config_path}")
        user_config = load_yaml(user_config_path)
        final_config = deep_merge(final_config, user_config)

    # 3. Apply CLI Overrides
    if cli_overrides:
        logger.debug("Applying CLI overrides")
        final_config = deep_merge(final_config, cli_overrides)

    # 4. Process Enhancements (Presets & Product Size)
    final_config = _process_enhancements(final_config)

    # 5. Validate
    validate_config(final_config)
    
    return final_config

def _process_enhancements(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies v0.1.1 enhancements:
    1. Presets (e.g., preset: "long_range")
    2. product_size (min/opt/max) -> product_size_range
    """
    params = config.get("parameters", {})
    
    # 1. Presets
    preset = config.get("preset")
    if preset:
        logger.info(f"Applying preset: {preset}")
        if preset == "long_range":
            # Long-range PCR defaults
            params["product_size"] = {"min": 1000, "opt": 2000, "max": 3000}
            params["tm"] = {"min": 60.0, "opt": 62.0, "max": 65.0} # Higher Tm for long PCR
        elif preset == "standard_pcr":
             params["product_size"] = {"min": 100, "opt": 200, "max": 600}
        # Add more presets here as needed
        
    # 2. product_size -> product_size_range
    # Primer3 expects [[min, max]] for PRIMER_PRODUCT_SIZE_RANGE
    # We support user-friendly product_size: {min: X, opt: Y, max: Z}
    
    p_size = params.get("product_size")
    p_range = params.get("product_size_range")
    
    if p_size and not p_range:
        # Convert user-friendly size to range format
        # Note: Primer3 takes a list of ranges. We use min-max.
        min_s = p_size.get("min", 100)
        max_s = p_size.get("max", 300)
        params["product_size_range"] = [[min_s, max_s]]
        logger.debug(f"Converted product_size {p_size} to range [[{min_s}, {max_s}]]")
        
    return config
