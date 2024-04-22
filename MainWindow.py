import sys
from functools import partial
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItemModel, QPainter, QMouseEvent
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QApplication, QItemDelegate, QStyleOptionViewItem, QDialog, QAction, QMessageBox, \
    QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton

import Cell
import GameField
from ColorSettings import ColorSettings
from GameState import GameState
from TypeOfCells import TypeOfCell


# todo 1) добавить звуки при нажатии 2) сделать нормальный размер поля, и чтобы окно подгонялось под него
# todo 3)уведомление о проигрыше 4) лейблы для счёта и кол-ва блоков
# todo 5) во всплывающем окне где написано о проигрыше добавить кнопку рестарта. Можно докрутить ввод имени
# чтобы сохранять прогресс и выводить топ игроков.


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.game = GameField.Game(15, 12)
        self.game.fill_field()
        self.color_for_blocks = ColorSettings()
        self._dict_for_colors = dict()
        self.sound = {'default': QSound('sounds/default_sound.wav'),
                      'blocks': QSound('sounds/change_count_of_blocks.wav'),
                      'big_blocks': QSound('sounds/bitGroupOfBlocks.wav')}
        self.setWindowTitle('PyGame')
        self.setGeometry(500, 300, 507, 700)

        self.game_field = QtWidgets.QTableView(self)
        self.game_field.setGeometry(10, 10, 500, 700)
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
        self.setCentralWidget(self.game_field)
        self.set_menu_bar()
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
        if self.game.rows <= idx.row() < 0 or self.game.columns <= idx.column() < 0:
            return
        cell = self.game.cells[idx.row()][idx.column()]
        color = None
        cell_type = cell.type_of_cell
        match cell_type:
            case TypeOfCell.star:
                color = self.color_for_blocks.star
            case TypeOfCell.circle:
                color = self.color_for_blocks.cir
            case TypeOfCell.triangle:
                color = self.color_for_blocks.tri
            case TypeOfCell.rectangle:
                color = self.color_for_blocks.rec
            case TypeOfCell.empty:
                color = self.color_for_blocks.empty
        painter.fillRect(option.rect, color)

    def on_click(self, e: QModelIndex, me: QMouseEvent = None):
        if me.button() == Qt.LeftButton:
            # print('row - ', e.row(), 'col - ', e.column())
            if e.row() == -1 or e.column() == -1:
                return
            sound = self.game.handle_click(e.row(), e.column())
            match sound:
                case 'default':
                    self.sound['default'].play()
                case 'blocks':
                    self.sound['blocks'].play()
                case 'big_blocks':
                    self.sound['big_blocks'].play()
            self.check_game_state()
            self.update_view()

    def check_game_state(self):
        if self.game.state == GameState.FAILED:
            dial = QDialog(self)
            dial.setWindowTitle('End of the game')
            dial.resize(100, 100)
            dial.exec()

    def set_menu_bar(self):
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('Settings')

        change_colors = QAction('Change colors', self)
        change_colors.triggered.connect(self.pick_color_menu)
        change_colors.setShortcut('Ctrl+P')
        file_menu.addAction(change_colors)

        display_info = QAction('About game', self)
        display_info.triggered.connect(self.show_info_menu)
        display_info.setShortcut('Ctrl+I')
        file_menu.addAction(display_info)

        restart = QAction('Restart', self)
        restart.triggered.connect(self.restart_game)
        restart.setShortcut('Ctrl+R')
        file_menu.addAction(restart)

    def restart_game(self):
        self.game.state = GameState.PLAYING
        self.game = GameField.Game(15, 12)
        self.game.fill_field()
        self.color_for_blocks = ColorSettings()
        self.update_view()

    # fixme доделать по красоте, пока выглядит вырвиглазно, но хотя бы работает чисто в теории
    def pick_color_menu(self):
        self._dict_for_colors.clear()
        pick_col_dialog = QDialog()
        pick_col_dialog.setWindowTitle('Выбрать цвета для кубиков')
        layout = QVBoxLayout(pick_col_dialog)

        buttons_layout = QHBoxLayout()
        star_but = QPushButton('звёздочка')
        star_but.clicked.connect(partial(self.pick_color, 'star_color'))
        buttons_layout.addWidget(star_but)

        circle_but = QPushButton('круг')
        circle_but.clicked.connect(partial(self.pick_color, 'circ_color'))
        buttons_layout.addWidget(circle_but)

        triangle_but = QPushButton('треугольник')
        triangle_but.clicked.connect(partial(self.pick_color, 'tri_color'))
        buttons_layout.addWidget(triangle_but)

        empty_but = QPushButton('пустой')
        empty_but.clicked.connect(partial(self.pick_color, 'empty_color'))
        buttons_layout.addWidget(empty_but)

        rectangle_but = QPushButton('квадрат')
        rectangle_but.clicked.connect(partial(self.pick_color, 'rec_color'))
        buttons_layout.addWidget(rectangle_but)
        layout.addLayout(buttons_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Reset | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).clicked.connect(partial(self.update_colors, pick_col_dialog))
        button_box.rejected.connect(pick_col_dialog.reject)
        button_box.button(QDialogButtonBox.Reset).clicked.connect(partial(self.reset_colors, pick_col_dialog))
        layout.addWidget(button_box)

        pick_col_dialog.exec_()

    def pick_color(self, block_name: str):
        color_dia = QtWidgets.QColorDialog()
        start_color = None
        match block_name:
            case 'star_color':
                start_color = self.color_for_blocks.star
            case 'circ_color':
                start_color = self.color_for_blocks.cir
            case 'tri_color':
                start_color = self.color_for_blocks.tri
            case 'empty_color':
                start_color = self.color_for_blocks.empty
            case 'rec_color':
                start_color = self.color_for_blocks.rec
        color_dia.setCurrentColor(start_color)

        color_dia.exec_()
        color = color_dia.selectedColor()
        if color.isValid():
            self._dict_for_colors[block_name] = color

    def update_colors(self, qdialog):
        qdialog.accept()
        self.color_for_blocks = ColorSettings(**self._dict_for_colors)
        self.update_view()

    def reset_colors(self, qdialog):
        qdialog.accept()
        self.color_for_blocks = ColorSettings()
        self.update_view()

    def show_info_menu(self):
        infoMsgBox = QtWidgets.QMessageBox(self)
        infoMsgBox.setWindowTitle('Игра \"Одинаковые блоки\"')
        infoMsgBox.setIcon(QMessageBox.Information)
        infoMsgBox.setText('Правила игры:')
        infoMsgBox.setInformativeText(
            "Вы должны исключать одинаковые блоки. За это даются очки. Ваша задача - набрать максимальное" +
            "количество очков. Чем больше очков, тем большую группу блоков нужно исключить, чтобы поле обновилось. " +
            "Вы проигрываете, когда нет ни одной группы блоков.")
        infoMsgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        infoMsgBox.exec_()


class ColorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выберите цвет")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
