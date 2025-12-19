"""
Tests for v0.2.1 features: IUPAC support and Circular Template detection.
"""

import pytest
from primerlab.core.insilico.engine import (
    InsilicoPCR,
    calculate_match_percent,
    find_binding_sites,
    predict_products,
    DEFAULT_INSILICO_PARAMS
)
from primerlab.core.insilico.binding import analyze_binding
from primerlab.core.sequence import reverse_complement, bases_match

# Test data
DEGENERATE_TEMPLATE = "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTT"
# R = A or G. S = G or C.
DEGENERATE_PRIMER = "ATGAGTRNAS" 

CIRCULAR_TEMPLATE = "ATGAGTAAAG" # 10bp
# Primer matches E-A junction: AG + ATGA = AGATGA
# If reversed: AGATG ... 
WRAP_PRIMER = "AAGATGAGTA" # Matches end (AAG) + start (ATGAGTA)

def test_bases_match():
    """Verify semantic matching of IUPAC bases."""
    assert bases_match('A', 'A') is True
    assert bases_match('A', 'G') is False
    assert bases_match('R', 'A') is True
    assert bases_match('R', 'G') is True
    assert bases_match('R', 'C') is False
    assert bases_match('N', 'T') is True
    assert bases_match('Y', 'C') is True
    assert bases_match('Y', 'T') is True
    assert bases_match('S', 'G') is True
    assert bases_match('S', 'C') is True

def test_calculate_match_percent_iupac():
    """Verify IUPAC aware match calculation."""
    # R (A/G) vs A -> Match
    pct, mm, tp = calculate_match_percent("ATGR", "ATGA")
    assert pct == 100.0
    assert mm == 0
    assert tp == 4
    
    # R (A/G) vs T -> Mismatch
    pct, mm, tp = calculate_match_percent("ATGR", "ATGT")
    assert pct == 75.0
    assert mm == 1
    assert tp == 0 # 3' mismatch (R vs T)

def test_degenerate_primer_binding():
    """Verify that degenerate primers bind correctly."""
    params = {**DEFAULT_INSILICO_PARAMS, "min_total_match_percent": 90}
    # ATGAGTAAAG (template)
    # ATGAGTRNAS (primer)
    # R(A/G) matches A(7th)
    # N matches A(8th)
    # A matches A(9th)
    # S(G/C) matches G(10th)? No, S is G/C. Template matches.
    
    # Let's use simpler one
    primer = "ATGAGTR" # R matches A
    template = "ATGAGTAAAAA"
    
    bindings = find_binding_sites(
        primer_seq=primer,
        template_seq=template,
        primer_name="Degen",
        strand='+',
        params=params
    )
    assert len(bindings) >= 1
    assert bindings[0].match_percent == 100.0

def test_circular_template_binding():
    """Verify primer binding across the start-end boundary."""
    # Template: ATGAGTAAAG (10bp)
    # Primer: AAGATGAG (8bp)
    # Template doubled: ATGAGTAAAGATGAGTAAAG
    #                   01234567890123456789
    #                             AAGATGAG (matches at index 7)
    # Index 7 in doubled template is "AAG" (pos 7,8,9) + "ATGAG" (pos 0,1,2,3,4)
    
    primer = "AAGATGAG"
    template = "ATGAGTAAAG"
    
    # Normal (non-circular) should fail
    params_normal = {**DEFAULT_INSILICO_PARAMS, "circular": False}
    bindings_normal = find_binding_sites(primer, template, "Wrap", '+', params_normal)
    assert len(bindings_normal) == 0
    
    # Circular should succeed
    params_circular = {**DEFAULT_INSILICO_PARAMS, "circular": True}
    bindings_circular = find_binding_sites(primer, template, "Wrap", '+', params_circular)
    assert len(bindings_circular) >= 1
    assert bindings_circular[0].position == 7

def test_weighted_scoring_mismatches():
    """Verify that 3' mismatches penalize more than 5' mismatches."""
    engine = InsilicoPCR()
    template = "ATGAGTAAAGGAGAAGAACTTTTC"
    
    # Case A: Mismatch at 5' end (first base)
    # Template start: ATGAGT...
    # Primer A:       GTGAGT...
    primer_5p_mm = "G" + template[1:20]
    
    # Case B: Mismatch at 3' end (last base)
    # Template end: ...CTTTTC
    # Primer B:     ...CTTTTG
    primer_3p_mm = template[0:19] + "G"
    
    # For comparison, we need to manually create bindings or run engine
    # Actually, predict_products calculates likelihood
    
    # Relax parameters to ensure we find sites despite mismatches and short amplicons
    params = {
        **DEFAULT_INSILICO_PARAMS, 
        "min_3prime_match": 0, 
        "min_total_match_percent": 70,
        "product_size_min": 10
    }
    
    # Binder 5p mm
    fwd_5p = find_binding_sites(primer_5p_mm, template, "5p", '+', params)[0]
    # Binder 3p mm
    fwd_3p = find_binding_sites(primer_3p_mm, template, "3p", '+', params)[0]
    
    # Mock reverse binder (perfect)
    rev = find_binding_sites(reverse_complement(template[-20:]), template, "Rev", '-', params)[0]
    
    products_5p = predict_products([fwd_5p], [rev], template, params)
    products_3p = predict_products([fwd_3p], [rev], template, params)
    
    assert products_5p[0].likelihood_score > products_3p[0].likelihood_score
    print(f"5p mismatch score: {products_5p[0].likelihood_score}")
    print(f"3p mismatch score: {products_3p[0].likelihood_score}")

def test_binding_tm_3prime_penalty():
    """Verify binding Tm penalty in binding.py."""
    template = "ATGAGTAAAGGAGAAGAACTTTTC"
    
    # 5' mismatch
    primer_5p = "G" + template[1:20]
    site_5p = analyze_binding(primer_5p, template[:20], 0, '+')
    
    # 3' mismatch
    primer_3p = template[0:19] + "G"
    site_3p = analyze_binding(primer_3p, template[:20], 0, '+')
    
    # Site 3p should have lower Tm than Site 5p
    assert site_3p.binding_tm < site_5p.binding_tm
