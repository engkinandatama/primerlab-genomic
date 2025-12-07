"""Tests for ViennaRNA fallback behavior."""
import pytest
from primerlab.core.tools.vienna_wrapper import ViennaWrapper


def test_vienna_wrapper_is_available():
    """Test that is_available property works correctly."""
    wrapper = ViennaWrapper()
    # is_available should be a boolean
    assert isinstance(wrapper.is_available, bool)


def test_vienna_fold_fallback():
    """Test that fold returns error dict when ViennaRNA is not available."""
    wrapper = ViennaWrapper()
    
    if not wrapper.is_available:
        # When ViennaRNA is not installed, should return fallback dict
        result = wrapper.fold("ATGCATGC")
        assert "error" in result
        assert result["mfe"] == 0.0
    else:
        # When ViennaRNA is installed, should return real result
        result = wrapper.fold("ATGCATGC")
        assert "mfe" in result
        assert isinstance(result["mfe"], float)


def test_vienna_cofold_fallback():
    """Test that cofold returns error dict when ViennaRNA is not available."""
    wrapper = ViennaWrapper()
    
    if not wrapper.is_available:
        # When ViennaRNA is not installed, should return fallback dict
        result = wrapper.cofold("ATGC", "GCAT")
        assert "error" in result
        assert result["mfe"] == 0.0
    else:
        # When ViennaRNA is installed, should return real result
        result = wrapper.cofold("ATGC", "GCAT")
        assert "mfe" in result
        assert isinstance(result["mfe"], float)
