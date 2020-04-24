import math
import requests
import json

from random import choice
from os import listdir, path, makedirs
from os.path import isfile, join

from PIL import Image, ExifTags
from io import BytesIO

from datetime import datetime
from typing import Dict

from generators import gallery_templates
from helpers.exif import generate_exif_dict


# Gather the following:
# - album name: album.name
# - date: datetime of first photo
# - URL, thumbnail URL of each photo
# - exif data for photo: have to download each thumbnail and read EXIF data
def generate_page(
    album: object,
    bucket_url: str,
    C: object,
    logger: object,
) -> str:
    first = None
    images = []
    count = 0
    logger.info(
        f"Generating gallery for [album={album.name}] with {len(album.images)} images"
    )
    cache = get_cache(C.CACHE)

    for image in album.images:
        image_url = bucket_url + image.key
        is_thumbnail = "_thumbs." in image_url.lower()

        if not is_thumbnail:
            continue

        logger.info(f"{image.name} started processing.")

        date, date_pretty = populate_image_data(
            image, album, bucket_url, C, cache, logger
        )

        # Set our album info to our first image
        if not first:
            album.date = date
            album.date_pretty = date_pretty
            first = image

        # Construct HTML for image
        t = gallery_templates.image[:]
        t = t.replace("$URL_THUMBS", image.url_thumbs)
        t = t.replace("$URL", image.url)
        t = t.replace("$EXIF_DATA", image.exif_data)
        t = t.replace("$DATE_PRETTY", image.date_pretty)
        t = t.replace(
            "$IMAGE_NAME", remove_thumbs_str(image.name)
        )

        images.append(t)

        logger.info(f"{image.name} finished processing.")

    # Constructing page
    frontmatter = gallery_templates.frontmatter[:]
    frontmatter = frontmatter.replace(
        "$TITLE", album.name.lower()
    )
    frontmatter = frontmatter.replace(
        "$DATE", str(album.date)
    )

    # Pick a random image for our cover.
    # Keeps things interesting for me!
    frontmatter = frontmatter.replace(
        "$COVER_URL",
        choice(
            list(
                filter(
                    lambda x: "_thumbs" in x.name,
                    album.images,
                )
            )
        ).url_thumbs,
    )
    frontmatter = frontmatter.replace(
        "$IMAGE_COUNT", f"{len(images)} images"
    )

    body = gallery_templates.body[:]
    body = body.replace("$IMAGES", "\n".join(images))

    return f"{frontmatter}\n{body}\n{gallery_templates.footer[:]}"


def populate_image_data(
    image: object,
    album: object,
    bucket_url: str,
    C: object,
    cache: Dict,
    logger: object,
) -> object:
    # Get image URLs
    image_url = bucket_url + image.key
    image.url_thumbs = image_url
    image.url = root_url(image, bucket_url)

    # Get exif data
    exif = get_image_and_cache(image, cache, C, logger)

    # Check if image had exif data
    if exif:
        # https://en.wikipedia.org/wiki/Mathematical_Alphanumeric_Symbols
        image.exif_data += f"{get_processed(exif, 'Model')} · "
        image.exif_data += (
            f"{get_processed(exif, 'FocalLength')} · "
        )
        image.exif_data += f"{get_processed(exif, 'FNumber').replace('f', 'ƒ')} · "
        image.exif_data += (
            f"{get_processed(exif, 'ExposureTime')}𝗌 · "
        )

        image.date = get_processed(exif, "DateTimeOriginal")
        image.date_pretty += f"{human_datetime(get_processed(exif, 'DateTimeOriginal'))}"

        # Lowercase because we're chill
        image.exif_data = image.exif_data.lower()
        image.date_pretty = image.date_pretty.lower()

        # Add ISO last to stay capitalized
        image.exif_data += (
            f"ISO{get_processed(exif, 'ISOSpeedRatings')}"
        )
    else:
        image.exif_data = "unknown · unknown · unknown"
        image.date_pretty = "unknown, unknown"

    return image.date, image.date_pretty


# Map of get_cached_key(image.name) to cachedir
def get_cache(cachedir: str) -> Dict:
    cache = {}
    # Create cache directory if it doesn't exist already
    if not path.exists(cachedir):
        makedirs(cachedir)

    for f in listdir(cachedir):
        p = join(cachedir, f)
        if not isfile(p):
            continue

        cache[f] = p

    return cache


def get_image_and_cache(
    image: object, cache: Dict, C: object, logger: object
) -> Dict:
    # New image. Save to cache
    cache_key = get_cached_key(image.key)
    exif = {}
    if cache_key not in cache:
        logger.info(
            f"{image.key} not in cache. Downloading."
        )
        r = requests.get(image.url_thumbs)
        b = BytesIO(r.content)
        i = Image.open(b)
        has_exif = bool(i.info.get('exif', False))

        if has_exif:
            exif_raw = i.info['exif']
            exif = generate_exif_dict(i, close=False)

        cached_filename = C.CACHE + get_cached_key(image.key)

        if not path.exists(path.dirname(cached_filename)):
            try:
                makedirs(path.dirname(cached_filename))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        if has_exif:
            i.save(cached_filename, "JPEG", exif=exif_raw)
        else:
            i.save(cached_filename, "JPEG")


    # Cached image. Grab from cache.
    else:
        logger.info(f"{image.key} in cache. Grabbing.")
        i = Image.open(cache[cache_key])
        has_exif = bool(i.info.get('exif', False))

        if has_exif:
            exif_raw = i.info['exif']
            exif = generate_exif_dict(i, close=True)

    # Check for corrupted exif data
    if not get_processed(exif, 'ISOSpeedRatings'):
        return None

    return exif


def get_processed(exif: Dict, key: str) -> str:
    return exif.get(key, {}).get("processed")


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
    time = dt.strftime("%I:%M%p").lstrip("0")
    year = dt.strftime("%Y")

    fancy_date = f"{month} {day} {time}, {year}"
    return fancy_date


def root_url(image: object, bucket_url: str) -> str:
    filename, ext = image.key.split(".")
    return f"{bucket_url}{filename.replace('_thumbs', '')}.{ext}"


def remove_thumbs_str(s: str) -> str:
    return s.replace("_thumbs", "")


def get_cached_key(key):
    return key.replace("/", "$$")
