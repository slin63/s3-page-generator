# 1. Check S3 for new files
# 2. If any files less than <time> old, run, otherwise sleep
import os
import boto3
import glob
from typing import List, Dict


from generators import gallery
from helpers.logger import get_logger
from datetime import datetime


logger = get_logger("icu_generator")


class C:
    BUCKET = str(os.getenv("BUCKET"))
    UNPROCESSED = str(os.getenv("UNPROCESSED"))
    TEMP = str(os.getenv("TEMP"))
    CACHE = str(os.getenv("CACHE"))
    LIMIT = int(os.getenv("LIMIT"))
    HUGODIR = str(os.getenv("HUGODIR"))


class Album(object):
    def __init__(self, name):
        self.name: str = name
        self.images: List[Image] = []
        self.date: datetime = None
        self.date_pretty: str = ""
        self.cover_image: Image = None

    def __repr__(self):
        return f"{self.name}, {self.images}"


class Image(object):
    def __init__(self, name, key):
        self.name: str = name
        self.key: str = key
        self.exif_data: str = ""
        self.date_pretty: str = ""
        self.date: datetime = None
        self.url: str = None
        self.url_thumbs: str = None

    def __repr__(self):
        return f"{self.name}, {self.key}"


def get_all_s3_objects(s3, **base_kwargs):
    continuation_token = None
    while True:
        list_kwargs = dict(MaxKeys=1000, **base_kwargs)
        if continuation_token:
            list_kwargs["ContinuationToken"] = continuation_token
        response = s3.list_objects_v2(**list_kwargs)
        yield from response.get("Contents", [])
        if not response.get("IsTruncated"):  # At the end of the list?
            break
        continuation_token = response.get("NextContinuationToken")


def separate_into_albums(d: List[Dict], limit: int) -> List[Album]:
    if limit == -1:
        limit = float("inf")

    albums = {}
    album_objs = []
    count = 0
    for obj in d:
        key = obj["Key"]
        if C.UNPROCESSED in key and key != C.UNPROCESSED:
            raise Exception(
                f"Files still sitting in unprocessed queue: {key}. Please process or remove file before trying again."
            )
        # Parse the directory of the file, ignoring files that are not in a directory
        split_key = key.split("/")
        if split_key[0] in C.UNPROCESSED or len(split_key) < 2:
            continue
        album_name, name = key.split("/")
        albums[album_name] = albums.get(album_name, []) + [
            Image(name, key)
        ]
        count += 1
        if count > limit:
            break

    for k, v in albums.items():
        album = Album(k)
        album.images = v
        album_objs.append(album)

    return album_objs


# Initialize s3 resources and get relevant data
s3 = boto3.client("s3")
s3r = boto3.resource("s3")

# d = get_contents(s3, C.LIMIT)
d = get_all_s3_objects(s3, Bucket=C.BUCKET)
albums = separate_into_albums(d, C.LIMIT)
bucket_url = "https://s3.amazonaws.com/%s/" % C.BUCKET

# Generate a page for each album
pages = []
for album in albums:
    pages.append(
        (album, gallery.generate_page(album, bucket_url, C, logger))
    )
    logger.info(f"Finish generating post for: {album.name}")

# Clear out existing pages
for f in glob.glob(f"{C.HUGODIR}/*.md"):
    os.remove(f)
    logger.info(f"Removed old post: {f}")

# Regenerate pages
if not os.path.exists(C.HUGODIR):
    os.makedirs(C.HUGODIR)

for album, page in pages:
    p_path = os.path.join(C.HUGODIR, album.name) + ".md"
    with open(p_path, "w") as f:
        f.write(page)
        logger.info(f"Created new post: {p_path}")
