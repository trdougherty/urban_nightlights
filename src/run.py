import os
import sys
import argparse
import json

import numpy as np
import numpy.ma as ma
import pandas as pd

import rasterio
from rasterio.mask import mask

from src.dateparse import extract_date_from_filename
from src.geotiff_manager import GeoTiffManager
from src.cities_manager import CitiesManager

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--cities", type=str, default="cities.txt")
    parser.add_argument("--data_path", type=str, default="data")
    parser.add_argument("--n_rings", type=int, default=3)
    parser.add_argument("--geotiff_path", type=str, default="geotiff")
    parser.add_argument("--settings", type=str, default="settings.yml")
    parser.add_argument(
        "--import_epsg", type=int, default=4326
    )  # pseudo-mercator, which is in meters but not perfect for distance calculations
    parser.add_argument("--intermediate_epsg", type=int, default=3857)
    parser.add_argument("--buffer_size", type=int, default=25e3)
    parser.add_argument("--output", type=str, default="output.csv")
    parser.add_argument("--count_threshold", type=int, default=2)

    parser.add_argument("--monthly", action="store_true")
    parser.add_argument("--no-monthly", dest="monthly", action="store_false")
    parser.set_defaults(monthly=True)

    args = parser.parse_args()

    # 1. partition cities images from the geotiff files
    city_manager = CitiesManager(
        cities_path=args.cities,
        data_path=args.data_path,
        import_epsg=args.import_epsg,
        intermediate_epsg=args.intermediate_epsg,
        buffer_size=args.buffer_size,
        n_rings=args.n_rings,
    )

    # 2. now get the geotiff manager into it
    geotiff_manager = GeoTiffManager(
        geotiff_path=args.geotiff_path, monthly=args.monthly
    )

    radius_columns = [
        x for x in city_manager.geo_cities.columns if x.startswith("radius")
    ]

    unique_cities = city_manager.geo_cities.name.unique()
    aggregate_statistics = []

    for c, i in enumerate(geotiff_manager.geotiff_files):
        print("Processing Index: {} -\t {}".format(c, i))
        instance_date = extract_date_from_filename(i)
        instance_rad = rasterio.open(geotiff_manager.geotiff_files[c])
        instance_cfo = rasterio.open(geotiff_manager.cloudfreeobservations[c])

        for city in unique_cities:
            city_characteristics = city_manager.geo_cities[
                city_manager.geo_cities.name == city
            ]
            for radius_feature in radius_columns:
                city_radius = city_characteristics[radius_feature]
                out_image, out_transform = mask(instance_cfo, city_radius, crop=True)
                out_rad, out_radtransform = mask(instance_rad, city_radius, crop=True)

                m1 = np.ma.masked_equal(out_image, instance_cfo.nodata)
                base_pixels = (m1.data > 0).sum()

                if base_pixels <= 0:
                    percent_valid = None
                    valid_mean = None
                    mean_rad = None
                else:
                    ## to capture the mean number of samples per pixel
                    mvalid = np.ma.masked_greater_equal(m1, 1)
                    valid_mean = np.ma.mean(
                        np.ma.masked_array(out_image, mask=(~mvalid.mask))
                    )

                    m2 = np.ma.masked_greater_equal(m1, args.count_threshold)
                    percent_valid = ((m2.mask) > 0).sum() / base_pixels

                    # now I just have a regular numpy array to work with
                    output_rad = np.ma.masked_array(
                        out_rad, mask=(~m2.mask)
                    ).compressed()

                    try:
                        quantiles = np.quantile(output_rad, [0.25, 0.5, 0.75])
                        mean_rad = np.mean(output_rad)
                    except IndexError:
                        quantiles = (None, None, None)
                        mean_rad = None

                aggregate_statistics.append(
                    [
                        instance_date,
                        city,
                        radius_feature,
                        percent_valid,
                        valid_mean,
                        mean_rad,
                        quantiles[0],
                        quantiles[1],
                        quantiles[2],
                    ]
                )

                result = pd.DataFrame(
                    aggregate_statistics,
                    columns=[
                        "date",
                        "name",
                        "zone",
                        "coverage",
                        "mean_coverage_count",
                        "mean_rad",
                        "q25",
                        "q50",
                        "q75",
                    ],
                )

                result.to_csv(args.output, index=False, float_format="%.3f")

    # city_features = json.loads(city_manager.geo_cities.geometry.to_json())['features']
    # 3. now to combine them
    # print("Processing Buffer Size: {}".format(args.buffer_size))
    # for index, city_information in city_manager.geo_cities.iterrows():
    #     print("Processing Index: {} -\t {}".format(index, city_information["name"]))
    #     city_footprint = [city_features[index]["geometry"]]
    #     city_path = city_manager.cities_dir[city_information["name"]]

    #     city_image_path = os.path.join(city_path, "images")
    #     city_numpy_path = os.path.join(city_path, "numpy")

    #     if (not os.path.exists(city_image_path)) or (
    #         not os.path.exists(city_numpy_path)
    #     ):
    #         os.makedirs(city_image_path, exist_ok=True)
    #         os.makedirs(city_numpy_path, exist_ok=True)

    #         geotiff_manager.manage_images(
    #             city_footprint=city_footprint,
    #             output_dir=city_numpy_path,
    #             image_dir=city_image_path,
    #         )
