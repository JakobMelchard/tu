// P1103 named modules (flags: -fcxx-modules -x c++-module; Apple clang needs -fcxx-modules)
export module probe;
export int answer() { return 42; }
