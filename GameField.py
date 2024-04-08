import random as rnd

from TypeOfCells import TypeOfCell
from Cell import Cell


class Game:
    _score = 0
    _blocks_to_add = 3
    _one_cube_price = 100

    def __init__(self, rows: int = 0, columns: int = 0, path_to_file: str = None):
        if path_to_file is not None:
            params = Game.read_field_from_file(path_to_file)
            self._rows = params[0]
            self._columns = params[1]
            self._cells = params[2]
            return

        self._cells = None
        self._rows = rows
        self._columns = columns

    def fill_field(self) -> None:
        self._cells = []
        list_of_enums = list(TypeOfCell)
        for i in range(self._rows):
            self._cells.append([])
            for j in range(self._columns):
                self._cells[i].append(Cell(i, j, rnd.choice(list_of_enums)))

    @staticmethod
    def read_field_from_file(path_to_file: str) -> tuple[int, int, list[list[Cell]]]:
        row_size = 0
        col_size = 0
        cell_field = []
        with open(path_to_file, 'r') as f:
            for rowIndex, stringRow in enumerate(f):
                cell_field.append([])
                cells = stringRow.strip().split('\t')
                if col_size == 0:
                    col_size = len(cells)
                elif col_size != len(cells):
                    raise ValueError("It is not square field")
                row_size += 1
                for col, cell in enumerate(cells):
                    type_of_cell = None
                    cell = cell.strip()
                    match cell:
                        case 'r':
                            type_of_cell = TypeOfCell.rectangle
                        case 'c':
                            type_of_cell = TypeOfCell.circle
                        case 't':
                            type_of_cell = TypeOfCell.triangle
                        case 's':
                            type_of_cell = TypeOfCell.star
                    cell_field[rowIndex].append(Cell(rowIndex, col, type_of_cell))
            return row_size, col_size, cell_field

    def find_neighbours(self, row: int, col: int) -> set[Cell]:
        cells_to_delete: set[Cell] = set()
        if self._rows <= row < 0 and self._columns <= col < 0:
            return cells_to_delete
        stack = [self._cells[row][col]]
        cells_to_delete.add(self._cells[row][col])
        while stack:
            cell = stack.pop()
            type_cell = cell.typeOfCell
            x = cell.row
            y = cell.col
            if (x + 1 < self._rows and self._cells[x + 1][y].typeOfCell == type_cell
                    and self._cells[x + 1][y] not in cells_to_delete):
                cells_to_delete.add(self._cells[x + 1][y])
                stack.append(self._cells[x + 1][y])
            if (x - 1 >= 0 and self._cells[x - 1][y].typeOfCell == type_cell
                    and self._cells[x - 1][y] not in cells_to_delete):
                cells_to_delete.add(self._cells[x - 1][y])
                stack.append(self._cells[x - 1][y])
            if (y + 1 < self._columns and self._cells[x][y + 1].typeOfCell == type_cell
                    and self._cells[x][y + 1] not in cells_to_delete):
                cells_to_delete.add(self._cells[x][y + 1])
                stack.append(self._cells[x][y + 1])
            if (y - 1 >= 0 and self._cells[x][y - 1].typeOfCell == type_cell
                    and self._cells[x][y - 1] not in cells_to_delete):
                cells_to_delete.add(self._cells[x][y - 1])
                stack.append(self._cells[x][y - 1])

        del stack
        return cells_to_delete

    def delete_cells(self, cells_to_delete: set[Cell]) -> dict[int, int]:
        deepest_cells = dict()
        for cell in cells_to_delete:
            self._cells[cell.row][cell.col] = None
            if cell.col in deepest_cells:
                deepest_cells[cell.col] = max(deepest_cells[cell.col], cell.row)
            else:
                deepest_cells[cell.col] = cell.row

        return deepest_cells

    def move_cells(self, firs_to_move: dict[int, int], is_need_to_add: bool) -> None:
        first_empty_col = -1
        for col, row in firs_to_move.items():
            count_of_none = 0
            for curIndex in range(row, -1, -1):
                if self._cells[curIndex][col] is None:
                    count_of_none += 1
                    continue
                self._cells[curIndex + count_of_none][col] = self._cells[curIndex][col]
                self._cells[curIndex][col] = None
            if is_need_to_add:
                list_of_types = list(TypeOfCell)
                for i in range(count_of_none):
                    self._cells[i][col] = Cell(i, col, rnd.choice(list_of_types))
            elif count_of_none == self._rows:
                first_empty_col = max(col, first_empty_col)
        if first_empty_col != -1:
            self.move_empty_column(first_empty_col)

    def move_empty_column(self, left_empty_col) -> None:
        count_to_shift = 1
        for i in range(left_empty_col + 1, self._columns):
            if self._cells[self._rows - 1][i] is None:
                count_to_shift += 1
                continue
            for rowIndexToCopy in range(self._rows):
                self._cells[rowIndexToCopy][i - count_to_shift] = self._cells[rowIndexToCopy][i]
                self._cells[rowIndexToCopy][i] = None

    def print(self) -> None:
        for i in self._cells:
            for j in i:
                letter = 'r'
                if j is None:
                    letter = 'N'
                elif j.typeOfCell == TypeOfCell.circle:
                    letter = 'c'
                elif j.typeOfCell == TypeOfCell.star:
                    letter = 's'
                elif j.typeOfCell == TypeOfCell.triangle:
                    letter = 't'
                print(letter, "\t", end="")
            print()
        print('-' * 3 * (len(self._cells[0])))

    def handle_click(self, x: int, y: int):
        set_to_remove = self.find_neighbours(x, y)
        len_to_remove = len(set_to_remove)
        if len_to_remove < 2:
            return
        self.score += len_to_remove * self._one_cube_price
        add_new_blocks = False
        if len_to_remove >= self.blocks_to_add:
            add_new_blocks = True
        deleted = self.delete_cells(set_to_remove)
        self.move_cells(deleted, add_new_blocks)
        self.update_count_of_blocks()

    def update_count_of_blocks(self):
        self.blocks_to_add = self.score // 1000 + 2

    @property
    def score(self):
        return self._score

    @property
    def blocks_to_add(self):
        return self._blocks_to_add

    @score.setter
    def score(self, value):
        self._score = value

    @blocks_to_add.setter
    def blocks_to_add(self, value):
        self._blocks_to_add = value


# проверить как работает метод сдвига пустых столбцов
if __name__ == '__main__':
    game = Game(path_to_file="testField.txt")

    game.print()
    to_delete = game.find_neighbours(1, 3)
    deepest = game.delete_cells(to_delete)
    game.print()
    game.move_cells(deepest, False)
    game.print()
