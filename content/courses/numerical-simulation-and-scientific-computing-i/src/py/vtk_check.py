"""A validating reader for the legacy VTK format (topic 09).

Note 09 writes legacy `.vtk` files by hand in `../cpp/vtk_writer.cpp`. Hand-written
format code is exactly the kind that "looks right and ParaView refuses it", so
this module parses the format back **against the specification** [S12] and
rejects every violation the note lists as a pitfall:

  section 1  `# vtk DataFile Version x.x`  -- the version is NOT fixed at 3.0
  section 2  title, at most 256 characters
  section 3  `ASCII` or `BINARY`
  section 4  `DATASET <type>` + that type's structure
  section 5  `POINT_DATA n` / `CELL_DATA n` + attributes

Checks beyond plain parsing: `DIMENSIONS` counts **points**, not cells; point
data is ordered **x fastest, then y, then z** [S12]; `size` in `CELLS n size` is
the total number of integers *including* each cell's leading count; every
`CELL_TYPES` entry is a real id, read from the vendored `vtkCellType.h` [S13];
`POINTS` and `VECTORS` always carry three components, in 2D too.

Run `python3 vtk_check.py path.vtk` to validate a file, or with no argument to
self-test. Tests: test_vtk_check.py.
"""
import re
import sys
from pathlib import Path

import numpy as np

VENDORED_HEADER = Path(__file__).resolve().parents[2] / "refs" / "vendor" / "vtkCellType.h"

_POINTS_PER_CELL = {1: 1, 3: 2, 5: 3, 8: 4, 9: 4, 10: 4, 11: 8, 12: 8, 13: 6, 14: 5}


class VtkFormatError(ValueError):
    """The file violates the legacy VTK specification [S12]."""

def cell_type_names(header=VENDORED_HEADER):
    """{id: name} read from the vendored vtkCellType.h [S13], the normative list.

    Deliberately has no hard-coded fallback: a table typed out here would be
    exactly the thing this module exists to stop anyone trusting.
    """
    text = Path(header).read_text()
    out = {}
    for name, val in re.findall(r"^\s*(VTK_[A-Z0-9_]+)\s*=\s*(\d+)\s*,", text, re.M):
        out.setdefault(int(val), name)
    if not out:
        raise VtkFormatError(f"no cell types parsed from {header}")
    return out


def parse(text):
    """Parse an ASCII legacy VTK file, raising VtkFormatError on any violation.

    Returns a dict with the dataset type, its structure, and the attributes.
    """
    lines = text.splitlines()
    if len(lines) < 4:
        raise VtkFormatError("fewer than the four mandatory header lines")

    # Section 1: version and identifier.
    if not re.fullmatch(r"# vtk DataFile Version \d+\.\d+", lines[0].rstrip()):
        raise VtkFormatError(f"section 1 must be '# vtk DataFile Version x.x', got {lines[0]!r}")

    # Section 2: title, at most 256 characters.
    if len(lines[1]) > 256:
        raise VtkFormatError(f"section 2 title is {len(lines[1])} chars, limit is 256")

    # Section 3: file format.
    fmt = lines[2].strip().upper()
    if fmt not in ("ASCII", "BINARY"):
        raise VtkFormatError(f"section 3 must be ASCII or BINARY, got {lines[2]!r}")
    if fmt == "BINARY":
        raise VtkFormatError("this reader only validates ASCII files")

    # Section 4: dataset.
    m = re.match(r"\s*DATASET\s+(\w+)", lines[3])
    if not m:
        raise VtkFormatError(f"section 4 must start with DATASET, got {lines[3]!r}")
    kind = m.group(1)

    body = lines[4:]
    out = {"version": lines[0].split()[-1], "title": lines[1], "format": fmt, "dataset": kind}

    if kind == "STRUCTURED_POINTS":
        out.update(_parse_structured_points(body))
    elif kind == "UNSTRUCTURED_GRID":
        out.update(_parse_unstructured_grid(body))
    else:
        raise VtkFormatError(f"unsupported DATASET {kind} (this reader does "
                             f"STRUCTURED_POINTS and UNSTRUCTURED_GRID)")

    out["attributes"] = _parse_attributes(body, out["n_points"], out.get("n_cells", 0))
    return out


def _kw(body, name, count):
    """The `count` numbers following the line beginning with `name`."""
    for i, ln in enumerate(body):
        if ln.split()[:1] == [name]:
            vals = ln.split()[1:]
            j = i + 1
            while len(vals) < count and j < len(body):
                vals += body[j].split()
                j += 1
            if len(vals) < count:
                raise VtkFormatError(f"{name}: expected {count} values, found {len(vals)}")
            return vals[:count]
    raise VtkFormatError(f"missing required keyword {name}")


def _parse_structured_points(body):
    dims = [int(v) for v in _kw(body, "DIMENSIONS", 3)]
    if any(d < 1 for d in dims):
        raise VtkFormatError(f"DIMENSIONS must all be >= 1, got {dims}")
    origin = [float(v) for v in _kw(body, "ORIGIN", 3)]
    spacing = [float(v) for v in _kw(body, "SPACING", 3)]
    if any(s <= 0 for s in spacing):
        raise VtkFormatError(f"SPACING must all be > 0, got {spacing}")
    nx, ny, nz = dims
    return {"dimensions": dims, "origin": origin, "spacing": spacing,
            "n_points": nx * ny * nz,
            "n_cells": max(nx - 1, 1) * max(ny - 1, 1) * max(nz - 1, 1)}


def _parse_unstructured_grid(body):
    idx = next((i for i, ln in enumerate(body) if ln.split()[:1] == ["POINTS"]), None)
    if idx is None:
        raise VtkFormatError("missing POINTS")
    parts = body[idx].split()
    if len(parts) < 3:
        raise VtkFormatError(f"POINTS needs 'n dataType', got {body[idx]!r}")
    npts = int(parts[1])
    coords = []
    j = idx + 1
    while len(coords) < 3 * npts and j < len(body):
        if body[j].split()[:1] and body[j].split()[0].isalpha():
            break
        coords += body[j].split()
        j += 1
    if len(coords) != 3 * npts:
        raise VtkFormatError(f"POINTS: expected {3 * npts} coordinates (3 per point, "
                             f"in 2D as well), found {len(coords)}")
    pts = np.array(coords, float).reshape(npts, 3)

    ci = next((i for i, ln in enumerate(body) if ln.split()[:1] == ["CELLS"]), None)
    if ci is None:
        raise VtkFormatError("missing CELLS")
    cparts = body[ci].split()
    if len(cparts) < 3:
        raise VtkFormatError(f"CELLS needs 'n size', got {body[ci]!r}")
    ncells, size = int(cparts[1]), int(cparts[2])
    ints, j = [], ci + 1
    while len(ints) < size and j < len(body):
        toks = body[j].split()
        if toks and toks[0].isalpha():
            break
        ints += [int(t) for t in toks]
        j += 1
    if len(ints) != size:
        raise VtkFormatError(f"CELLS: 'size' is the TOTAL number of integers including each "
                             f"cell's leading count; header says {size}, file has {len(ints)}")
    cells, k = [], 0
    while k < len(ints):
        m = ints[k]
        cells.append(ints[k + 1:k + 1 + m])
        k += 1 + m
    if len(cells) != ncells:
        raise VtkFormatError(f"CELLS: header says {ncells} cells, connectivity holds {len(cells)}")
    for c in cells:
        if c and (min(c) < 0 or max(c) >= npts):
            raise VtkFormatError(f"CELLS: point id out of range 0..{npts - 1} "
                                 f"(ids are 0-based) in {c}")

    ti = next((i for i, ln in enumerate(body) if ln.split()[:1] == ["CELL_TYPES"]), None)
    if ti is None:
        raise VtkFormatError("missing CELL_TYPES")
    declared = int(body[ti].split()[1])
    if declared != ncells:
        raise VtkFormatError(f"CELL_TYPES {declared} but CELLS declares {ncells}")
    types, j = [], ti + 1
    while len(types) < ncells and j < len(body):
        toks = body[j].split()
        if toks and toks[0].isalpha():
            break
        types += [int(t) for t in toks]
        j += 1
    if len(types) != ncells:
        raise VtkFormatError(f"CELL_TYPES: expected {ncells} ids, found {len(types)}")
    known = cell_type_names()
    for t, c in zip(types, cells):
        if t not in known:
            raise VtkFormatError(f"CELL_TYPES: {t} is not a VTK cell type id")
        want = _POINTS_PER_CELL.get(t)
        if want is not None and len(c) != want:
            raise VtkFormatError(f"{known[t]} needs {want} points, cell has {len(c)}")
    return {"points": pts, "cells": cells, "cell_types": types,
            "n_points": npts, "n_cells": ncells}


def _parse_attributes(body, n_points, n_cells):
    attrs = {"POINT_DATA": {}, "CELL_DATA": {}}
    section, expect = None, 0
    i = 0
    while i < len(body):
        toks = body[i].split()
        if toks[:1] == ["POINT_DATA"]:
            section, expect = "POINT_DATA", int(toks[1])
            if expect != n_points:
                raise VtkFormatError(f"POINT_DATA {expect} but the dataset has {n_points} points "
                                     f"(DIMENSIONS counts points, not cells)")
        elif toks[:1] == ["CELL_DATA"]:
            section, expect = "CELL_DATA", int(toks[1])
            if n_cells and expect != n_cells:
                raise VtkFormatError(f"CELL_DATA {expect} but the dataset has {n_cells} cells")
        elif toks[:1] == ["SCALARS"] and section:
            name = toks[1]
            ncomp = int(toks[3]) if len(toks) > 3 else 1
            if i + 1 >= len(body) or body[i + 1].split()[:1] != ["LOOKUP_TABLE"]:
                raise VtkFormatError("SCALARS must be followed by LOOKUP_TABLE")
            vals, j = [], i + 2
            while len(vals) < expect * ncomp and j < len(body):
                t = body[j].split()
                if t and t[0].isalpha():
                    break
                vals += t
                j += 1
            if len(vals) != expect * ncomp:
                raise VtkFormatError(f"SCALARS {name}: expected {expect * ncomp} values, "
                                     f"found {len(vals)}")
            attrs[section][name] = np.array(vals, float)
            i = j - 1
        elif toks[:1] == ["VECTORS"] and section:
            name = toks[1]
            vals, j = [], i + 1
            while len(vals) < 3 * expect and j < len(body):
                t = body[j].split()
                if t and t[0].isalpha():
                    break
                vals += t
                j += 1
            if len(vals) != 3 * expect:
                raise VtkFormatError(f"VECTORS {name}: expected {3 * expect} values "
                                     f"(3 components per point, in 2D too), found {len(vals)}")
            attrs[section][name] = np.array(vals, float).reshape(expect, 3)
            i = j - 1
        i += 1
    return attrs


def structured_index(i, j, k, dims):
    """Position of grid point (i, j, k) in a STRUCTURED_POINTS value list. [S12]:
    "ordered with x increasing fastest, then y, then z"."""
    nx, ny, _ = dims
    return i + nx * (j + ny * k)


def write_structured_points(path, dims, origin, spacing, values, name="u", title="NSSC I field"):
    """Write a conforming STRUCTURED_POINTS file; `values` in x-fastest order."""
    nx, ny, nz = dims
    if len(values) != nx * ny * nz:
        raise VtkFormatError("values must hold nx*ny*nz entries")
    with open(path, "w") as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write(f"{title[:256]}\n" "ASCII\n" "DATASET STRUCTURED_POINTS\n")
        f.write(f"DIMENSIONS {nx} {ny} {nz}\n")
        f.write("ORIGIN {} {} {}\n".format(*origin))
        f.write("SPACING {} {} {}\n".format(*spacing))
        f.write(f"POINT_DATA {nx * ny * nz}\n")
        f.write(f"SCALARS {name} double 1\nLOOKUP_TABLE default\n")
        f.write("\n".join(repr(float(v)) for v in values) + "\n")
    return path


def _main(argv):
    if len(argv) > 1:
        info = parse(Path(argv[1]).read_text())
        print(f"{argv[1]}: valid legacy VTK {info['version']}, {info['dataset']}, "
              f"{info['n_points']} points, {info.get('n_cells', 0)} cells")
        for sec, d in info["attributes"].items():
            for k, v in d.items():
                print(f"  {sec}: {k} shape {np.shape(v)}")
        return 0

    import tempfile
    known = cell_type_names()
    print("cell type ids, read from the vendored vtkCellType.h [S13]:")
    print("  " + "  ".join(f"{t}={known[t]}" for t in (1, 3, 5, 9, 10, 12, 13, 14)))
    d = (5, 4, 1)
    vals = np.arange(d[0] * d[1], dtype=float)
    with tempfile.TemporaryDirectory() as td:
        f = write_structured_points(Path(td) / "f.vtk", d, (0, 0, 0), (0.25, 0.25, 1), vals)
        info = parse(Path(f).read_text())
    print(f"\nself-test: wrote and re-read a {d} grid, {info['n_points']} point values; "
          f"x-fastest index of (2,1,0) = {structured_index(2, 1, 0, d)}")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
