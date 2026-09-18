# Copyright (c) 2025-2026 Tilmann Unte, Antonia Geßwein
# SPDX-License-Identifier:  Apache-2.0

from numpy import zeros
from math import ceil

# please adjust accordingly
file_name = "dense-clutter"
file_nr = 0
snippet_size = 199
input_file_path = "../rodata/" + file_name + "-" + str(file_nr) + ".csv"

# read all data from .csv file into sensor_data variable

input_file = open(input_file_path, "r")
sensor_data = []

while True:
    rotation_data = zeros(360, dtype = int)
    rotation = input_file.readline()
    if not rotation:  # EOF reached
        break
    rotation = rotation.split(',')
    rotation.pop()  # remove last element ("\n")
    for measurement in rotation:
        m = measurement.split(":")
        angle = int(m[0])
        if (angle >= 360):
            angle -= 360
        distance = int(m[1])
        rotation_data[angle] = distance
    sensor_data.append(rotation_data)
input_file.close()


# create snippets of sensor data and save them in separate .c files

snippet_amount = ceil(len(sensor_data) / snippet_size)
snippet_nr = 0
snippet_rest_size = len(sensor_data) % snippet_size

for snippet in range(snippet_amount):
    output_file_path = "../rodata/data_snippets/" + file_name + "-" + str(file_nr) + "-" + str(snippet_nr) + ".c"
    output_file = open(output_file_path, "w")

    if snippet == snippet_amount - 1:   # -1 for index
        output_file.write("const int sensor_data[" + str(snippet_rest_size) + "][360] = {\n")
    else:
        output_file.write("const int sensor_data[" + str(snippet_size) + "][360] = {\n")
    for rotation in range(snippet_size):
        if snippet == snippet_amount - 1 and rotation == snippet_rest_size:
            break
        output_file.write("{")
        for angle in range(360):
            output_file.write(str(sensor_data[rotation + snippet * snippet_size][angle]))
            if angle < 359:
                output_file.write(",")
        output_file.write("},\n")
    output_file.write("};\n")

    output_file.close()
    snippet_nr += 1
