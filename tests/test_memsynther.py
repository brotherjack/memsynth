import itertools
from numpy import nan
import pytest

from memsynth import exceptions, config
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
    assert memsynther_ideallist.check_membership_list_on_parameters() == True

@pytest.mark.usefixtures("memsynther_less_than_ideallist")
def test_verify_memlist_data_integrity_on_less_than_ideal_list(memsynther_less_than_ideallist):
    assert memsynther_less_than_ideallist.check_membership_list_on_parameters() == False

@pytest.mark.usefixtures("memsynther")
def test_verify_memlist_data_integrity_on_normal_list(memsynther):
    with pytest.raises(exceptions.MembershipListIntegrityExcepton):
        memsynther.check_membership_list_on_parameters()

@pytest.mark.parametrize(
    'col', config.EXPECTED_FORMAT_MEM_LIST['columns']
)
@pytest.mark.usefixtures("memsynther_ideallist")
def test_check_ideal(memsynther_ideallist, col):
    assert memsynther_ideallist.expectations[col].check(memsynther_ideallist.df[col])

@pytest.mark.parametrize(
    'col, expected_number_of_failures',
    [("last_name", 1), ("Mobile_Phone", 1), ("Home_Phone", 2)]
)
@pytest.mark.usefixtures("memsynther")
def test_get_a_failure(memsynther, col, expected_number_of_failures):
    with pytest.raises(exceptions.MembershipListIntegrityExcepton):
        memsynther.check_membership_list_on_parameters()
    num_of_fails = len([f for _, f in memsynther.get_failures(col)])
    assert num_of_fails == expected_number_of_failures

@pytest.mark.parametrize(
    'col',
    set(config.EXPECTED_FORMAT_MEM_LIST).difference(fixtures.FAIL_COLS)
)
@pytest.mark.usefixtures("memsynther")
def test_get_a_failure_that_is_actually_a_success(memsynther, col):
    # Every column should produce 0 errors
    with pytest.raises(exceptions.MembershipListIntegrityExcepton):
        memsynther.check_membership_list_on_parameters()
    fails = len([f for _, f in memsynther.get_failures(col)])
    assert fails == 0

@pytest.mark.parametrize(
    'col1,fails1,col2,fails2',
    [
        ('last_name', 1, 'Mobile_Phone', 1),
        ('last_name', 1, 'Home_Phone', 2),
        ('Mobile_Phone', 1, 'Home_Phone', 2)
    ]
)
@pytest.mark.usefixtures("memsynther")
def test_get_multiple_failures(memsynther, col1, fails1, col2, fails2):
    with pytest.raises(exceptions.MembershipListIntegrityExcepton):
        memsynther.check_membership_list_on_parameters()
    fails = memsynther.return_failure_dict([col1, col2])
    assert len(fails.keys()) == 2 and len(fails[col1]) == fails1 and \
           len(fails[col1]) == fails1


@pytest.mark.usefixtures("memsynther")
def test_get_all_failures(memsynther):
    with pytest.raises(exceptions.MembershipListIntegrityExcepton):
        memsynther.check_membership_list_on_parameters()
    fails = memsynther.return_failure_dict()
    num_of_fails = len([x for x in itertools.chain.from_iterable(fails.values())])
    assert len(fails.keys()) == len(fixtures.FAIL_COLS) and \
           num_of_fails == fixtures.NUM_HARD_FAILS

@pytest.mark.usefixtures("memsynther_ideallist")
def test_check_nullable_is_successful_after_load(memsynther_ideallist):
    memsynther_ideallist.df.at[1, "AK_ID"] = nan # This column should not be null
    with pytest.raises(exceptions.MembershipListIntegrityExcepton):
        memsynther_ideallist.check_membership_list_on_parameters()

@pytest.mark.usefixtures("memsynther")
def test_memsynther_ignores_soft_falures_when_not_being_a_strict_asshole(memsynther):
    assert memsynther.check_membership_list_on_parameters(strict=False)
