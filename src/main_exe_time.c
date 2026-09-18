/*
 * Copyright (c) 2024-2026 Antonia Geßwein, Tilmann Unte
 * SPDX-License-Identifier:  Apache-2.0
*/

#ifndef CONFIG_ARCH_POSIX
#include <zephyr/timing/timing.h>
#endif

#include <zephyr/kernel.h>

#include "read_ro_mem.c"
// Pick an input file here
#include "../rodata/data_snippets/zigzag-0-0.c"

int main(void)
{
	// dry run (touches code and data locations to initialize hw states)
	for (int i = 0; i < ANGLE_COUNT; i++) {
		distances[i] = 1500;
	}

	calculate_obstacles(distances, &obstacle_data0);

	printf("begin %s\n", file_name);
	while (1) {
      	// read data from one rotation
                 int snippet_size = sizeof(sensor_data) / sizeof(sensor_data[0]);
                 int ret = read_input(snippet_size);

#ifndef CONFIG_ARCH_POSIX
                 timing_t start_time, end_time;
                 uint64_t total_cycles;

                 timing_init();
                 timing_start();

                 start_time = timing_counter_get();
#endif

                 calculate_obstacles(distances, &obstacle_data0);

#ifndef CONFIG_ARCH_POSIX
                 end_time = timing_counter_get();

                 total_cycles = timing_cycles_get(&start_time, &end_time);

                 timing_stop();

                 // write measured execution times to serial port
                 // format: cycles, time_in_nano_s
                 printk("%lli, %u, %u\n", total_cycles, obstacle_data0.point_count, obstacle_data0.cluster_count);
#endif

                 if (ret == RETURN_END) {
                         // reached end of sensor data array
                         printf("end %s\n", file_name);
                         break;
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
