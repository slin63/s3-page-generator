#!/bin/sh
# Generates posts for, builds, and deploys knoppers.icu

timestamp() {
  date +"%T"
}

BASE="/Users/seanlin/projects/go/src/github.com/slin63"

echo "$(timestamp): [CREATING HUGO PAGES FROM S3]"
python3 $BASE/knoppers.icu.generator/main.py

echo "$(timestamp): [BUILDING HUGO SITE]"
hugo -s $BASE/knoppers.icu

echo "$(timestamp): [DEPLOYING HUGO SITE]"
hugo deploy -s $BASE/knoppers.icu


