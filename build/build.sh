#!/usr/bin/env bash
# One reproducible build: compile the design export, then apply every fix.
set -e
cd "$(dirname "$0")"
echo "[1/2] compile"    && python compile.py     | tail -2
echo "[2/2] postprocess" && python postprocess.py
echo "done -> docs/"
python redirects.py
