#!/bin/bash

set -e

echo "🔁 Running NSE MTF data fetcher..."

DATE=$(date -d "-7 days" "+%d-%b-%Y" | tr '[:lower:]' '[:upper:]')
DEST_DIR="data"
CSV_DIR="$DEST_DIR/unzipped"
ZIP_NAME="MTF_${DATE}.zip"
URL="https://www.nseindia.com/api/archives-reports?archives=%5B%7B%22name%22%3A%22CM%20-%20Margin%20Trading%20Disclosure%22%2C%22type%22%3A%22archives%22%2C%22category%22%3A%22capital-market%22%2C%22section%22%3A%22equities%22%7D%5D&type=equities&mode=single&date=${DATE}"

mkdir -p "$CSV_DIR"

curl -s -L -o "$DEST_DIR/$ZIP_NAME" "$URL" \
-H "User-Agent: Mozilla/5.0" \
-H "Referer: https://www.nseindia.com/" \
-H "Accept: application/zip"

if [ -s "$DEST_DIR/$ZIP_NAME" ]; then
    echo "✅ Downloaded $ZIP_NAME"
    unzip -o "$DEST_DIR/$ZIP_NAME" -d "$CSV_DIR"
    echo "📂 Extracted to $CSV_DIR"
else
    echo "❌ Failed to download. ZIP is empty."
    exit 1
fi
