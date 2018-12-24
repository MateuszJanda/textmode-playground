#!/bin/bash

if [[ $1 == "-c" || $1 == "--capture" ]]; then
    ffmpeg -video_size 640x480 -framerate 25 -f x11grab -i :0.0+0,45 output.mp4
fi

# PALETTE_FILE="tmp_pallete.png"
# VIDEO_FILE="output_video.mp4"
# INPUT_FILES="img-%4d.png"
# OUTPUT_FILE="output.gif"
# FILTERS="fps=25"

# ffmpeg -r 100 -i $INPUT_FILES -c:v libx264 -crf 0 -preset veryslow $VIDEO_FILE
# ffmpeg -v warning -i $VIDEO_FILE -vf "$FILTERS,palettegen" -y $PALETTE_FILE
# ffmpeg -v warning -i $VIDEO_FILE -i $PALETTE_FILE -lavfi "$FILTERS [x]; [x][1:v] paletteuse" -y $OUTPUT_FILE