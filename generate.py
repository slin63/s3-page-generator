# 1. Check S3 for new files
# 2. If any files less than <time> old, run, otherwise sleep
import os
import boto3

from typing import List, Dict
from helpers.logger import get_logger

logger = get_logger("icu_generator")

class C:
    BUCKET = str(os.getenv("BUCKET"))
    UNPROCESSED = str(os.getenv("UNPROCESSED"))


class Album(object):
    def __init__(self, name):
        self.name = name
        self.images = []

    def __repr__(self):
        return f"{self.name}, {self.images}"


class Image(object):
    def __init__(self, name, key):
        self.name = name
        self.key = key

    def __repr__(self):
        return f"{self.name}, {self.key}"


def get_contents(s3):
    get_last_modified = lambda obj: int(
        obj["LastModified"].strftime("%s")
    )
    objs = s3.list_objects_v2(Bucket=C.BUCKET)["Contents"]

    return [
        obj for obj in sorted(objs, key=get_last_modified)
    ]


def separate_into_albums(d: List[Dict]) -> List[Album]:
    albums = {}
    album_objs = []
    for obj in d:
        key = obj["Key"]
        album_name, name = key.split("/")
        if album_name in C.UNPROCESSED:
            continue

        albums[album_name] = albums.get(album_name, []) + [Image(name, key)]

    for k, v in albums.items():
        album = Album(k)
        album.images = v
        album_objs.append(album)

    return album_objs


s3 = boto3.client("s3")
s3r = boto3.resource("s3")

d = get_contents(s3)
albums = separate_into_albums(d)

# Generate a home page showing a single photo from all the albums
generate_index(albums)

# Generate a page for each album
generate_pages(albums)
