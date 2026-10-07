// modules_main.cpp -- imports the geometry module (note 01).
import geometry;
#include "../check.hpp"

int main() {
    CHECK(geo::norm({3, 4}) == 5.0);
    CHECK(perimeter_of_square(1.5) == 6.0);
    // twice(1.0);  // error: 'twice' is not exported, so it is not visible here
    return chk::report("modules");
}
