# -*- coding: utf-8 -*-


from .scalars import *
from .interpolations import interp_bilinear as s_interp_bilinear, interp_linear



def arrToTuple(arr1D: 'array[Number]') -> Tuple[float, ...]:
    """
    Modified from: https://stackoverflow.com/questions/10016352/convert-numpy-array-to-tuple
    Works just for 1D arrays

    :param arr1D: the 1D-arrays whose components have to be extracted.
    :type arr1D: numpy array.
    :return: a tuple derived from the array values extraction.
    :rtype: tuple of float.

    Examples:
      >>> levels = array([1,2,3,4,5])
      >>> arrToTuple(levels)
      (1.0, 2.0, 3.0, 4.0, 5.0)
    """

    return tuple(map(float, arr1D))


def toFloats(iterable_obj: Sequence[Number]) -> List[float]:
    """
    Converts an iterable object storing float-compatible values to a list of floats.

    :param iterable_obj:
    :type iterable_obj:
    :return:
    :rtype: list of Floats.

    Examples:
      >>> toFloats([1, 2, 3])
      [1.0, 2.0, 3.0]
    """

    return [float(item) for item in iterable_obj]


def arraysAreClose(
        a_array: 'array',
        b_array: 'array',
        rtol: float=1e-012,
        atol: float=1e-12,
        equal_nan: bool=False,
        equal_inf: bool=False) -> bool:
    """
    Check for equivalence between two numpy arrays.

    :param a_array: first array to be compared.
    :type a_array: numpy array.
    :param b_array: second array to be compared with the first one.
    :type b_array: numpy array.
    :param rtol: relative tolerance.
    :type rtol:
    :param atol: absolute tolerance.
    :type atol:
    :param equal_nan: consider nan values equivalent or not.
    :type equal_nan:
    :param equal_inf: consider inf values equivalent or not.
    :type equal_inf:
    :return: whether the two arrays are close as component values.
    :rtype: bool.

    Examples:
      >>> arraysAreClose(array([1,2,3]), array([1,2,3]))
      True
      >>> arraysAreClose(array([[1,2,3], [4, 5, 6]]), array([1,2,3]))
      False
      >>> arraysAreClose(array([[1,2,3], [4,5,6]]), array([[1,2,3], [4,5,6]]))
      True
      >>> arraysAreClose(array([[1,2,np.nan], [4,5,6]]), array([[1,2,np.nan], [4,5,6]]))
      False
      >>> arraysAreClose(array([[1,2,np.nan], [4,5,6]]), array([[1,2,np.nan], [4,5,6]]), equal_nan=True)
      True
    """
    if a_array.shape != b_array.shape:
        return False

    are_close = []
    for a, b in np.nditer([a_array, b_array]):
        are_close.append(areClose(a.item(0), b.item(0), rtol=rtol, atol=atol, equal_nan=equal_nan, equal_inf=equal_inf))

    return all(are_close)


def arraysSameShape(
        a_array: 'array',
        b_array: 'array') -> bool:
    """
    Checks that two arrays have the same shape.

    :param a_array: first array
    :type a_array: Numpy array.
    :param b_array: second array
    :type b_array: Numpy array.
    :return: whether the two arrays have the same shape.
    :rtype: bool.

    Examples:
      >>> arraysSameShape(np.ones((2,2)), np.ones(4))
      False
      >>> arraysSameShape(np.ones((2,2,3)), np.zeros((2,2,3)))
      True
    """

    return a_array.shape == b_array.shape


def interp_bilinear(arr: 'array', i: Number, j: Number) -> Optional[float]:
    """
    Interpolate the z value at a given i,j values couple.
    Interpolation method: bilinear.

    0, 0   0, 1

    1, 0,  1, 1

    :param arr: array with values for which the interpolation will be made.
    :type arr: Numpy array.
    :param i: i array index of the point (may be fractional).
    :type i: Number.
    :param j: j array index of the point (may be fractional).
    :type j: Number.
    :return: interpolated z value.
    :rtype: optional float.
    """

    i_max, j_max = arr.shape
    di = i - floor(i)
    dj = j - floor(j)

    if i < 0.0 or j < 0.0:
        return None
    elif i > i_max - 1 or j > j_max - 1:
        return None
    elif i == i_max - 1 and j == j_max - 1:
        return arr[i, j]
    elif i == i_max - 1:
        v0 = arr[i, int(floor(j))]
        v1 = arr[i, int(floor(j+1))]
        return interp_linear(
            frac_s=dj,
            v0=v0,
            v1=v1)
    elif j == j_max - 1:
        v0 = arr[int(floor(i)), j]
        v1 = arr[int(floor(i+1)), j]
        return interp_linear(
            frac_s=di,
            v0=v0,
            v1=v1)
    else:
        v00 = arr[int(floor(i)), int(floor(j))]
        v01 = arr[int(floor(i)), int(floor(j+1))]
        v10 = arr[int(floor(i+1)), int(floor(j))]
        v11 = arr[int(floor(i+1)), int(floor(j+1))]
        return s_interp_bilinear(di, dj, v00, v01, v10, v11)


def pointSolution(a_array: 'array[Number]', b_array: 'array[Number]'):
    """
    Finds a non-unique solution for a set of linear equations.

    :param a_array:
    :type a_array: numpy array.
    :param b_array:
    :type b_array: numpy array.
    :return:
    :rtype:

    Examples:
    """

    try:
        return np.linalg.lstsq(a_array, b_array, rcond=None)[0]
    except:
        return None, None, None


def xyzSvd(xyz_array) -> dict:
    """
    Calculates the SVD solution given a Numpy array.

    # modified after:
    # http://stackoverflow.com/questions/15959411/best-fit-plane-algorithms-why-different-results-solved

    :param xyz_array:
    :type xyz_array: numpy array.
    :return:
    :rtype:

    Examples:
    """

    try:
        result = np.linalg.svd(xyz_array)
    except:
        result = None

    return dict(result=result)


if __name__ == "__main__":

    import doctest
    doctest.testmod()
