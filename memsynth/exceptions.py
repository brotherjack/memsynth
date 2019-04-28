"""This is where MemSynth's custom exceptions live

If there are any special exceptions, they should live here.

"""
class MemSynthBaseError(Exception):
    """A base exception for all MemSynth specific errors

    All MemSynth errors should inherit from this base class

    :param memsynth_obj: the MemSynther class that is raising the error
    :param msg: an informative error message (default None)
    """
    def __init__(self, memsynth_obj, msg=None):
        if msg is None:
            msg = f"An error occurred with {memsynth_obj}"
        super().__init__(msg)
        self.memsynth_obj = memsynth_obj


class LoadMembershipListException(MemSynthBaseError):
    """An error that is raised when a membership list cannot be loaded

    This is an error that is raised because of a formatting or other error
    involved in loading the membership list.

    :param memsynth_obj: the MemSynther class that is raising the error
    :param fname, default None: the filename of the membership list delivered to us by
        national DSA. If fname is None, then the membership data has been
        loaded by memory
    :param msg: an informative error message (default None)
    """
    def __init__(self, memsynth_obj, fname=None, msg=None):
        if fname:
            msg = f"An error has occurred in loading membership file '{fname}'" \
                f": {msg}"
        else:
            msg = f"An error has occurred in loading membership data. {msg}"
        super().__init__(memsynth_obj, msg=msg)


class MembershipListIntegrityExcepton(MemSynthBaseError):
    """An error that is raised when the data in the membership list is wrong

    This error is raised when the data in a loaded membership list does not
    match what is expected in the configuration file.


    :param memsynth_obj: the MemSynther class that is raising the error
    :param expectation: (`memsynth.MembershipListIntegrityExcepton`) The
        failed expectation.
    """
    def __init__(self, memsynth_obj, expectation):
        super().__init__(
            memsynth_obj,
            msg=f"There was an error in '{expectation.col}': {expectation.err}"
        )


class MemExpectationBaseError(Exception):
    """A base exception for all MemExpectation specific errors

    All MemExpectation errors should inherit from this base class

    :param col: (string) the column that the expectation refers to
    :param msg: (string, default None) an informative error message
    """
    def __init__(self, col, msg=None):
        if msg is None:
            msg = f"An error occurred in column '{col}': '{msg}'"
        super().__init__(msg)


class MemExpectationFormationError(MemExpectationBaseError):
    """An error raised when the MemExpectation encounters an error in forming

    This error is raised when the MemExpectation class encounters an error in
    forming, such as an unidentified paramater

    :param col: (string) the column that the expectation refers to
    :param msg: (string, default None) an informative error message
    """
    def __init__(self, col, msg=None):
        msg = f"There is an error in forming an exception for '{col}': {msg}"
        super().__init__(col, msg)
