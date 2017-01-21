
from geosurf.qgs_tools import loaded_point_layers


def parse_field_choice(val, choose_message):

    if val == choose_message:
        return None
    else:
        return val


def ptlayer_valid_params(structural_input_params):

    if structural_input_params["plane_azimuth_name_field"] is not None and \
                    structural_input_params["plane_dip_name_field"] is not None:
        return True
    elif structural_input_params["line_azimuth_name_field"] is not None and \
                    structural_input_params["line_dip_name_field"] is not None:
        return True
    else:
        return False


def formally_valid_angles_params(structural_input_params):

    for param_key in structural_input_params:
        if structural_input_params[param_key] is None:
            return False
    return True


def get_input_ptlayer_params(dialog):

    point_layer = dialog.point_layer

    field_undefined_txt = dialog.field_undefined_txt

    plane_azimuth_type = dialog.input_plane_orient_azimuth_type_QComboBox.currentText()
    plane_azimuth_name_field = parse_field_choice(dialog.input_plane_azimuth_srcfld_QComboBox.currentText(),
                                                       field_undefined_txt)

    plane_dip_type = dialog.input_plane_orient_dip_type_QComboBox.currentText()
    plane_dip_name_field = parse_field_choice(dialog.input_plane_dip_srcfld_QComboBox.currentText(),
                                                   field_undefined_txt)

    line_azimuth_type = dialog.input_line_orient_azimuth_type_QComboBox.currentText()
    line_azimuth_name_field = parse_field_choice(dialog.input_line_azimuth_srcfld_QComboBox.currentText(),
                                                      field_undefined_txt)

    line_dip_type = dialog.input_line_orient_dip_type_QComboBox.currentText()
    line_dip_name_field = parse_field_choice(dialog.input_line_dip_srcfld_QComboBox.currentText(),
                                                  field_undefined_txt)

    return point_layer, dict(plane_azimuth_type=plane_azimuth_type,
                             plane_azimuth_name_field=plane_azimuth_name_field,
                             plane_dip_type=plane_dip_type,
                             plane_dip_name_field=plane_dip_name_field,
                             line_azimuth_type=line_azimuth_type,
                             line_azimuth_name_field=line_azimuth_name_field,
                             line_dip_type=line_dip_type,
                             line_dip_name_field=line_dip_name_field)


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


def get_stereoplot_data_type(stereoplot_input_params):

    # define type for planar data
    if stereoplot_input_params["plane_azimuth_name_field"] is not None and \
                    stereoplot_input_params["plane_dip_name_field"] is not None:
        planar_data = True
        if stereoplot_input_params["plane_azimuth_type"] == "dip dir.":
            planar_az_type = "dip_dir"
        elif stereoplot_input_params["plane_azimuth_type"] == "strike rhr":
            planar_az_type = "strike_rhr"
        planar_dip_type = "dip"
    else:
        planar_data = False
        planar_az_type = None
        planar_dip_type = None

    # define type for linear data
    if stereoplot_input_params["line_azimuth_name_field"] is not None and \
                    stereoplot_input_params["line_dip_name_field"] is not None:
        linear_data = True
        linear_az_type = "trend"
        linear_dip_type = "plunge"
    else:
        linear_data = False
        linear_az_type = None
        linear_dip_type = None

    return dict(planar_data=planar_data,
                planar_az_type=planar_az_type,
                planar_dip_type=planar_dip_type,
                linear_data=linear_data,
                linear_az_type=linear_az_type,
                linear_dip_type=linear_dip_type)


def get_angle_data_type(structural_input_params):

    # define type for planar data
    if structural_input_params["plane_azimuth_name_field"] is not None and \
                    structural_input_params["plane_dip_name_field"] is not None:
        planar_data = True
        if structural_input_params["plane_azimuth_type"] == "dip dir.":
            planar_az_type = "dip_dir"
        elif structural_input_params["plane_azimuth_type"] == "strike rhr":
            planar_az_type = "strike_rhr"
        planar_dip_type = "dip"
    else:
        planar_data = False
        planar_az_type = None
        planar_dip_type = None

    return dict(planar_data=planar_data,
                planar_az_type=planar_az_type,
                planar_dip_type=planar_dip_type)


def parse_stereoplot_geodata(input_data_types, structural_data):

    xy_vals = [(float(rec[0]), float(rec[1])) for rec in structural_data]

    try:
        if input_data_types["planar_data"]:
            if input_data_types["planar_az_type"] == "dip_dir":
                dipdir_vals = [float(rec[2]) for rec in structural_data]
            elif input_data_types["planar_az_type"] == "strike_rhr":
                dipdir_raw_vals = [float(rec[2]) + 90.0 for rec in structural_data]
                dipdir_vals = [val if val < 360.0 else val - 360.0 for val in dipdir_raw_vals]
            dipangle_vals = [float(rec[3]) for rec in structural_data]
            plane_vals = zip(dipdir_vals, dipangle_vals)
            line_data_ndx_start = 4
        else:
            plane_vals = None
            line_data_ndx_start = 2
    except:
        raise Exception("Error in planar data")

    try:
        if input_data_types["linear_data"]:
            line_vals = [(float(rec[line_data_ndx_start]), float(rec[line_data_ndx_start + 1])) for rec in
                         structural_data]
        else:
            line_vals = None
    except:
        raise Exception("Error in linear data")

    return xy_vals, plane_vals, line_vals


def parse_angles_geodata(input_data_types, structural_data):

    xy_vals = [(float(rec[0]), float(rec[1])) for rec in structural_data]

    try:
        if input_data_types["planar_data"]:
            if input_data_types["planar_az_type"] == "dip_dir":
                dipdir_vals = [float(rec[2]) for rec in structural_data]
            elif input_data_types["planar_az_type"] == "strike_rhr":
                dipdir_raw_vals = [float(rec[2]) + 90.0 for rec in structural_data]
                dipdir_vals = [val if val < 360.0 else val - 360.0 for val in dipdir_raw_vals]
            dipangle_vals = [float(rec[3]) for rec in structural_data]
            plane_vals = zip(dipdir_vals, dipangle_vals)
        else:
            plane_vals = None
    except:
        raise Exception("Error in planar data")

    return xy_vals, plane_vals

