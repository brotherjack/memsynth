import pytest

from memsynth import exceptions
from memsynth.main import MemExpectation, Parameter
import tests.conftest as fixtures


def test_expectation_encounters_an_incorrect_parameter():
    with pytest.raises(exceptions.MemExpectationFormationError) as ex:
        MemExpectation(
            "AK_ID", {
                    Parameter(name="data_type", value="integer"),
                    Parameter(name="bad_param", value="not_good")
                }
        )
        assert "bad_param is not a recognized col." in str(ex.value)

@pytest.mark.usefixtures("correct_ak_id_exp")
def test_correct_expectation_forms(correct_ak_id_exp):
    assert correct_ak_id_exp.is_an_expectation

@pytest.mark.usefixtures("correct_ak_id_exp")
def test_correct_regex_expectation_condition_passes(correct_ak_id_exp):
    assert correct_ak_id_exp._check_regex("12345")

@pytest.mark.usefixtures("correct_ak_id_exp")
def test_correct_expectation_passes(correct_ak_id_exp):
    assert hasattr(correct_ak_id_exp, "check") and \
           correct_ak_id_exp.check(fixtures.AK_ID_CORRECT_DATA)

@pytest.mark.usefixtures("memsynther")
def test_verification_of_data_integrity(memsynther):
    assert False
