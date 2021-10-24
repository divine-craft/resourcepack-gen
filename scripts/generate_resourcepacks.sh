#!/usr/bin/env bash

# Files excluded from generated archives
readonly ARCHIVE_EXCLUSIONS='*.git*'

# Make this script fail in case of failed commands
set -ev

##################
# Read constants #
##################

readonly DESCRIPTION=$(cat description.txt)
echo "Description: $DESCRIPTION"

###############################
# Initialize target directory #
###############################

# Create empty directory to store build files
mkdir -p ./target/
find ./target/ -mindepth 1 -delete

############################
# Generate resourcepack V3 #
############################

# Create directory for storing resourcepack files
mkdir ./target/resourcepack_v3/

# Copy resourcepack files to manipulated directory
cp -r ./assets/ ./target/resourcepack_v3/assets/
if [ -e ./pack.png ]; then
  cp ./pack.png ./target/resourcepack_v3/
fi

# Find valid Python interpreter
if [[ "$(python --version)" == "Python 3.*" ]]; then
  PYTHON_INTERPRETER=python
else
  PYTHON_INTERPRETER=python3
fi
echo "Using \`${PYTHON_INTERPRETER}\` as Python interpreter"

# Generate v3 multimodel files
${PYTHON_INTERPRETER} ./scripts/generate_multimodels.py --mappings ./mappings/ \
--target ./target/resourcepack_v3/assets/minecraft/models/item/ --format 3

# Compress JSON models
${PYTHON_INTERPRETER} ./scripts/compress_models.py --models ./target/resourcepack_v3/assets/divinecraft/models/

# Create valid pack.mcmeta
${PYTHON_INTERPRETER} ./scripts/generate_pack_mcmeta.py \
--path ./target/resourcepack_v3/ --version 3 --description "$DESCRIPTION"

# Generate v3 ZIP-archive
# `cd` is used not to keep full path to files
cd ./target/resourcepack_v3/
zip -r ../resourcepack_v3 . -x "$ARCHIVE_EXCLUSIONS"
cd ../../

############################
# Generate resourcepack V4 #
############################

# note: mkdir is *not* needed as it will change copy-semantics
# Copy resourcepack files to manipulated directory
cp -r ./target/resourcepack_v3/ ./target/resourcepack_v4

# Generate v4 multimodel files
rm -r ./target/resourcepack_v4/assets/minecraft/models/item/
${PYTHON_INTERPRETER} ./scripts/generate_multimodels.py --mappings ./mappings/ \
--target ./target/resourcepack_v4/assets/minecraft/models/item/ --format 4

# Fix models
${PYTHON_INTERPRETER} ./scripts/patch_v3_models_to_v4.py --models ./target/resourcepack_v4/assets/divinecraft/models/
${PYTHON_INTERPRETER} ./scripts/patch_v3_models_to_v4.py --models ./target/resourcepack_v4/assets/minecraft/models/

# Create valid pack.mcmeta
${PYTHON_INTERPRETER} ./scripts/generate_pack_mcmeta.py \
--path ./target/resourcepack_v4/ \--version 4 --description "$DESCRIPTION"

# Generate v4 ZIP-archive
# `cd` is used not to keep full path to files
cd ./target/resourcepack_v4/
zip -r ../resourcepack_v4 . -x "$ARCHIVE_EXCLUSIONS"
cd ../../
