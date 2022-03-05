import maya.cmds as cmds
from maya.api import OpenMaya as om

from utility.rigging import matrix
from utility.datatype.vector import Vector3


def fk_matching(
        jnt_root_mat,
        jnt_mid_mat,
        jnt_top_mat,
        jnt_root,
        jnt_mid,
        jnt_top,
        fk_root,
        fk_mid,
        fk_top
):
    """
    Match FK position to IK joint position

    :param jnt_root_mat: om.MMatrix. FK mode root joint transformation matrix
    :param jnt_mid_mat: om.MMatrix. FK mode mid joint transformation matrix
    :param jnt_top_mat: om.MMatrix. FK mode top joint transformation matrix
    :param jnt_root: str. root joint name
    :param jnt_mid: str. mid joint name
    :param jnt_top: str. top joint name
    :param fk_root: str. fk root controller name
    :param fk_mid: str. fk mid controller name
    :param fk_top: str. fk top controller name
    :return:
    """
    fk_root_rot = get_ctrl_target_rot(jnt_root_mat, jnt_root, fk_root)
    fk_mid_rot = get_ctrl_target_rot(jnt_mid_mat, jnt_mid, fk_mid)
    fk_top_rot = get_ctrl_target_rot(jnt_top_mat, jnt_top, fk_top)
    
    rotate_ctrl_to_target(fk_root, fk_root_rot)
    rotate_ctrl_to_target(fk_mid, fk_mid_rot)
    rotate_ctrl_to_target(fk_top, fk_top_rot)


def ik_matching(        
        jnt_root_mat,
        jnt_mid_mat,
        jnt_top_mat,
        jnt_top,
        ik_pole,
        ik_handle
):
    """
    Match IK position to FK joint position

    :param jnt_root_mat: om.MMatrix. FK mode root joint transformation matrix
    :param jnt_mid_mat: om.MMatrix. FK mode mid joint transformation matrix
    :param jnt_top_mat: om.MMatrix. FK mode top joint transformation matrix
    :param jnt_top: str. top joint name
    :param ik_pole: str. ik pole control name
    :param ik_handle: str. ik handle control name
    """
    ik_handle_pos = get_ctrl_target_pos(jnt_top_mat, jnt_top, ik_handle)
    ik_handle_rot = get_ctrl_target_rot(jnt_top_mat, jnt_top, ik_handle)

    jnt_root_pos = matrix.decompose_translation(om.MTransformationMatrix(jnt_root_mat))
    jnt_mid_pos = matrix.decompose_translation(om.MTransformationMatrix(jnt_mid_mat))
    jnt_top_pos = matrix.decompose_translation(om.MTransformationMatrix(jnt_top_mat))
    ik_pole_pos = get_pole_target_pos(jnt_root_pos, jnt_mid_pos, jnt_top_pos)

    snap_ctrl_to_target(ik_handle, ik_handle_pos)
    rotate_ctrl_to_target(ik_handle, ik_handle_rot)

    snap_ctrl_to_target(ik_pole, ik_pole_pos)


def get_ctrl_target_pos(jnt_target_mat, jnt, ctrl):
    """
    Calculate the control target position (in world space)
    based off current ctrl and joint offset,
    and the joint target transformation matrix

    :param jnt_target_mat: om.MMatrix. joint transformation matrix that
    the current ctrl want to match
    :param jnt: str. current joint name
    :param ctrl: str. current ctrl name
    :return: list. positions
    """
    jnt_target_pos = matrix.decompose_translation(jnt_target_mat)

    jnt_pos = Vector3(cmds.xform(jnt, ws=1, q=1, t=1))
    ik_pos = Vector3(cmds.xform(ctrl, ws=1, q=1, t=1))
    offset = jnt_pos - ik_pos

    return jnt_target_pos - offset


def get_ctrl_target_rot(jnt_target_mat, jnt, ctrl):
    """
    Calculate the control target rotation (in world space)
    based off current ctrl and joint offset,
    and the joint target transformation matrix

    Note: the ctrl and joint offset is represented as const matrix

    :param jnt_target_mat: om.MMatrix. joint transformation matrix that
    the current ctrl want to match
    :param jnt: str. current joint name
    :param ctrl: str. current ctrl name
    :return: list. rotations
    """
    # constraint matrix can convert any joint rotation
    # to controller rotation in world space
    jnt_rot = matrix.get_matrix(jnt)
    ctrl_rot = matrix.get_matrix(ctrl)
    const_mat = matrix.get_pre_mult_matrix(jnt_rot, ctrl_rot)

    # jnt target ws rotation to ctrl target ws rotation, using const mat
    target_ctrl_mat = om.MTransformationMatrix(
        const_mat.inverse() * jnt_target_mat
    )

    return matrix.decompose_rotation(target_ctrl_mat)


def get_pole_target_pos(root_pos, mid_pos, top_pos):
    """
    Get IK pole target position based on joint positions

    :param root_pos: list. FK joint root position
    :param mid_pos: list. FK joint mid position
    :param top_pos: list. FK joint top position
    """
    fk_root_vec = om.MVector(root_pos[0], root_pos[1], root_pos[2])
    fk_mid_vec = om.MVector(mid_pos[0], mid_pos[1], mid_pos[2])
    fk_top_vec = om.MVector(top_pos[0], top_pos[1], top_pos[2])

    mid_point_vec = (fk_root_vec + fk_top_vec) / 2
    pole_dir = fk_mid_vec - mid_point_vec
    pole_pos = fk_mid_vec + pole_dir

    return pole_pos


def rotate_ctrl_to_target(ctrl, target_rot):
    """
    Rotate controller to target rotation (in world space)

    :param ctrl:
    :param target_rot:
    :return:
    """
    cmds.xform(ctrl, ro=target_rot, ws=1)


def snap_ctrl_to_target(ctrl, target):
    """
    Snap controller to target position (in world space)

    :param ctrl:
    :param target:
    :return:
    """
    # get ik ctrl transform
    ctrl_pos = cmds.xform(ctrl, ws=1, q=1, sp=1)

    # move ik ctrls
    cmds.move(
        target[0]-ctrl_pos[0],
        target[1]-ctrl_pos[1],
        target[2]-ctrl_pos[2],
        ctrl,
        relative=1
    )
