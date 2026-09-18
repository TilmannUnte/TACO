# Copyright (c) 2025-2026 Tilmann Unte, Antonia Geßwein
# SPDX-License-Identifier:  Apache-2.0

import math
from scipy.spatial import ConvexHull, convex_hull_plot_2d
import numpy as np
import matplotlib.pyplot as plt

def gen_circle(distance):
	output = []
	for i in range (360):
		output.append(distance)
	return output
	
def gen_circles():
	output = []
	# high precision area
	i = 0.15
	while(i < 1.5):
		output.append(gen_circle(i))
		i = i + 0.00005
	# lower precision area
	i = 1.5
	while (i < 12.0):
		i = i * 1.01
		output.append(gen_circle(i))
	return output

def print_as_csv(inputs):
	for input in inputs:
		i = 0.0
		for sample in input:
			print(str(i) + ":" + str(sample) + ",", sep="", end="")
			i = i + 1.0
		print("\n", end="")
		
legal_values = []

def gen_legal_values():
	i = 0.15
	while(i < 1.5):
		legal_values.append(i)
		i = i + 0.00005
	i = 1.5
	while (i < 12.0):
		i = i * 1.01
		legal_values.append(i)
	
gen_legal_values()

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)


def gen_random_full_rotation():
	rng = np.random.default_rng()
	dists = rng.choice(legal_values,4)
	start_list = [(0,0)]
	for i in range(4):
		start_list.append(pol2cart(dists[i], i * math.pi / 2))
	
	dt = np.dtype('float64')
	start_array = np.array(start_list, dtype=dt)
	hull = ConvexHull(start_array, incremental=True, qhull_options='QG0')
	#print(hull.good)
	while (len(hull.vertices) <= 360):
		dist = rng.choice(legal_values)
		point = [pol2cart(dist,math.radians(rng.random() * 360))]
		hull_point_array = np.array(point, dtype=dt)
		try:
			hull.add_points(hull_point_array)
			start_list.append(point)
		except QhullError:
			pass
	
	print(hull.good)
	plt.plot(hull.points[:,0], hull.points[:,1], 'o')
	for simplex in hull.simplices:
		plt.plot(hull.points[simplex, 0], hull.points[simplex, 1], 'k-')
	
	plt.plot(hull.points[hull.vertices,0], hull.points[hull.vertices,1], 'r--', lw=2)
	plt.plot(hull.points[hull.vertices[0],0], hull.points[hull.vertices[0],1], 'ro')
	plt.show()
	
gen_random_full_rotation()
