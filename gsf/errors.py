

class SubparallelLineationException(Exception):
    """
    Exception for subparallel GAxis/GVect instances.
    """
    pass

class SlickelineTypeException(Exception):
    """
    Exception for slickenline type.
    """
    pass

class SlickelineSenseException(Exception):
    """
    Exception for slickenline movement sense.
    """
    pass

class RasterParametersException(Exception):
    """
    Exception for raster parameters.
    """
    pass


class VectorInputException(Exception):
    """
    Exception for vector input parameters.
    """
    pass


class FunInputException(Exception):
    """
    Exception for function input errors.
    """
    pass


class OutputException(Exception):
    """
    Exception for output errors.
    """
    pass


class ConnectionException:
    pass


class AnaliticSurfaceIOException(Exception):
    pass


class AnaliticSurfaceCalcException(Exception):
    pass


class GPXIOException(Exception):
    pass


class VectorIOException(Exception):
    pass


class OGRIOException(Exception):
    """
    Exception for raster parameters.
    """
    pass
