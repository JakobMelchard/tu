// basics_main.cpp -- translation units, linkage and the ODR, made observable (note 01).
// Build: two TUs compiled separately and linked, see the Makefile rule for bin/basics.
#include "basics.hpp"
#include "check.hpp"

int main() {
    // inline variable: both TUs see the same object
    CHECK(&shared_counter == other_shared());
    bump_shared();
    CHECK(*other_shared() == 1);

    // static in a header: two different objects with the same name
    CHECK(&per_tu_counter != other_per_tu());
    bump_per_tu();                          // increments main's copy
    CHECK(per_tu_counter == 1 && *other_per_tu() == 0);

    // The inline function bump_per_tu names a DIFFERENT entity in each TU. That is
    // formally an ODR violation (same inline function, definitions refer to different
    // entities [basic.def.odr]); the linker keeps one body and the result depends on
    // which. We only check that the two counters together moved by one.
    int before = per_tu_counter + *other_per_tu();
    other_bump_per_tu();
    CHECK(per_tu_counter + *other_per_tu() == before + 1);

    // constexpr at namespace scope: internal linkage, one object per TU (if odr-used)
    CHECK(&answer != other_answer() && *other_answer() == 42);

    CHECK(defined_once == 7);               // resolved by the linker
    return chk::report("basics");
}
