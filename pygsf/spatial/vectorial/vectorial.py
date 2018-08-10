# -*- coding: utf-8 -*-


from ...orientations.defaults import *
from ...mathematics.vectors import *


class Point(object):
    """
    Cartesian point.
    Dimensions: 3D (space)
    """

    def __init__(self, x: [int, float], y: [int, float], z: [int, float]=0.0):
        """
        Construct a Point instance.
        """

        vals = [x, y, z]
        if any(map(lambda val: not isinstance(val, (int, float)), vals)):
            raise VectorInputException("Input values must be integer of float")
        elif not all(map(isfinite, vals)):
            raise VectorInputException("Input values must be finite")
        else:
            self._a = array(vals, dtype=np.float64)

    def __repr__(self) -> str:

        return "Point({:.4f}, {:.4f}, {:.4f})".format(self.x, self.y, self.z)

    def __eq__(self, another: 'Point') -> Optional[bool]:
        """
        Return True if objects are equal.

        Example:
          >>> Point(1., 1., 1.) == Point(1, 1, 1)
          True
          >>> Point(1., 1., 1.) == Point(1, 1, -1)
          False
        """

        if not isinstance(another, Point):
            raise VectorInputException("Variables must be of the same type")
        else:
            return all([
                self.x == another.x,
                self.y == another.y,
                self.z == another.z])

    def __ne__(self, another: 'Point') -> Optional[bool]:
        """
        Return False if objects are equal.

        Example:
          >>> Point(1., 1., 1.) != Point(0., 0., 0.)
          True
        """

        if not isinstance(another, Point):
            return None
        else:
            return not (self == another)

    @property
    def a(self) -> 'np.array':
        """
        Return a copy of the object inner array.

        :return: double array of x, y, z values

        Examples:
          >>> Point(4, 3, 7).a
          array([4., 3., 7.])
        """

        return np.copy(self._a)

    @property
    def x(self) -> float:
        """
        Return x value

        Example:
          >>> Point(1.5, 1, 1).x
          1.5
        """

        return self.a[0]

    @property
    def y(self) -> float:
        """
        Return y value

        Example:
          >>> Point(1.5, 3.0, 1).y
          3.0
        """
        return self.a[1]

    @property
    def z(self) -> float:
        """
        Return z value

        Example:
          >>> Point(1.5, 3.2, 41.).z
          41.0
        """
        return self.a[2]

    def toXYZ(self) -> Tuple[float, float, float]:
        """
        Returns the spatial components as a tuple of three values.

        :return: the spatial components (x, y, z).
        :rtype: a tuple of three floats.

        Examples:
          >>> Point(1, 0, 3).toXYZ()
          (1.0, 0.0, 3.0)
        """

        return self.x, self.y, self.z

    def toArray(self) -> 'array':
        """
        Return a double Numpy array representing the point values.

        :return: Numpy array

        Examples:
          >>> Point(1, 2, 3).toArray()
          array([1., 2., 3.])
        """

        return self.a

    def pXY(self) -> 'Point':
        """
        Projection on the x-y plane

        :return: projected object instance

        Examples:
          >>> Point(2, 3, 4).pXY()
          Point(2.0000, 3.0000, 0.0000)
        """

        return self.__class__(self.x, self.y, 0.0)

    def pXZ(self) -> 'Point':
        """
        Projection on the x-z plane

        :return: projected object instance

        Examples:
          >>> Point(2, 3, 4).pXZ()
          Point(2.0000, 0.0000, 4.0000)
        """

        return self.__class__(self.x, 0.0, self.z)

    def pYZ(self) -> 'Point':
        """
        Projection on the y-z plane

        :return: projected object instance

        Examples:
          >>> Point(2, 3, 4).pYZ()
          Point(0.0000, 3.0000, 4.0000)
        """

        return self.__class__(0.0, self.y, self.z)

    @property
    def len3D(self) -> float:
        """
        Spatial distance of the point from the axis origin.

        :return: distance
        :rtype: float

        Examples:
          >>> Point(4.0, 3.0, 0.0).len3D
          5.0
        """

        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    @property
    def len2D(self) -> float:
        """
        2D distance of the point from the axis origin.

        Example:
          >>> Point(3, 4, 0).len2D
          5.0
          >>> Point(12, 5, 3).len2D
          13.0
        """

        return sqrt(self.x * self.x + self.y * self.y)

    def deltaX(self, another: 'Point') -> Optional[float]:
        """
        Delta between x components of two Point Instances.

        :return: difference value
        :rtype: float

        Examples:
          >>> Point(1, 2, 3).deltaX(Point(4, 7, 1))
          3.0
        """

        if not isinstance(another, Point):
            return None
        else:
            return another.x - self.x

    def deltaY(self, another: 'Point') -> Optional[float]:
        """
        Delta between y components of two Point Instances.

        :return: difference value
        :rtype: float

        Examples:
          >>> Point(1, 2, 3).deltaY(Point(4, 7, 1))
          5.0
        """

        if not isinstance(another, Point):
            return None
        else:
            return another.y - self.y

    def deltaZ(self, another: 'Point') -> Optional[float]:
        """
        Delta between x components of two Point Instances.

        :return: difference value
        :rtype: float

        Examples:
          >>> Point(1, 2, 3).deltaZ(Point(4, 7, 1))
          -2.0
        """

        if not isinstance(another, Point):
            return None
        else:
            return another.z - self.z

    def dist3DWith(self, another: 'Point') -> Optional[float]:
        """
        Calculate Euclidean spatial distance between two points.

        Examples:
          >>> Point(1., 1., 1.).dist3DWith(Point(4., 5., 1,))
          5.0
          >>> Point(1, 1, 1).dist3DWith(Point(4, 5, 1))
          5.0
        """

        if not isinstance(another, Point):
            return None
        else:
            return sqrt((self.x - another.x) ** 2 + (self.y - another.y) ** 2 + (self.z - another.z) ** 2)

    def dist2DWith(self, another: 'Point') -> Optional[float]:
        """
        Calculate horizontal (2D) distance between two points.

        Examples:
          >>> Point(1., 1., 1.).dist2DWith(Point(4., 5., 7.))
          5.0
        """

        if not isinstance(another, Point):
            return None
        else:
            return sqrt((self.x - another.x) ** 2 + (self.y - another.y) ** 2)

    def scale(self, scale_factor: [int, float]) -> Optional['Point']:
        """
        Create a scaled object.

        Example;
          >>> Point(1, 0, 1).scale(2.5)
          Point(2.5000, 0.0000, 2.5000)
          >>> Point(1, 0, 1).scale(np.nan) is None
          True
          >>> Point(1, 0, 1).scale(np.inf) is None
          True
        """

        if not isinstance(scale_factor, (int, float)):
            return None
        elif not isfinite(scale_factor):
            return None
        else:
            x, y, z = arrToTuple(self.a * scale_factor)
            return self.__class__(x, y, z)

    def invert(self) -> 'Point':
        """
        Create a new object with inverted direction.

        Examples:
          >>> Point(1, 1, 1).invert()
          Point(-1.0000, -1.0000, -1.0000)
          >>> Point(2, -1, 4).invert()
          Point(-2.0000, 1.0000, -4.0000)
        """

        return self.scale(-1)

    def isCoinc(self, another: 'Point', tolerance: [int, float] = MIN_SEPARATION_THRESHOLD) -> Optional[bool]:
        """
        Check spatial coincidence of two points

        Example:
          >>> Point(1., 0., -1.).isCoinc(Point(1., 1.5, -1.))
          False
          >>> Point(1., 0., 0.).isCoinc(Point(1., 0., 0.))
          True
          >>> Point(1.2, 7.4, 1.4).isCoinc(Point(1.2, 7.4, 1.4))
          True
          >>> Point(1.2, 7.4, 1.4).isCoinc(Point(1.2, 7.4, 1.4), tolerance=np.nan) is None
          True
        """

        if not isinstance(another, Point):
            return None
        elif not isinstance(tolerance, (int, float)):
            return None
        elif not isfinite(tolerance):
            return None
        else:
            distance_2d = self.dist2DWith(another)
            if np.isnan(distance_2d) or distance_2d > tolerance:
                return False
            else:
                distance_3d = self.dist3DWith(another)
                if np.isnan(distance_3d) or distance_3d > tolerance:
                    return False
                else:
                    return True

    def shift(self, sx: float, sy: float, sz: float) -> Optional['Point']:
        """
        Create a new object shifted by given amount from the self instance.

        Example:
          >>> Point(1, 1, 1).shift(0.5, 1., 1.5)
          Point(1.5000, 2.0000, 2.5000)
          >>> Point(1, 2, -1).shift(0.5, 1., 1.5)
          Point(1.5000, 3.0000, 0.5000)
          >>> Point(1, 2, -1).shift(0.5, np.nan, 1.5) is None
          True
       """

        vals = [sx, sy, sz]
        if not all(map(lambda val: isinstance(val, (int, float)), vals)):
            return None
        elif not all(map(isfinite, vals)):
            return None
        else:
            return self.__class__(self.x + sx, self.y + sy, self.z + sz)

    def asVect(self) -> 'Vect':
        """
        Create a vector based on the point coordinates

        Example:
          >>> Point(1, 1, 0).asVect()
          Vect(1.0000, 1.0000, 0.0000)
          >>> Point(0.2, 1, 6).asVect()
          Vect(0.2000, 1.0000, 6.0000)
        """

        return Vect(self.x, self.y, self.z)


class CPlane(object):
    """
    Cartesian plane.
    Expressed by equation:
    ax + by + cz + d = 0

    Note: Plane is locational - its position in space is defined.
    This contrast with PPlane, defined just by its attitude, but with undefined position

    """

    def __init__(self, a, b, c, d):

        self._a = float(a)
        self._b = float(b)
        self._c = float(c)
        self._d = float(d)

    @property
    def a(self):
        """
        Return a coefficient of a Plane instance.

        Example:
          >>> CPlane(1, 0, 0, 2).a
          1.0
        """

        return self._a

    @property
    def b(self):
        """
        Return b coefficient of a Plane instance.

        Example:
          >>> CPlane(1, 4, 0, 2).b
          4.0
        """

        return self._b

    @property
    def c(self):
        """
        Return a coefficient of a Plane instance.

        Example:
          >>> CPlane(1, 0, 5.4, 2).c
          5.4
        """

        return self._c

    @property
    def d(self):
        """
        Return a coefficient of a Plane instance.

        Example:
          >>> CPlane(1, 0, 0, 2).d
          2.0
        """

        return self._d

    @property
    def v(self):
        """
        Return coefficients of a Plane instance.

        Example:
          >>> CPlane(1, 1, 7, -4).v
          (1.0, 1.0, 7.0, -4.0)
        """
        return self.a, self.b, self.c, self.d

    @classmethod
    def fromPoints(cls, pt1, pt2, pt3):
        """
        Create a Plane from three given Point instances.

        Example:
          >>> CPlane.fromPoints(Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0))
          CPlane(0.0000, 0.0000, 1.0000, 0.0000)
          >>> CPlane.fromPoints(Point(0, 0, 0), Point(0, 1, 0), Point(0, 0, 1))
          CPlane(1.0000, 0.0000, 0.0000, 0.0000)
        """

        matr_a = array(
            [[pt1.y, pt1.z, 1],
            [pt2.y, pt2.z, 1],
            [pt3.y, pt3.z, 1]])

        matr_b = - array(
            [[pt1.x, pt1.z, 1],
            [pt2.x, pt2.z, 1],
            [pt3.x, pt3.z, 1]])

        matr_c = array(
            [[pt1.x, pt1.y, 1],
            [pt2.x, pt2.y, 1],
            [pt3.x, pt3.y, 1]])

        matr_d = - array(
            [[pt1.x, pt1.y, pt1.z],
            [pt2.x, pt2.y, pt2.z],
            [pt3.x, pt3.y, pt3.z]])

        return cls(
            np.linalg.det(matr_a),
            np.linalg.det(matr_b),
            np.linalg.det(matr_c),
            np.linalg.det(matr_d))

    def __repr__(self):

        return "CPlane({:.4f}, {:.4f}, {:.4f}, {:.4f})".format(*self.v)

    def normVersor(self):
        """
        Return the versor normal to the cartesian plane.

        Examples:
          >>> CPlane(0, 0, 5, -2).normVersor()
          Vect(0.0000, 0.0000, 1.0000)
          >>> CPlane(0, 7, 0, 5).normVersor()
          Vect(0.0000, 1.0000, 0.0000)
        """

        return Vect(self.a, self.b, self.c).versor()

    def toPoint(self):
        """
        Returns a point lying in the plane (non-unique solution).

        Examples:
          >>> CPlane(0, 0, 1, -1).toPoint()
          Point(0.0000, 0.0000, 1.0000)
        """

        point = Point(*pointSolution(array([[self.a, self.b, self.c]]),
                                     array([-self.d])))
        return point

    def intersVersor(self, another):
        """
        Return intersection versor for two intersecting planes.

        >>> a = CPlane(1, 0, 0, 0)
        >>> b = CPlane(0, 0, 1, 0)
        >>> a.intersVersor(b)
        Vect(0.0000, -1.0000, 0.0000)
        """

        return self.normVersor().vCross(another.normVersor()).versor()

    def intersPoint(self, another):
        """
        Return point on intersection line (obviously non-unique solution)
        for two planes.

        >>> a = CPlane(1, 0, 0, 0)
        >>> b = CPlane(0, 0, 1, 0)
        >>> a.intersPoint(b)
        Point(0.0000, 0.0000, 0.0000)
        """

        # find a point lying on the intersection line (this is a non-unique solution)
        a = array([[self.a, self.b, self.c], [another.a, another.b, another.c]])
        b = array([-self.d, -another.d])
        x, y, z = pointSolution(a, b)

        return Point(x, y, z)

    def isPointInPlane(self, pt):
        """
          Check whether a point lie in a plane.

          >>> pl = CPlane(0, 0, 1, 0)
          >>> pt = Point(0, 1, 0)
          >>> pl.isPointInPlane(pt)
          True
        """

        if abs(self.a * pt.x + self.b * pt.y + self.c * pt.z + self.d) < MIN_SCALAR_VALUE:
            return True
        else:
            return False

    def angle(self, another):
        """
        Calculate angle (in degrees) between two planes.

        Examples:
          >>> CPlane(1,0,0,0).angle(CPlane(0,1,0,0))
          90.0
          >>> CPlane(1,0,0,0).angle(CPlane(1,0,1,0))
          45.0
          >>> CPlane(1,0,0,0).angle(CPlane(1,0,0,0))
          0.0
        """

        angle_degr = self.normVersor().angle(another.normVersor())
        if abs(angle_degr) < MIN_ANGLE_DEGR_VALUE:
            angle_degr = 0.0
        elif angle_degr > 90.0:
            angle_degr = 180.0 - angle_degr

        return angle_degr

    def isSubParallel(self, another, angle_tolerance=PLANE_ANGLE_THRESHOLD):
        """
        Check that two Plane are sub-parallel

        :param another: a Plane instance
        :param angle_tolerance: the maximum allowed divergence angle (in degrees)
        :return: Boolean

         Examples:
          >>> CPlane(1,0,0,0).isSubParallel(CPlane(1,0,0,0))
          True
          >>> CPlane(1,0,0,0).isSubParallel(CPlane(1,0,1,0))
          False
        """

        return self.angle(another) < angle_tolerance


# TODO class Path
"""
The trajectory of a Point with time
"""


class Segment(object):
    """
    Segment is a geometric object defined by a straight line between
    two points.
    """

    def __init__(self, start_pt, end_pt):

        self._start_pt = start_pt
        self._end_pt = end_pt

    @property
    def start_pt(self):

        return self._start_pt

    @property
    def end_pt(self):

        return self._end_pt

    def clone(self):

        return Segment(self.start_pt, self.end_pt)

    def increasing_x(self):

        if self.end_pt.x < self.start_pt.x:
            return Segment(self.end_pt, self.start_pt)
        else:
            return self.clone()

    @property
    def x_range(self):

        if self.start_pt.x < self.end_pt.x:
            return self.start_pt.x, self.end_pt.x
        else:
            return self.end_pt.x, self.start_pt.x

    @property
    def y_range(self):

        if self.start_pt.y < self.end_pt.y:
            return self.start_pt.y, self.end_pt.y
        else:
            return self.end_pt.y, self.start_pt.y

    @property
    def z_range(self):

        if self.start_pt.z < self.end_pt.z:
            return self.start_pt.z, self.end_pt.z
        else:
            return self.end_pt.z, self.start_pt.z

    @property
    def delta_x(self):

        return self.end_pt.x - self.start_pt.x

    @property
    def delta_y(self):

        return self.end_pt.y - self.start_pt.y

    @property
    def delta_z(self):

        return self.end_pt.z - self.start_pt.z

    @property
    def length_2d(self):

        return self.start_pt.dist_2d(self.end_pt)

    @property
    def length_3d(self):

        return self.start_pt.dist_3d(self.end_pt)

    def vector(self):

        return Vect(self.delta_x,
                    self.delta_y,
                    self.delta_z)

    def segment_2d_m(self):

        return (self.end_pt.y - self.start_pt.y) / (self.end_pt.x - self.start_pt.x)

    def segment_2d_p(self):

        return self.start_pt.y - self.segment_2d_m() * self.start_pt.x

    def intersection_2d_pt(self, another):

        assert self.length_2d > 0.0
        assert another.length_2d > 0.0

        if self.start_pt.x == self.end_pt.x:  # self segment parallel to y axis
            x0 = self.start_pt.x
            try:
                m1, p1 = another.segment_2d_m(), another.segment_2d_p()
            except:
                return None
            y0 = m1 * x0 + p1
        elif another.start_pt.x == another.end_pt.x:  # another segment parallel to y axis
            x0 = another.start_pt.x
            try:
                m1, p1 = self.segment_2d_m(), self.segment_2d_p()
            except:
                return None
            y0 = m1 * x0 + p1
        else:  # no segment parallel to y axis
            m0, p0 = self.segment_2d_m(), self.segment_2d_p()
            m1, p1 = another.segment_2d_m(), another.segment_2d_p()
            x0 = (p1 - p0) / (m0 - m1)
            y0 = m0 * x0 + p0

        return Point(x0, y0)

    def contains_2d_pt(self, pt2d):

        segment_length2d = self.length_2d
        segmentstart_pt2d_distance = self.start_pt.dist_2d(pt2d)
        segmentend_pt2d_distance = self.end_pt.dist_2d(pt2d)

        if segmentstart_pt2d_distance > segment_length2d or \
                segmentend_pt2d_distance > segment_length2d:
            return False
        else:
            return True

    def fast_2d_contains_pt(self, pt2d):
        """
        to work properly, this function requires that the pt lies on the line defined by the segment
        """

        range_x = self.x_range
        range_y = self.y_range

        if range_x[0] <= pt2d.x <= range_x[1] or \
                range_y[0] <= pt2d.y <= range_y[1]:
            return True
        else:
            return False

    def scale(self, scale_factor):
        """
        Scale a segment by the given scale_factor.
        Start point does not change.

        :param scale_factor: float
        :return: Segment instance
        """

        delta_x = self.delta_x * scale_factor
        delta_y = self.delta_y * scale_factor
        delta_z = self.delta_z * scale_factor

        end_pt = Point(self.start_pt.x + delta_x,
                       self.start_pt.y + delta_y,
                       self.start_pt.z + delta_z)

        return Segment(self.start_pt,
                       end_pt)

    def densify_2d_segment(self, densify_distance):
        """
        Densify a segment by adding additional points
        separated a distance equal to densify_distance.
        The result is no longer a Segment instance, instead it is a Line instance.

        :param densify_distance: float
        :return: Line
        """

        assert densify_distance > 0.0

        length2d = self.length_2d

        assert length2d > 0.0

        vect = self.vector()
        vers_2d = vect.versor_2d
        generator_vector = vers_2d.scale(densify_distance)

        assert generator_vector.len_2d > 0.0

        interpolated_line = Line([self.start_pt])
        n = 0
        while True:
            n += 1
            new_pt = self.start_pt.vect_offset(generator_vector.scale(n))
            distance = self.start_pt.dist_2d(new_pt)
            if distance >= length2d:
                break
            interpolated_line.add_pt(new_pt)
        interpolated_line.add_pt(self.end_pt)

        return interpolated_line


class Line(object):
    """
    A list of Point objects.
    """

    def __init__(self, pts=None):

        if pts is None:
            pts = []
        self._pts = pts

    @property
    def pts(self):

        return self._pts

    @property
    def num_pts(self):

        return len(self.pts)

    def clone(self):

        return Line(map(lambda pt: pt.clone(), self.pts))

    def add_pt(self, pt):
        """
        In-place transformation of the original Line instance
        by adding a new point at the end.

        :param pt: Point
        :return: self
        """

        self.pts.append(pt)

    def add_pts(self, pt_list):
        """
        In-place transformation of the original Line instance
        by adding a new set of points at the end.

        :param pt_list: list
        :return: self
        """

        self._pts += pt_list

    @property
    def x_list(self):

        return [pt.x for pt in self.pts]

    @property
    def y_list(self):

        return [pt.y for pt in self.pts]

    @property
    def z_list(self):

        return [pt.z for pt in self.pts]

    def xy_lists(self):

        return self.x_list, self.y_list

    @property
    def x_min(self):

        return np.nanmin(self.x_list)

    @property
    def x_max(self):

        return np.nanmax(self.x_list)

    @property
    def y_min(self):

        return np.nanmin(self.y_list)

    @property
    def y_max(self):

        return np.nanmax(self.y_list)

    @property
    def z_min(self):

        return np.nanmin(self.z_list)

    @property
    def z_max(self):

        return np.nanmax(self.z_list)

    def z_array(self):

        return np.array(self.z_list)

    @property
    def z_mean(self):

        return np.nanmean(self.z_array())

    @property
    def z_var(self):

        return np.nanvar(self.z_array())

    @property
    def z_std(self):

        return np.nanstd(self.z_array())

    def remove_coincident_points(self):
        """
        Remove coincident successive points

        :return: Line instance
        """

        assert self.num_pts >= 2

        new_line = Line(self.pts[:1])
        for ndx in range(1, self.num_pts):
            if not self.pts[ndx].coincident(new_line.pts[-1]):
                new_line.add_pt(self.pts[ndx])

        return new_line

    def as_segments(self):
        """
        Convert to a list of segments.

        :return: list of Segment objects
        """

        pts_pairs = zip(self.pts[:-1], self.pts[1:])

        segments = [Segment(pt_a, pt_b) for (pt_a, pt_b) in pts_pairs]

        return segments

    def densify_2d_line(self, sample_distance):
        """
        Densify a line into a new line instance,
        using the provided sample distance.
        Returned Line instance has coincident successive points removed.

        :param sample_distance: float
        :return: Line instance
        """

        assert sample_distance > 0.0

        segments = self.as_segments()

        densified_line_list = [segment.densify_2d_segment(sample_distance) for segment in segments]

        assert len(densified_line_list) > 0

        densifyied_multiline = MultiLine(densified_line_list)

        densifyied_line = densifyied_multiline.to_line()

        densifyied_line_wo_coinc_pts = densifyied_line.remove_coincident_points()

        return densifyied_line_wo_coinc_pts

    def join(self, another):
        """
        Joins together two lines and returns the join as a new line without point changes,
        with possible overlapping points
        and orientation mismatches between the two original lines
        """

        return Line(self.pts + another.pts)

    @property
    def length_3d(self):

        length = 0.0
        for ndx in range(self.num_pts - 1):
            length += self.pts[ndx].dist_3d(self.pts[ndx + 1])
        return length

    @property
    def length_2d(self):

        length = 0.0
        for ndx in range(self.num_pts - 1):
            length += self.pts[ndx].dist_2d(self.pts[ndx + 1])
        return length

    def incremental_length_3d(self):

        incremental_length_list = []
        length = 0.0
        incremental_length_list.append(length)
        for ndx in range(self.num_pts - 1):
            length += self.pts[ndx].dist_3d(self.pts[ndx + 1])
            incremental_length_list.append(length)

        return incremental_length_list

    def incremental_length_2d(self):

        lIncrementalLengths = []
        length = 0.0
        lIncrementalLengths.append(length)
        for ndx in range(self.num_pts - 1):
            length += self.pts[ndx].dist_2d(self.pts[ndx + 1])
            lIncrementalLengths.append(length)

        return lIncrementalLengths

    def reverse_direction(self):

        new_line = self.clone()
        new_line.pts.reverse()  # in-place operation on new_line

        return new_line

    def slopes(self):

        lSlopes = []
        for ndx in range(self.num_pts - 1):
            vector = Segment(self.pts[ndx], self.pts[ndx + 1]).vector()
            lSlopes.append(-vector.slope)  # minus because vector convetion is positive downward
        lSlopes.append(np.nan)  # slope value for last point is unknown

        return lSlopes

    def absolute_slopes(self):

        return map(abs, self.slopes())

    def crs_project(self, srcCrs, destCrs):

        points = []
        for point in self.pts:
            destCrs_point = project_point(point, srcCrs, destCrs)
            points.append(destCrs_point)

        return Line(points)


class MultiLine(object):
    """
    MultiLine is a list of Line objects
    """

    def __init__(self, lines_list=None):

        if lines_list is None:
            lines_list = []
        self._lines = lines_list

    @property
    def lines(self):

        return self._lines

    def add(self, line):

        return MultiLine(self.lines + [line])

    def clone(self):

        return MultiLine(self.lines)

    @property
    def num_parts(self):

        return len(self.lines)

    @property
    def num_points(self):

        num_points = 0
        for line in self.lines:
            num_points += line.num_pts

        return num_points

    @property
    def x_min(self):

        return np.nanmin([line.x_min for line in self.lines])

    @property
    def x_max(self):

        return np.nanmax([line.x_max for line in self.lines])

    @property
    def y_min(self):

        return np.nanmin([line.y_min for line in self.lines])

    @property
    def y_max(self):

        return np.nanmax([line.y_max for line in self.lines])

    @property
    def z_min(self):

        return np.nanmin([line.z_min for line in self.lines])

    @property
    def z_max(self):

        return np.nanmax([line.z_max for line in self.lines])

    def is_continuous(self):

        for line_ndx in range(len(self._lines) - 1):
            if not self.lines[line_ndx].pts[-1].coincident(self.lines[line_ndx + 1].pts[0]) or \
                    not self.lines[line_ndx].pts[-1].coincident(self.lines[line_ndx + 1].pts[-1]):
                return False

        return True

    def is_unidirectional(self):

        for line_ndx in range(len(self.lines) - 1):
            if not self.lines[line_ndx].pts[-1].coincident(self.lines[line_ndx + 1].pts[0]):
                return False

        return True

    def to_line(self):

        return Line([point for line in self.lines for point in line.pts])

    def crs_project(self, srcCrs, destCrs):

        lines = []
        for line in self.lines:
            lines.append(line.crs_project(srcCrs, destCrs))

        return MultiLine(lines)

    def densify_2d_multiline(self, sample_distance):

        lDensifiedLines = []
        for line in self.lines:
            lDensifiedLines.append(line.densify_2d_line(sample_distance))

        return MultiLine(lDensifiedLines)

    def remove_coincident_points(self):

        cleaned_lines = []
        for line in self.lines:
            cleaned_lines.append(line.remove_coincident_points())

        return MultiLine(cleaned_lines)


class ParamLine3D(object):
    """
    parametric line
    srcPt: source Point
    l, m, n: .....
    """

    def __init__(self, srcPt, l, m, n):

        assert -1.0 <= l <= 1.0
        assert -1.0 <= m <= 1.0
        assert -1.0 <= n <= 1.0

        self._srcPt = srcPt
        self._l = l
        self._m = m
        self._n = n

    def intersect_cartes_plane(self, cartes_plane):
        """
        Return intersection point between parametric line and Cartesian plane
        """

        # line parameters
        x1, y1, z1 = self._srcPt.x, self._srcPt.y, self._srcPt.z
        l, m, n = self._l, self._m, self._n

        # Cartesian plane parameters
        a, b, c, d = cartes_plane.a, cartes_plane.b, cartes_plane.c, cartes_plane.d

        try:
            k = (a * x1 + b * y1 + c * z1 + d) / (a * l + b * m + c * n)
        except ZeroDivisionError:
            return None

        return Point(x1 - l * k,
                     y1 - m * k,
                     z1 - n * k)


def eq_xy_pair(xy_pair_1, xy_pair_2):
    if xy_pair_1[0] == xy_pair_2[0] and xy_pair_1[1] == xy_pair_2[1]:
        return True

    return False


def remove_equal_consecutive_xypairs(xy_list):
    out_xy_list = [xy_list[0]]

    for n in range(1, len(xy_list)):
        if not eq_xy_pair(xy_list[n], out_xy_list[-1]):
            out_xy_list.append(xy_list[n])

    return out_xy_list


def xytuple_list_to_Line(xy_list):
    return Line([Point(x, y) for (x, y) in xy_list])


def xytuple_l2_to_MultiLine(xytuple_list2):
    # input is a list of list of (x,y) values

    assert len(xytuple_list2) > 0
    lines_list = []
    for xy_list in xytuple_list2:
        assert len(xy_list) > 0
        lines_list.append(xytuple_list_to_Line(xy_list))

    return MultiLine(lines_list)


def merge_line(line):
    """
    line: a list of (x,y,z) tuples for line
    """

    line_type, line_geometry = line

    if line_type == 'multiline':
        path_line = xytuple_l2_to_MultiLine(line_geometry).to_line()
    elif line_type == 'line':
        path_line = xytuple_list_to_Line(line_geometry)
    else:
        raise Exception("unknown line type")

    # transformed into a single Line

    return MultiLine([path_line]).to_line().remove_coincident_points()


def merge_lines(lines, progress_ids):
    """
    lines: a list of list of (x,y,z) tuples for multilines
    """

    sorted_line_list = [line for (_, line) in sorted(zip(progress_ids, lines))]

    line_list = []
    for line in sorted_line_list:

        line_type, line_geometry = line

        if line_type == 'multiline':
            path_line = xytuple_l2_to_MultiLine(line_geometry).to_line()
        elif line_type == 'line':
            path_line = xytuple_list_to_Line(line_geometry)
        else:
            continue
        line_list.append(path_line)  # now a list of Lines

    # now the list of Lines is transformed into a single Line
    line = MultiLine(line_list).to_line().remove_coincident_points()

    return line


if __name__ == "__main__":

    import doctest
    doctest.testmod()
