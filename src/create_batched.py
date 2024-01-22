import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma

import pandas as pd
import copy
import os

from src.masks import build_masks, mask_statistics
from src.partition import batch_statistics

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--images_base")
parser.add_argument("--output_file")

args = parser.parse_args()

print(args)
batched = batch_statistics(args.images_base)
batched.to_csv(args.output_file, index=False)
