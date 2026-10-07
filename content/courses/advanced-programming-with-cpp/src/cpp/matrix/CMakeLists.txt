# The matrix hand-in as a CMake project, in the shape of the course's public
# exercise repositories (include/, tests/, ctest) [S4].
#   cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ctest --test-dir build
cmake_minimum_required(VERSION 3.25)
project(la_matrix LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)          # -std=c++23, not -std=gnu++23

add_library(la INTERFACE)               # header-only: nothing to compile, only usage requirements
target_include_directories(la INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(la INTERFACE cxx_std_23)

option(LA_SANITIZE "build tests with ASan and UBSan" OFF)

enable_testing()
add_executable(test_matrix tests/test_matrix.cpp)
target_link_libraries(test_matrix PRIVATE la)
target_include_directories(test_matrix PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)   # check.hpp
target_compile_options(test_matrix PRIVATE -Wall -Wextra)
if(LA_SANITIZE)
  target_compile_options(test_matrix PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
  target_link_options(test_matrix PRIVATE -fsanitize=address,undefined)
endif()
add_test(NAME test_matrix COMMAND test_matrix)
