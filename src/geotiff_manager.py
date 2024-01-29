from ctypes import Union
import os
import glob
import numpy as np
from pathlib import Path
import rasterio
from rasterio.mask import mask
from PIL import Image
import PIL

from typing import Union


class GeoTiffManager:
    def __init__(
        self,
        geotiff_path: str,
        import_epsg: int = 4326,
        intermediate_epsg: int = 3857,
        monthly: bool = True,
    ) -> None:
        self.import_epsg = import_epsg
        self.intermediate_epsg = intermediate_epsg
        self.cloudfreeobservations = []
        if monthly:
            self.geotiff_files = sorted(
                glob.glob(os.path.join(geotiff_path, "*_rade9h.tif"))
            )
            self.cloudfreeobservations = sorted(
                glob.glob(os.path.join(geotiff_path, "*cf_cvg.tif"))
            )
        else:
            self.geotiff_files = glob.glob(os.path.join(geotiff_path, "*.tif"))

    def manage_images(
        self, city_footprint: str, output_dir: str, image_dir: Union[str, None] = None
    ):
        for geotiff_file in self.geotiff_files:
            filename = Path(geotiff_file).stem
            numpy_filename = os.path.join(output_dir, filename)
            numpy_arr = self.extract_image(city_footprint, geotiff_file)
            self.save_numpy(numpy_arr, numpy_filename)
            if image_dir is not None:
                image_filename = os.path.join(image_dir, filename) + ".png"
                self.save_image(numpy_arr, image_filename)

    def save_numpy(self, image, save_path):
        np.save(save_path, image)

    def extract_image(self, city_footprint, geotiff):
        nightlight_geotiff = rasterio.open(geotiff)
        out_img, output_transform = mask(
            nightlight_geotiff, shapes=city_footprint, crop=True
        )
        return out_img.squeeze()

    def save_image(self, image, image_save_path):
        temp_im = image.clip(0, 65)
        im = Image.fromarray(np.uint8(temp_im * 3.9), "L")
        im = im.resize((512, 512), resample=Image.NEAREST)
        im.save(image_save_path)
