// geometry.cppm -- a C++20 named module interface unit (note 01).
// Apple clang 21 only parses `export module` with -fcxx-modules (probe.sh finds this).
module;                       // global module fragment: #includes go here, not after
#include <cmath>
export module geometry;

export namespace geo {
struct vec2 { double x, y; };
double norm(vec2 v) { return std::hypot(v.x, v.y); }
}

// not exported: invisible to importers, a module-local helper
double twice(double x) { return 2 * x; }
export double perimeter_of_square(double side) { return twice(twice(side)); }
