#!/bin/bash

# Setup QuixBugs
git clone https://github.com/jkoppel/QuixBugs.git

# File paths
PAUL_DIR="../../"
PATCHES_DIR="${PAUL_DIR}/src/paul/patches"
FILENAMES_FILE="./java_filenames.txt"
QUIXBUGS_DIR="./QuixBugs/"

# Invoke with all instances
while IFS= read -r filename <&3; do
    echo "========== Processing ${filename} =========="
    git -C ${QUIXBUGS_DIR} reset --hard HEAD
    CMD="paul quixbugs java --path ${QUIXBUGS_DIR} --instance ${filename} --verify"
    echo -e "${CMD}\n\n"
    $CMD
    echo -e "\n\n"
done 3< "$FILENAMES_FILE"

echo "All files processed!"