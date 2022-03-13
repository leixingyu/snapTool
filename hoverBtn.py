import re

from Qt import QtCore, QtGui, QtWidgets


class HoverBtn(QtWidgets.QLabel):

    clicked = QtCore.Signal(QtCore.QObject)

    def __init__(self, parent):
        super(HoverBtn, self).__init__(parent)

        style = """
        QFrame{
            border-radius: 25px;
            border-width: 2px;
            border-style: solid;
            border-color: rgb(20, 20, 20);
            background-color: rgb(170, 170, 170);
        }
        """
        self.installEventFilter(self)
        self.setStyleSheet(style)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self.set_outline(1)
            return True
        elif event.type() == QtCore.QEvent.Leave:
            self.set_outline(0)
            return True

        if event.type() == QtCore.QEvent.MouseButtonPress \
                and event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)
            return True

        return False

    def set_outline(self, status):
        """
        Update widget stylesheet when highlight
        """
        style = self.styleSheet()

        border_pattern = r'border-color\: rgb\(\d+, \d+, \d+\)'
        dark = 'border-color: rgb(20, 20, 20)'
        light = 'border-color: rgb(21, 255, 9)'

        if status == 1:
            style = re.sub(border_pattern, light, style)
        elif status == 0:
            style = re.sub(border_pattern, dark, style)

        self.setStyleSheet(style)

    def set_color(self, status):
        """
        Update widget stylesheet
        """
        style = self.styleSheet()

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

        self.setStyleSheet(style)
