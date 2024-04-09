import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItemModel, QPainter, QMouseEvent
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QItemDelegate, QStyleOptionViewItem
from PyQt5 import QtGui

import Cell
import GameField
from TypeOfCells import TypeOfCell


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.game = GameField.Game(25, 10)
        self.game.fill_field()

        self.setWindowTitle('PyGame')
        self.setGeometry(500, 300, 500, 700)

        self.game_field = QtWidgets.QTableView(self)
        self.game_field.setGeometry(10, 10, 500, 500)
        self.model = QStandardItemModel(self.game.rows, self.game.columns, self)
        self.game_field.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.game_field.horizontalHeader().setVisible(False)
        self.game_field.horizontalHeader().setDefaultSectionSize(30)
        self.game_field.verticalHeader().setVisible(False)

        self.game_field.setModel(self.model)

        class MyDelegate(QItemDelegate):
            def __init__(self, parent=None, *args):
                QItemDelegate.__init__(self, parent, *args)

            def paint(self, painter: QPainter, option: QStyleOptionViewItem, idx: QModelIndex):
                painter.save()
                self.parent().on_item_paint(idx, painter, option)
                painter.restore()

        def mousePressEvent(event):
            idx = self.game_field.indexAt(event.pos())
            self.on_click(idx, event)

        self.game_field.setItemDelegate(MyDelegate(self))
        self.game_field.mousePressEvent = mousePressEvent

        self.show()

    @staticmethod
    def convert_cells(cell: Cell) -> str:
        cell_type = cell.typeOfCell
        match cell_type:
            case TypeOfCell.star:
                return 's'
            case TypeOfCell.circle:
                return 'c'
            case TypeOfCell.triangle:
                return 't'
            case TypeOfCell.rectangle:
                return 'r'

    def update_view(self):
        self.game_field.viewport().update()

    def on_item_paint(self, idx: QModelIndex, painter: QPainter, option: QStyleOptionViewItem) -> None:
        if self.game.rows <= idx.row() < 0 and self.game.columns <= idx.column() < 0:
            return
        cell = self.game.cells[idx.row()][idx.column()]
        color = QtCore.Qt.gray
        if cell is not None:
            cell_type = cell.typeOfCell
            match cell_type:
                case TypeOfCell.star:
                    color = QtCore.Qt.yellow
                case TypeOfCell.circle:
                    color = QtCore.Qt.blue
                case TypeOfCell.triangle:
                    color = QtCore.Qt.green
                case TypeOfCell.rectangle:
                    color = QtCore.Qt.red
        painter.fillRect(option.rect, color)

    def on_click(self, e: QModelIndex, me: QMouseEvent = None):
        if me.button() == Qt.LeftButton:
            self.game.handle_click(e.row(), e.column())
        self.update_view()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
