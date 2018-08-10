# -*- coding: utf-8 -*-


from .defaults import *


def matrScaling(scale_factor_x, scale_factor_y, scale_factor_z):
    """
    
    :param scale_factor_x: 
    :param scale_factor_y: 
    :param scale_factor_z: 
    :return:

    Examples:
    """

    return np.array([(scale_factor_x, 0.0, 0.0),
                     (0.0, scale_factor_y, 0.0),
                     (0.0, 0.0, scale_factor_z)])


def matrHorizSimpleShear(phi_angle_degr, alpha_angle_degr):
    """
    
    :param phi_angle_degr: 
    :param alpha_angle_degr: 
    :return:

    Examples:
    """

    phi_angle_rad = radians(phi_angle_degr)
    alpha_angle_rad = radians(alpha_angle_degr)

    gamma = tan(phi_angle_rad)
    sin_a = sin(alpha_angle_rad)
    cos_a = cos(alpha_angle_rad)

    return np.array([(1.0 - gamma * sin_a * cos_a, gamma * cos_a * cos_a, 0.0),
                     (-gamma * sin_a * sin_a, 1.0 + gamma * sin_a * cos_a, 0.0),
                     (0.0, 0.0, 1.0)])


def matrVertSimpleShear(phi_angle_degr, alpha_angle_degr):
    """
    
    :param phi_angle_degr: 
    :param alpha_angle_degr: 
    :return:

    Examples:
    """

    phi_angle_rad = radians(phi_angle_degr)
    alpha_angle_rad = radians(alpha_angle_degr)

    gamma = tan(phi_angle_rad)
    sin_a = sin(alpha_angle_rad)
    cos_a = cos(alpha_angle_rad)

    return np.array([(1.0, 0.0, gamma * cos_a),
                     (0.0, 1.0, gamma * sin_a),
                     (0.0, 0.0, 1.0)])


def deformMatrices(deform_params):
    """
    
    :param deform_params: 
    :return:

    Examples:
    """

    deform_matrix = []

    for deform_param in deform_params:
        if deform_param['type'] == 'displacement':
            displ_x = deform_param['parameters']['deltaX']
            displ_y = deform_param['parameters']['deltaY']
            displ_z = deform_param['parameters']['deltaZ']
            deformation = {'increment': 'additive',
                           'matrix': np.array([displ_x, displ_y, displ_z])}
        elif deform_param['type'] == 'rotation':
            rot_matr = RotationAxis(
                deform_param['parameters']['rotation axis trend'],
                deform_param['parameters']['rotation axis plunge'],
                deform_param['parameters']['rotation angle']).toRotMatrix
            deformation = {'increment': 'multiplicative',
                           'matrix': rot_matr,
                           'shift_pt': np.array([deform_param['parameters']['center x'],
                                                 deform_param['parameters']['center y'],
                                                 deform_param['parameters']['center z']])}
        elif deform_param['type'] == 'scaling':
            scal_matr = matrScaling(deform_param['parameters']['x factor'],
                                    deform_param['parameters']['y factor'],
                                    deform_param['parameters']['z factor'])
            deformation = {'increment': 'multiplicative',
                           'matrix': scal_matr,
                           'shift_pt': np.array([deform_param['parameters']['center x'],
                                                 deform_param['parameters']['center y'],
                                                 deform_param['parameters']['center z']])}
        elif deform_param['type'] == 'simple shear - horizontal':
            simple_shear_horiz_matr = matrHorizSimpleShear(deform_param['parameters']['psi angle (degr.)'],
                                                           deform_param['parameters']['alpha angle (degr.)'])
            deformation = {'increment': 'multiplicative',
                           'matrix': simple_shear_horiz_matr,
                           'shift_pt': np.array([deform_param['parameters']['center x'],
                                                 deform_param['parameters']['center y'],
                                                 deform_param['parameters']['center z']])}
        elif deform_param['type'] == 'simple shear - vertical':
            simple_shear_vert_matr = matrVertSimpleShear(deform_param['parameters']['psi angle (degr.)'],
                                                         deform_param['parameters']['alpha angle (degr.)'])
            deformation = {'increment': 'multiplicative',
                           'matrix': simple_shear_vert_matr,
                           'shift_pt': np.array([deform_param['parameters']['center x'],
                                                 deform_param['parameters']['center y'],
                                                 deform_param['parameters']['center z']])}
        else:
            continue

        deform_matrix.append(deformation)

    return deform_matrix


if __name__ == "__main__":

    import doctest
    doctest.testmod()
