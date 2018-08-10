# -*- coding: utf-8 -*-


def string2dict(strng, valsep=",", kvsep="="):
    """
    Creates a dictionary from a string.

    :param strng: string to convert into dictionary
    :param valsep: separator between key-value pairs
    :param kvsep: separator between key and value
    :return: a dictionary

    Examples:
      >>> string2dict("m=s, c=blue")
      {'c': 'blue', 'm': 's'}
    """

    vals = strng.split(valsep)
    kv_vals = map(lambda kvstr: kvstr.strip().split(kvsep), vals)
    return dict(kv_vals)


