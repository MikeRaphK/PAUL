#!/bin/bash

# Setup QuixBugs
git clone https://github.com/jkoppel/QuixBugs.git

# File paths
PAUL_DIR="../../"
PATCHES_DIR="${PAUL_DIR}/src/paul/patches"
FILENAMES_FILE="./python_filenames.txt"
QUIXBUGS_DIR="./QuixBugs/"
MODEL_NAME="$1"

# Invoke with all instances
while IFS= read -r filename <&3; do
    echo "========== Processing ${filename} =========="
    git -C ${QUIXBUGS_DIR} reset --hard HEAD
    CMD="paul quixbugs python --path ${QUIXBUGS_DIR} --instance ${filename} --verify --model ${MODEL_NAME}"
    echo -e "${CMD}\n\n"
    $CMD
    echo -e "\n\n"
done 3< "$FILENAMES_FILE"

echo "All files processed!"