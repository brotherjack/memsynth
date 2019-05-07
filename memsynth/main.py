"""Membership Synthesis Program - MemSynth

Orlando DSA's membership list updating and maintaince solution.

"""
from collections import namedtuple
import json

import pandas as pd

from memsynth.config import uss_regex
import memsynth.exceptions as ex
from memsynth.parameters import Parameter, ACCEPTABLE_PARAMS


Failure = namedtuple("Failure", ['line', 'why', 'data'])


class MemExpectation():
    """An expectation that a column of data is expected to conform to

    :param col: (str) Name of the column the expectation refers to
    :param expectation: (iterable of `Parameter`) The various parameters of the expectation
        which reflect an expectation of what the data is to conform to
    """
    def  __init__(self, col, expectation):
        self.col = col
        self._acceptable_parameters = dict(
            data_type=dict(checked=True, unique=True, required=True),
            regex=dict(checked=True, unique=False, required=False),
            nullable=dict(checked=False, unique=True, required=False)
        )
        self.parameters = set()
        self.fails = []
        self.soft_fails = []
        self._form_expectation(expectation)

    def _form_expectation(self, params):
        for param in params:
            if param.name not in self._acceptable_parameters:
                raise ex.MemExpectationFormationError(
                    self.col, f"{param.name} is not a recognized col. "
                    f"These are {self._acceptable_parameters.keys()}"
                )
            self.parameters.add(param.name)
            if hasattr(self, param.name):
                if self._acceptable_parameters[param.name].get('unique'):
                    raise ex.MemExpectationFormationError(
                        self.col,
                        f"has multiple '{param.name}' unique parameters"
                    )
                else:
                    getattr(self, param.name).append(param)
            else:
                if self._acceptable_parameters[param.name].get('unique'):
                    setattr(self, param.name, param)
                else:
                    setattr(self, param.name, [param])
        if not self.parameters:
            raise ex.MemExpectationFormationError(
                self.col, "There is no data_type for column"
            )
        self.is_an_expectation = True

    def _check_regex(self, data, i):
        if pd.isnull(data):
            if hasattr(self, 'nullable') and (self.nullable.value == False):
                f = Failure(line=i, why=[Parameter(name='nullable')], data=data)
                self.fails.append(f)
                yield None, getattr(self, 'nullable')
        else:
            for rx in getattr(self, 'regex'):
                flags = 0 if not 'args' in rx else rx.args.get('flags', 0)
                if rx.args and 'match' in rx.args:
                    if rx.args['match'].lower() == "full":
                        yield rx.value.fullmatch(data, flags) is not None, rx
                    elif rx.args['match'].lower() == 'us_states':
                        # re flag for IGNORECASE == 2
                        yield uss_regex.fullmatch(data, 2) is not None, rx
                    else:
                        yield rx.value.match(data, flags) is not None, rx
                else:
                    yield rx.value.match(data, flags) is not None, rx

    def check(self, col):
        """Checks to see if the condition of the expectation are met

        :param col: (list of str) The data to check the expectation against
        :return: (boolean)
        """
        self.fails = []
        chkdparams = [
            k for k,v in self._acceptable_parameters.items() if v.get('checked')
        ]
        for param_name in chkdparams:
            checkfn_str = "_check_" + param_name
            if hasattr(self, checkfn_str):
                for i,cell in enumerate(col):
                    for check, param in getattr(self, checkfn_str)(cell, i):
                        try:
                            # If None, then another thing failed in the
                            # check (eg. nullable)
                            if check is None:
                                continue
                            else:
                                assert check
                        except AssertionError:
                            f = Failure(line=i, why=[param], data=cell)
                            if param.soft:
                                self.soft_fails.append(f)
                            else:
                                self.fails.append(f)
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
        self.expectations = {}

    def load_expectations_from_json(self, fname):
        """Loads expectations from a JSON file

        :param fname: JSON file containing expectations
        :raises: `MemExpectationFormationError` if the JSON file is
            misconfigured
        :raises: `FileNotFoundError` if file is not found
        :return: None
        """
        with open(fname, 'r') as f:
            self.expectations = json.load(f)
            acceptable_columns = self.expectations.keys()
            #found_cols = self._acceptable_columns.copy()
            for col, exps in self.expectations.items():
                if col not in acceptable_columns:
                    raise ex.MemExpectationFormationError(
                        col, "is not a valid column."
                    )
                else:
                    self.expectations[col] = [Parameter(**exp) for exp in exps]
            #       found_cols.remove(col)
            # TODO: Might want to add a warning if a column has no expectations

    def _verify_memlist_format(self, fname=None, softload=False):
        """Checks the format of the membership list

        Checks format of columns and other elements of the membership list
        sent to us from National DSA

        :param fname: (str, default None) File name of the excel file with
            membership data, if None the `MemSynther` attempts to read from
            `df` parameter
        :param softload: (boolean, default False) If true, then
            `LoadMembershipListException` is not raised on extra columns
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
        expected_cols = set(self.expectations.keys())
        actual_cols = set(df.columns)
        if expected_cols != actual_cols:
            if expected_cols.difference(actual_cols) == expected_cols:
                raise ex.LoadMembershipListException(
                    self,
                    msg="None of the columns match. Are you sure this is a "
                    "membership file?"
                )
            elif expected_cols.issuperset(actual_cols):
                raise ex.LoadMembershipListException(
                    self,
                    msg=f"The membership list appears to be missing the "
                    f"following columns '{expected_cols.difference(actual_cols)}'"
                )
            elif actual_cols.issuperset(expected_cols):
                if not softload:
                    raise ex.LoadMembershipListException(
                        self,
                        msg=f"The membership list appears to have added new "
                        f"columns that need to be added. These columns are the"
                        f" following {actual_cols.difference(expected_cols)}"
                    )
                else:
                    return df
            else:
                raise ex.LoadMembershipListException(
                    self,
                    msg=f"The membership list appears to be missing the "
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

    def load_from_excel(self, flist, softload=False):
        """Loads a membership list from an excel file

        Function loads a membership list in xlsx format and runs a
        verification function to make sure that the data in the file is
        what the `MemSynther` is expecting.

        :param flist: File name of the excel file with membership data
        :param softload: (boolean, default False) If true, then
            `LoadMembershipListException` is not raised on extra columns
        :raises: `memsynth.exceptions.LoadMembershipListException` if the
            data does not meet expectations.
        :return: None
        """
        try:
            self.df = self._verify_memlist_format(flist, softload)
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

    def load_from_memory(self, mem, softload=False):
        """Loads a membership list from a variable in memory

        Function attempts to create membership `pandas.DataFrame` from a
        variable in memory, then loads it into the `MemSynther`.

        :param mem: Membership data in a form that can be made into
            a `pandas.DataFrame`
        :param softload: (boolean, default False) If true, then
            `LoadMembershipListException` is not raised on extra columns
        :raises: `memsynth.exceptions.LoadMembershipListException` if the
            data does not meet expectations.
        :return: None
        """
        try:
            self.df = pd.DataFrame(mem)
            self._verify_memlist_format(softload=softload)
        except ex.LoadMembershipListException as lmle:
            print("Encountered a problem loading membership list from memory")
            self.df = None
            raise lmle
        except:
            print("Encountered an unkonwn problem loading membership list")
            self.df = None
            raise
