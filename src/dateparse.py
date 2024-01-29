import os
import sys
import datetime
import re

from dateutil.parser import parse as dateparse


def extract_date_from_filename(filename):
    # Use regular expression to find the date pattern (YYYYMMDD)
    match = re.search(r"\d{8}", filename)
    if match:
        date_str = match.group(0)
        # Convert the string to datetime object
        return datetime.datetime.strptime(date_str, "%Y%m%d").date()
    else:
        return None  # or raise an exception if you prefer
