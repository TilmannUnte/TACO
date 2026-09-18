# How Bad Does it Get? A Case Study on the Limitations of WCET Analysis

In this repository one can find the benchmark, input data, and associated scripts
for the paper with the above title.

The benchmark itself is contained in the *fast_obstacles.c* file.
Input data can be found in the *rodata* folder.

To get started immediately, it is recommended to use a Zephyr RTOS build environment.
The XMC4500 is the only board natively supported, but any other board with basic
UART support is equally viable.

Choose between two variants of the program:
- Execution Time Measurement
- Data Output for Visualization

This can be done in the *CMakeLists* file.

Next, choose an input data snippet and include it in either *main_exe_time*
or *obstacles_for_visualization*.

Compile, Flash, Run!

If you chose execution time measurement, the MCU will output a series of cycle counts
via the serial interface.

If instead you chose visualization, it will output of the obstacle detection
algorithm. This can be visualized by using the *gui.py* script.

Regarding WCET analysis, you can use the included *aiT.ais* annotations file.
The *report.txt* contains the output of the aiT analysis used in the paper.

## NOTE FOR REVIEW PHASE

- Copyright holder and benchmark name information has been redacted
- report.txt file has been modified to remove folder and host computer names that could lead to unblinding
- aiT project file has been withheld, as it contains unblinding info which is challenging to remove
