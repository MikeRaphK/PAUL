#!/bin/sh
set -e

python3 /app/main.py "$@"

echo "[AFTER] Current directory: $(pwd)"
echo "[AFTER] ls -al /app:"
ls -al /app || echo "/app does not exist"
echo "[AFTER] ls -al /github/workspace:"
ls -al /github/workspace || echo "/github/workspace does not exist"
