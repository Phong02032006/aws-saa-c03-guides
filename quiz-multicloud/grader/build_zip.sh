#!/usr/bin/env bash
# Build grader.zip for upload to AWS Lambda (runtime Python 3.12, handler: handler.lambda_handler).
set -euo pipefail
cd "$(dirname "$0")"
rm -rf build grader.zip
mkdir build
# fpdf2 pulls in Pillow (native code): fetch wheels matching the Lambda runtime, not the local machine.
pip install -r requirements.txt -t build --quiet --only-binary=:all: \
  --platform manylinux2014_x86_64 --implementation cp --python-version 3.12
cp -r *.py fonts build/
(cd build && zip -qr ../grader.zip .)
rm -rf build
echo "Created $(pwd)/grader.zip"
