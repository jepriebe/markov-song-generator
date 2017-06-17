import sys
import os


def get_script_path():
    """Gets the absolute filepath of the script calling it"""

    return os.path.dirname(os.path.realpath(sys.argv[0]))
