// vtk_writer.cpp -- legacy VTK output for ParaView (topic 09).
//
//   STRUCTURED_POINTS: only dimensions, origin and spacing are stored; point data
//   follows in x-fastest order. UNSTRUCTURED_GRID: explicit point list, cell
//   connectivity and cell types (5 = VTK_TRIANGLE, 9 = VTK_QUAD, 10 = VTK_TETRA).
//   The demo writes field.vtk (structured, scalar + vector field) and mesh.vtk (a
//   triangulated unit square with a scalar). Open both in ParaView: File > Open.
//
// Sources: the legacy VTK file format, five sections, x-fastest point order [S12];
// cell type ids from vtkCellType.h [S13] (vendored in refs/vendor/). The output
// is re-parsed against the specification by ../py/vtk_check.py.
//
// Usage: ./vtk_writer [--test | --bench]      (--test writes to and removes tmp files)
#include "common.hpp"
#include <array>
#include <cstdio>
#include <fstream>
#include <sstream>
#include <vector>

struct Vec3 { double x, y, z; };

static void write_structured_points(const std::string& fn, std::size_t nx, std::size_t ny, std::size_t nz,
                                    double dx, double dy, double dz,
                                    const std::string& scalar_name, const std::vector<double>& scalars,
                                    const std::string& vector_name = "", const std::vector<Vec3>& vectors = {}) {
    std::ofstream f(fn);
    f << "# vtk DataFile Version 3.0\nNSSC I structured field\nASCII\n"
      << "DATASET STRUCTURED_POINTS\nDIMENSIONS " << nx << ' ' << ny << ' ' << nz
      << "\nORIGIN 0 0 0\nSPACING " << dx << ' ' << dy << ' ' << dz
      << "\nPOINT_DATA " << nx * ny * nz << "\nSCALARS " << scalar_name << " double 1\nLOOKUP_TABLE default\n";
    for (double s : scalars) f << s << '\n';            // x varies fastest, then y, then z
    if (!vectors.empty()) {
        f << "VECTORS " << vector_name << " double\n";
        for (const Vec3& v : vectors) f << v.x << ' ' << v.y << ' ' << v.z << '\n';
    }
}

// Cells: each entry lists its point ids; type per cell (5 triangle, 9 quad, 10 tet).
static void write_unstructured_grid(const std::string& fn, const std::vector<Vec3>& pts,
                                    const std::vector<std::vector<int>>& cells, const std::vector<int>& types,
                                    const std::string& scalar_name, const std::vector<double>& point_scalars) {
    std::ofstream f(fn);
    f << "# vtk DataFile Version 3.0\nNSSC I unstructured mesh\nASCII\nDATASET UNSTRUCTURED_GRID\n";
    f << "POINTS " << pts.size() << " double\n";
    for (const Vec3& p : pts) f << p.x << ' ' << p.y << ' ' << p.z << '\n';
    std::size_t list_size = 0;
    for (const auto& c : cells) list_size += c.size() + 1;
    f << "CELLS " << cells.size() << ' ' << list_size << '\n';
    for (const auto& c : cells) { f << c.size(); for (int id : c) f << ' ' << id; f << '\n'; }
    f << "CELL_TYPES " << cells.size() << '\n';
    for (int t : types) f << t << '\n';
    f << "POINT_DATA " << pts.size() << "\nSCALARS " << scalar_name << " double 1\nLOOKUP_TABLE default\n";
    for (double s : point_scalars) f << s << '\n';
}

// Structured triangulation of the unit square: (n+1)^2 points, 2 n^2 triangles.
static void square_triangles(std::size_t n, std::vector<Vec3>& pts, std::vector<std::vector<int>>& cells) {
    const double h = 1.0 / n;
    for (std::size_t j = 0; j <= n; ++j)
        for (std::size_t i = 0; i <= n; ++i) pts.push_back({i * h, j * h, 0.0});
    auto id = [&](std::size_t i, std::size_t j) { return static_cast<int>(j * (n + 1) + i); };
    for (std::size_t j = 0; j < n; ++j)
        for (std::size_t i = 0; i < n; ++i) {
            cells.push_back({id(i, j), id(i + 1, j), id(i + 1, j + 1)});   // counter-clockwise
            cells.push_back({id(i, j), id(i + 1, j + 1), id(i, j + 1)});
        }
}

// Minimal reader used by the test: counts numeric values after LOOKUP_TABLE and
// returns the DIMENSIONS / POINTS line for checking.
static std::pair<std::string, std::size_t> read_back(const std::string& fn, const std::string& key) {
    std::ifstream f(fn);
    std::string line, found;
    std::size_t count = 0;
    bool in_scalars = false;
    while (std::getline(f, line)) {
        if (line.rfind(key, 0) == 0) found = line;
        if (line.rfind("VECTORS", 0) == 0) in_scalars = false;
        if (in_scalars) { std::istringstream is(line); double v; while (is >> v) ++count; }
        if (line.rfind("LOOKUP_TABLE", 0) == 0) in_scalars = true;
    }
    return {found, count};
}

int main(int argc, char** argv) {
    const std::string mode = mode_of(argc, argv);
    const bool test = mode == "test";
    const std::size_t n = 40;
    const double h = 1.0 / n, PI = 3.14159265358979323846;

    // structured: scalar u = sin(pi x) sin(pi y) and its gradient as a vector field
    std::vector<double> u; std::vector<Vec3> grad;
    for (std::size_t j = 0; j <= n; ++j)
        for (std::size_t i = 0; i <= n; ++i) {
            double x = i * h, y = j * h;
            u.push_back(std::sin(PI * x) * std::sin(PI * y));
            grad.push_back({PI * std::cos(PI * x) * std::sin(PI * y), PI * std::sin(PI * x) * std::cos(PI * y), 0.0});
        }
    const std::string f1 = test ? "test_field.vtk" : "field.vtk", f2 = test ? "test_mesh.vtk" : "mesh.vtk";
    write_structured_points(f1, n + 1, n + 1, 1, h, h, 1.0, "u", u, "grad_u", grad);

    // unstructured: same square as triangles with a radial scalar
    std::vector<Vec3> pts; std::vector<std::vector<int>> cells;
    square_triangles(10, pts, cells);
    std::vector<int> types(cells.size(), 5);
    std::vector<double> r;
    for (const Vec3& p : pts) r.push_back(std::hypot(p.x - 0.5, p.y - 0.5));
    write_unstructured_grid(f2, pts, cells, types, "r", r);
    std::printf("wrote %s (%zux%zu structured points, scalar + vector) and %s (%zu points, %zu triangles)\n",
                f1.c_str(), n + 1, n + 1, f2.c_str(), pts.size(), cells.size());

    if (test) {
        auto [dims, cnt] = read_back(f1, "DIMENSIONS");
        CHECK(dims == "DIMENSIONS 41 41 1");
        CHECK(cnt == (n + 1) * (n + 1));
        auto [ptsline, cnt2] = read_back(f2, "POINTS");
        CHECK(ptsline == "POINTS 121 double");
        CHECK(cnt2 == 121 && cells.size() == 200);
        // every triangle has positive (counter-clockwise) area
        for (const auto& c : cells) {
            const Vec3 &a = pts[c[0]], &b = pts[c[1]], &d = pts[c[2]];
            CHECK((b.x - a.x) * (d.y - a.y) - (b.y - a.y) * (d.x - a.x) > 0);
        }
        std::remove(f1.c_str()); std::remove(f2.c_str());
        std::puts("vtk_writer: ok");
    }
    return 0;
}
