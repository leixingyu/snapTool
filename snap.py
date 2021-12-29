import re
import os

import maya.cmds as cmds
import maya.OpenMaya as om

from Qt import QtCore, QtGui, QtWidgets
from Qt import _loadUi


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = r'ui/snap.ui'
PNG_PATH = r'ui/snap.png'


class SnapWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """
        Initialization
        """
        super(SnapWindow, self).__init__()
        _loadUi(os.path.join(CURRENT_PATH, UI_PATH), self)

        # set flag
        self.setWindowFlags(QtCore.Qt.Window)
        self.setMouseTracking(1)

        self.ui_root_Label.installEventFilter(self)
        self.ui_mid_Label.installEventFilter(self)
        self.ui_top_Label.installEventFilter(self)

        # initialize instance attribute
        self._root_jnt = list()
        self._mid_jnt = list()
        self._top_jnt = list()

        # initialize ui property
        pixmap = QtGui.QPixmap()
        pixmap.load(os.path.join(CURRENT_PATH, PNG_PATH))
        self.ui_snap_Label.setPixmap(pixmap)

        # initialize methods
        self.connect_signals()

    def eventFilter(self, widget, event):
        """
        Override: define mouse hover, click behavior on certain ui elements
        """
        # hover effect
        if event.dtype() == QtCore.QEvent.Enter:
            SnapWindow.update_jnt_highlight(widget, 1)
        elif event.dtype() == QtCore.QEvent.Leave:
            SnapWindow.update_jnt_highlight(widget, 0)

        # mouse click effect
        if event.dtype() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                self.open_menu(widget)
            elif event.button() == QtCore.Qt.RightButton:
                print("Right Button Clicked")

        return False

    def open_menu(self, widget, target=None):
        """
        Create context menu on certain ui elements
        """
        if widget is self.ui_root_Label:
            target = self._root_jnt
        elif widget is self.ui_mid_Label:
            target = self._mid_jnt
        elif widget is self.ui_top_Label:
            target = self._top_jnt

        menu = QtWidgets.QMenu()
        # menu option
        title = QtWidgets.QLabel(str(target))
        title_action = QtWidgets.QWidgetAction(title)
        title_action.setDefaultWidget(title)
        menu.addAction(title_action)
        menu.addSeparator()

        action = menu.addAction('Assign selected')
        action.triggered.connect(
            lambda: self.update_jnt(widget, target))

        cursor = QtGui.QCursor()
        menu.exec_(cursor.pos())

    def connect_signals(self):
        """
        Connect signals and slots
        """
        self.ui_snap_Btn.clicked.connect(lambda: self.snap())
        self.ui_clear_Btn.clicked.connect(lambda: self.clear())

        push_buttons = [
            self.ui_ik_handle_Btn,
            self.ui_ik_pole_Btn,

            self.ui_fk_ctrl_root_Btn,
            self.ui_fk_ctrl_mid_Btn,
            self.ui_fk_ctrl_top_Btn,
        ]
        line_edits = [
            self.ui_ik_handle_LineEdit,
            self.ui_ik_pole_LineEdit,

            self.ui_fk_ctrl_root_LineEdit,
            self.ui_fk_ctrl_mid_LineEdit,
            self.ui_fk_ctrl_top_LineEdit,
        ]
        for index in range(len(line_edits)):
            # TODO: use partial
            push_buttons[index].clicked.connect(
                lambda _='', l=line_edits[index]: SnapWindow.set_selected(l)
            )

    @staticmethod
    def update_jnt(widget, target, status=0):
        """
        Update selected joint to use for base reference when snapping

        :param widget: QWidget
        :param target: list. reference to instance attribute (transform)
        :param status: int. status code
        """
        # TODO: use enum for status
        if cmds.ls(selection=1):
            jnt_name = cmds.ls(selection=1)[0]
            try:
                target[:] = get_target_transform(jnt_name)
                status = 1
            except:
                status = -1
        # update status
        SnapWindow.update_jnt_status(widget, status)

    @staticmethod
    def set_selected(line_edit):
        """
        Set QLineEdit based on scene selection
        """
        sl = cmds.ls(selection=1)
        if sl:
            line_edit.setText(sl[0])

    @staticmethod
    def update_jnt_status(widget, status):
        """
        Update widget stylesheet when status updated

        :param widget: QWidget
        :param status: int. status code
        """
        style = widget.styleSheet()

        background_pattern = r'background-color\: rgb\(\d+, \d+, \d+\)'
        red = 'background-color: rgb(255, 0, 0)'
        green = 'background-color: rgb(0, 255, 0)'
        null = 'background-color: rgb(170, 170, 170)'

        if status == 1:
            style = re.sub(background_pattern, green, style)
        elif status == 0:
            style = re.sub(background_pattern, null, style)
        elif status == -1:
            style = re.sub(background_pattern, red, style)

        widget.setStyleSheet(style)

    @staticmethod
    def update_jnt_highlight(widget, status):
        """
        Update widget stylesheet when highlight

        :param widget: QWidget
        :param status: int. status code
        """
        style = widget.styleSheet()

        border_pattern = r'border-color\: rgb\(\d+, \d+, \d+\)'
        dark = 'border-color: rgb(20, 20, 20)'
        light = 'border-color: rgb(21, 255, 9)'

        if status == 1:
            style = re.sub(border_pattern, light, style)
        elif status == 0:
            style = re.sub(border_pattern, dark, style)

        widget.setStyleSheet(style)

    def snap(self):
        """
        Snap/Match position either for IK mode or FK mode
        """
        if self.tabWidget.currentIndex() == 0:
            # ik to fk
            ik_handle = self.ui_ik_handle_LineEdit.text()
            pole_vector = self.ui_ik_pole_LineEdit.text()

            if '' in [ik_handle, pole_vector]:
                return

            snap_ik_to_fk(
                ik_handle,
                pole_vector,
                self._root_jnt[1],
                self._mid_jnt[1],
                self._top_jnt[1],
                self._top_jnt[2]
            )

        else:
            # fk to ik
            fk_root = self.ui_fk_ctrl_root_LineEdit.text()
            fk_mid = self.ui_fk_ctrl_mid_LineEdit.text()
            fk_top = self.ui_fk_ctrl_top_LineEdit.text()

            if '' in [fk_root, fk_mid, fk_top]:
                return

            snap_fk_to_ik(
                [fk_root, fk_mid, fk_top],
                self._root_jnt[2],
                self._mid_jnt[2],
                self._top_jnt[2],
            )

    def clear(self):
        """
        Clear out ui element and reset instance attribute
        :return:
        """
        # reset class property
        self._root_jnt = list()
        self._mid_jnt = list()
        self._top_jnt = list()

        # reset field
        for widget in [self.ui_root_Label, self.ui_mid_Label, self.ui_top_Label]:
            SnapWindow.update_jnt_status(widget, 0)

        self.ui_ik_pole_LineEdit.setText('')
        self.ui_ik_handle_LineEdit.setText('')
        self.ui_fk_ctrl_root_LineEdit.setText('')
        self.ui_fk_ctrl_mid_LineEdit.setText('')
        self.ui_fk_ctrl_top_LineEdit.setText('')


def show():
    """
    Display main gui
    """
    window = SnapWindow()
    try:
        window.close()
    except:
        pass
    window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    window.show()
    return window


def get_target_transform(jnt):
    """
    Get joint transformation info

    :param jnt: str. maya scene node
    :return: list. [transform name, vec3 position, vec3 rotation]
    """
    return [
        jnt,
        [round(attr, 2) for attr in cmds.xform(jnt, ws=1, q=1, t=1)],
        [round(attr, 2) for attr in cmds.xform(jnt, ws=1, q=1, ro=1)]
    ]


def snap_ik_to_fk(ik_handle, pole_vector, root_pos, mid_pos, top_pos, top_rot):
    """
    Snap IK controls based on FK joints

    :param ik_handle: str. IK handle name
    :param pole_vector: str. IK pole vector name
    :param root_pos: list. FK joint root position
    :param mid_pos: list. FK joint mid position
    :param top_pos: list. FK joint top position
    :param top_rot: int. FK joint top rotation
    """
    # build vectors
    fk_root_vec = om.MVector(root_pos[0], root_pos[1], root_pos[2])
    fk_mid_vec = om.MVector(mid_pos[0], mid_pos[1], mid_pos[2])
    fk_top_vec = om.MVector(top_pos[0], top_pos[1], top_pos[2])

    mid_point_vec = (fk_root_vec + fk_top_vec) / 2
    pole_dir = fk_mid_vec - mid_point_vec
    pole_pos = fk_mid_vec + pole_dir

    # get ik ctrl transform
    pv_ctrl_pos = cmds.xform(pole_vector, ws=1, q=1, sp=1)

    # move ik ctrls
    cmds.move(
        pole_pos[0]-pv_ctrl_pos[0],
        pole_pos[1]-pv_ctrl_pos[1],
        pole_pos[2]-pv_ctrl_pos[2],
        pole_vector,
        relative=1
    )

    cmds.move(top_pos[0], top_pos[1], top_pos[2], ik_handle)
    cmds.xform(ik_handle, ro=top_rot, ws=1)


def snap_fk_to_ik(fk_ctrls, root_rot, mid_rot, top_rot):
    """
    Snap FK controls based on IK joints

    :param fk_ctrls: list. three-segment fk controllers
    :param root_rot: int. ik joint root rotation value
    :param mid_rot: int. ik joint mid rotation value
    :param top_rot: int. ik joint top rotation value
    """
    cmds.xform(fk_ctrls[0], ro=root_rot, ws=1)
    cmds.xform(fk_ctrls[1], ro=mid_rot, ws=1)
    cmds.xform(fk_ctrls[2], ro=top_rot, ws=1)
