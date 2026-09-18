/*
 * Copyright (c) 2026 Tilmann Unte, Antonia Geßwein
 * SPDX-License-Identifier:  Apache-2.0
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "wcclibm.h"

#define ANGLE_COUNT		360		// amount of angles the sensor can measure
#define LOWEST_ANGLE		0
#define HIGHEST_ANGLE		(ANGLE_COUNT - 1)

#define GAP_THRESH		0.15f   // allowable gap between two points in the input set, technically this grows with distance from the sensor, but we use a simplified model
#define DIST_THRESH		0.08f   // allowable distance between a point and the current best-fit line when considering whether the point should join the cluster
#define LINEARITY_THRESH	0.02f   // How well is the cluster being represented by linear fit?
#define MIN_CLUSTER_SIZE	6	// How many points are required for a cluster to be recognized as such?

#define CLUSTER_ERR -1

#define PI 3.1415925026e+00f
#define EPSILON 1.0e-10f
#define HUGE 1.0e10f

#define SQUARED(x) ((x) * (x))

struct point {
	float x, y;
	int16_t cluster_id;
};

struct point_stats {
	float sum_x, sum_y;
	float sum_xx, sum_xy, sum_yy;
	int n;
};

struct line {
	// centroid
	float cx, cy;
	// eigenvector
	float vx, vy;
	// eigenvalue
	float l1, l2;
	// distance spanning projection
	float min, max;
};

struct cluster {
	size_t start_index;
	size_t size;
	struct line line;
};

struct obstacle_data {
	struct point points[ANGLE_COUNT];
	size_t point_count;

	struct cluster clusters[ANGLE_COUNT];
	size_t cluster_count;
};

int16_t distances[ANGLE_COUNT];
struct obstacle_data obstacle_data0;

static float angle_to_radians(uint16_t angle) {
    return (float) angle * PI / 180.0f;
}

static float sin_func(float x) {
    return basicmath___sinf(x);
}

static float cos_func(float x) {
    return basicmath___cosf(x);
}

static float sqrt_func(float a) {
    return basicmath___ieee754_sqrtf(a);
}

static float fabs_func(float a) {
	return basicmath___fabsf(a);
}

static void polar_to_cartesian(float offset, float rad, struct point* out_point)
{
	out_point->x = cos_func(rad) * offset;
	out_point->y = -sin_func(rad) * offset;
}

static int read_distances(int16_t* distances, struct point* points)
{
	uint16_t valid_input_count = 0;

	for (size_t i = 0; i < ANGLE_COUNT; i++) {
		if (distances[i] != 0) {
			polar_to_cartesian(((float) distances[i]) / 1000.0f, angle_to_radians(i), &points[valid_input_count]);
			points[valid_input_count].cluster_id = -1;
			valid_input_count++;
		}
	}

	// aiT may require annotation here. The worst-case path should follow a valid_input_count > 2
	if (valid_input_count > 2) {
		return valid_input_count;
	} else {
		return CLUSTER_ERR;
	}
}

static void point_stats_add(struct point_stats* stats, struct point* point)
{
	stats->sum_x += point->x;
	stats->sum_y += point->y;
	stats->sum_xx += SQUARED(point->x);
	stats->sum_xy += point->x * point->y;
	stats->sum_yy += SQUARED(point->y);
	stats->n++;
}

static void point_stats_subtract(struct point_stats* stats, struct point* point)
{
	stats->sum_x -= point->x;
	stats->sum_y -= point->y;
	stats->sum_xx -= SQUARED(point->x);
	stats->sum_xy -= point->x * point->y;
	stats->sum_yy -= SQUARED(point->y);
	stats->n--;
}

static void compute_pca_line(struct point_stats *stats, struct line *line)
{
	line->cx = stats->sum_x / stats->n;
	line->cy = stats->sum_y / stats->n;

	float cov_xx = stats->sum_xx / stats->n - SQUARED(line->cx);
	float cov_xy = stats->sum_xy / stats->n - line->cx * line->cy;
	float cov_yy = stats->sum_yy / stats->n - SQUARED(line->cy);

	// compute eigenvalues
	float trace = cov_xx + cov_yy;
	float det = cov_xx * cov_yy - SQUARED(cov_xy);
	float temp = trace * trace / 4.0f - det;
	temp = temp > 0.0f ? sqrt_func(temp) : 0.0f;

	line->l1 = trace / 2.0f + temp;
	line->l2 = trace / 2.0f - temp;

	// compute eigenvector for largest eigenvalue
	if (fabs_func(cov_xy) > EPSILON) {
		line->vx = line->l1 - cov_yy;
		line->vy = cov_xy;
	} else {
		line->vx = 1.0f;
		line->vy = 0.0f;
	}

	// normalize vector
	float norm = sqrt_func(SQUARED(line->vx) + SQUARED(line->vy));
	if (norm > 0.0f) {
		line->vx /= norm;
		line->vy /= norm;
	}
}

static float point_distance(struct point* a, struct point* b)
{
	return sqrt_func(SQUARED(b->x - a->x) + SQUARED(b->y - a->y));
}

static float point_line_distance(struct point* point, struct line* line)
{
	// determine normal vector
	float nx = -1.0f * line->vy;
	float ny = line->vx;

	return fabs_func((point->x - line->cx) * nx + (point->y - line->cy) * ny);
}

static int extract_lines(struct obstacle_data* data)
{
	int cluster = 0;

	for (int point = 0; point < data->point_count; point++) {
		// Has the current point already been clustered?
		if (data->points[point].cluster_id >= 0) continue;

		struct point_stats stats = {0};
		
		point_stats_add(&stats, &data->points[point]);
		int left_index = point, right_index = point;

		// Try out right neighbor
		if (point + 1 < data->point_count) {
			right_index = point + 1;
			point_stats_add(&stats, &data->points[right_index]);
		}

		// Grow right
		while (right_index + 1 < data->point_count) {
			int test_index = right_index + 1;

			if (data->points[test_index].cluster_id >= 0) break;

			float gap = point_distance(&data->points[right_index], &data->points[test_index]);
			if (gap > GAP_THRESH) break;
			
			point_stats_add(&stats, &data->points[test_index]);

			struct line line;
			compute_pca_line(&stats, &line);

			float ratio = line.l1 > 0.0f ? (line.l2 / line.l1) : 1.0f;
			float dist = point_line_distance(&data->points[test_index], &line);

			// Does the point still fit the current cluster?
			if (ratio > LINEARITY_THRESH || dist > DIST_THRESH) {
				point_stats_subtract(&stats, &data->points[test_index]);
				break;
			} else {
				right_index = test_index;
			}
		}

		// Grow left
		while (left_index - 1 >= 0) {
			int test_index = left_index - 1;

			if (data->points[test_index].cluster_id >= 0) break;

			float gap = point_distance(&data->points[left_index], &data->points[test_index]);
			if (gap > GAP_THRESH) break;

			point_stats_add(&stats, &data->points[test_index]);

			struct line line;
			compute_pca_line(&stats, &line);

			float ratio = line.l1 > 0.0f ? (line.l2 / line.l1) : 1.0f;
			float dist = point_line_distance(&data->points[test_index], &line);

			// Does the point still fit the current cluster?
			if (ratio > LINEARITY_THRESH || dist > DIST_THRESH) {
				point_stats_subtract(&stats, &data->points[test_index]);
				break;
			} else {
				left_index = test_index;
			}
		}

		int cluster_size = right_index - left_index + 1;

		if (cluster_size >= MIN_CLUSTER_SIZE) {
			/*for (int i = left_index; i <= right_index; i++) {
				data->points[i].cluster_id = cluster;
			}*/

			data->clusters[cluster].start_index = left_index;
			data->clusters[cluster].size = cluster_size;
			
			// We need to recompute the final line, as the final test point had to be removed from stats
			compute_pca_line(&stats, &data->clusters[cluster].line);

			// Determine line end points
			float min = HUGE, max = -HUGE;

			for (size_t i = data->clusters[cluster].start_index; i < data->clusters[cluster].start_index + data->clusters[cluster].size; i++) {
				data->points[i].cluster_id = cluster;

				float tx = data->points[i].x - data->clusters[cluster].line.cx;
				float ty = data->points[i].y - data->clusters[cluster].line.cy;

				float t = tx * data->clusters[cluster].line.vx + ty * data->clusters[cluster].line.vy;

				if (t < min) min = t;
				if (t > max) max = t;
			}

			data->clusters[cluster].line.min = min;
			data->clusters[cluster].line.max = max;

			cluster++;
		}
	}

	if (cluster > 0) {
		return cluster;
	} else {
		return CLUSTER_ERR;
	}
}

int calculate_obstacles(int16_t* distances, struct obstacle_data* data) {
	int ret = 0;

	ret = read_distances(distances, data->points);
	if (ret < 0) {
		return CLUSTER_ERR;
	} else {
		data->point_count = ret;

		ret = extract_lines(data);
		if (ret < 0) {
			return CLUSTER_ERR;
		} else {
			data->cluster_count = ret;
			return 0;
		}
	}
}

