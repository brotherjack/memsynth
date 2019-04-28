import os

import pandas as pd
import pytest

from memsynth import config
from memsynth import exceptions
from memsynth.main import MemSynther, MemExpectation

FAKE_MEM_LIST = os.path.join(config.TEST_DIR, "fakeodsa.xlsx")


@pytest.fixture
def memsynther():
    memsynth = MemSynther()
    memsynth.load_from_excel(FAKE_MEM_LIST)
    return memsynth


def test_load_excel_file():
    """Checks to make sure that the membership file can be loaded

    This test requires the "fakeodsa.xlsx" file with an `AK_ID` column
    """
    df = pd.read_excel(FAKE_MEM_LIST)
    assert "AK_ID" in df.columns


def test_incorrect_column_headers(memsynther):
    """Makes sure that MemSynther notices when the column headers are wrong"""
    with pytest.raises(exceptions.LoadMembershipListException):
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
    with pytest.raises(exceptions.LoadMembershipListException):
        if add_or_del.startswith('add'):
            memsynther.df[col] = [[]] * len(memsynther.df)
        else:
            memsynther.df.drop(col, 1, inplace=True)
        memsynther._verify_memlist_format()

def test_expectation_encounters_an_incorrect_parameter():
    with pytest.raises(exceptions.MemExpectationFormationError):
        MemExpectation(
            "AK_ID", {
                    "data_type": "integer",
                    "bad_param": "not_good"
                }
        )

def test_verification_of_data_integrity(memsynther):
    assert False
