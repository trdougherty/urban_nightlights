import os
import sys

import numpy as np
import numpy.ma as ma
import copy

from src.dimensions import rectange_dimensions


def mask_statistics(image, mask):
    masked_data = ma.masked_array(image, ~mask)
    mask_median = ma.median(masked_data)
    mask_mean = ma.mean(masked_data)
    mask_std = ma.std(masked_data)

    return {"median": mask_median, "mean": mask_mean, "std": mask_std}


def build_masks(original_image):
    """Returns a copy of the original image with the mask applied"""
    assert original_image.shape[0] == original_image.shape[1]
    original_sidelength = original_image.shape[0]

    # Base Mask
    base_mask = np.zeros_like(original_image).astype(bool)

    # M0 - Core
    m0_boundaries = rectange_dimensions(original_sidelength, 1 / 3)
    m0x, m0y = m0_boundaries[0], m0_boundaries[1]
    m0 = copy.deepcopy(base_mask)
    m0[m0x:m0y, m0x:m0y] = True

    # M2 - Outer
    m2_boundaries = rectange_dimensions(original_sidelength, 2 / 3)
    m2x, m2y = m2_boundaries[0], m2_boundaries[1]
    m2 = copy.deepcopy(base_mask)
    m2[m2x:m2y, m2x:m2y] = True
    m2 = ~m2

    # M1 - Middle
    m1 = copy.deepcopy(base_mask)
    m1 = ~(m2 | m0)

    return {
        "m0": m0,
        "m1": m1,
        "m2": m2,
    }
