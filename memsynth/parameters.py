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

DATATYPE_MAP = {
    "string": "object",
    "object": "object",
    "integer": "int64",
    "date": "datetime64[ns]",
    "boolean": "bool"
}
