# 09 Mesh generation and visualisation

How a domain becomes points and cells, how to store them, and how to get a field on screen in ParaView.

This is one of the two notes in the course with a **normative** source. The legacy VTK format is specified by Kitware [S12] and the cell-type ids are fixed by VTK's own header [S13], which is BSD-3 and therefore vendored at [`../refs/vendor/vtkCellType.h`](../refs/vendor/vtkCellType.h). Every format claim below was checked against those two, and `src/py/vtk_check.py` is a validating reader that re-reads the C++ writer's output and rejects each pitfall listed at the end of this note. The Delaunay material follows Shewchuk [S32].

Reference code: `src/cpp/vtk_writer.cpp`, `src/py/vtk_check.py`, `src/py/delaunay.py`, `src/py/plot_helper.py`.

## Structured grids

- **Cartesian / uniform**: $x_i = x_0 + i h$; connectivity implicit; a field is a flat array with `idx = i*(ny) + j` (or $k$-fastest in 3D, matching VTK's $x$-fastest convention when you write files). Stencils are index arithmetic; solvers are fastest here (note 04).
- **Rectilinear**: independent 1D coordinate arrays per axis (refinement near a wall).
- **Curvilinear / mapped**: logically an $(i,j)$ grid, physical coordinates stored per point $x_{ij}$; PDE transformed to computational space via the Jacobian (body-fitted grids around airfoils).
- **Block-structured, AMR**: several structured blocks or hierarchically refined patches; keeps stencil efficiency on complex domains.

Advantages: no connectivity memory, perfect cache behaviour, simple parallel decomposition. Limitation: geometry.

## Unstructured meshes

Points plus an explicit element-node table. Element types: triangle, quadrilateral (2D); tetrahedron, hexahedron, prism, pyramid (3D). Minimal storage (note 08): `nodes[n][3]`, `elements[m][k]`, boundary tags. Orientation convention: counter-clockwise (2D), outward normals by the right-hand rule (3D); the signed area $\frac{1}{2}[(x_1 - x_0)(y_2 - y_0) - (y_1 - y_0)(x_2 - x_0)] > 0$ test in `vtk_writer --test` checks it.

**Quality measures**: aspect ratio, minimum angle (FE stiffness matrix condition number degrades with small angles, interpolation error with large angles), skewness, Jacobian positivity for mapped elements.

**Generation methods**:
- **Delaunay triangulation** [S32]: no node lies inside the circumcircle of any triangle; among all triangulations of a point set it **maximises the minimum angle** (and is unique unless four points are cocircular). Built incrementally by **Bowyer-Watson**: insert a point, delete every triangle whose circumcircle contains it, retriangulate the star-shaped cavity by joining the point to each cavity boundary edge; $O(n \log n)$ expected with a good insertion order. Implemented in `src/py/delaunay.py` and checked against the defining property, against the Euler count **(a triangulation of $n$ points with $h$ of them on the convex hull has exactly $2n - 2 - h$ triangles)**, and against `scipy.spatial.Delaunay` in `test_delaunay.py`.
  Constrained Delaunay respects prescribed boundary edges. **Delaunay refinement** (Ruppert; Chew) inserts the circumcentres of poor-quality triangles until a minimum-angle bound is met - Shewchuk's variant guarantees **20.7°** and terminates, and reaches about 33° in practice [S32]. Note that the guaranteed bound is a theorem about termination, not the angle you will actually get. Tools: Triangle [S32], TetGen, CGAL, gmsh [S33], `scipy.spatial.Delaunay`.
  In floating point the InCircle predicate is a determinant that can be evaluated with the wrong sign for nearly-cocircular input, which can produce an inconsistent mesh; Shewchuk's exact adaptive predicates exist for this reason [S32]. `delaunay.py` uses a plain tolerance and says so.
- **Advancing front**: start from the boundary, add elements inward layer by layer; good boundary layers, harder to make robust.
- **Octree / quadtree**: refine cells hierarchically, then cut to the geometry; robust for CAD input.
- **Mapped / transfinite**: structured mesh on a simple block deformed to the geometry.
- **Uniform refinement**: split each triangle into 4 by edge midpoints (needs an edge -> midpoint map, a hash on `(min,max)` node pairs), each tet into 8.

Mesh size function $h(x)$: small where the solution has gradients (boundary layers, corners, singularities); the a-posteriori error estimate drives adaptive refinement. Gmsh calls this a *size field* and takes it from the geometry, from an attractor or from a background mesh [S33].

*(Unsourced: advancing front, octree meshing and transfinite mapping are described from general knowledge. No source consulted for this course says which generator 360.242 uses, or whether it covers generation at all beyond the Delaunay idea - TISS gives only the words "Mesh Generation" [S1].)*

## Storing fields

Point data (values at nodes: FE solutions, FD grids) vs cell data (one value per element: FV averages, material ids). Both exist in VTK; filters convert.

## Legacy VTK file format

ASCII, human readable, written by `vtk_writer.cpp` and validated by `vtk_check.py`. [S12] defines exactly **five** sections, in this order:

1. the file version and identifier, `# vtk DataFile Version x.x`;
2. the title, at most 256 characters, terminated by a newline;
3. the file format, `ASCII` or `BINARY`;
4. the dataset structure, beginning with `DATASET`;
5. the dataset attributes, beginning with `POINT_DATA` or `CELL_DATA`.

```
# vtk DataFile Version 3.0          <- section 1; the version is x.x, NOT fixed at 3.0
NSSC I structured field             <- title, max 256 chars
ASCII                               <- or BINARY (big-endian raw bytes after each keyword)
DATASET STRUCTURED_POINTS
DIMENSIONS 41 41 1                  <- number of POINTS per axis (nx ny nz), 2D: nz = 1
ORIGIN 0 0 0
SPACING 0.025 0.025 1
POINT_DATA 1681                     <- nx*ny*nz values follow. [S12]: "ordered with x
                                       increasing fastest, then y, then z"
SCALARS u double 1                  <- name, type, components
LOOKUP_TABLE default
0
0.0784591
...
VECTORS grad_u double               <- 3 components per point, also for 2D
3.14159 0 0
...
```

Unstructured:

```
DATASET UNSTRUCTURED_GRID
POINTS 121 double
0 0 0
0.1 0 0
...
CELLS 200 800                       <- n cells, then `size` = the TOTAL number of integers
                                       in the list, INCLUDING each cell's leading count.
                                       200 triangles x (1 + 3) = 800.
3 0 1 12                            <- 3 nodes: ids 0, 1, 12 (0-based)
...
CELL_TYPES 200
5                                   <- VTK_TRIANGLE
...
POINT_DATA 121
SCALARS r double 1
LOOKUP_TABLE default
...
CELL_DATA 200                       <- optional, one value per cell
```

Cell type ids, from VTK's own `vtkCellType.h` [S13] (all eight verified in `test_vtk_check.py`): **1** `VTK_VERTEX`, **3** `VTK_LINE`, **5** `VTK_TRIANGLE`, **9** `VTK_QUAD`, **10** `VTK_TETRA`, **12** `VTK_HEXAHEDRON`, **13** `VTK_WEDGE`, **14** `VTK_PYRAMID`. Two easy to confuse: **8** `VTK_PIXEL` and **11** `VTK_VOXEL` are the *axis-aligned* quad and hexahedron with a different node ordering - not the same as 9 and 12. The type array is `unsigned char`, so ids stop at 255 [S13]. Other datasets: `STRUCTURED_GRID` (dimensions + explicit `POINTS`, for curvilinear), `RECTILINEAR_GRID` (`X_COORDINATES` etc.), `POLYDATA` (surfaces: `POLYGONS`, `LINES`).

The XML formats (`.vti` image, `.vtr` rectilinear, `.vts` structured, `.vtu` unstructured, `.vtp` polydata) support binary appended data with compression and parallel pieces (`.pvtu`); a `.pvd` file lists time steps. For anything beyond a few MB use XML binary, or `meshio` / `pyevtk` from Python, `vtkXMLUnstructuredGridWriter` from C++.

## ParaView workflow

File > Open the `.vtk` (or a series `field_*.vtk`, detected as a time series) > Apply. Colour by the scalar; useful filters: **Warp By Scalar** (2D field as a surface), **Contour** (isolines/isosurfaces), **Slice** and **Clip** (3D interiors), **Glyph** (vectors as arrows), **Stream Tracer** (streamlines), **Calculator** (derived fields), **Plot Over Line** (1D cut for comparison with exact solutions), **Threshold**. Python shell / `pvpython` scripts automate batch rendering; `paraview --state=` reloads a pipeline. Colour maps: viridis/coolwarm, never rainbow for quantitative reading (perceptually non-uniform).

For quick 2D plots from Python `matplotlib.pyplot.imshow` / `pcolormesh` / `tripcolor` (`plot_helper.py`); for convergence plots always log-log with a reference slope line.

## Worked example

Write the field $u = \sin\pi x \sin\pi y$ on a $41 \times 41$ grid and its gradient, and the unit square as 200 triangles with a radial scalar: `./bin/vtk_writer` produces `field.vtk` and `mesh.vtk`. Check the structured file by hand: `DIMENSIONS 41 41 1` means 1681 point values must follow `LOOKUP_TABLE default`; the value at file position $k$ belongs to point $(i, j) = (k \bmod 41, k / 41)$. In ParaView, `field.vtk` > Warp By Scalar shows the sine bump; `mesh.vtk` > Wireframe representation shows the two triangles per square. The triangulation of the $n \times n$ square uses the node numbering `id(i, j) = j (n+1) + i` and the two triangles `(id(i,j), id(i+1,j), id(i+1,j+1))` and `(id(i,j), id(i+1,j+1), id(i,j+1))`, both counter-clockwise.

## Pitfalls

- Writing point data in $j$-fastest order for a `DIMENSIONS nx ny nz` file: the picture is transposed. [S12] wants **$x$ fastest**; `vtk_check.structured_index` is the index that gets it right.
- `DIMENSIONS` counts points, not cells; a $40 \times 40$ cell grid has 41 x 41 points.
- Off-by-one in the `CELLS` size field (it includes the leading count of each cell) or 1-based node ids: ParaView refuses the file or draws garbage. Both are rejected by `vtk_check.parse`.
- Forgetting the third coordinate in 2D (`POINTS` and `VECTORS` always have 3 components).
- ASCII files for 3D problems: a $200^3$ grid is 8 M values = 100 MB of text and slow parsing; use XML binary.
- Inconsistent triangle orientation: normals flip, shading and outward-flux computations break.
- Delaunay on a point set with four cocircular points (structured grids!) is not unique; the triangulation of a square grid needs the diagonal chosen explicitly, as above.
- Bad elements (sliver tets, tiny angles) make the discrete system ill-conditioned; check the quality histogram before blaming the solver.

## Exam-style questions

1. **What is the Delaunay property and why is it desirable for finite-element meshes?** No node lies strictly inside any triangle's circumcircle. Among all triangulations of the point set it maximises the smallest angle, which keeps interpolation error and stiffness-matrix conditioning under control.
2. **Write the legacy VTK header lines needed to store a scalar $T$ on a $3 \times 2$ uniform grid with spacing 0.5.** `# vtk DataFile Version 3.0`, a title, `ASCII`, `DATASET STRUCTURED_POINTS`, `DIMENSIONS 3 2 1`, `ORIGIN 0 0 0`, `SPACING 0.5 0.5 1`, `POINT_DATA 6`, `SCALARS T double 1`, `LOOKUP_TABLE default`, then 6 values in the order $(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)$. This exact answer is asserted in `test_vtk_check.py::test_note_09_exam_answer_parses`, so it is checked against the specification rather than remembered [S12].
3. **Compare the memory to store a 2D field on a structured grid vs an unstructured triangle mesh with the same number of nodes $n$.** Structured: $8n$ bytes (values only). Unstructured: $8n$ values + $24n$ coordinates + triangles ($\approx 2n$ of them, 12 bytes each = $24n$) $\approx 56n$, seven times more, plus adjacency if needed.
4. **What is the difference between point data and cell data, and when does each arise?** Point data: one value per node (FE nodal values, FD grid values), interpolated inside cells. Cell data: one value per element (FV cell averages, material id), piecewise constant. A cell-to-point filter averages neighbours when a smooth picture is needed.
5. **How would you store the mesh so that "elements around node $i$" and "neighbour across edge $e$" are both $O(1)$?** Node-element adjacency as CSR (`offset`, `elems`); element neighbours as an $m \times 3$ array `neighbor[e][k]` (element across the edge opposite node $k$, or $-1$ on the boundary), built once by sorting or hashing edges.

Code: `src/cpp/vtk_writer.cpp` (`write_structured_points`, `write_unstructured_grid`, `square_triangles`), `src/py/vtk_check.py` (`parse`, `structured_index`, `cell_type_names`, `write_structured_points` - a validating reader for the format above), `src/py/delaunay.py` (`triangulate`, `is_delaunay`, `min_angle_degrees`), `src/py/plot_helper.py` (`plot_convergence`, `plot_field`); tests `src/py/test_vtk_check.py`, `src/py/test_delaunay.py`. Sources: [S12] [S13] [S32] [S33].
