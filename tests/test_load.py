import pytest
import pandas as pd


def test_load_excel_file():
    df = pd.read_excel("fakeodsa.xlsx")
    assert "AK_ID" in df.columns
