# -*- coding: utf-8 -*-


from ..vectorial.vectorial import Point


class RectangularDomain(object):
    """
    Rectangular spatial domain class.

    """

    def __init__(self, pt_llc: Point, pt_trc: Point):
        """
        Class constructor.

        :param  pt_llc:  lower-left corner of the domain.
        :type  pt_llc:  Point.
        :param  pt_trc:  top-right corner of the domain.
        :type  pt_trc:  Point.

        :return:  RectangularDomain instance.

        Examples:
        """

        self._llcorner = pt_llc
        self._trcorner = pt_trc

    @property
    def llcorner(self):
        """
        Get lower-left corner of the spatial domain.

        :return:  lower-left corner of the spatial domain - Point.

        Examples:
        """

        return self._llcorner

    @property
    def trcorner(self):
        """
        Get top-right corner of the spatial domain.

        :return:  top-right corner of the spatial domain - Point.

        Examples:
        """

        return self._trcorner

    @property
    def xrange(self):
        """
        Get x range of spatial domain.

        :return:  x range - float.

        Examples:
        """

        return self.trcorner.x - self.llcorner.x

    @property
    def yrange(self):
        """
        Get y range of spatial domain.

        :return:  y range - float.

        Examples:
        """

        return self.trcorner.y - self.llcorner.y

    @property
    def zrange(self):
        """
        Get z range of spatial domain.

        :return:  z range - float.

        Examples:
        """

        return self.trcorner.z - self.llcorner.z

    @property
    def horiz_area(self):
        """
        Get horizontal area of spatial domain.

        :return:  area - float.

        Examples:
        """

        return self.xrange * self.yrange


def prjEquiv(prj1: str, prj2: str) -> bool:
    """
    Naive check on two projections equivalence.

    :param prj1: the first projection string.
    :type prj1: str.
    :param prj2: the second projection string.
    :type prj2: str.
    :return: bool
    """

    return prj1 == prj2


if __name__ == "__main__":

    import doctest
    doctest.testmod()
