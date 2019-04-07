import os

import pandas as pd

from memsynth import config


def test_load_excel_file():
    """Checks to make sure that the membership file can be loaded

    This test requires the "fakeodsa.xlsx" file with an `AK_ID` column
    """
    path = os.path.join(config.TEST_DIR, "fakeodsa.xlsx")
    df = pd.read_excel(path)
    assert "AK_ID" in df.columns
