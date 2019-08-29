#!/bin/bash

set -e

echo "core-ci package script running."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # this script's directory
STAGING="${DIR}/../_staging"
echo "STAGING=${STAGING}"

# Setup, cleanup.
cd $DIR
mkdir -p $STAGING # files dir for lambdas
rm -rf $STAGING/*

# Copy deployspec and CFN templates into staging folder.
cp -pr $DIR/../*.yaml $STAGING/

# Package lambdas into files subfolder of staging .
# TODO write bash to iterate directories when we have more than 1 lambda.

cd $DIR/../lambdas/ci_trigger
zip --symlinks -r9 $STAGING/ci_trigger.zip *

echo "core-ci package step complete, run.sh can be executed now."
