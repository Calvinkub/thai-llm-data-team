#!/usr/bin/env bash
# Run all 4 parquet preprocessors sequentially.
# Edit SSD_ROOT and OUTPUT_ROOT to match your mount points.
#
# Usage:
#   bash run_all_parquet.sh
#   bash run_all_parquet.sh /mnt/ssd /mnt/ssd/shards   # override paths

set -euo pipefail

SSD_ROOT="${1:-/mnt/ssd/data}"
OUTPUT_ROOT="${2:-/mnt/ssd/shards}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== SSD root   : $SSD_ROOT"
echo "=== Output root: $OUTPUT_ROOT"
echo ""

echo "--- [1/4] THAILLM ---"
python "$SCRIPT_DIR/preprocess_thaillm.py" \
    --input  "$SSD_ROOT/thaillm" \
    --output "$OUTPUT_ROOT/thaillm"

echo ""
echo "--- [2/4] SEAPILE (Thai subset) ---"
python "$SCRIPT_DIR/preprocess_seapile.py" \
    --input  "$SSD_ROOT/seapile" \
    --output "$OUTPUT_ROOT/seapile"

echo ""
echo "--- [3/4] The Stack V2 ---"
python "$SCRIPT_DIR/preprocess_thestack_v2.py" \
    --input  "$SSD_ROOT/thestack_v2" \
    --output "$OUTPUT_ROOT/thestack_v2"

echo ""
echo "--- [4/4] FineMath ---"
python "$SCRIPT_DIR/preprocess_finemath.py" \
    --input  "$SSD_ROOT/finemath" \
    --output "$OUTPUT_ROOT/finemath"

echo ""
echo "=== All done. Output at: $OUTPUT_ROOT"
