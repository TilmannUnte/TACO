/*
 * Copyright (c) 2025-2026 Antonia Geßwein, Tilmann Unte
 * SPDX-License-Identifier:  Apache-2.0
 */
#include "fast_obstacles.c"

#define RETURN_CONTINUE 1
#define RETURN_END 0

int read_input(int rotations) {
    static int rotation_nr = 0;

    for (int i = 0; i < ANGLE_COUNT; ++i) {
        distances[i] = sensor_data[rotation_nr][i];
    }

    ++rotation_nr;

    if (rotation_nr == rotations) {
        return RETURN_END;
    } else {
        return RETURN_CONTINUE;
    }
}

