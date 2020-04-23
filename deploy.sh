#!/bin/bash
# Generates posts for, builds, and deploys knoppers.icu

timestamp() {
  date +"%T"
}

BASE="/Users/seanlin/projects/go/src/github.com/slin63"

echo "$(timestamp): [CREATING HUGO PAGES FROM S3]"
/usr/local/bin/python3 $BASE/knoppers.icu.generator/main.py

echo "$(timestamp): [BUILDING HUGO SITE]"
/usr/local/bin/hugo -s $BASE/knoppers.icu

echo "$(timestamp): [DEPLOYING HUGO SITE]"
/usr/local/bin/hugo deploy -s $BASE/knoppers.icu


