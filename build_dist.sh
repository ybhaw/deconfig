#!/bin/bash

set -e
HOME_DIR=$(pwd)
BASE_PYTHONPATH="$PYTHONPATH"
BUILD_TIME=$(date '+%Y%m%d%H%M%S')
export DEV_VERSION

# Installing build & twine
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine

# Building deconfig
cd src
rm -rf dist/
rm -rf deconfig.egg-info/
PYTHONPATH="$BASE_PYTHONPATH:$(pwd)"
DEV_VERSION="$(python3 -c "import deconfig; print(deconfig.__version__)").$BUILD_TIME"
python3 -m build
python3 -m twine upload --repository testpypi dist/*

# Revert all changes
cd "$HOME_DIR"
PYTHONPATH="$BASE_PYTHONPATH"
