from collections import namedtuple


Parameter = namedtuple(
    "Parameter",
   ['name', 'value', 'soft', 'args'],
)
Parameter.__new__.__defaults__ = (None, None, False, None)

ACCEPTABLE_PARAMS = (
    "data_type",
    "regex",
    "nullable",
    "relative_to",
)

UNIQUE_PARAMS = (
    "data_type",
    "nullable",
)
