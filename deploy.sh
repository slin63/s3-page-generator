#!/bin/sh
# Generates posts for, builds, and deploys knoppers.icu

timestamp() {
  date +"%T"
}

echo "$(timestamp): [CREATING HUGO PAGES FROM S3]"
python3 $HOME/knoppers.icu.gen/main.py

echo "$(timestamp): [BUILDING HUGO SITE]"
hugo -s $HOME/knoppers.icu

echo "$(timestamp): [DEPLOYING HUGO SITE]"
hugo deploy -s $HOME/knoppers.icu


