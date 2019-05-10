"""Membership Synthesis Program - MemSynth

Orlando DSA's membership list updating and maintaince solution.

"""
from collections import namedtuple
import json
import re

import pandas as pd

from memsynth.config import uss_regex
import memsynth.exceptions as ex
from memsynth.parameters import Parameter, ACCEPTABLE_PARAMS, UNIQUE_PARAMS


Failure = namedtuple("Failure", ['line', 'why', 'data'])


class MemExpectation():
    """An expectation that a column of data is expected to conform to

    :param col: (str) Name of the column the expectation refers to
    :param parameters: (iterable of `Parameter`) The various parameters of the expectation
        which reflect an expectation of what the data is to conform to
    """
    def  __init__(self, col, parameters, required=True):
        self.col = col
        self.parameters = set()
        self.fails = []
        self.soft_fails = []
        self.required = required
        self._form_parameters(parameters)

    def _form_parameters(self, params):
        for param in params:
            param_name = param.get('name')
            if param_name not in ACCEPTABLE_PARAMS:
                raise ex.MemExpectationFormationError(
                    self.col, f"{param_name} is not a recognized col. "
                    f"These are {ACCEPTABLE_PARAMS}"
                )
            self.parameters.add(param_name)
            if param_name == 'regex':
                param['value'] = re.compile(param['value'])
            if hasattr(self, param_name):
                if param.get('unique'):
                    raise ex.MemExpectationFormationError(
                        self.col,
                        f"has multiple '{param_name}' unique parameters"
                    )
                else:
                    getattr(self, param_name).append(param)
            else:
                if param_name in UNIQUE_PARAMS:
                    setattr(self, param_name, Parameter(**param))
                else:
                    setattr(self, param_name, [Parameter(**param)])
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
        for param_name in ACCEPTABLE_PARAMS:
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
                    self.expectations[col] = MemExpectation(
                        col, exps["parameters"], exps["required"]
                    )
            #       found_cols.remove(col)
            # TODO: Might want to add a warning if a column has no expectations

    def _verify_memlist_format(self, df=None, softload=False):
        """Checks the format of the membership list

        Checks format of columns and other elements of the membership list
        sent to us from National DSA

        :param df: (`pandas.DataFrame`, default None) DataFrame containing
            membership infomation. If none, then class member `df` has been set
        :param softload: (boolean, default False) If true, then
            `LoadMembershipListException` is not raised on extra columns
        :return `pandas.DataFrame`: Returns the membership list, if verified
        :raises `LoadMembershipListException`: If the format does not match
            the one listed in `EXPECTED_FORMAT_MEM_LIST` the config file or
            if a filename is not supplied and the membership list hasn't been
            loaded from a variable in memory,
        """
        if df is None:
            df = self.df
        expected_cols, not_required = set([]), set([])
        for k, v in self.expectations.items():
            if v.required:
                expected_cols.add(k)
            else:
                not_required.add(k)
        actual_cols = set(df.columns).difference(not_required)
        if expected_cols != actual_cols:
            if expected_cols.difference(actual_cols) == expected_cols:
                raise ex.LoadMembershipListException(
                    self,
                    msg="None of the columns match. Are you sure this is a "
                        "membership file?"
                )
            elif expected_cols.intersection(actual_cols) == expected_cols:
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
                if actual_cols.difference(expected_cols) == set():
                    raise ex.LoadMembershipListException(
                        self,
                        msg=f"The membership list appears to be missing the "
                        f"following columns '{expected_cols.difference(actual_cols)}'"
                    )
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

    def verify_memlist_data_integrity(self, verify_format=False):
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

    def _load(self, df, softload=False):
        df = self._verify_memlist_format(df, softload)
        if hasattr(self, "expectations") and len(self.expectations.keys()) != 0:
            for col, expectation in self.expectations.items():
                if expectation.data_type.value.startswith("str"):
                    df[col].astype("object", inplace=True)
        return df

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
            self.df = self._load(pd.read_excel(flist), softload)
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
            if mem and hasattr(mem, "columns"):
                self.df = self._load(mem, softload)
            else:
                self.df = self._load(pd.DataFrame(mem), softload=softload)
        except Exception as e:
            self.df = None
            raise ex.LoadMembershipListException(self, msg=str(e))
