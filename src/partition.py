import os
import numpy as np
import numpy.ma as ma
import copy
import pandas as pd

from datetime import datetime
import re

from src.masks import mask_statistics, build_masks


def batch_statistics(images_directory):
    """Returns a dataframe of mask statistics for each image in the list of image filepaths"""
    cities = os.listdir(images_directory)

    prototype_city = cities[0]
    prototype_city_directory = os.path.join(
        images_directory, prototype_city, "postprocessed_numpy"
    )

    prototype_filepaths = os.listdir(prototype_city_directory)
    prototype_image = np.load(
        os.path.join(prototype_city_directory, prototype_filepaths[0])
    ).squeeze()

    assert prototype_image.shape[0] == prototype_image.shape[1]
    original_sidelength = prototype_image.shape[0]
    masks = build_masks(prototype_image)

    pd_dictionaries = []
    for city in cities:
        city_directory = os.path.join(images_directory, city, "postprocessed_numpy")
        city_filepaths = os.listdir(city_directory)

        for city_file in city_filepaths:
            image_filepath = os.path.join(city_directory, city_file)
            timestamp_match = re.search(r"(\d{8})-\d{8}", image_filepath)
            timestamp = timestamp_match.group(1) if timestamp_match else None
            parsed_timestamp = (
                datetime.strptime(timestamp, "%Y%m%d") if timestamp else None
            )

            original_image = np.load(image_filepath).squeeze()

            for mask_key in masks.keys():
                mask = masks[mask_key]
                mask_features = mask_statistics(original_image, mask)

                for mask_feature_key in mask_features.keys():
                    pd_dictionaries.append(
                        {
                            "City": city,
                            "Date": parsed_timestamp,
                            "Mask": mask_key,
                            "Statistic": mask_feature_key,
                            "Value": mask_features[mask_feature_key],
                        }
                    )

    batched_data = pd.DataFrame(pd_dictionaries)
    # batched_data.set_index("Date", inplace=True)
    return batched_data


# def build_masked_image(original_image):
#     """Returns a copy of the original image with the mask applied"""
#     base_mask = np.ones_like(original_image)
#     masked_image = original_image.copy()
#     masked_image[mask] = 0
#     return masked_image

# def build_masks(image, n_masks):
#     mask_spacings = np.linspace(0,1,n_masks+2)[1:-1]

#     for mask_spacing in mask_spacings:
#         mask = np.ones_like(image)
#         mask[rectange_dimensions(image.shape[0], mask_spacing)[0]:rectange_dimensions(image.shape[0], mask_spacing)[1],
#              rectange_dimensions(image.shape[0], mask_spacing)[0]:rectange_dimensions(image.shape[0], mask_spacing)[1]] = 1
#         yield mask
