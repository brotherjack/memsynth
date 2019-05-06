import pytest
import pandas as pd

from memsynth import exceptions, config
try:
    import tests.conftest as fixtures
except:
    import conftest as fixtures


@pytest.mark.usefixtures("memsynther")
def test_load_bad_excel_file(memsynther):
    """Make sure that program can identify when the file is completely wrong

    This test requires the "badlist.xlsx" file with the first row containing
    nothing matching the expected columns
    """
    with pytest.raises(exceptions.LoadMembershipListException) as ex:
        memsynther.load_from_excel(fixtures.BAD_MEM_LIST)
    assert "None of the columns match." in str(ex.value)

def test_load_excel_file():
    """Checks to make sure that the membership file can be loaded

    This test requires the "fakeodsa.xlsx" file with an `AK_ID` column
    """
    df = pd.read_excel(fixtures.FAKE_MEM_LIST)
    assert "AK_ID" in df.columns

@pytest.mark.usefixtures("memsynther")
def test_incorrect_column_headers(memsynther):
    """Makes sure that MemSynther notices when the column headers are wrong"""
    with pytest.raises(exceptions.LoadMembershipListException) as ex:
        # Fuck up the data, then explicitly call the verification function
        memsynther.df.rename({"AK_ID": "NARBAR"}, axis=1, inplace=True)
        memsynther._verify_memlist_format()
        assert "missing the following columns 'AK_ID'" in str(ex.value)


@pytest.mark.parametrize(
    'col, add_or_del', [
        ("AK_ID", "del"),
        ("DERP", "add"),
        (("AK_ID", "DERP"), 'add_and_del')
    ]
)
@pytest.mark.usefixtures("memsynther")
def test_wrong_number_of_cols(memsynther, col, add_or_del):
    with pytest.raises(exceptions.LoadMembershipListException) as ex:
        if add_or_del == 'add':
            memsynther.df[col] = [[]] * len(memsynther.df)
        elif add_or_del == 'del':
            memsynther.df.drop(col, 1, inplace=True)
        else:
            memsynther.df[col[1]] = [[]] * len(memsynther.df)
            memsynther.df.drop(col[0], 1, inplace=True)

        memsynther._verify_memlist_format()

    # Check error messages to make sure they are correct
    if add_or_del == 'add':
        assert "added new columns" in str(ex.value)
    elif add_or_del == 'del':
        assert "appears to be missing" in str(ex.value)
    else:
        assert "added new columns" in str(ex.value) and \
            "appears to be missing" in str(ex.value)

@pytest.mark.usefixtures("memsynther")
def test_load_expectation_json_file_successful(memsynther):
    expected_cols = config.EXPECTED_FORMAT_MEM_LIST.get("columns")
    memsynther.load_expectations_from_json(fixtures.PARAM_JSON_FILE)
    assert len(memsynther.expectations.keys()) == len(expected_cols)

@pytest.mark.usefixtures("memsynther")
def test_softload_verify_memlist_format(memsynther):
    memsynther.df['extraneousCol'] = [[]] * len(memsynther.df)
    df = memsynther._verify_memlist_format()
    assert hasattr(df, 'columns')
