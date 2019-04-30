import os

import pandas as pd
import pytest

from memsynth import config
from memsynth import exceptions
from memsynth.main import MemSynther, MemExpectation

FAKE_MEM_LIST = os.path.join(config.TEST_DIR, "fakeodsa.xlsx")
BAD_MEM_LIST = os.path.join(config.TEST_DIR, "badlist.xlsx")

AK_ID_CORRECT = {
    "data_type": "integer",
    "regex": "[0-9]+",
    "nullable": False
}

@pytest.fixture
def memsynther():
    memsynth = MemSynther()
    memsynth.load_from_excel(FAKE_MEM_LIST)
    return memsynth

def test_load_bad_excel_file(memsynther):
    """Make sure that program can identify when the file is completely wrong

    This test requires the "badlist.xlsx" file with the first row containing
    nothing matching the expected columns
    """
    with pytest.raises(exceptions.LoadMembershipListException) as ex:
        memsynther.load_from_excel(BAD_MEM_LIST)
        assert "None of the columns match." in str(ex.value)

def test_load_excel_file():
    """Checks to make sure that the membership file can be loaded

    This test requires the "fakeodsa.xlsx" file with an `AK_ID` column
    """
    df = pd.read_excel(FAKE_MEM_LIST)
    assert "AK_ID" in df.columns


def test_incorrect_column_headers(memsynther):
    """Makes sure that MemSynther notices when the column headers are wrong"""
    with pytest.raises(exceptions.LoadMembershipListException) as ex:
        # Fuck up the data, then explicitly call the verification function
        memsynther.df.rename({"AK_ID": "NARBAR"}, axis=1, inplace=True)
        memsynther._verify_memlist_format()


@pytest.mark.parametrize(
    'col, add_or_del', [
        ("AK_ID", "del"),
        ("DERP", "add"),
    ]
)
def test_wrong_number_of_cols(memsynther, col, add_or_del):
    with pytest.raises(exceptions.LoadMembershipListException) as ex:
        if add_or_del.startswith('add'):
            memsynther.df[col] = [[]] * len(memsynther.df)
        else:
            memsynther.df.drop(col, 1, inplace=True)

        memsynther._verify_memlist_format()

        # Check error messages to make sure they are correct
        if add_or_del.startswith('add'):
            assert "added new columns" in str(ex.value)
        else:
            assert "appears to be missing" in str(ex.value)

def test_expectation_encounters_an_incorrect_parameter():
    with pytest.raises(exceptions.MemExpectationFormationError) as ex:
        MemExpectation(
            "AK_ID", {
                    "data_type": "integer",
                    "bad_param": "not_good"
                }
        )
        assert "bad_param is not a recognized col." in str(ex.value)

def test_correct_expectation_forms():
    exp = MemExpectation('AK_ID', AK_ID_CORRECT)
    assert exp.is_an_expectation

def test_correct_regex_expectation_passes():
    exp = MemExpectation('AK_ID', AK_ID_CORRECT)
    assert hasattr(exp, "check") and exp.check()

def test_verification_of_data_integrity(memsynther):
    assert False
