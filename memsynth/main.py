"""Membership Synthesis Program - MemSynth

Orlando DSA's membership list updating and maintaince solution.

"""
from collections import namedtuple
import re

import pandas as pd

from memsynth.config import EXPECTED_FORMAT_MEM_LIST
import memsynth.exceptions as ex


Parameter = namedtuple(
    "Parameter",
   ['name', 'checked', 'value'],
)
Parameter.__new__.__defaults__ = (None, None, None)
Failure = namedtuple("Failure", ['line', 'msg'])


class MemExpectation():
    """An expectation that a column of data is expected to conform to

    :param col: (str) Name of the column the expectation refers to
    :param expectation: (dict) The various parameters of the expectation
        and an expectation of what the data is to conform to
    """
    def  __init__(self, col, expectation):
        self.col = col
        self._acceptable_parameters = [
            Parameter(name="data_type", checked=True),
            Parameter(name="regex", checked=True),
            Parameter(name="nullable", checked=False)
        ]
        self.fails = []
        self._form_expectation(expectation)

    def _get_parameters(self, only_checked=False):
        if only_checked:
            return [x for x in self._acceptable_parameters]
        else:
            return [
                x for x in self._acceptable_parameters if not only_checked
            ]

    def _form_expectation(self, params):
        for param in params:
            if param.name not in [x.name for x in self._get_parameters()]:
                raise ex.MemExpectationFormationError(
                    self.col, f"{param.name} is not a recognized col. "
                    f"These are {self._acceptable_parameters}"
                )
            setattr(self, param.name, param)
            if hasattr(self, "regex") and param.name.startswith("regex"):
                self.regex = re.compile(param.value)
        if not hasattr(self, "data_type"):
            raise ex.MemExpectationFormationError(
                self.col, "There is no data_type for column"
            )
        self.is_an_expectation = True

    def _check_regex(self, data):
        return self.regex.match(data)

    def check(self, col):
        """Checks to see if the condition of the expectation are met

        :param col: (list of str) The data to check the expectation against
        :return: (boolean)
        """
        self.fails = []
        for param in self._get_parameters(only_checked=True):
            try:
                checkfn_str = "_check_" + param.name
                if hasattr(self, checkfn_str):
                    for i,cell in enumerate(col):
                        assert getattr(self, checkfn_str)(cell)
            except AssertionError:
                self.fails.append(
                    Failure(
                        line=i, msg=f"Cell '{cell}' failed on '{param.name}'"
                    )
                )
            except:
                raise
        return len(self.fails) == 0


class MemSynther():
    """Core class of the MemSynth program.

    This class manages membership list files, coordinates with local and
    remote databases, and API's
    """
    def __init__(self):
        self.df = None

    def _verify_memlist_format(self, fname=None):
        """Checks the format of the membership list

        Checks format of columns and other elements of the membership list
        sent to us from National DSA

        :param fname: File name of the excel file with membership data,
            if None the `MemSynther` attempts to read from `df` parameter
        :return `pandas.DataFrame`: Returns the membership list, if verified
        :raises `LoadMembershipListException`: If the format does not match
            the one listed in `EXPECTED_FORMAT_MEM_LIST` the config file or
            if a filename is not supplied and the membership list hasn't been
            loaded from a variable in memory,
        """
        if fname:
            df = pd.read_excel(fname)
        elif not fname and hasattr(self.df, "columns"):
            df = self.df
        else:
            raise ex.LoadMembershipListException(
                f"No filename passed to MemSynther and no dataframe loaded "
                f"from memory."
            )
        expected_cols = set(EXPECTED_FORMAT_MEM_LIST.get("columns"))
        actual_cols = set(df.columns)
        if expected_cols != actual_cols:
            if actual_cols.intersection(expected_cols):
                raise ex.LoadMembershipListException(
                    "None of the columns match. Are you sure this is a "
                    "membership file?"
                )
            elif expected_cols.issuperset(actual_cols):
                raise ex.LoadMembershipListException(
                    f"The membership list appears to be missing the "
                    f"following columns '{expected_cols.difference(actual_cols)}'"
                )
            elif actual_cols.issuperset(expected_cols):
                raise ex.LoadMembershipListException(
                    f"The membership list appears to have added new columns "
                    f"that need to be added. These columns are the following "
                    f"{actual_cols.difference(expected_cols)}"
                )
            else:
                raise ex.LoadMembershipListException(
                    f"The membership list appears to be missing the "
                    f"following columns '{expected_cols.difference(actual_cols)}'"
                    f" and the membership list appears to have added new columns "
                    f"that need to be added. These columns are the following "
                    f"{actual_cols.difference(expected_cols)}"
                )
        else:
            return df

    def verify_memlist_data_integrity(self, config, verify_format=False):
        """Checks the data of a loaded membership list to verify integrity

        Checks the data in the membership dataframe against the configuration
        data and make's sure that it matches expectations.

        :param verify_format: (boolean, default False) If True, runs
            `_verify_memlist_format` before anything else in this method
        :param config: (dict) The keys are columns and the values are lists
            of `MemExpectation` classes that need to pass for the data in the
            column to be considered correct.
        :return: (boolean) If all columns pass
        :raises `MembershipListIntegrityExcepton`: If a column fails
        """
        pass

    def load_from_excel(self, flist):
        """Loads a membership list from an excel file

        Function loads a membership list in xlsx format and runs a
        verification function to make sure that the data in the file is
        what the `MemSynther` is expecting.

        :param flist: File name of the excel file with membership data
        :raises: `memsynth.exceptions.LoadMembershipListException` if the
            data does not meet expectations.
        :return: None
        """
        try:
            self.df = self._verify_memlist_format(flist)
        except ex.LoadMembershipListException as lmle:
            print(f"Encountered a problem loading membership list {flist}")
            self.df = None
            raise lmle
        except:
            print(
                f"Encountered an unkonwn problem loading "
                f"membership list {flist}"
            )
            self.df = None
            raise

    def load_from_memory(self, mem):
        """Loads a membership list from a variable in memory

        Function attempts to create membership `pandas.DataFrame` from a
        variable in memory, then loads it into the `MemSynther`.

        :param mem: Membership data in a form that can be made into
            a `pandas.DataFrame`
        :raises: `memsynth.exceptions.LoadMembershipListException` if the
            data does not meet expectations.
        :return: None
        """
        try:
            self.df = pd.DataFrame(mem)
            self._verify_memlist_format()
        except ex.LoadMembershipListException as lmle:
            print("Encountered a problem loading membership list from memory")
            self.df = None
            raise lmle
        except:
            print("Encountered an unkonwn problem loading membership list")
            self.df = None
            raise
