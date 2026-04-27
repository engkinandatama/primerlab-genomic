import pytest
from primerlab.core.models.primer import Primer

def test_primer_no_degeneracy():
    p = Primer(id="1", sequence="ATGC", tm=60.0, gc=50.0, length=4)
    assert p.degeneracy_multiplier == 1
    assert len(p.possible_sequences) == 0

def test_primer_with_degeneracy():
    p = Primer(id="1", sequence="ATRY", tm=60.0, gc=50.0, length=4)
    # R = A/G, Y = C/T. Degeneracy = 2 * 2 = 4
    assert p.degeneracy_multiplier == 4
    assert len(p.possible_sequences) == 4
    assert "ATAC" in p.possible_sequences
    assert "ATAT" in p.possible_sequences
    assert "ATGC" in p.possible_sequences
    assert "ATGT" in p.possible_sequences

def test_primer_high_degeneracy():
    p = Primer(id="1", sequence="NNNNNNNNN", tm=60.0, gc=50.0, length=9)
    # N = 4. 4^9 = 262144
    assert p.degeneracy_multiplier == 262144
    assert "High degeneracy (>256)" in p.warnings
    assert len(p.possible_sequences) == 0

def test_primer_to_dict_degeneracy():
    p = Primer(id="1", sequence="ATRY", tm=60.0, gc=50.0, length=4)
    d = p.to_dict()
    assert d["degeneracy_multiplier"] == 4
    assert len(d["possible_sequences"]) == 4
