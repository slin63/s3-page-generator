frontmatter = """
---
title: "$TITLE"
date: $DATE
draft: false
description: "$COVER_URL"
summary: "$IMAGE_COUNT"
---
<meta property="og:image" content="$COVER_URL">
<meta property="og:title" content="$TITLE" />
<meta property="og:description" content="some photos, brace yourself" />

"""

body = """
<!-- GENERATED WITH knopper.icu.generator (https://github.com/slin63/s3-page-generator) -->
<div class="grid-container">
  $IMAGES
</div>"""

image = """
<div class="grid-item">
  <div class="grid-image">
    <a href="$URL">
      <img src="$URL_THUMBS">
    </a>
  </div>
  <label class="checkbox-inline">
    <div>
      <input type="checkbox" class="download-check" value="$URL">$IMAGE_NAME
      <div class="exif">$EXIF_DATA</div>
      <div class="exif">$DATE_PRETTY</div>
    </div>
  </label>
</div>"""

footer = """{{% download_checked %}}"""
