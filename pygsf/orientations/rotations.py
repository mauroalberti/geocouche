# -*- coding: utf-8 -*-


from pygsf.mathematics.quaternions import *
from .orientations import *


class RotationAxis(object):
    """
    Rotation axis, expressed by an Orientation and a rotation angle.
    """

    def __init__(self, trend: [int, float], plunge: [int, float], rot_ang: [int, float]):
        """
        Constructor.

        :param trend: Float/Integer
        :param plunge: Float/Integer
        :param rot_ang: Float/Integer

        Example:
        >> RotationAxis(0, 90, 120)
        RotationAxis(0.0000, 90.0000, 120.0000)
        """

        self.dr = Direct.fromAzPl(trend, plunge)
        self.a = float(rot_ang)

    @classmethod
    def fromQuater(cls, quat: Quaternion):
        """
        Calculates the Rotation Axis expressed by a quaternion.
        The resulting rotation asVect is set to point downward.
        Examples are taken from Kuipers, 2002, chp. 5.

        :return: RotationAxis instance.

        Examples:
          >>> RotationAxis.fromQuater(Quaternion(0.5, 0.5, 0.5, 0.5))
          RotationAxis(45.0000, -35.2644, 120.0000)
          >>> RotationAxis.fromQuater(Quaternion(sqrt(2)/2, 0.0, 0.0, sqrt(2)/2))
          RotationAxis(0.0000, -90.0000, 90.0000)
          >>> RotationAxis.fromQuater(Quaternion(sqrt(2)/2, sqrt(2)/2, 0.0, 0.0))
          RotationAxis(90.0000, -0.0000, 90.0000)
        """

        if abs(quat) < quat_magn_thresh:

            rot_ang = 0.0
            rot_direct = Direct.fromAzPl(0.0, 0.0)

        elif areClose(quat.scalar, 1):

            rot_ang = 0.0
            rot_direct = Direct.fromAzPl(0.0, 0.0)

        else:

            unit_quat = quat.normalize()
            rot_ang = unit_quat.rotAngle()
            rot_direct = Direct.fromVect(unit_quat.vector)

        return RotationAxis(*rot_direct.d, rot_ang)

    @classmethod
    def fromDirect(cls, direct: Direct, angle: float):
        """
        Class constructor from a Direct instance and an angle value.

        :param direct: a Direct instance
        :param angle: float value
        :return: RotationAxis instance

        Example:
          >>> RotationAxis.fromDirect(Direct.fromAzPl(320, 12), 30)
          RotationAxis(320.0000, 12.0000, 30.0000)
          >>> RotationAxis.fromDirect(Direct.fromAzPl(315.0, -0.0), 10)
          RotationAxis(315.0000, -0.0000, 10.0000)
        """

        return RotationAxis(*direct.d, angle)

    @classmethod
    def fromVect(cls, vector: Vect, angle: float):
        """
        Class constructor from a Vect instance and an angle value.

        :param vector: a Vect instance
        :param angle: float value
        :return: RotationAxis instance

        Example:
          >>> RotationAxis.fromVect(Vect(0, 1, 0), 30)
          RotationAxis(0.0000, -0.0000, 30.0000)
          >>> RotationAxis.fromVect(Vect(1, 0, 0), 30)
          RotationAxis(90.0000, -0.0000, 30.0000)
          >>> RotationAxis.fromVect(Vect(0, 0, -1), 30)
          RotationAxis(0.0000, 90.0000, 30.0000)
        """

        direct = Direct.fromVect(vector)

        return RotationAxis.fromDirect(direct, angle)

    def __repr__(self):

        return "RotationAxis({:.4f}, {:.4f}, {:.4f})".format(*self.dr.d, self.a)

    @property
    def rotAngle(self) -> float:
        """
        Returns the rotation angle of the rotation axis.

        :return: rotation angle (Float)

        Example:
          >>> RotationAxis(10, 15, 230).rotAngle
          230.0
        """

        return self.a

    @property
    def rotDirect(self) -> Direct:
        """
        Returns the rotation axis, expressed as a Direct.

        :return: Direct instance

        Example:
          >>> RotationAxis(320, 40, 15).rotDirect
          Direct(az: 320.00°, pl: 40.00°)
          >>> RotationAxis(135, 0, -10).rotDirect
          Direct(az: 135.00°, pl: 0.00°)
          >>> RotationAxis(45, 10, 10).rotDirect
          Direct(az: 45.00°, pl: 10.00°)
        """

        return self.dr

    @property
    def versor(self) -> Vect:
        """
        Return the versor equivalent to the Rotation geological asVect.

        :return: Vect
        """

        return self.dr.asVersor()

    def specular(self):
        """
        Derives the rotation axis with opposite asVect direction
        and rotation angle that is the complement to 360°.
        The resultant rotation is equivalent to the original one.

        :return: RotationAxis instance.

        Example
          >>> RotationAxis(90, 45, 320).specular()
          RotationAxis(270.0000, -45.0000, 40.0000)
          >>> RotationAxis(135, 0, -10).specular()
          RotationAxis(315.0000, -0.0000, 10.0000)
          >>> RotationAxis(45, 10, 10).specular()
          RotationAxis(225.0000, -10.0000, 350.0000)
        """

        gvect_opp = self.rotDirect.opposite()
        opposite_angle = (360.0 - self.rotAngle) % 360.0

        return RotationAxis.fromDirect(gvect_opp, opposite_angle)

    def compl180(self):
        """
        Creates a new rotation axis that is the complement to 180 of the original one.

        :return: RotationAxis instance.

        Example:
          >>> RotationAxis(90, 45, 120).compl180()
          RotationAxis(90.0000, 45.0000, 300.0000)
          >>> RotationAxis(117, 34, 18).compl180()
          RotationAxis(117.0000, 34.0000, 198.0000)
          >>> RotationAxis(117, 34, -18).compl180()
          RotationAxis(117.0000, 34.0000, 162.0000)
        """

        rot_ang = - (180.0 - self.rotAngle) % 360.0
        return RotationAxis.fromDirect(self.dr, rot_ang)

    def strictlyEquival(self, another, angle_tolerance: [int, float]=VECTOR_ANGLE_THRESHOLD) -> bool:
        """
        Checks if two RotationAxis are almost equal, based on a strict checking
        of the Direct component and of the rotation angle.

        :param another: another RotationAxis instance, to be compared with
        :type another: RotationAxis
        :parameter angle_tolerance: the tolerance as the angle (in degrees)
        :type angle_tolerance: int, float
        :return: the equivalence (true/false) between the two compared RotationAxis
        :rtype: bool

        Examples:
          >>> ra_1 = RotationAxis(180, 10, 10)
          >>> ra_2 = RotationAxis(180, 10, 10.5)
          >>> ra_1.strictlyEquival(ra_2)
          True
          >>> ra_3 = RotationAxis(180.2, 10, 10.4)
          >>> ra_1.strictlyEquival(ra_3)
          True
          >>> ra_4 = RotationAxis(184.9, 10, 10.4)
          >>> ra_1.strictlyEquival(ra_4)
          False
        """

        if not self.dr.isSubParallel(another.dr, angle_tolerance):
            return False

        if not areClose(self.a, another.a, atol=1.0):
            return False

        return True

    def toRotQuater(self) -> Quaternion:
        """
        Converts the RotationAxis instance to the corresponding rotation quaternion.

        :return: the rotation quaternion.
        :rtype: Quaternion
        """

        rotation_angle_rad = radians(self.a)
        rotation_vector = self.dr.asVersor()

        w = cos(rotation_angle_rad / 2.0)
        x, y, z = rotation_vector.scale(sin(rotation_angle_rad / 2.0)).toXYZ()

        return Quaternion(w, x, y, z).normalize()

    def toRotMatrix(self):
        """
        Derives the rotation matrix from the RotationAxis instance.

        :return: 3x3 numpy array
        """

        rotation_versor = self.versor
        phi = radians(self.a)

        l = rotation_versor.x
        m = rotation_versor.y
        n = rotation_versor.z

        cos_phi = cos(phi)
        sin_phi = sin(phi)

        a11 = cos_phi + ((l * l) * (1 - cos_phi))
        a12 = ((l * m) * (1 - cos_phi)) - (n * sin_phi)
        a13 = ((l * n) * (1 - cos_phi)) + (m * sin_phi)

        a21 = ((l * m) * (1 - cos_phi)) + (n * sin_phi)
        a22 = cos_phi + ((m * m) * (1 - cos_phi))
        a23 = ((m * n) * (1 - cos_phi)) - (l * sin_phi)

        a31 = ((l * n) * (1 - cos_phi)) - (m * sin_phi)
        a32 = ((m * n) * (1 - cos_phi)) + (l * sin_phi)
        a33 = cos_phi + ((n * n) * (1 - cos_phi))

        return np.array([(a11, a12, a13),
                         (a21, a22, a23),
                         (a31, a32, a33)])

    def toMinRotAxis(self):
        """
        Calculates the minimum rotation axis from the given quaternion.

        :return: RotationAxis instance.
        """

        return self if abs(self.rotAngle) <= 180.0 else self.specular()


def sortRotations(rotation_axes: List[RotationAxis]) -> List[RotationAxis]:
    """
    Sorts a list or rotation axes, based on the rotation angle (absolute value),
    in an increasing order.

    :param rotation_axes: o list of RotationAxis objects.
    :return: the sorted list of RotationAxis

    Example:
      >>> rots = [RotationAxis(110, 14, -23), RotationAxis(42, 13, 17), RotationAxis(149, 87, 13)]
      >>> sortRotations(rots)
      [RotationAxis(149.0000, 87.0000, 13.0000), RotationAxis(42.0000, 13.0000, 17.0000), RotationAxis(110.0000, 14.0000, -23.0000)]
    """

    return sorted(rotation_axes, key=lambda rot_ax: abs(rot_ax.rotAngle))


def rotVectByQuater(quat: Quaternion, vect: Vect) -> Vect:
    """
    Calculates a rotated solution of a Vect instance given a normalized quaternion.
    Original formula in Ref. [1].
    Eq.6: R(qv) = q qv q(-1)

    :param quat: a Quaternion instance
    :param vect: a Vect instance
    :return: a rotated Vect instance

    Example:
      >>> q = Quaternion.i()  # rotation of 180° around the x axis
      >>> rotVectByQuater(q, Vect(0, 1, 0))
      Vect(0.0000, -1.0000, 0.0000)
      >>> rotVectByQuater(q, Vect(0, 1, 1))
      Vect(0.0000, -1.0000, -1.0000)
      >>> q = Quaternion.k()  # rotation of 180° around the z axis
      >>> rotVectByQuater(q, Vect(0, 1, 1))
      Vect(0.0000, -1.0000, 1.0000)
      >>> q = Quaternion.j()  # rotation of 180° around the y axis
      >>> rotVectByQuater(q, Vect(1, 0, 1))
      Vect(-1.0000, 0.0000, -1.0000)
    """

    q = quat.normalize()
    qv = Quaternion.fromVect(vect)

    rotated_v = q * (qv * q.inverse)

    return rotated_v.vector


if __name__ == "__main__":
    import doctest

    doctest.testmod()
