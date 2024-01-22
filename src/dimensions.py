import os
import numpy as np


def rectange_dimensions(original_dimension, percentage):
    """Returns a list of dimensions which from the origin compose the listed percentage of the photo"""
    total_pixels = original_dimension * original_dimension
    area_pixels = np.floor(percentage * total_pixels).astype(int)
    side_length = np.floor(area_pixels**0.5).astype(int)
    side_buffer = (original_dimension - side_length) // 2
    return [side_buffer, original_dimension - side_buffer]
