#!/bin/sh

BOARD_DIR="$(dirname $0)"
OVERLAY_CFG="${BOARD_DIR}/overlay"
TARGET_CFG="${TARGET_DIR}"
OUTPUT_CFG="${BASE_DIR}"

echo "This is delta post build"
echo "copy some files and pest at target folder"
echo "board dir" "${OVERLAY_CFG}"
echo "build dir" "${TARGET_CFG}"
echo "output dir" "${OUTPUT_CFG}"
echo "board dir" "${BR2_EXTERNAL_EVDC2_PATH}"
echo "build dir" "${BINARIES_DIR}"


echo "copying file"




