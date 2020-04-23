frontmatter = """---
title: "$TITLE"
date: $DATE
draft: false
---"""

body = """
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
