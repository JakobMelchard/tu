// basics_other.cpp -- the second translation unit of the basics program (note 01).
#include "basics.hpp"

int defined_once = 7;   // the one definition that `extern int defined_once;` refers to

int* other_shared() { return &shared_counter; }
int* other_per_tu() { return &per_tu_counter; }
const int* other_answer() { return &answer; }
int other_bump_per_tu() { return bump_per_tu(); }
