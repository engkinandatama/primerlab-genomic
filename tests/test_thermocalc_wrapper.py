import pytest
from primerlab.core.tools.thermocalc_wrapper import ThermocalcWrapper, ThermoResult

def test_thermocalc_init_default():
    """Test initialization with default parameters."""
    wrapper = ThermocalcWrapper()
    assert wrapper.mv_conc == 50.0
    assert wrapper.dv_conc == 1.5
    assert wrapper.dntp_conc == 0.6
    assert wrapper.dna_conc == 50.0
    assert wrapper.tm_method == 'santalucia'
    assert wrapper.salt_corrections == 'santalucia'

def test_thermocalc_init_custom():
    """Test initialization with custom parameters."""
    wrapper = ThermocalcWrapper(
        mv_conc=60.0,
        dv_conc=2.0,
        dntp_conc=0.8,
        dna_conc=100.0,
        tm_method='breslauer',
        salt_corrections='owczarzy'
    )
    assert wrapper.mv_conc == 60.0
    assert wrapper.dv_conc == 2.0
    assert wrapper.tm_method == 'breslauer'
    assert wrapper.salt_corrections == 'owczarzy'

def test_calc_tm():
    """Test basic Tm calculation."""
    wrapper = ThermocalcWrapper()
    tm = wrapper.calc_tm("ATGCGTACGTAGCTAGCT")
    assert isinstance(tm, float)
    assert tm > 0.0

def test_calc_hairpin():
    """Test hairpin calculation."""
    wrapper = ThermocalcWrapper()
    # Sequence likely to form a hairpin
    res = wrapper.calc_hairpin("GCGCGCGCGCGCGCGC")
    assert isinstance(res, ThermoResult)
    assert isinstance(res.tm, float)
    assert isinstance(res.dg, float)
    assert isinstance(res.structure_found, bool)

def test_calc_homodimer():
    """Test homodimer calculation."""
    wrapper = ThermocalcWrapper()
    res = wrapper.calc_homodimer("ATGCGTACGTAGCTAGCT")
    assert isinstance(res, ThermoResult)
    assert isinstance(res.tm, float)

def test_calc_heterodimer():
    """Test heterodimer calculation."""
    wrapper = ThermocalcWrapper()
    res = wrapper.calc_heterodimer("ATGCGTACGTAGCTAGCT", "CGCTAGCTAGCTACGTAG")
    assert isinstance(res, ThermoResult)
    assert isinstance(res.tm, float)

def test_calc_end_stability():
    """Test end stability calculation."""
    wrapper = ThermocalcWrapper()
    res = wrapper.calc_end_stability("ATGCGTACGTAGCTAGCT")
    assert isinstance(res, ThermoResult)
    assert isinstance(res.dg, float)
    assert res.structure_found is True
