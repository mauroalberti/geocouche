# -*- coding: utf-8 -*-


from ...mathematics.defaults import *


def get_statistics(array):
    """

    :param array: numpy array
    :return:
    """

    min = np.nanmin(array)
    max = np.nanmax(array)
    mean = np.nanmean(array)
    var = np.nanvar(array)
    std = np.nanstd(array)

    stats = dict(min=min,
                 max=max,
                 mean=mean,
                 var=var,
                 std=std)

    return stats