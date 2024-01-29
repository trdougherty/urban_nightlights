import os
import sys

from shapely.geometry import Point


def radius_compute(radius: float, n_rings: int) -> list:
    """Computes the radius terms for equivalent area regions"""
    rings = []
    for i in range(1, n_rings + 1):
        rings.append((i / n_rings) ** 0.5 * radius)

    return rings


def rings_shapes(point, radius_list: list) -> list:
    """Computes the rings for equivalent area regions"""
    rings = [point.buffer(radius_list[0])]
    for c, i in enumerate(radius_list[1:], start=1):
        rings.append(
            point.buffer(radius_list[c]).difference(point.buffer(radius_list[c - 1]))
        )

    return rings
