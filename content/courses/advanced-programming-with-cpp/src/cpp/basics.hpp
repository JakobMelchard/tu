// basics.hpp -- included by basics_main.cpp AND basics_other.cpp (note 01).
// Each declaration below is chosen to show one linkage rule [basic.link].
#pragma once

inline int shared_counter = 0;     // inline variable: external linkage, ONE object per program
static int per_tu_counter = 0;     // internal linkage: one object PER translation unit (a header smell)
extern int defined_once;           // declaration only; the definition lives in basics_other.cpp
constexpr int answer = 42;         // const/constexpr at namespace scope => internal linkage, harmless

inline int bump_shared() { return ++shared_counter; }   // inline function: may be defined in every TU
inline int bump_per_tu() { return ++per_tu_counter; }   // careful: which per_tu_counter? see note 01

// Implemented in basics_other.cpp, so the "other" TU's objects can be inspected from main.
int* other_shared();
int* other_per_tu();
const int* other_answer();
int other_bump_per_tu();
