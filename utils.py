"""
General purpose utility functions
"""


def is_number(val):
    if type(val) == int or type(val) == float:
        return True
    return False
