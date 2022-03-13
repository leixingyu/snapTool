import logging
import os

import maya.cmds as cmds
from maya.api import OpenMaya as om

from Qt import QtGui, QtWidgets, QtCore
from Qt import _loadUi

from . import util
from . import hoverBtn
from .utility.rigging import matrix


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join('ui', 'snap.ui')
PNG_PATH = os.path.join('ui', 'snap.png')


# TODO: use enum for status

class SnapWindow(QtWidgets.QMainWindow):
    def __init__(self):
        """
        Initialization
        """
        super(SnapWindow, self).__init__()
        _loadUi(os.path.join(CURRENT_PATH, UI_PATH), self)

        # custom ui element
        self.ui_root_Label = hoverBtn.HoverBtn(parent=self.frame)
        self.ui_root_Label.setGeometry(105, 51, 50, 50)

        self.ui_mid_Label = hoverBtn.HoverBtn(parent=self.frame)
        self.ui_mid_Label.setGeometry(177, 134, 50, 50)

        self.ui_top_Label = hoverBtn.HoverBtn(parent=self.frame)
        self.ui_top_Label.setGeometry(290, 56, 50, 50)

        # initialize instance attribute
        self._root_jnt_mat = None
        self._mid_jnt_mat = None
        self._top_jnt_mat = None

        self._root_jnt = ''
        self._mid_jnt = ''
        self._top_jnt = ''

        # initialize ui property
        pixmap = QtGui.QPixmap()
        pixmap.load(os.path.join(CURRENT_PATH, PNG_PATH))
        self.ui_snap_Label.setPixmap(pixmap)

        # initialize methods
        self.connect_signals()

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
            push_buttons[index].clicked.connect(
                lambda _='', l=line_edits[index]: SnapWindow.set_selected(l)
            )

        self.ui_root_Label.clicked.connect(self.open_menu)
        self.ui_mid_Label.clicked.connect(self.open_menu)
        self.ui_top_Label.clicked.connect(self.open_menu)

    def open_menu(self, widget):
        """
        Create context menu on certain ui elements
        """
        jnt_info = self.get_jnt_info(widget)

        menu = QtWidgets.QMenu()
        title = menu.addAction(jnt_info)
        title.setEnabled(False)
        menu.addSeparator()

        action = menu.addAction('Assign selected')
        action.triggered.connect(
            lambda: self.assign_jnt(widget)
        )

        cursor = QtGui.QCursor()
        menu.exec_(cursor.pos())

    def get_jnt_info(self, widget):
        """
        Get joint info snapshot of the current joint
        used to display and debug joint target information

        :param widget: QWidget. selected UI element
        :return: str. joint info to display
        """
        jnt_mat = None
        jnt_name = ''

        if widget is self.ui_root_Label:
            jnt_mat = self._root_jnt_mat
            jnt_name = self._root_jnt
        elif widget is self.ui_mid_Label:
            jnt_mat = self._mid_jnt_mat
            jnt_name = self._mid_jnt
        elif widget is self.ui_top_Label:
            jnt_mat = self._top_jnt_mat
            jnt_name = self._top_jnt

        try:
            jnt_pos = matrix.decompose_translation(om.MTransformationMatrix(jnt_mat))
            jnt_rot = matrix.decompose_rotation(om.MTransformationMatrix(jnt_mat))
        except:
            jnt_pos = 'void'
            jnt_rot = 'void'

        return '{}\n{}\n{}\n'.format(jnt_name, jnt_pos, jnt_rot)

    def assign_jnt(self, widget):
        """
        Update selected joint to use for base reference when snapping

        :param widget: QWidget. selected UI element
        """
        if not cmds.ls(selection=1):
            return

        jnt_name = cmds.ls(selection=1)[0]
        try:
            jnt_mat = matrix.get_matrix(jnt_name)
            if widget is self.ui_root_Label:
                self._root_jnt_mat = jnt_mat
                self._root_jnt = jnt_name
            elif widget is self.ui_mid_Label:
                self._mid_jnt_mat = jnt_mat
                self._mid_jnt = jnt_name
            elif widget is self.ui_top_Label:
                self._top_jnt_mat = jnt_mat
                self._top_jnt = jnt_name
            status = 1

        except Exception as e:
            logging.error(e)
            status = -1

        # update ui status
        widget.set_color(status)

    @staticmethod
    def set_selected(line_edit):
        """
        Set QLineEdit based on scene selection
        """
        sl = cmds.ls(selection=1)
        if sl:
            line_edit.setText(sl[0])

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

            util.ik_matching(
                jnt_root_mat=self._root_jnt_mat,
                jnt_mid_mat=self._mid_jnt_mat,
                jnt_top_mat=self._top_jnt_mat,
                jnt_top=self._top_jnt,
                ik_pole=pole_vector,
                ik_handle=ik_handle
            )

        else:
            # fk to ik
            fk_root = self.ui_fk_ctrl_root_LineEdit.text()
            fk_mid = self.ui_fk_ctrl_mid_LineEdit.text()
            fk_top = self.ui_fk_ctrl_top_LineEdit.text()

            if '' in [fk_root, fk_mid, fk_top]:
                return

            util.fk_matching(
                jnt_root_mat=self._root_jnt_mat,
                jnt_mid_mat=self._mid_jnt_mat,
                jnt_top_mat=self._top_jnt_mat,
                jnt_root=self._root_jnt,
                jnt_mid=self._mid_jnt,
                jnt_top=self._top_jnt,
                fk_root=fk_root,
                fk_mid=fk_mid,
                fk_top=fk_top
            )

    def clear(self):
        """
        Clear out ui element and reset instance attribute
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
    window = SnapWindow()
    try:
        window.close()
    except:
        pass
    window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    window.show()
