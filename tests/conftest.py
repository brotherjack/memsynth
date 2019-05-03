import os
import re

import numpy as np
import pytest

from memsynth.main import MemSynther, MemExpectation
from memsynth.parameters import Parameter
from memsynth import config


AK_ID_CORRECT = (
    Parameter(name="data_type", value="integer"),
    Parameter(name="regex", value=re.compile("[0-9]+")),
    Parameter(name="nullable", value=False),
)

ADDRESS_PARAMS = (
    Parameter(name="data_type", value="string"),
    Parameter(name="nullable", value=False),
)

ADDRESS_PARAMS_FULL_MATCH = tuple(
    list(ADDRESS_PARAMS) + [
    Parameter(
        name="regex",
        value=re.compile("\d+[ \t]+[sSnNwWEe]{0,1}[ \tA-Za-z]+"),
        soft=True,
        args={'match': 'full'}
    ),
])

ADDRESS_PARAMS_PARTIAL_MATCH = tuple(
    list(ADDRESS_PARAMS) + [
    Parameter(
        name="regex",
        value=re.compile("\d+[ \t]+[sSnNwWEe]{0,1}[ \tA-Za-z]+"),
        soft=True,
    ),
])

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
ADDRESSES_SOFT_FAILS_PARTIAL_MATCH = 1
ADDRESSES_SOFT_FAILS_FULL_MATCH = 3
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
def address_partial_exp():
    return MemExpectation('Address', ADDRESS_PARAMS_PARTIAL_MATCH)

@pytest.fixture
def address_full_exp():
    return MemExpectation('Address', ADDRESS_PARAMS_FULL_MATCH)
