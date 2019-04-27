"""Membership Synthesis Program - MemSynth

Orlando DSA's membership list updating and maintaince solution.

"""
import pandas as pd

from memsynth.config import EXPECTED_FORMAT_MEM_LIST
from memsynth.exceptions import LoadMembershipListException

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
        :raises LoadMembershipListException: If the format does not match
            the one listed in `EXPECTED_FORMAT_MEM_LIST` the config file or
            if a filename is not supplied and the membership list hasn't been
            loaded from a variable in memory,
        """
        if fname:
            df = pd.read_excel(fname)
        elif not fname and hasattr(self.df, "columns"):
            df = self.df
        else:
            raise LoadMembershipListException(
                f"No filename passed to MemSynther and no dataframe loaded "
                f"from memory."
            )
        expected_cols = set(EXPECTED_FORMAT_MEM_LIST.get("columns"))
        actual_cols = set(df.columns)
        if expected_cols != actual_cols:
            if expected_cols.issuperset(actual_cols):
                raise LoadMembershipListException(
                    f"The membership list appears to be missing the "
                    f"following columns '{expected_cols.difference(actual_cols)}'"
                )
            elif actual_cols.issuperset(expected_cols):
                raise LoadMembershipListException(
                    f"The membership list appears to have added new columns "
                    f"that need to be added. These columns are the following "
                    f"{actual_cols.difference(expected_cols)}"
                )
            else:
                raise LoadMembershipListException(
                    f"The membership list appears to be missing the "
                    f"following columns '{expected_cols.difference(actual_cols)}'"
                    f" and the membership list appears to have added new columns "
                    f"that need to be added. These columns are the following "
                    f"{actual_cols.difference(expected_cols)}"
                )
        else:
            return df

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
        except LoadMembershipListException as lmle:
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
        except LoadMembershipListException as lmle:
            print("Encountered a problem loading membership list from memory")
            self.df = None
            raise lmle
        except:
            print("Encountered an unkonwn problem loading membership list")
            self.df = None
            raise
