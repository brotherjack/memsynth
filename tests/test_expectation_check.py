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

@pytest.mark.usefixtures("correct_ak_id_exp")
def test_incorrect_expectation_fails(correct_ak_id_exp):
    assert hasattr(correct_ak_id_exp, "check")
    assert correct_ak_id_exp.check(fixtures.AK_ID_INCORRECT_DATA) == False

@pytest.mark.usefixtures("correct_ak_id_exp")
def test_fails_nullable_expectation(correct_ak_id_exp):
    if hasattr(correct_ak_id_exp, "check"):
        correct_ak_id_exp.check(fixtures.AK_ID_CORRECT_DATA)
        if len(correct_ak_id_exp.fails) > 0:
            for fail in correct_ak_id_exp.fails:
                if "nullable" in fail.msg:
                    assert True
            assert False, "There should be a nullable failure"
        else:
            assert False, "There are no failures"

    else:
        assert False, "correct_ak_id_exp does not have a check parameter"

@pytest.mark.usefixtures("memsynther")
def test_verification_of_data_integrity(memsynther):
    assert False

def test_soft_expectation_fails():
    assert False

def test_soft_expectation_passes():
    assert False