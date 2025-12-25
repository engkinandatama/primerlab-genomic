"""
Tests for Overlap Detection module.
"""

import pytest
from primerlab.core.compat_check.overlap_detection import (
    check_overlap,
    analyze_overlaps,
    PredictedAmplicon,
    AmpliconOverlap,
    OverlapAnalysisResult,
)


class TestCheckOverlap:
    def test_no_overlap(self):
        has_overlap, start, end, length = check_overlap(0, 100, 200, 300)
        assert not has_overlap
        assert length == 0
    
    def test_partial_overlap(self):
        has_overlap, start, end, length = check_overlap(0, 150, 100, 200)
        assert has_overlap
        assert start == 100
        assert end == 150
        assert length == 50
    
    def test_contained_overlap(self):
        has_overlap, start, end, length = check_overlap(0, 300, 100, 200)
        assert has_overlap
        assert start == 100
        assert end == 200
        assert length == 100
    
    def test_adjacent_no_overlap(self):
        has_overlap, start, end, length = check_overlap(0, 100, 100, 200)
        assert not has_overlap


class TestAnalyzeOverlaps:
    def test_no_overlaps(self):
        amplicons = [
            PredictedAmplicon("A", 0, 100, 100, "ATGC", "FWD", "REV", True),
            PredictedAmplicon("B", 200, 300, 100, "ATGC", "FWD", "REV", True),
        ]
        overlaps = analyze_overlaps(amplicons)
        assert len(overlaps) == 0
    
    def test_with_overlap(self):
        amplicons = [
            PredictedAmplicon("A", 0, 150, 150, "ATGC", "FWD", "REV", True),
            PredictedAmplicon("B", 100, 250, 150, "ATGC", "FWD", "REV", True),
        ]
        overlaps = analyze_overlaps(amplicons, min_overlap_warning=20)
        assert len(overlaps) == 1
        assert overlaps[0].overlap_length == 50
        assert overlaps[0].is_problematic
    
    def test_failed_amplicons_excluded(self):
        amplicons = [
            PredictedAmplicon("A", 0, 150, 150, "ATGC", "FWD", "REV", True),
            PredictedAmplicon("B", 100, 250, 150, "ATGC", "FWD", "REV", False, "Error"),
        ]
        overlaps = analyze_overlaps(amplicons)
        assert len(overlaps) == 0


class TestOverlapAnalysisResult:
    def test_to_dict(self):
        result = OverlapAnalysisResult(
            template_name="test",
            template_length=1000,
            amplicons=[],
            overlaps=[],
            has_problems=False,
            warnings=[]
        )
        d = result.to_dict()
        assert d["template_name"] == "test"
        assert d["template_length"] == 1000
        assert d["has_problems"] == False
