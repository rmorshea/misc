import os
import re


def undo(original):
    """Undo swapped changes

    This is a simple helper function that writes
    the values of a dictionary to the file paths
    specified by its keys.
    
    Paramters
    ---------
    original : dict
        A dictionary keyed on file paths, whose values
        are strings that will overwrite the contents of
        their keyed files.
    

    Returns
    -------
    A dictionary keyed on file paths, whose values where
    their original contents. This means, undo could be
    reapplied to restore a modified file state.
    """
    modified = {}
    for path in original:
        with open(path, "r") as file:
            modified[path] = file.read()
        with open(path, "w") as file:
            file.write(original[path])
    return modified


def swapiter(finds, modifier):
    """Swap sections of a file with modified text

    Paramters
    ---------
    finds : dict of dicts
        A dictionary of the form returned by ``sift`` - A dictionary
        keyed on matching file paths, whose values are dictionaries
        keyed on match spans (indices) whose values will be modified
    modifier : function
        Takes in a value from the ``finds`` dictionary and returns a
        new string that will be used to replace the span of the given
        find.

    Returns
    -------
    An iterator which yields paths, and their modified texts.
    """
    for path in finds:
        diff = 0
        with open(path, "r") as file:
            text = file.read()
            for span in sorted(finds[path].keys()):
                change = modifier(finds[path][span])
                s0, s1 = (span[0] + diff, span[1] + diff)
                diff += len(change) - (s1 - s0)
                text = text[:s0] + change + text[s1:]
                yield (path, text)


def swap(finds, modifier):
    """Swap sections of a file with modified text

    Paramters
    ---------
    finds : dict of dicts
        A dictionary of the form returned by ``sift`` - A dictionary
        keyed on matching file paths, whose values are dictionaries
        keyed on match spans (indices) whose values will be modified
    modifier : function
        Takes in a value from the ``finds`` dictionary and returns a
        new string that will be used to replace the span of the given
        find.

    Returns
    -------
    A dictionary keyed on file paths, whose
    values are the original file contents.
    """
    return undo(dict(swapiter(finds, modifier)))


class Schema(object):

    def __init__(self, path, index, find, context):
        self.path = path
        self.index = index
        self.find = find
        self.context = context

    def __iter__(self):
        yield self.path
        yield self.index
        yield self.find
        yield self.context


def sift(files, pattern, context="", schema=Schema):
    """Search files for a given pattern

    Parameters
    ----------
    files : iterable of str
        Paths to files that will be searched
    pattern : str
        A regex pattern to which each file will be matched
    context : str
        A regex pattern applied adjacent to each match's span.
    schema : callable
        Defines how finds are presented in the returned result. By default
        this is the :class:``Schema`` constructor. Its signature must be
        of the form ``(path, index, find, context)`` where ``path`` is the
        path to the matched file, ``index`` is the index of the line where
        the first matched character, ``find`` is a regex match object, and
        ``context`` is a tuple of two matched objects created by the
        context pattern.


    Returns
    -------
    A dictionary keyed on matching file paths, whose values
    are dictionaries keyed on match spans (indices) whose values
    are defined by the ``schema`` callable.
    """
    pattern = re.compile(pattern)
    
    context = (
        re.compile("[\s\S]*" + context + "\Z"),
        re.compile("\A" + context + "[\s\S]*"),
    )

    finds = {}
    for path in files:
        filefinds = {}
        with open(path, "r") as file:
            text = file.read()
            for find in pattern.finditer(text):
                span = find.span()
                filefinds[span] = schema(
                    path, text[:span[0]].count("\n"), find, (
                        context[0].match(text[:span[0]]),
                        context[1].match(text[span[1]:]),
                    )
                )
        if filefinds:
            finds[path] = filefinds
    return finds


def scan(root, filetype):
    """Return files of a given type in a directory.
    
    Parameters
    ----------
    root : str
        A path to a directory that will be scanned.
    filetype: str
        A regex pattern for matching file names.
    
    Returns
    -------
    All files under the 'root' path that
    match the given 'filetype' pattern.
    """
    
    filetype = re.compile(filetype)
    
    return [
        path for path in [
            os.path.join(root, file) for root, file in [
                (root, file) for root, sub, files in
                os.walk(root) for file in files
            ] if filetype.match(file)
        ]
    ]