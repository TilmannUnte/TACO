/*
 * Copyright (c) 2024-2026 Antonia Geßwein, Tilmann Unte
 * SPDX-License-Identifier:  Apache-2.0
*/

#include <stdio.h>

#include <zephyr/kernel.h>

#include "read_ro_mem.c"
// Pick an input file here
#include "../rodata/data_snippets/testrun-7-0.c"


int main(void) {
    int package_nr = 0;

    while (1) {
        // read data from one rotation
        int snippet_size = sizeof(sensor_data) / sizeof(sensor_data[0]);
        int ret = read_input(snippet_size);

        calculate_obstacles(distances, &obstacle_data0);

        printf("start, %i\n", package_nr);
                
        for (int i = 0; i < obstacle_data0.point_count; ++i) {
            printf("p, %.5f, %.5f, %i\n", (double) obstacle_data0.points[i].x, (double) obstacle_data0.points[i].y, obstacle_data0.points[i].cluster_id);
        }

        for (int i = 0; i < obstacle_data0.cluster_count; ++i) {	// print the data for each obstacle
            printf("l, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f, %.5f\n", (double) obstacle_data0.clusters[i].line.cx, (double) obstacle_data0.clusters[i].line.cy, (double) obstacle_data0.clusters[i].line.vx, (double) obstacle_data0.clusters[i].line.vy, (double) obstacle_data0.clusters[i].line.l1, (double) obstacle_data0.clusters[i].line.l2, (double) obstacle_data0.clusters[i].line.min, (double) obstacle_data0.clusters[i].line.max);
        }

        printf("end, %i\n", package_nr);

        if (ret == RETURN_END) {
            // reached end of sensor data array
            break;
        } else {
            package_nr++;
	}
    }

    #ifdef CONFIG_ARCH_POSIX
    exit(0);
    return 0;
    #else
    k_sleep(K_FOREVER);
    return 0;
    #endif
}
