from collections import namedtuple
import re


Parameter = namedtuple(
    "Parameter",
   ['name', 'value', 'soft', 'args'],
)
Parameter.__new__.__defaults__ = (None, None, False, None)


AK_ID_PARAMS = (
    Parameter(name="data_type", value="integer"),
    Parameter(name="regex", value=re.compile("[0-9]+")),
    Parameter(name="nullable", value=False),
)

DSA_ID_PARAMS = (
    Parameter(name="data_type", value="integer"),
    Parameter(name="regex", value=re.compile("[0-9]+")),
    Parameter(name="nullable", value=True),
)

NAME_PARAMS = (
Parameter(name="data_type", value="string"),
    Parameter(name="regex", value=re.compile("[0-9]+")),
    Parameter(name="nullable", value=True),
)