# Copyright (c) 2025-2026 Tilmann Unte, Antonia Geßwein
# SPDX-License-Identifier:  Apache-2.0

import csv
import math
import random
from typing import List

MIN_DIST = 150
MAX_DIST = 12000
ANGLES = list(range(360))


def clamp(x, lo=MIN_DIST, hi=MAX_DIST):
    return max(lo, min(hi, int(x)))


def threshold_jitter(base=3000, jitter=80, period=2):
    """
    Alternates distances around a threshold to trigger frequent segment breaks.
    """
    scan = []
    for i, a in enumerate(ANGLES):
        sign = 1 if (i // period) % 2 == 0 else -1
        d = base + sign * jitter + random.uniform(-10, 10)
        scan.append(clamp(d))
    return scan


def noisy_wall(base=4000, noise_amp=200):
    """
    Long wall with perpendicular noise -> large segments + unstable PCA.
    """
    scan = []
    for a in ANGLES:
        # simulate a slightly curved wall + noise
        curvature = 300 * math.sin(math.radians(a * 2))
        noise = random.uniform(-noise_amp, noise_amp)
        d = base + curvature + noise
        scan.append(clamp(d))
    return scan


def zigzag(amplitude=600, base=3500, freq=12):
    """
    Sawtooth-like pattern to force repeated direction changes.
    """
    scan = []
    for a in ANGLES:
        phase = (a % freq) / freq
        saw = (2 * phase - 1)  # -1 to 1
        d = base + amplitude * saw + random.uniform(-50, 50)
        scan.append(clamp(d))
    return scan


def dense_clutter(base=2500, gap_prob=0.15):
    """
    Many small objects with borderline separations.
    """
    scan = []
    for a in ANGLES:
        if random.random() < gap_prob:
            # simulate a gap just over threshold
            d = base + random.uniform(400, 800)
        else:
            # object cluster
            d = base + random.uniform(-150, 150)
        scan.append(clamp(d))
    return scan


def mixed():
    """
    Combine multiple adversarial patterns across angular sectors.
    """
    scan = [0] * 360

    parts = [
        (0, 90, threshold_jitter()),
        (90, 180, noisy_wall()),
        (180, 270, zigzag()),
        (270, 360, dense_clutter()),
    ]

    for start, end, segment in parts:
        for a in range(start, end):
            scan[a] = segment[a]

    return scan


def format_scan(scan: List[int]) -> List[str]:
    return [f"{angle}:{dist}" for angle, dist in zip(ANGLES, scan)]


def generate_file(filename, mode="mixed", n_scans=100):
    generators = {
        "threshold_jitter": threshold_jitter,
        "noisy_wall": noisy_wall,
        "zigzag": zigzag,
        "dense_clutter": dense_clutter,
        "mixed": mixed,
    }

    gen = generators[mode]

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        for _ in range(n_scans):
            scan = gen()
            writer.writerow(format_scan(scan))


if __name__ == "__main__":
    # Generate example datasets
    generate_file("worst-mixed-0.csv", mode="mixed", n_scans=200)
    generate_file("threshold-jitter-0.csv", mode="threshold_jitter", n_scans=200)
    generate_file("noisy-wall-0.csv", mode="noisy_wall", n_scans=200)
    generate_file("zigzag-0.csv", mode="zigzag", n_scans=200)
    generate_file("dense-clutter-0.csv", mode="dense_clutter", n_scans=200)
