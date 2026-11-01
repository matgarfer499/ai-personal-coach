import pytest

from coach.regioncode import real_region


@pytest.mark.parametrize("code", [None, "", "   ", "none", "NONE", " None "])
def test_no_region_spellings(code):
    assert real_region(code) is None


@pytest.mark.parametrize("code,expected", [("es", "es"), ("ES ", "es"), ("Pt-BR", "pt-br")])
def test_a_region_code_is_stripped_and_lower_cased(code, expected):
    assert real_region(code) == expected


@pytest.mark.parametrize("code", ["../x", "/abs", "es/../es", "a b", "es\\x", "e.s"])
def test_a_path_is_not_a_region_code(code):
    with pytest.raises(ValueError, match="not a region code"):
        real_region(code)
