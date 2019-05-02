import os
import re

import numpy as np
import pytest

from memsynth.main import MemSynther, MemExpectation, Parameter
from memsynth import config


AK_ID_CORRECT = (
    Parameter(name="data_type", value="integer"),
    Parameter(name="regex", value=re.compile("[0-9]+")),
    Parameter(name="nullable", value=False),
)

ADDRESS_PARAMS = (
    Parameter(name="data_type", value="string"),
    Parameter(
        name="regex", value=re.compile("\d+[ \t]+[sSnNwWEe]{0,1}[ \tA-Za-z]+"), soft=True
    ),
    Parameter(name="nullable", value=False),
)

AK_ID_CORRECT_DATA = ["127296", "5508", "94792"]
AK_ID_INCORRECT_DATA = ["127296", "d%sq+`1", "5508", "94792", "De32"]
DSA_ID_CORRECT_DATA = ["121227", np.nan, "117722", np.nan]
ADDRESSES = [
    "6123 NOBLE AVE",
    "444 S BUM AVE APT D",
    "4932 Data Dr",
    "4444 Fake Way, Apt.4",
    "87 Nope Ln #32",
    "P.O. Box 7621"
]
ADDRESSES_SOFT_FAILS = 1
FAKE_MEM_LIST = os.path.join(config.TEST_DIR, "fakeodsa.xlsx")
BAD_MEM_LIST = os.path.join(config.TEST_DIR, "badlist.xlsx")

@pytest.fixture
def memsynther():
    memsynth = MemSynther()
    memsynth.load_from_excel(FAKE_MEM_LIST)
    return memsynth

@pytest.fixture
def correct_ak_id_exp():
    return MemExpectation('AK_ID', AK_ID_CORRECT)

@pytest.fixture
def address_exp():
    return MemExpectation('Address', ADDRESS_PARAMS)
