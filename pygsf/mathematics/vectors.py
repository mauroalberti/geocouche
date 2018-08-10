# -*- coding: utf-8 -*-

from .exceptions import *
from .arrays import *


def normXYZ(x: Number, y: Number, z: Number) -> Tuple:
    """
    Normalize numeric values.

    :param x: x numeric value
    :param y: y numeric value
    :param z: z numeric value
    :return: the magnitude and a tuple of three float values
    """

    # input vals checks
    vals = [x, y, z]
    if not all(map(lambda val: isinstance(val, (int, float)), vals)):
        raise InputValuesException("Input values must be integer or float")
    elif not all(map(isfinite, vals)):
        raise InputValuesException("Input values must be finite")

    mag = sqrt(x*x + y*y + z*z)

    if mag <= MIN_VECTOR_MAGNITUDE:
        norm_xyz = None
    else:
        norm_xyz = x/mag, y/mag, z/mag

    return mag, norm_xyz


class Vect(object):
    """
    Cartesian 3D vector.
    Right-handed rectangular Cartesian coordinate system (ENU):
    x axis -> East
    y axis -> North
    z axis -> Up
    """

    def __init__(self, x: Number, y: Number, z: Number):
        """
        Vect constructor.

        Example;
          >>> Vect(1, 0, 1)
          Vect(1.0000, 0.0000, 1.0000)
          >>> Vect(1, np.nan, 1)
          Traceback (most recent call last):
          ...
          pygsf.mathematics.exceptions.VectorInputException: Input values must be finite
          >>> Vect(1, 0, np.inf)
          Traceback (most recent call last):
          ...
          pygsf.mathematics.exceptions.VectorInputException: Input values must be finite
          >>> Vect(0, 0, 0)
          Vect(0.0000, 0.0000, 0.0000)
        """

        vals = [x, y, z]
        if any(map(lambda val: not isinstance(val, (int, float)), vals)):
            raise VectorInputException("Input values must be integer of float")
        elif not all(map(isfinite, vals)):
            raise VectorInputException("Input values must be finite")
        else:
            self._a = array(vals, dtype=np.float64)

    def __eq__(self, another: 'Vect') -> bool:
        """
        Return True if objects are equal.

        Example:
          >>> Vect(1., 1., 1.) == Vect(1, 1, 1)
          True
          >>> Vect(1., 1., 1.) == Vect(1, 1, -1)
          False
        """

        if not isinstance(another, Vect):
            raise VectorInputException("Instances must be of the same type")
        else:
            return all([
                self.x == another.x,
                self.y == another.y,
                self.z == another.z])

    def __ne__(self, another: 'Vect') -> bool:
        """
        Return False if objects are equal.

        Example:
          >>> Vect(1., 1., 1.) != Vect(0., 0., 0.)
          True
        """

        if not isinstance(another, Vect):
            raise VectorInputException("Instances must be of the same type")
        else:
            return not (self == another)

    @property
    def a(self) -> 'numpy.array':
        """
        Return a copy of the object inner array.

        :return: double array of x, y, z values

        Examples:
          >>> Vect(4, 3, 7).a
          array([4., 3., 7.])
        """

        return np.copy(self._a)

    @property
    def x(self) -> float:
        """
        Return x value

        Example:
          >>> Vect(1.5, 1, 1).x
          1.5
        """

        return self.a[0]

    @property
    def y(self) -> float:
        """
        Return y value

        Example:
          >>> Vect(1.5, 3.0, 1).y
          3.0
        """
        return self.a[1]

    @property
    def z(self) -> float:
        """
        Return z value

        Example:
          >>> Vect(1.5, 3.2, 41.).z
          41.0
        """
        return self.a[2]

    def toXYZ(self) -> Tuple[float, float, float]:
        """
        Returns the spatial components as a tuple of three values.

        :return: the spatial components (x, y, z).
        :rtype: a tuple of three floats.

        Examples:
          >>> Vect(1, 0, 3).toXYZ()
          (1.0, 0.0, 3.0)
        """

        return self.x, self.y, self.z

    def toArray(self) -> 'numpy.array':
        """
        Return a double Numpy array representing the point values.

        :return: Numpy array

        Examples:
          >>> Vect(1, 2, 3).toArray()
          array([1., 2., 3.])
        """

        return self.a

    def pXY(self) -> 'Vect':
        """
        Projection on the x-y plane

        :return: projected object instance

        Examples:
          >>> Vect(2, 3, 4).pXY()
          Vect(2.0000, 3.0000, 0.0000)
        """

        return self.__class__(self.x, self.y, 0.0)

    def pXZ(self) -> 'Vect':
        """
        Projection on the x-z plane

        :return: projected object instance

        Examples:
          >>> Vect(2, 3, 4).pXZ()
          Vect(2.0000, 0.0000, 4.0000)
        """

        return self.__class__(self.x, 0.0, self.z)

    def pYZ(self) -> 'Vect':
        """
        Projection on the y-z plane

        :return: projected object instance

        Examples:
          >>> Vect(2, 3, 4).pYZ()
          Vect(0.0000, 3.0000, 4.0000)
        """

        return self.__class__(0.0, self.y, self.z)

    @property
    def len3D(self) -> float:
        """
        Spatial distance of the point from the axis origin.

        :return: distance
        :rtype: float

        Examples:
          >>> Vect(4.0, 3.0, 0.0).len3D
          5.0
        """

        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    @property
    def len2D(self) -> float:
        """
        2D distance of the point from the axis origin.

        Example:
          >>> Vect(3, 4, 0).len2D
          5.0
          >>> Vect(12, 5, 3).len2D
          13.0
        """

        return sqrt(self.x * self.x + self.y * self.y)

    def deltaX(self, another: 'Vect') -> float:
        """
        Delta between x components of two Vect Instances.

        :return: difference value
        :rtype: float

        Examples:
          >>> Vect(1, 2, 3).deltaX(Vect(4, 7, 1))
          3.0
        """

        if not isinstance(another, Vect):
            raise VectorInputException("Input instance must be of type Vect")
        else:
            return another.x - self.x

    def deltaY(self, another: 'Vect') -> float:
        """
        Delta between y components of two Vect Instances.

        :return: difference value
        :rtype: float

        Examples:
          >>> Vect(1, 2, 3).deltaY(Vect(4, 7, 1))
          5.0
        """

        if not isinstance(another, Vect):
            raise VectorInputException("Input instance must be of type Vect")
        else:
            return another.y - self.y

    def deltaZ(self, another: 'Vect') -> float:
        """
        Delta between x components of two Vect Instances.

        :return: difference value
        :rtype: float

        Examples:
          >>> Vect(1, 2, 3).deltaZ(Vect(4, 7, 1))
          -2.0
        """

        if not isinstance(another, Vect):
            raise VectorInputException("Input instance must be of type Vect")
        else:
            return another.z - self.z

    def scale(self, scale_factor: Number) -> 'Vect':
        """
        Create a scaled object.

        Example;
          >>> Vect(1, 0, 1).scale(2.5)
          Vect(2.5000, 0.0000, 2.5000)
          >>> Vect(1, 0, 1).scale(np.nan)
          Traceback (most recent call last):
          ...
          pygsf.mathematics.exceptions.VectorInputException: Scale factor must be finite
          >>> Vect(1, 0, 1).scale(np.inf)
          Traceback (most recent call last):
          ...
          pygsf.mathematics.exceptions.VectorInputException: Scale factor must be finite
        """

        if not isinstance(scale_factor, (int, float)):
            raise VectorInputException("Scale factor must be number")
        elif not isfinite(scale_factor):
            raise VectorInputException("Scale factor must be finite")
        else:
            x, y, z = arrToTuple(self.a * scale_factor)
            return self.__class__(x, y, z)

    def invert(self) -> 'Vect':
        """
        Create a new object with inverted direction.

        Examples:
          >>> Vect(1, 1, 1).invert()
          Vect(-1.0000, -1.0000, -1.0000)
          >>> Vect(2, -1, 4).invert()
          Vect(-2.0000, 1.0000, -4.0000)
        """

        return self.scale(-1)

    def __repr__(self) -> str:

        return "Vect({:.4f}, {:.4f}, {:.4f})".format(self.x, self.y, self.z)

    def __add__(self, another: 'Vect') -> 'Vect':
        """
        Sum of two vectors.

        Example:
          >>> Vect(1, 0, 0) + Vect(0, 1, 1)
          Vect(1.0000, 1.0000, 1.0000)
          >>> Vect(1, 1, 1) + Vect(-1, -1, -1)
          Vect(0.0000, 0.0000, 0.0000)
        """

        x, y, z = arrToTuple(self.a + another.a)
        return self.__class__(x, y, z)

    def __sub__(self, another: 'Vect') -> 'Vect':
        """Return object difference

        Example:
          >>> Vect(1., 1., 1.) - Vect(1., 1., 1.)
          Vect(0.0000, 0.0000, 0.0000)
          >>> Vect(1., 1., 3.) - Vect(1., 1., 2.2)
          Vect(0.0000, 0.0000, 0.8000)
        """

        x, y, z = arrToTuple(self.a - another.a)
        return self.__class__(x, y, z)

    @property
    def isAlmostZero(self) -> bool:
        """
        Check if the Vect instance length is near zero.

        :return: Boolean

        Example:
          >>> Vect(1, 2, 0).isAlmostZero
          False
          >>> Vect(0.0, 0.0, 0.0).isAlmostZero
          True
        """

        return areClose(self.len3D, 0)

    @property
    def isAlmostUnit(self) -> bool:
        """
        Check if the Vect instance length is near unit.

        :return: Boolean

        Example:
          >>> Vect(1, 2, 0).isAlmostUnit
          False
          >>> Vect(0.0, 1.0, 0.0).isAlmostUnit
          True
        """

        return areClose(self.len3D, 1)

    @property
    def isValid(self) -> bool:
        """
        Check if the Vect instance components are not all valid and the xyz not all zero-valued.

        :return: Boolean

        Example:
          >>> Vect(1, 2, 0).isValid
          True
          >>> Vect(0.0, 0.0, 0.0).isValid
          False
        """

        return not self.isAlmostZero

    def versor(self) -> Optional['Vect']:
        """
        Calculate versor in xyz space.

        Example:
          >>> Vect(5, 0, 0).versor()
          Vect(1.0000, 0.0000, 0.0000)
          >>> Vect(0, 0, -1).versor()
          Vect(0.0000, 0.0000, -1.0000)
          >>> Vect(0, 0, 0).versor() is None
          True
        """

        if not self.isValid:
            return None
        else:
            return self.scale(1.0 / self.len3D)

    def versor2D(self) -> Optional['Vect']:
        """
        Create 2D versor version of the current vector

        :return: unit vector

        Example:
          >>> Vect(7, 0, 10).versor2D()
          Vect(1.0000, 0.0000, 0.0000)
          >>> Vect(0, 0, 10).versor2D() is None
          True
        """

        vXY = self.pXY()
        if vXY.isValid:
            return self.pXY().versor()
        else:
            return None

    @property
    def isUpward(self) -> Optional[bool]:
        """
        Check that a vector is upward-directed.

        :return: boolean

        Example:
          >>> Vect(0,0,1).isUpward
          True
          >>> Vect(0,0,-0.5).isUpward
          False
          >>> Vect(1, 3, 0).isUpward
          False
          >>> Vect(0, 0, 0).isUpward is None
          True
        """

        if not self.isValid:
            return None
        else:
            return self.z > 0.0

    @property
    def isDownward(self) -> Optional[bool]:
        """
        Check that a vector is downward-directed.

        :return: boolean

        Example:
          >>> Vect(0,0,1).isDownward
          False
          >>> Vect(0,0,-0.5).isDownward
          True
          >>> Vect(1, 3, 0).isDownward
          False
          >>> Vect(0, 0, 0).isDownward is None
          True
        """

        if not self.isValid:
            return None
        else:
            return self.z < 0.0

    def upward(self) -> Optional['Vect']:
        """
        Calculate a new upward-pointing vector.

        Example:
          >>> Vect(1, 1, 1).upward()
          Vect(1.0000, 1.0000, 1.0000)
          >>> Vect(-1, -1, -1).upward()
          Vect(1.0000, 1.0000, 1.0000)
          >>> Vect(0, 0, 0).upward() is None
          True
        """

        if not self.isValid:
            return None
        elif self.z < 0.0:
            return self.scale(-1.0)
        else:
            return self.scale(1.0)

    def downward(self) -> Optional['Vect']:
        """
        Calculate a new vector downward-pointing.

        Example:
          >>> Vect(1, 1, 1).downward()
          Vect(-1.0000, -1.0000, -1.0000)
          >>> Vect(-1, -1, -1).downward()
          Vect(-1.0000, -1.0000, -1.0000)
          >>> Vect(0, 0, 0).downward() is None
          True
        """

        if not self.isValid:
            return None
        elif self.z > 0.0:
            return self.scale(-1.0)
        else:
            return self.scale(1.0)

    def vDot(self, another: 'Vect') -> float:
        """
        Vector scalar multiplication.

        Examples:
          >>> Vect(1, 0, 0).vDot(Vect(1, 0, 0))
          1.0
          >>> Vect(1, 0, 0).vDot(Vect(0, 1, 0))
          0.0
          >>> Vect(1, 0, 0).vDot(Vect(-1, 0, 0))
          -1.0
        """

        return self.x * another.x + self.y * another.y + self.z * another.z

    def angleCos(self, another: 'Vect') -> Optional[float]:
        """
        Return the cosine of the angle between two vectors.

        Examples:
          >>> Vect(1,0,0).angleCos(Vect(0,0,1))
          0.0
          >>> Vect(1,0,0).angleCos(Vect(-1,0,0))
          -1.0
          >>> Vect(1,0,0).angleCos(Vect(1,0,0))
          1.0
          >>> Vect(0, 0, 0).angleCos(Vect(1,0,0)) is None
          True
          >>> Vect(1, 0, 0).angleCos(Vect(0,0,0)) is None
          True
        """

        if not (self.isValid and another.isValid):
            return None
        else:
            val = self.vDot(another) / (self.len3D * another.len3D)
            if val > 1.0:
                return 1.0
            elif val < -1.0:
                return -1.0
            else:
                return val

    def angle(self, another: 'Vect', unit='d') -> Optional[float]:
        """
        Calculate angle between two vectors, as degrees
        in 0° - 180° range.

        Example:
          >>> Vect(1, 0, 0).angle(Vect(0, 0, 1))
          90.0
          >>> Vect(1, 0, 0).angle(Vect(-1, 0, 0))
          180.0
          >>> Vect(0, 0, 1).angle(Vect(0, 0, -1))
          180.0
          >>> Vect(1, 1, 1).angle(Vect(1, 1,1 ))
          0.0
          >>> Vect(0, 0, 0).angle(Vect(1,0,0)) is None
          True
          >>> Vect(1, 0, 0).angle(Vect(0,0,0)) is None
          True
        """

        if not (self.isValid and another.isValid):
            return None
        else:
            angle_rad = acos(self.angleCos(another))
            if unit == 'd':
                return degrees(angle_rad)
            elif unit == 'r':
                return angle_rad
            else:
                raise VectorInputException("Unit must be 'd' or 'r'")

    def vCross(self, another: 'Vect') -> 'Vect':
        """
        Vector product (cross product).

        Examples:
          >>> Vect(1, 0, 0).vCross(Vect(0, 1, 0))
          Vect(0.0000, 0.0000, 1.0000)
          >>> Vect(1, 0, 0).vCross(Vect(1, 0, 0))
          Vect(0.0000, 0.0000, 0.0000)
          >>> (Vect(1, 0, 0).vCross(Vect(-1, 0, 0))).isAlmostZero
          True
        """

        x, y, z = arrToTuple(np.cross(self.a[:3], another.a[:3]))
        return Vect(x, y, z)

    def byMatrix(self, array3x3: 'np.array') -> 'Vect':
        """
        Matrix multiplication of a vector.

        """

        x, y, z = arrToTuple(array3x3.dot(self.a))
        return Vect(x, y, z)


if __name__ == "__main__":

    import doctest
    doctest.testmod()
