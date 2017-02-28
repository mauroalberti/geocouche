
from geosurf.qgs_tools import loaded_point_layers
from auxiliary_windows import tFieldUndefined








def get_geolval(row):

    vals = row.split(',')
    az, dip = map(float, vals)
    return az, dip

def define_num_values(vals):

    if vals is None or vals == '':
        return False, "No value available"
    else:
        vals = vals.split("\n")
        valid_vals = filter(lambda row: len(row) > 1, vals)
        if len(valid_vals) == 0:
            return False, "No value available"
        else:
            try:
                geol_vals = map(get_geolval, valid_vals)
                return True, geol_vals
            except:
                return False, "Error in input values"


def formally_valid_angles_params(structural_input_params):

    for param_key in structural_input_params:
        if structural_input_params[param_key] is None:
            return False
    return True



def get_input_values_params(dialog):

    plane_azimuth_type = dialog.input_plane_orient_azimuth_type_QComboBox.currentText()

    values = dialog.input_values_QPlainTextEdit.toPlainText()

    return plane_azimuth_type, values


def get_anglecalc_input_params(dialog):

    point_layer = dialog.point_layer

    field_undefined_txt = dialog.field_undefined_txt

    plane_azimuth_type = dialog.input_plane_orient_azimuth_type_QComboBox.currentText()
    plane_azimuth_name_field = parse_field_choice(dialog.input_plane_azimuth_srcfld_QComboBox.currentText(),
                                                       field_undefined_txt)

    plane_dip_type = dialog.input_plane_orient_dip_type_QComboBox.currentText()
    plane_dip_name_field = parse_field_choice(dialog.input_plane_dip_srcfld_QComboBox.currentText(),
                                                   field_undefined_txt)

    target_dipdir = dialog.targetatt_dipdir_QDSB.value()
    target_dipangle = dialog.targetatt_dipang_QDSBB.value()

    output_shapefile_path = dialog.out_filename_QLEdit.text()

    return point_layer, dict(plane_azimuth_type=plane_azimuth_type,
                             plane_azimuth_name_field=plane_azimuth_name_field,
                             plane_dip_type=plane_dip_type,
                             plane_dip_name_field=plane_dip_name_field,
                             target_dipdir=target_dipdir,
                             target_dipangle=target_dipangle,
                             output_shapefile_path=output_shapefile_path)


def get_angle_data_type(structural_input_params):

    # define type for planar data
    if structural_input_params["plane_azimuth_name_field"] is not None and \
                    structural_input_params["plane_dip_name_field"] is not None:
        planar_data = True
        if structural_input_params["plane_azimuth_type"] == "dip dir.":
            planar_az_type = "dip_dir"
        elif structural_input_params["plane_azimuth_type"] == "strike rhr":
            planar_az_type = "strike_rhr"
        else:
            raise Exception("Error with input azimuth type")
        planar_dip_type = "dip"
    else:
        planar_data = False
        planar_az_type = None
        planar_dip_type = None

    return dict(planar_data=planar_data,
                planar_az_type=planar_az_type,
                planar_dip_type=planar_dip_type)








def parse_angles_geodata(input_data_types, structural_data):

    xy_vals = [(float(rec[0]), float(rec[1])) for rec in structural_data]

    try:
        if input_data_types["planar_data"]:
            azimuths = [float(rec[2]) for rec in structural_data]
            dipdir_vals = format_azimuth_values(azimuths,
                                                input_data_types["planar_az_type"])
            dipangle_vals = [float(rec[3]) for rec in structural_data]
            plane_vals = zip(dipdir_vals, dipangle_vals)
        else:
            plane_vals = None
    except Exception as e:
        raise Exception("Error in planar data parsing: {}".format(e.message))

    return xy_vals, plane_vals

