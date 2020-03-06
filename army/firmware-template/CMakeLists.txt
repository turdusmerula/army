cmake_minimum_required(VERSION 2.8)

set(PROJECT_PATH "$ENV{PROJECT_PATH}") 

set(board "$ENV{board}") 
set(BOARD_PATH "${PROJECT_PATH}/board/${board}") 
set(TOOLCHAIN_PATH "${BOARD_PATH}/toolchain") 

# unset to disable freertos dynamic memory
set(HEAP_MODEL 1)

# import helpers
include(${TOOLCHAIN_PATH}/cmake/helpers.cmake)

# Toolchain
include(${TOOLCHAIN_PATH}/cmake/core-${DEVICE}.cmake)
include(${BOARD_PATH}/cmake/board.cmake)
include(${TOOLCHAIN_PATH}/cmake/freertos-samd21.cmake)
include(${TOOLCHAIN_PATH}/cmake/print.cmake)
include(${TOOLCHAIN_PATH}/cmake/stream.cmake)
include(${TOOLCHAIN_PATH}/cmake/debug-samd21.cmake)
include(${TOOLCHAIN_PATH}/cmake/display-ssd1306.cmake)
include(${TOOLCHAIN_PATH}/cmake/lis3dh.cmake)
include(${TOOLCHAIN_PATH}/cmake/ledpin-samd21.cmake)
include(${TOOLCHAIN_PATH}/cmake/gps-neo.cmake)
include(${TOOLCHAIN_PATH}/cmake/sigfox-sfm.cmake)

# show informations about includes
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -H")
#set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -H")

# set build options from toolchain file
set(CMAKE_COMMON_FLAGS "${COMMON_FLAGS}") 
set(CMAKE_ASM_FLAGS "${ASM_FLAGS}")
set(CMAKE_C_FLAGS "${C_FLAGS}")
set(CMAKE_CXX_FLAGS "${CXX_FLAGS}")

message("Build type ${CMAKE_BUILD_TYPE}")
message("C flags: ${CMAKE_C_FLAGS}")
message("CPP flags: ${CMAKE_CXX_FLAGS}")
message("Link flags: ${LINKER_FLAGS}")
message("CMAKE_ASM_COMPILER ${CMAKE_ASM_COMPILER}")
message("CMAKE_C_COMPILER ${CMAKE_C_COMPILER}")
message("CMAKE_CXX_COMPILER ${CMAKE_CXX_COMPILER}")
message("CMAKE_CXX_LINK_EXECUTABLE ${CMAKE_CXX_LINK_EXECUTABLE}")

# build binaries
add_subdirectory(firmware)
