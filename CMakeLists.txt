# Copyright (c) 2021-2026 Tilmann Unte, Antonia Geßwein
# SPDX-License-Identifier:  Apache-2.0

cmake_minimum_required(VERSION 3.13.1)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(TACO)

# Choose your main program here
target_sources(app PRIVATE
  #src/obstacles_for_visualization.c
  src/main_exe_time.c
  src/wcclibm.c
)
