#!/bin/bash

#set -e
HOME_DIR=$(pwd)
BASE_PYTHONPATH="$PYTHONPATH"
export DEV_VERSION_SUFFIX
DEV_VERSION_SUFFIX=$(date '+%Y%m%d%H%M%S')

# Building deconfig
rm -rf dist/
rm -rf deconfig.egg-info/

python3 -m build
python3 -m twine upload --repository testpypi dist/*

# Revert all changes
cd "$HOME_DIR"
PYTHONPATH="$BASE_PYTHONPATH"
