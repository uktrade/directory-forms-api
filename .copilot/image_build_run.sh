#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# Use temporary default values in the dev config file to allow collectstatic to run at build time
export $(grep -v '^#' conf/env/dev | xargs)

# Add commands below to run inside the container after all the other buildpacks have been applied
python manage.py collectstatic --noinput
