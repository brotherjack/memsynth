import pytest

try:
    import tests.conftest as fixtures
except:
    import conftest as fixtures


@pytest.mark.usefixtures('memsynther')
def test_memsynther_loads_strings_correctly(memsynther):
    assert memsynther.df.first_name.dtype == 'object'
