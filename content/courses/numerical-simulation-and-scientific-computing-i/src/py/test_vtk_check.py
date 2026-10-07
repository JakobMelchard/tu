"""The legacy VTK format, checked clause by clause against the specification.

Reference: the VTK documentation [S12] for the format and the vendored
`refs/vendor/vtkCellType.h` [S13] for the cell type ids. Every rejection test
below corresponds to a pitfall listed in note 09.
"""
import subprocess
from pathlib import Path

import numpy as np
import pytest

from vtk_check import (VENDORED_HEADER, VtkFormatError, cell_type_names, parse, structured_index,
                       write_structured_points)

CPP_BIN = Path(__file__).resolve().parents[1] / "cpp" / "bin" / "vtk_writer"

GRID = """# vtk DataFile Version 3.0
title
ASCII
DATASET STRUCTURED_POINTS
DIMENSIONS 3 2 1
ORIGIN 0 0 0
SPACING 0.5 0.5 1
POINT_DATA 6
SCALARS T double 1
LOOKUP_TABLE default
0 1 2 3 4 5
"""

MESH = """# vtk DataFile Version 2.0
two triangles
ASCII
DATASET UNSTRUCTURED_GRID
POINTS 4 double
0 0 0
1 0 0
1 1 0
0 1 0
CELLS 2 8
3 0 1 2
3 0 2 3
CELL_TYPES 2
5
5
CELL_DATA 2
SCALARS mat double 1
LOOKUP_TABLE default
1
2
"""


def test_cell_type_ids_come_from_the_vendored_header():
    """The eight ids quoted in note 09, read out of VTK's own header [S13]."""
    assert VENDORED_HEADER.exists(), "refs/vendor/vtkCellType.h is missing"
    t = cell_type_names()
    assert t[1] == "VTK_VERTEX"
    assert t[3] == "VTK_LINE"
    assert t[5] == "VTK_TRIANGLE"
    assert t[9] == "VTK_QUAD"
    assert t[10] == "VTK_TETRA"
    assert t[12] == "VTK_HEXAHEDRON"
    assert t[13] == "VTK_WEDGE"
    assert t[14] == "VTK_PYRAMID"
    assert t[8] == "VTK_PIXEL" and t[11] == "VTK_VOXEL"   # the two easy to confuse with 9 and 12


def test_note_09_exam_answer_parses():
    """Exercise 2 of note 09 asks for exactly this header; it must be valid."""
    info = parse(GRID)
    assert info["dataset"] == "STRUCTURED_POINTS"
    assert info["dimensions"] == [3, 2, 1]
    assert info["n_points"] == 6
    assert np.allclose(info["attributes"]["POINT_DATA"]["T"], [0, 1, 2, 3, 4, 5])


def test_unstructured_grid_round_trip():
    info = parse(MESH)
    assert info["n_points"] == 4 and info["n_cells"] == 2
    assert info["cell_types"] == [5, 5]
    assert info["cells"] == [[0, 1, 2], [0, 2, 3]]
    assert np.allclose(info["attributes"]["CELL_DATA"]["mat"], [1, 2])


def test_version_number_is_not_fixed_at_3_0():
    """[S12] fixes the line as '# vtk DataFile Version x.x'. Note 09 used to say
    the first line must be exactly '... Version 3.0'; VTK's own example file is
    2.0."""
    assert parse(MESH)["version"] == "2.0"
    with pytest.raises(VtkFormatError, match="section 1"):
        parse(GRID.replace("# vtk DataFile Version 3.0", "# vtk DataFile Version"))


def test_x_varies_fastest():
    """[S12]: 'ordered with x increasing fastest, then y, then z'."""
    assert structured_index(0, 0, 0, (3, 2, 1)) == 0
    assert structured_index(2, 0, 0, (3, 2, 1)) == 2
    assert structured_index(0, 1, 0, (3, 2, 1)) == 3
    assert structured_index(1, 1, 2, (4, 3, 5)) == 1 + 4 * (1 + 3 * 2)


@pytest.mark.parametrize("bad, match", [
    (GRID.replace("ASCII", "TEXT"), "section 3"),
    (GRID.replace("DATASET STRUCTURED_POINTS", "GRID STRUCTURED_POINTS"), "section 4"),
    # DIMENSIONS counts points, not cells:
    (GRID.replace("POINT_DATA 6", "POINT_DATA 2"), "DIMENSIONS counts points"),
    (GRID.replace("SPACING 0.5 0.5 1", "SPACING 0.5 0 1"), "SPACING"),
    (GRID.replace("LOOKUP_TABLE default\n", ""), "LOOKUP_TABLE"),
    # 'size' in CELLS includes each cell's leading count (8, not 6):
    (MESH.replace("CELLS 2 8", "CELLS 2 6"), "TOTAL number of integers"),
    (MESH.replace("CELL_TYPES 2\n5\n5", "CELL_TYPES 2\n5\n99"), "not a VTK cell type"),
    # a triangle with four ids:
    (MESH.replace("3 0 1 2", "4 0 1 2 3").replace("CELLS 2 8", "CELLS 2 9"),
     "VTK_TRIANGLE needs 3"),
    # 1-based node ids:
    (MESH.replace("3 0 1 2", "3 1 2 4"), "out of range"),
    # 2D points written with two components:
    (MESH.replace("POINTS 4 double\n0 0 0\n1 0 0\n1 1 0\n0 1 0",
                  "POINTS 4 double\n0 0\n1 0\n1 1\n0 1"), "3 per point"),
])
def test_every_note_09_pitfall_is_rejected(bad, match):
    with pytest.raises(VtkFormatError, match=match):
        parse(bad)


def test_write_then_parse(tmp_path):
    dims = (5, 4, 1)
    vals = np.arange(20, dtype=float)
    p = write_structured_points(tmp_path / "f.vtk", dims, (0, 0, 0), (0.25, 0.25, 1), vals)
    info = parse(Path(p).read_text())
    assert info["n_points"] == 20
    assert np.allclose(info["attributes"]["POINT_DATA"]["u"], vals)


@pytest.mark.skipif(not CPP_BIN.exists(),
                    reason="build it with `make -C src/cpp bin/vtk_writer`")
def test_the_cpp_writer_output_conforms(tmp_path):
    """The real deliverable: cpp/vtk_writer.cpp writes the format by hand, so
    parse its output back against the specification [S12] [S13]."""
    subprocess.run([str(CPP_BIN)], cwd=tmp_path, check=True, capture_output=True)
    field = parse((tmp_path / "field.vtk").read_text())
    assert field["dataset"] == "STRUCTURED_POINTS"
    assert field["dimensions"] == [41, 41, 1]
    assert field["n_points"] == 1681 == 41 * 41
    u = field["attributes"]["POINT_DATA"]["u"]
    g = field["attributes"]["POINT_DATA"]["grad_u"]
    assert u.shape == (1681,) and g.shape == (1681, 3)
    # u = sin(pi x) sin(pi y) on [0,1]^2 with h = 0.025, x fastest.
    h = 0.025
    for (i, j) in [(0, 0), (20, 20), (10, 30), (40, 40)]:
        want = np.sin(np.pi * i * h) * np.sin(np.pi * j * h)
        assert abs(u[structured_index(i, j, 0, (41, 41, 1))] - want) < 1e-12
    assert np.allclose(g[:, 2], 0.0)          # 2D field, third component present and zero

    mesh = parse((tmp_path / "mesh.vtk").read_text())
    assert mesh["dataset"] == "UNSTRUCTURED_GRID"
    assert mesh["n_cells"] == 200 and set(mesh["cell_types"]) == {5}
    assert mesh["n_points"] == 121 == 11 * 11
    # every triangle counter-clockwise
    p = mesh["points"][:, :2]
    for c in mesh["cells"]:
        a, b, d = p[c[0]], p[c[1]], p[c[2]]
        assert (b[0] - a[0]) * (d[1] - a[1]) - (b[1] - a[1]) * (d[0] - a[0]) > 0
