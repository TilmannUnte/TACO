# Copyright (c) 2025-2026 Tilmann Unte, Antonia Geßwein
# SPDX-License-Identifier:  Apache-2.0

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import ceil, floor, log10

import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report

from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
from factor_analyzer.factor_analyzer import calculate_kmo

import scienceplots

plt.style.use(['science'])

# color-blind friendly palette, from cold to warm-toned, color names are "close enough" guesses
# navy, sky, teal, forest, mustard, dandelion, fuchsia, purple, lilac, pink, rust, carrot
colorsGlobal = ['#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499', '#EE3377', '#CC3311', '#EE7733']

# various gray tones
colorMisc =  ['#DDDDDD']
colorMisc2 =   ['#BBBBBB']
colorMisc3 = ['#111111']

df = pd.read_csv('new-measurements-O0.csv', on_bad_lines='warn', sep=';')

def pdfRealDataExecTime(df):
	RealData = df[df['SNIPPET'].str.contains("testrun")]
	RealData = RealData[~RealData['SNIPPET'].str.contains("synthetic")]
	NoiseData = RealData[RealData['SNIPPET'].str.contains("8-")]["CYCLES"]
	QualData = RealData[~RealData['SNIPPET'].str.contains("8-")]["CYCLES"]
	
	max_cycles = max(RealData["CYCLES"])
	category_size = 10000
	category_amount = ceil(max_cycles / category_size)
	noise_amount = np.zeros(category_amount, dtype=int)
	qual_amount  = np.zeros(category_amount, dtype=int)
	
	# Count NoiseData
	for cycle in NoiseData:
		cat = floor(cycle / category_size)
		noise_amount[cat] += 1

	# Count QualData
	for cycle in QualData:
		cat = floor(cycle / category_size)
		qual_amount[cat] += 1
	
	plt.rcParams["figure.figsize"] = (4.80315,  3.84252)
	x = range(category_amount)

	plt.bar(x, noise_amount, color=colorsGlobal[-1], label="Continuous")
	plt.bar(x, qual_amount, color=colorsGlobal[1], bottom=noise_amount, label="Intermittent")
	plt.xlabel('Execution Time in Millions of Cycles, Quantized to Multiples of 10000', size=10)
	plt.ylabel('Number of Input Samples', size=10)
	plt.legend()
	locs, labels = plt.xticks()
	print(locs)
	plt.xticks(np.delete(locs, 0), ['0', '0.25', '0.5', '0.75', '1.0', '1.25', '1.5', '1.75'])
	#plt.show()
	plt.savefig("measured_real_exec_times.pdf", bbox_inches="tight")

def pdfSynthDataExecTime(df):
	circle = df[df['SNIPPET'].str.contains("synthetic")]
	denseClutter = df[df['SNIPPET'].str.contains("dense-clutter")]
	noisyWall = df[df['SNIPPET'].str.contains("noisy-wall")]
	thresholdJitter = df[df['SNIPPET'].str.contains("threshold-jitter")]
	zigzag = df[df['SNIPPET'].str.contains("zigzag")]

	max_cycles = -1
	max_cycles = max(max_cycles, max(circle["CYCLES"]))
	max_cycles = max(max_cycles, max(denseClutter["CYCLES"]))
	max_cycles = max(max_cycles, max(noisyWall["CYCLES"]))
	max_cycles = max(max_cycles, max(thresholdJitter["CYCLES"]))
	max_cycles = max(max_cycles, max(zigzag["CYCLES"]))

	category_size = 10000
	category_amount = ceil(max_cycles / category_size)
	circle_amount = np.zeros(category_amount, dtype=int)
	denseClutter_amount  = np.zeros(category_amount, dtype=int)
	noisyWall_amount  = np.zeros(category_amount, dtype=int)
	thresholdJitter_amount  = np.zeros(category_amount, dtype=int)
	zigzag_amount  = np.zeros(category_amount, dtype=int)
	
	for cycle in circle["CYCLES"]:
		cat = floor(cycle / category_size)
		circle_amount[cat] += 1

	for cycle in denseClutter["CYCLES"]:
		cat = floor(cycle / category_size)
		denseClutter_amount[cat] += 1

	for cycle in noisyWall["CYCLES"]:
		cat = floor(cycle / category_size)
		noisyWall_amount[cat] += 1

	for cycle in thresholdJitter["CYCLES"]:
		cat = floor(cycle / category_size)
		thresholdJitter_amount[cat] += 1

	for cycle in zigzag["CYCLES"]:
		cat = floor(cycle / category_size)
		zigzag_amount[cat] += 1

	
	plt.rcParams["figure.figsize"] = (4.80315,  3.84252)
	x = range(category_amount)

	plt.bar(x, circle_amount, color=colorsGlobal[0], label="Conc. Circle")
	plt.bar(x, thresholdJitter_amount, color=colorsGlobal[3], bottom=circle_amount, label="Thresh. Jitter")
	plt.bar(x, zigzag_amount, color=colorsGlobal[8], bottom=thresholdJitter_amount, label="Zig Zag")
	plt.bar(x, noisyWall_amount, color=colorsGlobal[9], bottom=zigzag_amount, label="Noisy Wall")
	plt.bar(x, denseClutter_amount, color=colorsGlobal[10], bottom=noisyWall_amount, label="Dense Clutter")

	plt.xlim(100, 350)	

	plt.xlabel('Execution Time in Millions of Cycles, Quantized to Multiples of 10000', size=10)
	plt.ylabel('Number of Input Samples', size=10)
	plt.legend()
	locs, labels = plt.xticks()
	print(locs)
	#print(np.delete(locs, [0,1,2]))
	plt.xticks(locs, ['1.0', '1.5', '2.0', '2.5', '3.0', '3.5'])
	#plt.show()
	plt.savefig("measured_synth_exec_times.pdf", bbox_inches="tight")
	
def pdfRealDataCorrelation(df):
	RealData = df[df['SNIPPET'].str.contains("testrun")]
	RealData = RealData[~RealData['SNIPPET'].str.contains("synthetic")]
	NoiseData = RealData[RealData['SNIPPET'].str.contains("8-")]
	QualData = RealData[~RealData['SNIPPET'].str.contains("8-")]
	rd = QualData

	clean_rd = rd.drop(["SNIPPET", "INDEX"], axis=1)
	X = clean_rd.drop("CYCLES", axis=1)
	y = clean_rd["CYCLES"]
	
	scaler = StandardScaler()
	
	X_factor = scaler.fit_transform(X)
	dfed_X = X.reset_index()
	dfed_X_columns = dfed_X.columns.tolist()
	dfed_X_columns.pop(0)
	rd_factor = pd.DataFrame(data=X_factor, columns=dfed_X_columns)
	print(rd_factor)
	
	dfed_y = y.reset_index()
	dfed_y_columns = dfed_y.columns.tolist()
	dfed_y_columns.pop(0)
	
	rd_factor['CYCLES'] = y
	
	print(rd_factor.corr()["CYCLES"])
	plt.rcParams["figure.figsize"] = (4.80315,  3.2021)
	sns.heatmap(rd_factor.corr(), annot=True, cmap="coolwarm")
	plt.savefig("measured_real_correlation.pdf")
	
def pdfRealDistExecTime(df):
	RealData = df[df['SNIPPET'].str.contains("testrun")]
	RealData = RealData[~RealData['SNIPPET'].str.contains("synthetic")]
	NoiseData = RealData[RealData['SNIPPET'].str.contains("8-")]
	QualData = RealData[~RealData['SNIPPET'].str.contains("8-")]
	RealObstDistTime = QualData.drop(["SNIPPET","INDEX"], axis=1)
	
	plt.rcParams["figure.figsize"] = (4.80315,  3.84252/2.167)
	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()
	ax1.scatter(x = RealObstDistTime["CYCLES"].map(lambda x: floor(x/10000)),y = RealObstDistTime["POINTS"], c = "b", marker = "o", alpha=0.5)
	ax2.scatter(x = RealObstDistTime["CYCLES"].map(lambda x: floor(x/10000)), y = RealObstDistTime["OBSTACLES"], c = "r", marker = "*", alpha=0.5)
	#ax1.set_xticks([0, 20, 40, 60, 80, 100, 120], ["0", "0.2", "0.4", "0.6", "0.8", "1.0", "1.2"])
	#ax1.set_yticks([0, 1000, 2000, 3000, 4000, 5000], ["0", "1", "2", "3", "4", "5"])
	ax1.set_ylabel('Amount of Points in Sweep', size=10, c="b")
	ax1.set_xlabel('Execution Time in Millions of Cycles', size=10)
	ax2.set_ylabel('Amount of Obstacles Detected', size=10, color="r")
	#plt.show()
	plt.savefig("real_dist_obst_time.pdf", bbox_inches="tight")

def pdfCircleDistExecTime(df):
	circleObstDistTime = df.query('`SNIPPET` == "synthetic-0" or `SNIPPET` == "synthetic-10" or `SNIPPET` == "synthetic-20" or `SNIPPET` == "synthetic-30" or `SNIPPET` == "synthetic-40" or `SNIPPET` == "synthetic-50" or `SNIPPET` == "synthetic-60" or `SNIPPET` == "synthetic-70" or `SNIPPET` == "synthetic-80" or `SNIPPET` == "synthetic-90" or `SNIPPET` == "synthetic-100" or `SNIPPET` == "synthetic-110" or `SNIPPET` == "synthetic-120" or `SNIPPET` == "synthetic-130" or `SNIPPET` == "synthetic-135" or `SNIPPET` == "synthetic-136"').drop(["SNIPPET","SNIPPET_INDEX","CSV_DATASET","TOTAL","ZEROES","VALID","MAX","MIN"], axis=1)
	
	plt.rcParams["figure.figsize"] = (4.80315,  3.84252)
	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()
	ax1.scatter(x = circleObstDistTime["CYCLES"].map(lambda x: floor(x/10000)),y = circleObstDistTime["AVG"], c = "b", marker = "o", alpha=0.5)
	ax2.scatter(x = circleObstDistTime["CYCLES"].map(lambda x: floor(x/10000)), y = circleObstDistTime["OBSTACLES"], c = "r", marker = "*", alpha=0.5)
	ax1.set_xticks([0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260], ["0", "0.2", "0.4", "0.6", "0.8", "1.0", "1.2", "1.4", "1.6", "1.8", "2.0", "2.2", "2.4", "2.6"])
	ax1.set_yticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000], ["0", "", "2", "", "4", "", "6", "", "8", "", "10", "", "12"])
	ax1.set_ylabel('Circle Radius in Meters', size=10, c="b")
	ax1.set_xlabel('Execution Time in Millions of Cycles', size=10)
	ax2.set_ylabel('Amount of Obstacles Detected', size=10, color="r")
	#plt.show()
	plt.savefig("sythetic_circle_dist_obst_time.pdf", bbox_inches="tight")
	
def pdfAllExecTime(df):
	RealData = df[df['SNIPPET'].str.contains("testrun")]
	RealData = RealData[~RealData['SNIPPET'].str.contains("synthetic")]
	NoiseData = RealData[RealData['SNIPPET'].str.contains("8-")]["CYCLES"]
	QualData = RealData[~RealData['SNIPPET'].str.contains("8-")]["CYCLES"]
	
	max_cycles = max(RealData["CYCLES"])
	category_size = 10000
	category_amount = ceil(max_cycles / category_size)
	noise_amount = np.zeros(category_amount, dtype=int)
	qual_amount  = np.zeros(category_amount, dtype=int)
	
	# Count NoiseData
	for cycle in NoiseData:
		cat = floor(cycle / category_size)
		noise_amount[cat] += 1

	# Count QualData
	for cycle in QualData:
		cat = floor(cycle / category_size)
		qual_amount[cat] += 1

	x = range(category_amount)
	
	plt.rcParams["figure.figsize"] = (4.80315,  3.84252/2.375)
	plt.bar(x, noise_amount, color=colorsGlobal[-1], label="Continuous")
	plt.bar(x, qual_amount, color=colorsGlobal[1], bottom=noise_amount, label="Intermittent")
	plt.xlabel('Execution Time in Millions of Cycles, Quantized to Multiples of 10000', size=10)
	plt.ylabel('Number of Input Samples', size=10)
	print(str(ceil(max_cycles/category_size)) + " " +  str(ceil(3059656 / category_size)))
	plt.axvline(x = ceil(max_cycles/category_size), c = "r", linestyle = "solid", label="Observed WCET")
	plt.text(ceil(max_cycles/category_size)+3,10,'Observed WCET',rotation=90, c = "r")
	plt.axvline(x = ceil(max_cycles/category_size)*1.2, c = "g", linestyle = "dashed", label="Obs. WCET+20%")
	plt.text(ceil(max_cycles/category_size)*1.2+3,10,'Obs. WCET+20\\%',rotation=90, c = "g")
	plt.axvline(x = ceil(3059656 / category_size), c = "black", linestyle = "dotted", label="Synthetic WCET")
	plt.text(ceil(3059656 / category_size)+3,10,'Synthetic WCET',rotation=90, c = "black")

	locs, labels = plt.xticks()
	print(locs)
	plt.xticks(np.delete(locs, 0), ['0', '0.5', '1.0', '1.5', '2.0', '2.5', '3.0', '3.5'])
	#plt.show()
	plt.savefig("all_exec_times.pdf", bbox_inches="tight")
	
#pdfRealDataExecTime(df)
#pdfSynthDataExecTime(df)
#pdfRealDataCorrelation(df)
#pdfRealDistExecTime(df)
#pdfCircleDistExecTime(df)
pdfAllExecTime(df)

