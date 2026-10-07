// MUST NOT COMPILE: std::string is not a la::Scalar (it has + but no * or unary -).
// expect: constraints not satisfied
#include <string>
#include "la/matrix.hpp"
int main() { la::Matrix<std::string> m(2, 2); }
