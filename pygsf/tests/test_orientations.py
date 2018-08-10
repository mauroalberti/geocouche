# -*- coding: utf-8 -*-


import unittest

from ..orientations.orientations import *


class TestOrientations(unittest.TestCase):

    def setUp(self):

        pass

    def test_direct_general(self):
        """
        Check expected OrienM results for downward dip.
        """

        assert Direct.fromAzPl(90, 90).isDownward
        assert Direct.fromAzPl(90, -45).isUpward
        assert areClose(Direct.fromAzPl(90, 90).asVersor().z, -1.0)
        assert areClose(Direct.fromAzPl(90, -90).asVersor().z, 1.0)
        assert areClose(Direct.fromAzPl(0, 90).upward().asVersor().z, 1.0)
        assert areClose(Direct.fromAzPl(0, -90).downward().asVersor().z, -1.0)

    def test_direct_angle(self):

        assert areClose(Direct.fromAzPl(90, 45).angle(Direct.fromAzPl(90, 55)), 10.)
        assert areClose(Direct.fromAzPl(90, 45).angle(Direct.fromAzPl(270, 10)), 125.)
        assert areClose(Direct.fromAzPl(90, 90).angle(Direct.fromAzPl(135, 90)), 0.)
        assert areClose(Direct.fromAzPl(0, 0).angle(Direct.fromAzPl(135, 0)), 135.)
        assert areClose(Direct.fromAzPl(0, 80).angle(Direct.fromAzPl(180, 80)), 20.)

    def test_axis_angle(self):

        assert areClose(Axis.fromAzPl(90, 0).angle(Axis.fromAzPl(270, 0)), 0.)

    def test_plane_normal(self):

        assert areClose(Plane(90, 45).normDirectFrwrd().angle(Direct.fromAzPl(90, -45)), 0.)

    def test_plane2cplane(self):

        pl = Plane(90, 45).toCPlane(Point(0, 0, 0))
        assert areClose(pl.angle(CPlane(1, 0, 1, 0)), 0.)

    def test_plane_angle(self):

        assert areClose(Plane(90, 45).angle(Plane(90, 45)), 0.)
        assert areClose(Plane(90, 45).angle(Plane(90, 55)), 10.)
        assert areClose(Plane(90, 5).angle(Plane(270, 5)), 10.)
        assert areClose(Plane(90, 85).angle(Plane(270, 85)), 10.)
        assert areClose(Plane(0, 0).angle(Plane(0, 10)), 10.)
        assert areClose(Plane(0, 0).angle(Plane(180, 0)), 0.)

    def tearDown(self):

        pass


if __name__ == '__main__':

    unittest.main()
