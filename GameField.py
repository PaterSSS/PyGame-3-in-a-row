import random as rnd

from TypeOfCells import TypeOfCell
from Cell import Cell
from GameState import GameState


class Game:
    _score = 0
    _blocks_to_add = 3
    _one_cube_price = 100
    _state = GameState.PLAYING
    _list_of_choices = [TypeOfCell.star, TypeOfCell.circle, TypeOfCell.triangle, TypeOfCell.rectangle]

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
        for i in range(self._rows):
            self._cells.append([])
            for j in range(self._columns):
                self._cells[i].append(Cell(i, j, rnd.choice(self._list_of_choices)))

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
        if self._rows <= row < 0 or self._columns <= col < 0 or self._cells[row][col].type_of_cell == TypeOfCell.empty:
            return cells_to_delete
        stack = [self._cells[row][col]]
        cells_to_delete.add(self._cells[row][col])
        while stack:
            cell = stack.pop()
            type_cell = cell.type_of_cell
            x = cell.row
            y = cell.col
            if (x + 1 < self._rows and self._cells[x + 1][y].type_of_cell == type_cell
                    and self._cells[x + 1][y] not in cells_to_delete):
                cells_to_delete.add(self._cells[x + 1][y])
                stack.append(self._cells[x + 1][y])
            if (x - 1 >= 0 and self._cells[x - 1][y].type_of_cell == type_cell
                    and self._cells[x - 1][y] not in cells_to_delete):
                cells_to_delete.add(self._cells[x - 1][y])
                stack.append(self._cells[x - 1][y])
            if (y + 1 < self._columns and self._cells[x][y + 1].type_of_cell == type_cell
                    and self._cells[x][y + 1] not in cells_to_delete):
                cells_to_delete.add(self._cells[x][y + 1])
                stack.append(self._cells[x][y + 1])
            if (y - 1 >= 0 and self._cells[x][y - 1].type_of_cell == type_cell
                    and self._cells[x][y - 1] not in cells_to_delete):
                cells_to_delete.add(self._cells[x][y - 1])
                stack.append(self._cells[x][y - 1])
        del stack
        return cells_to_delete

    def delete_cells(self, cells_to_delete: set[Cell]) -> dict[int, int]:
        deepest_cells = dict()
        for cell in cells_to_delete:
            self._cells[cell.row][cell.col].type_of_cell = TypeOfCell.empty
            if cell.col in deepest_cells:
                deepest_cells[cell.col] = max(deepest_cells[cell.col], cell.row)
            else:
                deepest_cells[cell.col] = cell.row

        return deepest_cells

    def move_cells(self, firs_to_move: dict[int, int], is_need_to_add: bool) -> None:
        first_empty_col = len(self._cells[0])
        for col, row in firs_to_move.items():
            count_of_none = 0
            for curIndex in range(row, -1, -1):
                if self._cells[curIndex][col].type_of_cell == TypeOfCell.empty:
                    count_of_none += 1
                    continue
                self._cells[curIndex + count_of_none][col].type_of_cell = self._cells[curIndex][col].type_of_cell
                self._cells[curIndex][col].type_of_cell = TypeOfCell.empty

            if count_of_none == self._rows and not is_need_to_add:
                first_empty_col = min(col, first_empty_col)
        if first_empty_col != len(self._cells[0]):
            self.move_empty_column(first_empty_col)
        elif is_need_to_add:
            self.fill_empty_cells()

    def move_empty_column(self, left_empty_col) -> None:
        count_to_shift = 1
        for i in range(left_empty_col + 1, self._columns):
            if self._cells[self._rows - 1][i].type_of_cell == TypeOfCell.empty:
                count_to_shift += 1
                continue
            for rowIndexToCopy in range(self._rows):
                self._cells[rowIndexToCopy][i - count_to_shift].type_of_cell \
                    = self._cells[rowIndexToCopy][i].type_of_cell
                self._cells[rowIndexToCopy][i].type_of_cell = TypeOfCell.empty

    def fill_empty_cells(self):
        for col in range(len(self._cells[0])):
            for row in range(len(self._cells)):
                if self._cells[row][col].type_of_cell != TypeOfCell.empty:
                    break
                self._cells[row][col].type_of_cell = rnd.choice(self._list_of_choices)

    def print(self) -> None:
        for i in self._cells:
            for j in i:
                letter = 'r'
                if j.type_of_cell == TypeOfCell.empty:
                    letter = 'e'
                elif j.type_of_cell == TypeOfCell.circle:
                    letter = 'c'
                elif j.type_of_cell == TypeOfCell.star:
                    letter = 's'
                elif j.type_of_cell == TypeOfCell.triangle:
                    letter = 't'
                print(letter, "\t", end="")
            print()
        print('-' * 3 * (len(self._cells[0])))

    def handle_click(self, x: int, y: int) -> str:
        if self.state != GameState.PLAYING:
            return 'No'

        set_to_remove = self.find_neighbours(x, y)
        len_to_remove = len(set_to_remove)
        if len_to_remove < 2:
            return 'No'
        sound_peeker = 'default'
        self.score += len_to_remove * self._one_cube_price
        add_new_blocks = False
        if len_to_remove >= self.blocks_to_add:
            add_new_blocks = True
        if len_to_remove >= 2 * self.blocks_to_add:
            sound_peeker = 'big_blocks'
        deleted = self.delete_cells(set_to_remove)
        self.move_cells(deleted, add_new_blocks)
        if self.update_count_of_blocks():
            sound_peeker = 'blocks'
        if not self.is_possible_to_move():
            self._state = GameState.FAILED
            return 'No'
        return sound_peeker

    def update_count_of_blocks(self) -> bool:
        if self.score < 1000:
            return False
        cur_count = self.score // 1000 + 2
        if cur_count > self.blocks_to_add:
            self.blocks_to_add = cur_count
            return True
        return False

    def is_possible_to_move(self) -> bool:
        all_cells_set = self.get_all_cells()

        while all_cells_set:
            cell = all_cells_set.pop()
            row, col = cell.row, cell.col
            all_neighbours = self.find_neighbours(row, col)
            if len(all_neighbours) > 1:
                return True
            all_cells_set.difference(all_neighbours)
        return False

    def get_all_cells(self) -> set[Cell]:
        all_cells = set()
        for row in range(self._rows):
            for col in range(self._columns):
                if self._cells[row][col].type_of_cell != TypeOfCell.empty:
                    all_cells.add(self._cells[row][col])
        return all_cells

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

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def rows(self):
        return self._rows

    @property
    def columns(self):
        return self._columns

    @property
    def cells(self):
        return self._cells
