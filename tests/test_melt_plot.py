"""
Unit tests for melt curve visualization (v0.6.0 Phase 3).
"""

import pytest
import os
import tempfile
from primerlab.core.qpcr.melt_plot import (
    generate_melt_svg,
    generate_melt_png,
    annotate_peaks,
)
from primerlab.core.qpcr.melt_curve import predict_melt_curve


class TestGenerateMeltSvg:
    """Test SVG melt curve generation."""
    
    def test_basic_svg_generation(self):
        """Test basic SVG generation."""
        melt_curve = [
            {"temperature": 70 + i, "derivative": 0.1 * i if i < 10 else 0.1 * (20 - i)}
            for i in range(21)
        ]
        peaks = [{"temperature": 80.0, "is_primary": True}]
        
        svg = generate_melt_svg(
            melt_curve=melt_curve,
            peaks=peaks,
            predicted_tm=80.0,
        )
        
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "80.0°C" in svg
    
    def test_svg_with_file_output(self):
        """Test SVG saved to file."""
        melt_curve = [
            {"temperature": 65 + i * 0.5, "derivative": 0.05 * i if i < 30 else 0.05 * (60 - i)}
            for i in range(61)
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            output_path = f.name
        
        try:
            svg = generate_melt_svg(
                melt_curve=melt_curve,
                peaks=[],
                predicted_tm=80.0,
                output_path=output_path,
            )
            
            assert os.path.exists(output_path)
            with open(output_path, 'r') as f:
                content = f.read()
            assert "<svg" in content
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_svg_multiple_peaks(self):
        """Test SVG with multiple peaks."""
        melt_curve = [
            {"temperature": 70 + i, "derivative": 0.1 * i if i < 10 else 0.1 * (20 - i)}
            for i in range(21)
        ]
        peaks = [
            {"temperature": 80.0, "is_primary": True},
            {"temperature": 75.0, "is_primary": False},
        ]
        
        svg = generate_melt_svg(
            melt_curve=melt_curve,
            peaks=peaks,
            predicted_tm=80.0,
        )
        
        assert "80.0°C" in svg
        assert "75.0°C" in svg
    
    def test_empty_curve(self):
        """Test with empty curve."""
        svg = generate_melt_svg(
            melt_curve=[],
            peaks=[],
            predicted_tm=80.0,
        )
        
        assert svg == ""


class TestGenerateMeltPng:
    """Test PNG melt curve generation."""
    
    def test_png_generation(self):
        """Test PNG generation (requires matplotlib)."""
        melt_curve = [
            {"temperature": 70 + i, "derivative": 0.1 * i if i < 10 else 0.1 * (20 - i)}
            for i in range(21)
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output_path = f.name
        
        try:
            result = generate_melt_png(
                melt_curve=melt_curve,
                peaks=[{"temperature": 80.0, "is_primary": True}],
                predicted_tm=80.0,
                output_path=output_path,
            )
            
            # May fail if matplotlib not available
            if result:
                assert os.path.exists(output_path)
                assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_png_empty_curve(self):
        """Test with empty curve."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output_path = f.name
        
        try:
            result = generate_melt_png(
                melt_curve=[],
                peaks=[],
                predicted_tm=80.0,
                output_path=output_path,
            )
            
            assert result == False
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


class TestAnnotatePeaks:
    """Test peak annotation generation."""
    
    def test_single_peak_annotation(self):
        """Test single peak annotation."""
        peaks = [{"temperature": 80.0, "is_primary": True}]
        
        annotations = annotate_peaks(peaks, is_single_peak=True)
        
        assert len(annotations) >= 1
        assert any("Single peak" in a for a in annotations)
        assert any("80.0" in a for a in annotations)
    
    def test_multiple_peaks_annotation(self):
        """Test multiple peaks annotation."""
        peaks = [
            {"temperature": 80.0, "is_primary": True},
            {"temperature": 72.0, "is_primary": False},
        ]
        
        annotations = annotate_peaks(peaks, is_single_peak=False)
        
        assert any("Multiple peaks" in a for a in annotations)
        assert any("Secondary" in a for a in annotations)


class TestIntegrationWithMeltCurve:
    """Test integration with predict_melt_curve."""
    
    def test_svg_from_prediction(self):
        """Test SVG generation from melt curve prediction."""
        amplicon = "ATGC" * 30  # 120bp
        
        result = predict_melt_curve(amplicon)
        
        svg = generate_melt_svg(
            melt_curve=result.melt_curve,
            peaks=[p.to_dict() for p in result.peaks],
            predicted_tm=result.predicted_tm,
            title=f"Melt Curve - Tm: {result.predicted_tm:.1f}°C",
        )
        
        assert "<svg" in svg
        assert f"{result.predicted_tm:.1f}" in svg
