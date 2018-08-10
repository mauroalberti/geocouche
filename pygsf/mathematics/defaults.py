# -*- coding: utf-8 -*-

from math import isnan, isinf, sqrt, degrees, acos, ceil, floor # they are used in importing files
from math import radians, sin, cos, tan, pi, atan2 # they are used in importing files

import numpy as np

array = np.array
isfinite = np.isfinite

"""
Geometric parameters
"""

MIN_SEPARATION_THRESHOLD = 1e-10
MIN_VECTOR_MAGNITUDE = 1e-9
MIN_SCALAR_VALUE = 1e-12
MIN_POINT_POS_DIFF = MIN_SCALAR_VALUE
MIN_VECTOR_MAGN_DIFF = MIN_SCALAR_VALUE


"""
Quaternion parameters
"""

quat_normaliz_tolerance = 1.0e-6
quat_division_tolerance = 1.0e-10
quat_magn_thresh = 1.0e-6


