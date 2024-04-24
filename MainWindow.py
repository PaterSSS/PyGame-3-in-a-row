import sys
from functools import partial
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QStandardItemModel, QPainter, QMouseEvent, QFont
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import QApplication, QItemDelegate, QStyleOptionViewItem, QDialog, QAction, QMessageBox, \
    QVBoxLayout, QHBoxLayout, QDialogButtonBox, QPushButton, QHeaderView

import Cell
import GameField
from ColorSettings import ColorSettings
from GameState import GameState
from TypeOfCells import TypeOfCell


#Todo улучшить скорость отрисовки можно добавить кэширование, чтобы только необходимое перерисовывлось
#ещё можно заменить на drawItem() гпт предложил это. В корне будет лежать текстовик с тем что предложил гпт
# сделать нормальную структуру, а не мешанину как сейчас
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.is_frozen = False
        self.game = GameField.Game(15, 12)
        self.game.fill_field()
        self.color_for_blocks = ColorSettings()
        self._dict_for_colors = dict()
        self.sound = {'default': QSoundEffect(self),
                      'blocks': QSoundEffect(self),
                      'big_blocks': QSoundEffect(self)}
        self.sound['default'].setSource(QtCore.QUrl.fromLocalFile('sounds/default.wav'))
        self.sound['blocks'].setSource(QtCore.QUrl.fromLocalFile('sounds/change_count_of_blocks.wav'))
        self.sound['big_blocks'].setSource(QtCore.QUrl.fromLocalFile('sounds/big_count.wav'))
        self.setWindowTitle('PyGame')
        self.setGeometry(0, 0, 625, 700)
        self.center_on_screen()

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

        self.blocks_in_group = QtWidgets.QLabel("Количество блоков: 3", self)
        self.score = QtWidgets.QLabel("Счёт: 0", self)
        font = QFont("Times New Roman", 14)
        self.blocks_in_group.setFont(font)
        self.score.setFont(font)

        layoutHead = QtWidgets.QHBoxLayout()
        layoutHead.addWidget(self.blocks_in_group, alignment=Qt.AlignLeft)
        layoutHead.addWidget(self.score, alignment=Qt.AlignRight)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(layoutHead)
        main_layout.addWidget(self.game_field)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(main_layout)

        self.game_field.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.game_field.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.game_field.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.game_field.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.game_field.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.game_field.setItemDelegate(MyDelegate(self))
        self.game_field.mousePressEvent = mousePressEvent
        self.set_menu_bar()
        self.setCentralWidget(central_widget)
        self.show()

    def update_labels(self):
        self.blocks_in_group.setText(f"Количество блоков: {self.game.blocks_to_add}")
        self.score.setText(f"Счёт: {self.game.score}")

    def center_on_screen(self):
        # Получаем геометрию доступного рабочего стола
        screen_geometry = QApplication.desktop().availableGeometry()

        # Получаем размеры и центр экрана
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())

        # Устанавливаем окно в центре экрана
        self.move(window_geometry.topLeft())

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
        if me.button() == Qt.LeftButton and not self.is_frozen and e.row() != -1 and e.column() != -1:
            sound = self.game.handle_click(e.row(), e.column())
            match sound:
                case 'default':
                    self.sound['default'].play()
                case 'blocks':
                    self.sound['blocks'].play()
                case 'big_blocks':
                    self.sound['big_blocks'].play()
            self.check_game_state()
            self.update_labels()
            self.update_view()

    def check_game_state(self):
        if self.game.state == GameState.FAILED:
            dial = QMessageBox(self)
            dial.setWindowTitle("Вы проиграли!")
            dial.setIcon(QMessageBox.Information)
            dial.setText(f'Вы молодец. Ваш итоговый счёт составил - {self.game.score}')
            dial.setInformativeText("Если вы хотите сыграть снова и побить свой рекорд, то нажмите OK")
            btn_ok = QPushButton("OK", dial)
            btn_ok.clicked.connect(self.restart_game)

            btn_cancel = QPushButton("Cancel", dial)
            btn_cancel.clicked.connect(self.freeze_game)
            dial.addButton(btn_cancel, QMessageBox.ResetRole)
            dial.addButton(btn_ok, QMessageBox.AcceptRole)
            dial.exec_()

    def freeze_game(self):
        self.is_frozen = True

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

        resize_window = QAction('Resize', self)
        resize_window.triggered.connect(self.resize_win)
        resize_window.setShortcut('Ctrl+W')
        file_menu.addAction(resize_window)

    def resize_win(self):
        self.setGeometry(0, 0, 625, 700)
        self.center_on_screen()

    def restart_game(self):
        self.game.state = GameState.PLAYING
        self.is_frozen = False
        self.game = GameField.Game(15, 12)
        self.game.fill_field()
        self.color_for_blocks = ColorSettings()
        self.blocks_in_group.setText("Количество блоков: 3")
        self.score.setText("Счёт: 0")
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
            "Вы должны исключать одинаковые блоки. За это даются очки. Ваша задача - набрать максимальное " +
            "количество очков. Чем больше очков, тем большую группу блоков нужно исключить, чтобы поле обновилось. " +
            "Вы проигрываете, когда нет ни одной группы блоков.")
        infoMsgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        infoMsgBox.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
