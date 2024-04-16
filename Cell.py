from TypeOfCells import TypeOfCell


class Cell:
    def __init__(self, row: int, col: int, type_of_cell: TypeOfCell):
        self._typeOfCell = type_of_cell
        self._row = row
        self._col = col

    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

    @property
    def type_of_cell(self):
        return self._typeOfCell

    @type_of_cell.setter
    def type_of_cell(self, type_of_cell: TypeOfCell):
        self._typeOfCell = type_of_cell

    def __hash__(self):
        return hash((self._row, self._col, self._typeOfCell))

    def __eq__(self, other):
        if isinstance(other, Cell):
            return (self._row, self._col, self._typeOfCell) == (other.row, other.col, other.type_of_cell)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
