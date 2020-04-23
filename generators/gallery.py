import math
import requests
import json

from PIL import Image, ExifTags
from io import BytesIO

from datetime import datetime
from typing import Dict

from helpers.exif import generate_exif_dict


# Gather the following:
# - album name: album.name
# - date: datetime of first photo
# - URL, thumbnail URL of each photo
# - exif data for photo: have to download each thumbnail and read EXIF data
def generate_page(
    album: object, bucket_url: str, C: object
) -> str:
    first = None
    for image in album.images:
        image_url = bucket_url + image.key
        is_thumbnail = "_thumbs." in image_url.lower()

        if not is_thumbnail:
            continue

        image = populate_image_data(
            image, album, bucket_url, C
        )

        if not first:
            first = image

    return "1"


def populate_image_data(
    image: object, album: object, bucket_url: str, C: object
) -> object:
    r = requests.get(image_url)
    b = BytesIO(r.content)
    i = Image.open(b)
    exif = generate_exif_dict(i)

    # Populate image data
    image.url_thumbs = image_url
    image.url = root_url(image, bucket_url)

    # https://en.wikipedia.org/wiki/Mathematical_Alphanumeric_Symbols
    image.exif_data += f"{get_processed(exif, 'Model')} · "
    image.exif_data += (
        f"{get_processed(exif, 'FocalLength')} · "
    )
    image.exif_data += f"{get_processed(exif, 'FNumber').replace('f', 'ƒ')} · "
    image.exif_data += (
        f"{get_processed(exif, 'ExposureTime')}𝙨 · "
    )

    image.exif_data_2 += f"{human_datetime(get_processed(exif, 'DateTimeOriginal'))}"

    # Lowercase because we're chill
    image.exif_data = image.exif_data.lower()
    image.exif_data_2 = image.exif_data_2.lower()

    # Add ISO last to stay capitalized
    image.exif_data += (
        f"{get_processed(exif, 'ISOSpeedRatings')}ISO"
    )

    return image


def get_processed(exif: Dict, key: str) -> str:
    return exif[key]["processed"]


# month as text
# number as *th or *st or *2nd
# time
def human_datetime(dt: datetime) -> str:
    ordinal = lambda n: "%d%s" % (
        n,
        "tsnrhtdd"[
            (math.floor(n / 10) % 10 != 1)
            * (n % 10 < 4)
            * n
            % 10 :: 4
        ],
    )
    month = dt.strftime("%B")
    day = dt.strftime("%d")
    day = ordinal(int(day.lstrip("0")))
    time = dt.strftime("%H:%M")
    year = dt.strftime("%Y")

    fancy_date = f"{month} {day} {time}, {year}"
    return fancy_date


def root_url(image: object, bucket_url: str) -> str:
    filename, ext = image.key.split(".")
    return f"{bucket_url}{filename.replace('_thumbs', '')}.{ext}"
