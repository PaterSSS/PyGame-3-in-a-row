from TypeOfCells import TypeOfCell


class Cell:
    def __init__(self, row: int, col: int, typeOfCell: TypeOfCell):
        self._typeOfCell = typeOfCell
        self._row = row
        self._col = col

    @property
    def row(self):
        return self._row

    @property
    def col(self):
        return self._col

    @property
    def typeOfCell(self):
        return self._typeOfCell

    def __hash__(self):
        return hash((self._row, self._col, self._typeOfCell))

    def __eq__(self, other):
        if isinstance(other, Cell):
            return (self._row, self._col, self._typeOfCell) == (other.row, other.col, other.typeOfCell)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


if __name__ == "__main__":
    cells_list = [Cell(0, 0, TypeOfCell.star), Cell(0, 1, TypeOfCell.circle), Cell(0, 2, TypeOfCell.star),
                  Cell(0, 3, TypeOfCell.rectangle),None, Cell(0, 5, TypeOfCell.triangle)]
    cells_list[4] = cells_list[5]
    cells_list[5] = None
    for i in cells_list:
        print(i.row, i.col, i.typeOfCell)
