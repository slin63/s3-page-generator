# https://www.codedrome.com/reading-exif-data-with-python-and-pillow/ <-- this guy is my hero
import datetime
from fractions import Fraction
from typing import Dict

from PIL import Image
import PIL.ExifTags


def generate_exif_dict(
    image: Image, close: bool = True
) -> Dict:

    """
    Generate a dictionary of dictionaries.

    The outer dictionary keys are the names
    of individual items, eg Make, Model etc.

    The outer dictionary values are themselves
    dictionaries with the following keys:

        tag: the numeric code for the item names
        raw: the data as stored in the image, often
        in a non-human-readable format
        processed: the raw data if it is human-readable,
        or a processed version if not.
    """

    try:

        exif_data_PIL = image._getexif()

        exif_data = {}

        for k, v in PIL.ExifTags.TAGS.items():

            try:
                if k in exif_data_PIL:
                    value = exif_data_PIL[k]
                else:
                    value = None
            except TypeError:
                raise Exception(f"{image.filename}: invalid exif_data.")

            if len(str(value)) > 64:
                value = str(value)[:65] + "..."

            exif_data[v] = {
                "tag": k,
                "raw": value,
                "processed": value,
            }

        if close:
            image.close()

        exif_data = _process_exif_dict(exif_data)

        return exif_data

    except IOError as ioe:

        raise


def _derationalize(rational):
    if not rational:
        return -1
    return rational[0] / rational[1]


def _create_lookups():

    lookups = {}

    lookups["metering_modes"] = (
        "Undefined",
        "Average",
        "Center-weighted average",
        "Spot",
        "Multi-spot",
        "Multi-segment",
        "Partial",
    )

    lookups["exposure_programs"] = (
        "Undefined",
        "Manual",
        "Program AE",
        "Aperture-priority AE",
        "Shutter speed priority AE",
        "Creative (Slow speed)",
        "Action (High speed)",
        "Portrait ",
        "Landscape",
        "Bulb",
    )

    lookups["resolution_units"] = (
        "",
        "Undefined",
        "Inches",
        "Centimetres",
    )

    lookups["orientations"] = (
        "",
        "Horizontal",
        "Mirror horizontal",
        "Rotate 180",
        "Mirror vertical",
        "Mirror horizontal and rotate 270 CW",
        "Rotate 90 CW",
        "Mirror horizontal and rotate 90 CW",
        "Rotate 270 CW",
    )

    return lookups


def _process_exif_dict(exif_dict):

    date_format = "%Y:%m:%d %H:%M:%S"

    lookups = _create_lookups()
    exif_dict["DateTime"][
        "processed"
    ] = datetime.datetime.strptime(
        exif_dict["DateTime"]["raw"].replace("\x00", ""),
        date_format,
    )

    exif_dict["DateTimeOriginal"][
        "processed"
    ] = datetime.datetime.strptime(
        exif_dict["DateTimeOriginal"]["raw"], date_format
    )

    exif_dict["DateTimeDigitized"][
        "processed"
    ] = datetime.datetime.strptime(
        exif_dict["DateTimeDigitized"]["raw"], date_format
    )

    exif_dict["FNumber"]["processed"] = _derationalize(
        exif_dict["FNumber"]["raw"]
    )
    exif_dict["FNumber"]["processed"] = "f{}".format(
        exif_dict["FNumber"]["processed"]
    )

    exif_dict["MaxApertureValue"][
        "processed"
    ] = _derationalize(exif_dict["MaxApertureValue"]["raw"])
    exif_dict["MaxApertureValue"][
        "processed"
    ] = "f{:2.1f}".format(
        exif_dict["MaxApertureValue"]["processed"]
    )

    exif_dict["FocalLength"]["processed"] = _derationalize(
        exif_dict["FocalLength"]["raw"]
    )
    exif_dict["FocalLength"]["processed"] = "{}mm".format(
        exif_dict["FocalLength"]["processed"]
    )

    exif_dict["FocalLengthIn35mmFilm"][
        "processed"
    ] = "{}mm".format(
        exif_dict["FocalLengthIn35mmFilm"]["raw"]
    )

    exif_dict["Orientation"]["processed"] = lookups[
        "orientations"
    ][exif_dict["Orientation"]["raw"]]

    exif_dict["ResolutionUnit"]["processed"] = lookups[
        "resolution_units"
    ][exif_dict["ResolutionUnit"]["raw"]]

    exif_dict["ExposureProgram"]["processed"] = lookups[
        "exposure_programs"
    ][exif_dict["ExposureProgram"]["raw"]]

    exif_dict["MeteringMode"]["processed"] = lookups[
        "metering_modes"
    ][exif_dict["MeteringMode"]["raw"]]

    exif_dict["XResolution"]["processed"] = int(
        _derationalize(exif_dict["XResolution"]["raw"])
    )

    exif_dict["YResolution"]["processed"] = int(
        _derationalize(exif_dict["YResolution"]["raw"])
    )

    exif_dict["ExposureTime"]["processed"] = _derationalize(
        exif_dict["ExposureTime"]["raw"]
    )
    exif_dict["ExposureTime"]["processed"] = str(
        Fraction(
            exif_dict["ExposureTime"]["processed"]
        ).limit_denominator(8000)
    )

    exif_dict["ExposureBiasValue"][
        "processed"
    ] = _derationalize(
        exif_dict["ExposureBiasValue"]["raw"]
    )
    exif_dict["ExposureBiasValue"][
        "processed"
    ] = "{} EV".format(
        exif_dict["ExposureBiasValue"]["processed"]
    )

    return exif_dict
