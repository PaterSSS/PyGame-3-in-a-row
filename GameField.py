import random as rnd

from TypeOfCells import TypeOfCell
from Cell import Cell


class Game:
    def __init__(self, rows: int = 0, columns: int = 0, pathToFile: str = None):
        if pathToFile is not None:
            params = Game.read_field_from_file(pathToFile)
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
    def read_field_from_file(pathToFile: str) -> tuple[int, int, list[list[Cell]]]:
        row_size = 0
        col_size = 0
        cell_field = []
        with open(pathToFile, 'r') as f:
            for rowIndex, stringRow in enumerate(f):
                cell_field.append([])
                cells = stringRow.strip().split('\t')
                if col_size == 0:
                    col_size = len(cells)
                elif col_size != len(cells):
                    raise ValueError("It is not square field")
                row_size += 1
                for col, cell in enumerate(cells):
                    typeOfCell = None
                    cell = cell.strip()
                    match cell:
                        case 'r':
                            typeOfCell = TypeOfCell.rectangle
                        case 'c':
                            typeOfCell = TypeOfCell.circle
                        case 't':
                            typeOfCell = TypeOfCell.triangle
                        case 's':
                            typeOfCell = TypeOfCell.star
                    cell_field[rowIndex].append(Cell(rowIndex, col, typeOfCell))
            return row_size, col_size, cell_field

    def find_neighbours(self, row: int, col: int) -> set[Cell]:
        cells_to_delete: set[Cell] = set()
        if self._rows <= row < 0 and self._columns <= col < 0:
            return cells_to_delete
        stack = [self._cells[row][col]]
        cells_to_delete.add(self._cells[row][col])
        while stack:
            cell = stack.pop()
            typecell = cell.typeOfCell
            x = cell.row
            y = cell.col
            if (x + 1 < self._rows and self._cells[x + 1][y].typeOfCell == typecell
                    and self._cells[x + 1][y] not in cells_to_delete):

                cells_to_delete.add(self._cells[x + 1][y])
                stack.append(self._cells[x + 1][y])
            if (x - 1 > 0 and self._cells[x - 1][y].typeOfCell == typecell
                    and self._cells[x - 1][y] not in cells_to_delete):

                cells_to_delete.add(self._cells[x - 1][y])
                stack.append(self._cells[x - 1][y])
            if (y + 1 < self._columns and self._cells[x][y + 1].typeOfCell == typecell
                    and self._cells[x][y + 1] not in cells_to_delete):

                cells_to_delete.add(self._cells[x][y + 1])
                stack.append(self._cells[x][y + 1])
            if (y - 1 > 0 and self._cells[x][y - 1].typeOfCell == typecell
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

    def move_cells(self, firs_to_move: dict[int, int], isNeedToAdd: bool) -> None:
        columns_to_shift = []
        for col, row in firs_to_move.items():
            count_of_None = 0
            for curIndex in range(row, -1, -1):
                if self._cells[curIndex][col] is None:
                    count_of_None += 1
                    continue
                self._cells[curIndex + count_of_None][col] = self._cells[curIndex][col]
                self._cells[curIndex][col] = None
            if isNeedToAdd:
                list_of_types = list(TypeOfCell)
                for i in range(count_of_None):
                    self._cells[i][col] = Cell(i, col, rnd.choice(list_of_types))
            elif count_of_None == self._rows:
                columns_to_shift.append(col)

        if columns_to_shift:
            columns_to_shift.sort()
            self.move_empty_column(columns_to_shift)

    def move_empty_column(self, columns_to_shift: list) -> None:
        for curCol in columns_to_shift:
            for i in range(curCol + 1, self._columns):
                if self._cells[self._rows - 1][i] is None:
                    continue
                for rowIndexToCopy in range(self._rows):
                    self._cells[rowIndexToCopy][curCol] = self._cells[rowIndexToCopy][i]
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


# нужен метод который будет удалять одинаковые клетки и сдвигать те, что находятся над ними.


if __name__ == '__main__':
    game = Game(pathToFile="testField.txt")
    game.print()
    print('--------------------------')
    to_delete = game.find_neighbours(0, 4)
    deepest = game.delete_cells(to_delete)
    game.print()
    print('--------------------------')
    game.move_cells(deepest, True)
    game.print()
    print('--------------------------')
