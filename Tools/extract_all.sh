#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
python="${PYTHON:-python3}"
"$python" Tools/extract_assets.py
"$python" Tools/extract_loading.py
"$python" Tools/make_icon.py
"$python" Tools/validate_assets.py
