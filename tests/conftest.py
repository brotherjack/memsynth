import os

import numpy as np
import pytest

from memsynth.main import MemSynther, MemExpectation, Parameter
from memsynth import config


AK_ID_CORRECT = (
    Parameter(name="data_type", value="integer"),
    Parameter(name="regex", value="[0-9]+"),
    Parameter(name="nullable", value=False),
)

AK_ID_CORRECT_DATA = ["127296", "5508", "94792"]
AK_ID_INCORRECT_DATA = ["127296", "d%sq+`1", "5508", "94792", "De32"]
DSA_ID_CORRECT_DATA = ["121227", np.nan, "117722", np.nan]
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
