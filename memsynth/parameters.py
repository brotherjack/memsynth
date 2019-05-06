from collections import namedtuple
import re


Parameter = namedtuple(
    "Parameter",
   ['name', 'value', 'soft', 'args'],
)
Parameter.__new__.__defaults__ = (None, None, False, None)

ACCEPTABLE_PARAMS = [
    "data_type",
    "regex",
    "nullable",
    "relative_to",
    "required"
]
