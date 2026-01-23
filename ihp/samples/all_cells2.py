"""Write a GDS with all cells."""

import gdsfactory as gf

from ihp import PDK

if __name__ == "__main__":
    PDK.activate()

    skip = {"pack_doe", "pack_doe_grid", "import_gds"}
    cells = [cell() for cell_name, cell in PDK.cells.items() if cell_name not in skip]
    c = gf.pack(cells, spacing=30)[0]
    c.show()
