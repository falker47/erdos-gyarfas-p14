cmake_minimum_required(VERSION 3.25)

project(
  erdos_gyarfas_p14
  VERSION 0.1.0
  DESCRIPTION "Reproducible computational study of the Erdos-Gyarfas conjecture"
  LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS NO)

set(EG_UPSTREAM_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/erdos-gyarfas")

# This target is a build-system wrapper around the exact preserved upstream
# serial sources. It deliberately adds no project implementation or semantic
# patch. The original Makefile remains available in the snapshot.
add_executable(
  eg-upstream-serial
  "${EG_UPSTREAM_DIR}/src/graph.cpp"
  "${EG_UPSTREAM_DIR}/src/lib.cpp"
  "${EG_UPSTREAM_DIR}/src/main.cpp"
)

target_include_directories(
  eg-upstream-serial
  PRIVATE "${EG_UPSTREAM_DIR}/include"
)

if(MSVC)
  target_compile_options(eg-upstream-serial PRIVATE /W4)
else()
  target_compile_options(eg-upstream-serial PRIVATE -Wall -Wextra)
endif()

set_target_properties(
  eg-upstream-serial
  PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
