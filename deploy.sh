#!/bin/sh
# Generates posts for, builds, and deploys knoppers.icu

timestamp() {
  date +"%T"
}

echo "$(timestamp): [CREATING HUGO PAGES FROM S3]"
. $HOME/knoppers.icu.generator/.env && python main.py

echo "$(timestamp): [BUILDING HUGO SITE]"
hugo -s $HOME/knoppers.icu

echo "$(timestamp): [DEPLOYING HUGO SITE]"
hugo deploy -s $HOME/knoppers.icu


