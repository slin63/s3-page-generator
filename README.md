# knoppers.icu.generator

Generates Hugo pages for [knoppers.icu](https://github.com/slin63/knoppers-icu), a static photo gallery / frontend for my photography S3 bucket, updated automatically by a cronjob on an EC2 instance.

Read about the project here: [chronicpizza.net/posts/knoppersicu](https://www.chronicpizza.net/posts/knoppersicu/).

![grabbing images, generating markdown files, and deploying the hugo site](./kn.gif)

## Debugging:
`. $HOME/projects/go/src/github.com/slin63/knoppers.icu.generator/.env && $HOME/projects/go/src/github.com/slin63/knoppers.icu.generator/deploy_test.sh`

## Setup:

```
# Set up AWS credentials
aws configure

# Grab repoes
git clone https://github.com/slin63/s3-page-generator $HOME/knoppers.icu.gen
git clone --recursive https://github.com/slin63/knoppers-icu $HOME/knoppers.icu

# Install dependencies
pip3 install -r $HOME/knoppers.icu.gen/requirements.txt

# Update .env
vim $HOME/knoppers.icu.gen/.env

# Deploy
. $HOME/projects/go/src/github.com/slin63/knoppers.icu.generator/.env && $HOME/projects/go/src/github.com/slin63/knoppers.icu.generator/deploy.sh
```



## Uploading photos with `awscli`
knoppers.icu.generator generates pages from files inside your s3 bucket. If you want new posts to appear on the website, you have to upload photos there.
- `aws s3 sync <directory> s3://<bucket_name>/images/unprocessed/ --metadata Content-Type=image/jpeg`
