"""Membership Synthesis Program - MemSynth

Orlando DSA's membership list updating and maintaince solution.

"""
import json
import logging
import os
import re
import sys

import pandas as pd

from memsynth.config import uss_regex, EXPECTED_FORMAT_MEM_LIST
import memsynth.exceptions as ex
from memsynth.parameters import (
    Parameter, ACCEPTABLE_PARAMS, UNIQUE_PARAMS, DATATYPE_MAP
)
from memsynth.utils import setup_logging


class Failure:
    def __init__(self, line, why, data):
        self.logger = logging.getLogger(type(self).__name__)
        self.data = data
        self.is_soft = why.soft
        self._why = [why]
        self.line = line

    def __repr__(self):
        return f"<Failure: Why ({self.reasons}) - Data {self.data}>"

    @property
    def reasons(self):
        return ", ".join([r.name for r in self.why])

    @reasons.setter
    def reasons(self, x):
        self.logger.warning(f"Trying to set reasons to '{x}'. Silly Billy.")

    @property
    def why(self):
        return self._why

    @why.setter
    def why(self, reason):
        if self._why:
            self._why.append(reason)
        else:
            errmsg = "Why is there no _why!?"
            self.logger.error(errmsg)
            raise AttributeError(errmsg)

        if not reason.soft:
            self.is_soft = False


class MemExpectation():
    """An expectation that a column of data is expected to conform to

    :param col: (str) Name of the column the expectation refers to
    :param parameters: (iterable of `Parameter`) The various parameters of the expectation
        which reflect an expectation of what the data is to conform to
    """
    def  __init__(self, col, parameters, required=True):
        self.logger = logging.getLogger(type(self).__name__)
        self.col = col
        self.parameters = set()
        self._fails = []
        self.required = required
        self._form_parameters(parameters)

    def __repr__(self):
        return f"<MemExpectation: {self.col} - Fails: {len(self.fails)} " \
            f"- Soft Fails: {len(self.soft_fails)}>"

    @property
    def fails(self):
        return [fail for fail in self._fails if not fail.is_soft]

    @fails.setter
    def fails(self, x):
        self.logger.warning(f"Attempting to add {x} to fails property.")

    @property
    def soft_fails(self):
        return [fail for fail in self._fails if fail.is_soft]

    @soft_fails.setter
    def soft_fails(self, x):
        self.logger.warning(f"Attempting to add {x} to soft_fails property.")

    def is_hard_failure(self):
        return len(self.fails) > 0

    def is_soft_failure(self):
        return len(self.soft_fails) > 0 and not self.is_hard_failure()

    def _form_parameters(self, params):
        for param in params:
            param_name = param.get('name')
            self.logger.debug(f"Forming parameter '{param_name}'...")
            if param_name not in ACCEPTABLE_PARAMS:
                raise ex.MemExpectationFormationError(
                    self.col, f"{param_name} is not a recognized col. "
                    f"These are {ACCEPTABLE_PARAMS}"
                )
            self.parameters.add(param_name)
            if param_name == 'regex':
                self.logger.debug(f"Compiling regular expression '{param['value']}'")
                param['value'] = re.compile(param['value'])
            if hasattr(self, param_name):
                if param.get('unique'):
                    raise ex.MemExpectationFormationError(
                        self.col,
                        f"has multiple '{param_name}' unique parameters"
                    )
                else:
                    getattr(self, param_name).append(Parameter(**param))
            else:
                if param_name in UNIQUE_PARAMS:
                    self.logger.debug(f"Setting unique parameter '{param_name}'")
                    setattr(self, param_name, Parameter(**param))
                else:
                    self.logger.debug(f"Setting parameter '{param_name}'")
                    setattr(self, param_name, [Parameter(**param)])
        if not self.parameters:
            raise ex.MemExpectationFormationError(
                self.col, "There is no data_type for column"
            )
        self.is_an_expectation = True

    def _check_regex(self, data, i):
        if pd.isnull(data):
            yield True, None
        else:
            # For some reason Pandas delivers items from Object Series based on
            # assumed type, not as strings. Therefore, '4' is an integer.
            # We need to make sure we are working on strings
            data = str(data)
            for rx in getattr(self, 'regex'):
                flags = 0 if not 'args' in rx else rx.args.get('flags', 0)
                if rx.args and 'match' in rx.args:
                    if rx.args['match'].lower() == "full":
                        yield rx.value.fullmatch(data, flags) is not None, rx
                    elif rx.args['match'].lower() == 'us_states':
                        # re flag for IGNORECASE == 2
                        yield uss_regex.fullmatch(data) is not None, rx
                    else:
                        yield rx.value.match(data, flags) is not None, rx
                else:
                    yield rx.value.match(data, flags) is not None, rx

    def _check_nullable(self, data, i):
        if not self.nullable.value:
            yield not pd.isnull(data), getattr(self, 'nullable')

    def clear(self):
        if len(self._fails) > 0:
            self.logger.info("Clearing failures")
        self._fails = []

    def check(self, data):
        """Checks to see if the condition of the expectation are met

        :param data: (`pd.Series`) Data to check parameters against

        :return: (boolean)
        """
        self.logger.info(f"Checking column '{self.col}'...")
        self.clear()
        parameters = set(ACCEPTABLE_PARAMS).intersection(self.parameters)
        for i, cell in enumerate(data):
            f = None
            for param_name in parameters:
                checkfn_str = "_check_" + param_name
                if hasattr(self, checkfn_str):
                    self.logger.debug(f"Running '{checkfn_str}' on '{data}'")
                    # Some check functions will yield multiple checks (eg. _check_regex)
                    for check, param in getattr(self, checkfn_str)(cell, i):
                        self.logger.debug(f"On line '{i}' cell={cell}, check={check}")
                        try:
                            # If None, then another thing failed in the
                            # check (eg. nullable)
                            if check is None:
                                continue
                            else:
                                assert check
                        except AssertionError:
                            if not f:
                                f = Failure(line=i, why=param, data=cell)
                                self._fails.append(f)
                            else:
                                f.why = param
                            fmsg = f"Found a failure on line '{i}' running '{param}' on '{cell}'"
                            if param.soft:
                                self.logger.warning(fmsg)
                            else:
                                self.logger.error(fmsg)
                        except:
                            raise
        return len(self._fails) == 0


class MemSynther():
    """Core class of the MemSynth program.

    This class manages membership list files, coordinates with local and
    remote databases, and API's
    """
    def __init__(self, name=None):
        self.logger = logging.getLogger(type(self).__name__)
        self.df = None
        self.name = name if name else f'object at {hex(id(self))}'
        self.expectations = {}

    def __repr__(self):
        name_field = f'- {self.name}'
        exp_field = ' - Expectations '
        exp_field += ' LOADED' if self.expectations else ' NULL'
        df_field = ' - Data Frame '
        if self.df is None:
            df_field += ' NULL '
        else:
            if self.df.empty:
                df_field += ' EMPTY '
            else:
                df_field += ' LOADED '
        return f"<MemSynther {name_field}{exp_field}{df_field}>"

    def get_failures(self, fails=None, include_soft=False):
        cols = None
        if fails is None:
            cols = EXPECTED_FORMAT_MEM_LIST['columns']
        else:
            if hasattr(fails, 'capitalize'): # (ie. is a 'fail' not 'fails')
                fails = [fails]
            cols = set(fails).intersection(EXPECTED_FORMAT_MEM_LIST['columns'])

        self.logger.debug(
            f"Getting failures on columns '{cols}' "
            f"{'including soft failures' if include_soft else ''}"
        )
        for col in cols:
            if len(self.expectations[col].fails) > 0:
                for fail in self.expectations[col].fails:
                    yield col, fail
            if include_soft:
                if len(self.expectations[col].soft_fails) > 0:
                    for fail in self.expectations[col].soft_fails:
                        yield col, fail

    def return_failure_dict(self, fails=None, include_soft=False):
        failures = dict()
        for col, fail in self.get_failures(fails, include_soft):
            failures.setdefault(col, []).append(fail)
        return failures

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
        self.logger.debug(f"Verifying memlist format on {self.name}")
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

    def check_membership_list_on_parameters(self, verify_format=False, strict=True):
        """Checks the data of a loaded membership list to verify integrity

        Checks the data in the membership dataframe against the configuration
        data and make's sure that it matches expectations.

        :param verify_format: (boolean, default False) If True, runs
            `_verify_memlist_format` before anything else in this method
        :param strict: (boolean, default True) Considers soft failures to be
            failures if True, ignores them if they are soft.
        :return: (boolean) True, if there are no columns with failures. Will
            return False if one of the `MemExpectation` classes encounters a
            failure.
        """
        if verify_format:
            self._verify_memlist_format(self.df)

        hardFailEncountered = False
        softFailEncountered = False

        for col, exp in self.expectations.items():
            if not exp.check(self.df[col]):
                if exp.is_hard_failure():
                    hardFailEncountered = True
                elif exp.is_soft_failure() and not hardFailEncountered:
                    softFailEncountered = True
        if hardFailEncountered:
            self.logger.error(
                f"Check on membership list '{self.name}' has encountered failures"
            )
            return False
        elif softFailEncountered:
            self.logger.warning(
                f"Check on membership list '{self.name}' has encountered soft failures"
            )
            return False if strict else True
        else:
            self.logger.info(
                f"Check on membership list '{self.name}' has passed successfully"
            )
            return True


    def _load(self, df, softload=False):
        df = self._verify_memlist_format(df, softload)
        if hasattr(self, "expectations") and len(self.expectations.keys()) != 0:
            for col, expectation in self.expectations.items():
                dtype = expectation.data_type.value
                if dtype.lower() in DATATYPE_MAP:
                    dtype = DATATYPE_MAP[dtype.lower()]
                # The following is very hacky, but nececessary for how Pandas
                # (and ultimately Numpy) handle null values in Integer series
                # More here: https://pandas.pydata.org/pandas-docs/version/0.24/whatsnew/v0.24.0.html#optional-integer-na-support
                series_should_be_int = dtype.lower().startswith("int")
                series_is_not_an_int = not hasattr(df[col].dtype, 'is_unsigned_integer')
                if expectation.nullable and \
                        (series_should_be_int  and series_is_not_an_int):
                    df[col] = self._convert_npobject_series_with_nulls_to_int(df[col], dtype)
                else:
                    df[col] = df[col].astype(dtype, inplace=True)
        return df

    def _convert_npobject_series_with_nulls_to_int(self, series, inttype="Int64"):
        lst = [int(x) if not pd.isnull(x) else x for x in series.tolist()]
        return pd.Series(lst, dtype=inttype.capitalize())

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
        if self.name.startswith("object at"):
            nname = os.path.split(flist)[1]
            self.logger.debug(
                f"Chaging name of MemSynther '{self.name}' to '{nname}'"
            )
            self.name = nname
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

    def report_failures(self, report_soft_errors=True):
        # Add handler for terminal to make sure that the
        # console is logging errors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logging.getLogger(__name__).addHandler(console_handler)

        failures = self.return_failure_dict(include_soft=report_soft_errors)
        for fail_column in failures.keys():
            self.logger.info(
                f"{len(failures[fail_column])} failures found on "
                f"column '{fail_column}'"
            )
            for failure in failures[fail_column]:
                self.logger.info(f"On line {failure.line}: ")
                for param in failure.why:
                    logfn = getattr(self.logger, 'warning')\
                        if param.soft else getattr(self.logger, 'error')
                    logfn(
                        f"{'soft' if param.soft else 'HARD'} "
                        f"failure on the '{param.name}' constraint, "
                        f"value='{param.value}', with args='{param.args}' "
                    )
                self.logger.info(f"Data at line is {failure.data}")
