# Copyright (c) 2024-2026 Antonia Geßwein, Tilmann Unte
# SPDX-License-Identifier:  Apache-2.0

from tkinter import *
import math
import serial
import random


# connect so serial port
ser = serial.Serial("/dev/ttyUSB0", 115200, timeout = 5)
ser.readline()

class Point:
    def __init__(self, x, y, cluster):
        self.x = x
        self.y = y
        self.cluster = cluster

    def __str__(self):
        return f"{self.x}, {self.y}, {self.cluster}"

class Line:
    def __init__(self, cx, cy, vx, vy, l1, l2, tmin, tmax):
        self.cx = cx
        self.cy = cy
        self.vx = vx
        self.vy = vy
        self.l1 = l1
        self.l2 = l2
        self.tmin = tmin
        self.tmax = tmax

    def __str__(self):
        return f"{self.cx}, {self.cy}, {self.vx}, {self.vy}, {self.l1}, {self.l2}, {self.tmin}, {self.tmax}"


# create window with coordinate system (x: [-6000, 6000], y: [-6000, 6000])

# sensor can measure distance of up to 6 meters -> scale 1:20
coo_sys_size = 600
coo_sys_middle = coo_sys_size / 2
point_radius = 1
sensor_size = 3
scale = 20

root = Tk()
root.title("Visualising sensor data")
root.geometry("700x700")
root.config(bg = "#87CEFF")

padding = Label(root, height = 2, width = coo_sys_size, bg = "#87CEFF")
padding.pack()

coo_sys = Canvas(root, height = coo_sys_size, width = coo_sys_size)
coo_sys.pack()

padding2 = Label(root, height = 1, width = coo_sys_size, bg = "#87CEFF")
padding2.pack()

'''
purpose: write all data (points & obstacles) into file when button is pressed
return value: void
'''
def call_back():
    f = open("../data_set/data_set.txt", "w")
    for point in points:
        f.write("p, " + str(point) + "\n")
    for obstacle in obstacles:
        f.write("l, " + str(obstacle) + "\n")
    f.close()

button = Button(root, text = "Save current data", command = call_back)
button.pack()


angle_count = 360
points = []
obstacles = []

'''
purpose: finding start/end of package and read data inside one package
return values:
    "start" (str): when start of package is found
    "end" (str): when end of package is found
    "data" (str): when data inside the package was read
'''
def read():
    # read one line from serial port
    line = ser.readline()

    # split the data sting
    decoded_str = line.decode("utf-8")
    data = decoded_str.split(", ")
    data.append(data[-1].strip())
    data.pop(-2)

    # data_type can be: start, end, p (point) or l (line)
    data_type = data[0]
    data.pop(0)

    if (data_type == "start"):
        obstacles.clear()   # delete old obstacles
        points.clear()      # delete old points
        print("start package: " + str(data[0]))
        return "start"
    elif (data_type == "end"):
        print("end package: " + str(data[0]))
        return "end"

    if (data_type == "p"):
        points.append(Point(float(data[0]) * 1000.0, float(data[1]) * 1000.0, int(data[2])))
    elif (data_type == "l"):
        obstacles.append(Line(float(data[0]) * 1000.0, float(data[1]) * 1000.0, float(data[2]), float(data[3]), float(data[4]) * 1000000.0, float(data[5]) * 1000000.0, float(data[6]) * 1000.0, float(data[7]) * 1000.0))

    return "data"

'''
purpose: reading one whole package from serial port
return value: size of the package (int)
'''
def read_package():
    x = read()
    package_size = 0
    while "start" not in x:
        x = read()
    x = read()
    while "end" not in x:
        package_size += 1
        x = read()
    return package_size


'''
purpose: draw points into coordinate system (black circles)
return value: void
'''
def draw_points():
    for point in points:
        x = coo_sys_middle + (point.x / scale)
        y = coo_sys_middle - (point.y / scale)
        coo_sys.create_oval(x - point_radius, y - point_radius, x + point_radius, y + point_radius, fill = "black")
    print("#points drawn: " + str(len(points)))


def draw_lines():
    for line in obstacles:
        x0 = coo_sys_middle + ((line.cx + line.tmin * line.vx) / scale)
        y0 = coo_sys_middle - ((line.cy + line.tmin * line.vy) / scale)
        x1 = coo_sys_middle + ((line.cx + line.tmax * line.vx) / scale)
        y1 = coo_sys_middle - ((line.cy + line.tmax * line.vy) / scale)
        coo_sys.create_line(x0, y0, x1, y1, fill = "blue", width = 3)
        #print("" + str(x0) + " " + str(y0) + " " + str(x1) + " " + str(y1))
    print("#lines drawn: " + str(len(obstacles)))

'''
purpose: draw cluster into coordinate system (red lines)
return value: void
'''
def draw_cluster():
    for point in points:
        index = points.index(point)
        index_neighbor = index + 1
        if (index == points.index(points[-1])):
            index_neighbor = 0
        
        x_0 = coo_sys_middle + (point.x / scale)
        y_0 = coo_sys_middle - (point.y / scale)

        neighbor = points[index_neighbor]
        x_1 = coo_sys_middle + (neighbor.x / scale)
        y_1 = coo_sys_middle - (neighbor.y / scale)

        if (point.cluster == neighbor.cluster):
            coo_sys.create_line(x_0, y_0, x_1, y_1, fill = "red", width = 3)

'''
purpose: draw obstacles into coordinate system (blue lines)
return value: void
'''
def draw_obstacles():
    for obstacle in obstacles:
        x_0 = coo_sys_middle + (obstacle.lowest_x / scale)
        y_0 = coo_sys_middle - ((obstacle.lowest_x * obstacle.slope + obstacle.y_intercept) / scale)
        x_1 = coo_sys_middle + (obstacle.highest_x / scale)
        y_1 = coo_sys_middle - ((obstacle.highest_x * obstacle.slope + obstacle.y_intercept) / scale)
        coo_sys.create_line(x_0, y_0, x_1, y_1, fill = "blue", width = 3)
    #print("#obstacles drawn: " + str(len(obstacles)))

'''
purpose: drawing all components into window (sensor, reference lines, points, cluster, obstacles)
return value: void
'''
def draw():
    coo_sys.delete('all')
    # sensor
    coo_sys.create_rectangle(coo_sys_middle - 3, coo_sys_middle - 3, coo_sys_middle + 3, coo_sys_middle + 3, fill = "red")
    # reference lines (each meter)
    for i in range(6):
        radius = (i + 1) * 1000 / scale
        coo_sys.create_oval(coo_sys_middle - radius, coo_sys_middle - radius, coo_sys_middle + radius, coo_sys_middle + radius, width = 1, outline = "gray")

    draw_points()
    draw_lines()
    #draw_cluster()
    #draw_obstacles()


def update():
    package_size = read_package()
    #print("package size: " + str(package_size))
    draw()
    root.after(300, update)

root.after(1, update)
root.mainloop()


# plot
#plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-', linewidth=2)

# optional: plot centroid
#plt.scatter(cx, cy, color='blue')

#plt.axis('equal')
#plt.show()
