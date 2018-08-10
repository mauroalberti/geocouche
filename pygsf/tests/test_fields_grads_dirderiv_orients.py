# coding: utf-8


from pygsf.spatial.rasters.fields import *

import unittest


class TestDivergence(unittest.TestCase):

    def setUp(self):

        pass

    def test_gradients(self):
        """
        Test the gradients calculations.

        :return:
        """

        # Test pygsf gradients and directional derivative

        fld1 = array([
         [1, 1, 1, 1],
         [1, 1, 1, 1],
         [1, 1, 1, 1]])

        assert np.allclose(
         grad_x(fld1, cell_size_x=10),
         0.0)

        assert np.allclose(
         grad_y(fld1, cell_size_y=10),
         0.0)

        fld2 = array([
         [10, 10, 10, 10],
         [20, 20, 20, 20],
         [30, 30, 30, 30]])

        assert np.allclose(
         grad_x(fld2, cell_size_x=10),
         0.0)

        assert np.allclose(
         grad_y(fld2, cell_size_y=10),
         -1.0)

        assert np.allclose(
         dir_deriv(fld2, cell_size_x=10, cell_size_y=10, direct_rad=pi*45.0/180.0),
         -0.70710678)

        assert np.allclose(
         dir_deriv(fld2, cell_size_x=10, cell_size_y=10, direct_rad=pi*0.0/180.0),
         -1.0)

        assert np.allclose(
         dir_deriv(fld2, cell_size_x=10, cell_size_y=10, direct_rad=pi*180.0/180.0),
         1.0)

        assert np.allclose(
         dir_deriv(fld2, cell_size_x=10, cell_size_y=10, direct_rad=pi*90.0/180.0),
         0.0)

        assert np.allclose(
         dir_deriv(fld2, cell_size_x=10, cell_size_y=10, direct_rad=pi*270.0/180.0),
         0.0)

        assert np.allclose(
         dir_deriv(fld2, cell_size_x=10, cell_size_y=10, direct_rad=pi*315.0/180.0),
         -0.70710678)

        assert np.allclose(
         dir_deriv(fld2, cell_size_x=10, cell_size_y=10, direct_rad=pi*135.0/180.0),
         0.70710678)

    def test_orientations(self):
        """
        Test the gradients calculations.

        :return:
        """

        fld3 = array([
         [10, 10, 10, 10],
         [20, 20, 20, 20],
         [30, 30, 30, 30]])

        fld4 = fld3

        assert np.allclose(
         orients_d(fld3, fld4),
         45.0)

        assert np.allclose(
         orients_d(fld3, -fld4),
         135.0)

        assert np.allclose(
         orients_d(-fld3, fld4),
         315.0)

        assert np.allclose(
         orients_d(-fld3, -fld4),
         225.0)

        assert np.allclose(
         orients_d(fld3, 0.0),
         90.0)

        assert np.allclose(
         orients_d(0, fld4),
         0.0)

        assert np.allclose(
         orients_d(0, -fld4),
         180.0)

        assert np.allclose(
         orients_d(-fld3, 0.0),
         270.0)
