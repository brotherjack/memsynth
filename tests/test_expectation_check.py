from numpy import nan
import pytest

from memsynth import exceptions
from memsynth.main import MemExpectation, Parameter

try:
    import tests.conftest as fixtures
except:
    import conftest as fixtures


def test_expectation_encounters_an_incorrect_parameter():
    with pytest.raises(exceptions.MemExpectationFormationError) as ex:
        MemExpectation(
            "AK_ID", **{
                    "parameters": [
                        dict(name="data_type", value="integer"),
                        dict(name="bad_param", value="not_good")
                    ],
                    "required": True
                }
        )
        assert "bad_param is not a recognized col." in str(ex.value)

@pytest.mark.usefixtures("correct_ak_id_exp")
def test_correct_expectation_forms(correct_ak_id_exp):
    assert correct_ak_id_exp.is_an_expectation

@pytest.mark.usefixtures("correct_ak_id_exp")
def test_correct_regex_expectation_condition_passes(correct_ak_id_exp):
    assert correct_ak_id_exp._check_regex("12345", 1)

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
        # DSA ID has null values, which correct AK ID columns should not have
        correct_ak_id_exp.check(fixtures.DSA_ID_CORRECT_DATA)
        if len(correct_ak_id_exp.fails) > 0:
            for fail in correct_ak_id_exp.fails:
                if "nullable" in [whys.name for whys in fail.why]:
                    assert True
                else:
                    assert False, "There should be a nullable failure"
        else:
            assert False, "There are no failures"

    else:
        assert False, "correct_ak_id_exp does not have a check parameter"

@pytest.mark.usefixtures("address_partial_exp")
def test_soft_expectation_partial_match(address_partial_exp):
    address_partial_exp.check(fixtures.ADDRESSES)
    assert len(address_partial_exp.soft_fails) == fixtures.ADDRESSES_SOFT_FAILS_PARTIAL_MATCH

@pytest.mark.usefixtures("address_full_exp")
def test_soft_expectation_full_match(address_full_exp):
    address_full_exp.check(fixtures.ADDRESSES)
    assert len(address_full_exp.soft_fails) == fixtures.ADDRESSES_SOFT_FAILS_FULL_MATCH

@pytest.mark.usefixtures("address_full_exp")
def test_soft_expectation_and_hard_at_same_time(address_full_exp):
    NUMBER_OF_NULLS = 2
    address_full_exp.check(fixtures.ADDRESSES + [nan]*NUMBER_OF_NULLS)
    assert len(address_full_exp.soft_fails) == fixtures.ADDRESSES_SOFT_FAILS_FULL_MATCH
    assert len(address_full_exp.fails) == NUMBER_OF_NULLS

def test_regex_parameter_compilation():
    exp = MemExpectation(
        "AK_ID", **dict(
            parameters=[
                dict(name="data_type", value="integer"),
                dict(name="regex", value="[0-9]+"),
                dict(name="nullable", value=False)
            ],
            required=True)
    )
    assert exp.check(["3"])

@pytest.mark.usefixtures('correct_ak_id_exp')
def test_nullable_fail_properly(correct_ak_id_exp):
    chk = correct_ak_id_exp.check(["12345", nan])
    assert not chk and "nullable" in [
        n.name for f in correct_ak_id_exp.fails for n in f.why
    ]

@pytest.mark.usefixtures("memsynther")
def test_verify_memlist_data_integrity(memsynther):
    assert False
