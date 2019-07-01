import pytest

try:
    import tests.conftest as fixtures
except:
    import conftest as fixtures


@pytest.mark.usefixtures('memsynther')
def test_memsynther_loads_strings_correctly(memsynther):
    # First name's data_type in param.json is 'string'
    assert memsynther.df.first_name.dtype == 'object'

@pytest.mark.usefixtures('memsynther')
def test_memsynther_loads_default_integer_as_int64(memsynther):
    # There is a difference between 'Int64' and 'int64'
    # More here: https://pandas.pydata.org/pandas-docs/version/0.24/whatsnew/v0.24.0.html#optional-integer-na-support
    assert memsynther.df.AK_ID.dtype == 'Int64'

@pytest.mark.usefixtures('memsynther')
def test_memsynther_loads_object_as_string(memsynther):
    # Last name's data_type in param.json is 'object'
    assert memsynther.df.last_name.dtype == 'object'

@pytest.mark.usefixtures('memsynther')
def test_memsynther_loads_booleans_correctly(memsynther):
    assert memsynther.df.Do_Not_Call.dtype == 'bool'

@pytest.mark.usefixtures('memsynther')
def test_memsynther_loads_datetimes_correctly(memsynther):
    assert memsynther.df.Xdate.dtype == "datetime64[ns]"

@pytest.mark.usefixtures("memsynther_ideallist")
def test_verify_memlist_data_integrity_on_ideal_list(memsynther_ideallist):
    assert memsynther_ideallist.verify_memlist_data_integrity() == True

@pytest.mark.usefixtures("memsynther_ideallist")
def test_verify_memlist_data_integrity_on_less_than_ideal_list(memsynther):
    assert memsynther.verify_memlist_data_integrity() == False
