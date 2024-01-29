import os
import numpy as np
import pandas as pd
import geopandas as gpd

from pyproj import CRS

from src.projection_estimation import (
    determine_utm_zone,
    point_to_utm,
    transform_geometry,
)

from src.zone_partition import radius_compute, rings_shapes


class CitiesManager:
    def __init__(
        self,
        cities_path: str,
        data_path: str,
        buffer_size: int = 25e3,
        n_rings: int = 3,
        import_epsg: int = 4326,
        intermediate_epsg: int = 3857,
    ) -> None:
        self.import_epsg = import_epsg
        self.intermediate_epsg = intermediate_epsg
        self.n_rings = n_rings
        self.base_crs = CRS(f"EPSG:{self.import_epsg}")

        self.buffer_size = buffer_size
        self.cities_path = cities_path
        self.cities = pd.read_csv(self.cities_path, quotechar="'")
        self.geo_cities = self.geo_dataframe(buffer_size=self.buffer_size)

        self.cities_dir: dict = {}
        self.data_path = data_path
        self.generate_directory()

    def geo_dataframe(self, buffer_size: 25e3) -> gpd.GeoDataFrame:
        geo_cities = gpd.GeoDataFrame(
            self.cities,
            geometry=gpd.points_from_xy(self.cities.longitude, self.cities.latitude),
            crs=self.import_epsg,
        )

        geometries_list = []
        for geometry in geo_cities.geometry:
            specific_geometry = []
            utm_point, utm_crs = point_to_utm(geometry)
            radius_list = radius_compute(buffer_size, self.n_rings)
            rings = rings_shapes(utm_point, radius_list)
            for ring in rings:
                specific_geometry.append(
                    transform_geometry(ring, utm_crs, self.base_crs)
                )

            geometries_list.append(specific_geometry)

        transposed_geometries = list(map(list, zip(*geometries_list)))

        # Convert each transposed sublist into a GeoSeries
        geo_series_list = [
            gpd.GeoSeries(sublist, crs=self.base_crs)
            for sublist in transposed_geometries
        ]

        # Create a GeoDataFrame from the GeoSeries
        geo_df = gpd.GeoDataFrame(
            {f"radius{i}": geo_series for i, geo_series in enumerate(geo_series_list)}
        )

        return geo_cities.join(geo_df)

    def generate_directory(self) -> None:
        os.makedirs(self.data_path, exist_ok=True)
        for _, city in self.cities.iterrows():
            city_name = city["name"]
            city_path = os.path.join(self.data_path, city_name)
            self.cities_dir[city_name] = city_path
            os.makedirs(city_path, exist_ok=True)
