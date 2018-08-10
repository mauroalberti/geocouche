
from pygsf.libs_utils.gdal.gdal import *


data_path = r"../example_data/vx.asc"

dataset, geotransform, num_bands, projection = read_raster(data_path)

print("Geotransform: {}".format(geotransform))
print("Number of bands: {}".format(num_bands))
print("Projection: {}".format(projection))

band_params, band_array = read_band(dataset, 1)

print("Data type: {}".format(band_params["dataType"]))
print("Unit type: {}".format(band_params["unitType"]))
print("Statistics: {}".format(band_params["stats"]))
print("No data value: {}".format(band_params["noData"]))

print("Number of overviews: {}".format(band_params["numOverviews"]))
print("Number of color table entries: {}".format(band_params["numColorTableEntries"]))

