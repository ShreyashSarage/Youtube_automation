#!/bin/bash
# Make a messy "Downloads" folder to test the organizer on
set -e
D=${1:-Downloads}
mkdir -p "$D/old-stuff"
cd "$D"
for f in holiday.JPG screenshot-2026-11-20.png cat.gif invoice-0042.pdf \
         resume.docx notes.txt budget.csv trip.mp4 podcast-ep12.mp3 \
         rust-book.zip backup.tar.gz main.rs index.html README; do
    echo "sample file: $f" > "$f"
done
for f in notes.txt photo.png data.json; do
    echo "older file: $f" > "old-stuff/$f"
done
echo "made $(find . -type f | wc -l) files in $D"
