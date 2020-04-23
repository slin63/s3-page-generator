# knoppers.icu.generator

Generates Hugo pages for [knoppers.icu](https://github.com/slin63/knoppers-icu), a static photo gallery / frontend for my photography S3 bucket.

Pages receive a random cover photo on each regeneration.

## Setup:

```
# Set up AWS credentials
aws configure

# Grab repoes
git clone https://github.com/slin63/s3-page-generator $HOME/knoppers.icu.gen
git clone https://github.com/slin63/knoppers-icu $HOME/knoppers.icu

# Install dependencies
pip3 install -r $HOME/knoppers.icu.gen/requirements.txt

# Update .env
vim $HOME/knoppers.icu.gen/.env

# Deploy
. $HOME/projects/go/src/github.com/slin63/knoppers.icu.generator/.env && $HOME/projects/go/src/github.com/slin63/knoppers.icu.gen/deploy.sh
```



## Uploading photos with `awscli`
knoppers.icu.generator generates pages from files inside your s3 bucket. If you want new posts to appear on the website, you have to upload photos there.
- `aws s3 sync <directory> s3://<bucket_name>/images/unprocessed/ --metadata Content-Type=image/jpeg`
