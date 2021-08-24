#!/bin/bash
# Generates posts for, builds, and deploys knoppers.icu

timestamp() {
  date +"%T"
}

BASE="/Users/seanlin/projects/go/src/github.com/slin63"

echo "$(timestamp): [CREATING HUGO PAGES FROM S3]"
/Users/seanlin/.pyenv/shims/python3.7 $BASE/knoppers.icu.generator/main.py

echo "$(timestamp): [BUILDING HUGO SITE]"
/usr/local/bin/hugo -s $BASE/knoppers.icu

