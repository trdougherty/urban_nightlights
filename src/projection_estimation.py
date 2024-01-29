import os
import sys

from shapely.geometry import Point
from shapely.ops import transform as shapely_transform
import math
from pyproj import Proj, transform, Transformer, CRS


def determine_utm_zone(longitude):
    return math.floor((longitude + 180) / 6) + 1


def point_to_utm(point):
    """
    Converts a Shapely Point in EPSG 4326 to its correct UTM zone.
    :param point: Shapely Point in EPSG 4326 (longitude, latitude)
    :return: Shapely Point in the correct UTM zone, UTM projection
    """
    utm_zone = determine_utm_zone(point.x)
    hemisphere = "north" if point.y >= 0 else "south"
    utm_crs = CRS(
        f"+proj=utm +zone={utm_zone} +{hemisphere} +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
    )

    wgs84_crs = CRS("EPSG:4326")
    transformer = Transformer.from_crs(wgs84_crs, utm_crs, always_xy=True)
    utm_point = transformer.transform(point.x, point.y)
    return Point(utm_point), utm_crs


def transform_geometry(geom, src_crs, dest_crs):
    """
    Transform a Shapely geometry from src_crs to dest_crs.
    """
    transformer = Transformer.from_crs(src_crs, dest_crs, always_xy=True)
    return shapely_transform(transformer.transform, geom)
