from PyQt5 import QtGui, QtCore


class ColorSettings:
    def __init__(self, star_color=QtGui.QColor(QtCore.Qt.yellow), rec_color=QtGui.QColor(QtCore.Qt.red),
                 tri_color=QtGui.QColor(QtCore.Qt.green), circ_color=QtGui.QColor(QtCore.Qt.blue),
                 empty_color=QtGui.QColor(QtCore.Qt.white)):
        self._star_color = star_color
        self._rec_color = rec_color
        self._tri_color = tri_color
        self._circ_color = circ_color
        self._empty_color = empty_color

    @property
    def star(self):
        return self._star_color

    @property
    def rec(self):
        return self._rec_color

    @property
    def tri(self):
        return self._tri_color

    @property
    def cir(self):
        return self._circ_color

    @property
    def empty(self):
        return self._empty_color
