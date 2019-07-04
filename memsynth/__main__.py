import logging

from memsynth.main import MemSynther
from memsynth.utils import setup_logging


if __name__ == '__main__':
    # Example from the README :P
    setup_logging(default_level=logging.CRITICAL)

    msy = MemSynther()

    # Load the expectations and the memebership list
    msy.load_expectations_from_json("tests/params.json")
    msy.load_from_excel("tests/fakeodsa.xlsx")

    # Check to make sure it conforms to those expectations...it won't :/
    if not msy.check_membership_list_on_parameters(strict=True):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            handler.setLevel(logging.INFO)
        msy.report_failures()
