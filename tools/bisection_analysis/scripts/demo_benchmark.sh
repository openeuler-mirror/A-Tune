#!/bin/bash

# Define constants
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ROOT_DIR="${SCRIPT_DIR}/.."
VIDEO_PATH="${ROOT_DIR}/data/akiyo_cif.y4m"
FFMPEG_BIN_PATH="${ROOT_DIR}/projects/FFmpeg/build/bin/ffmpeg"
TIME_STAMP=$(date '+%Y-%m-%d_%H-%M-%S')

# Set log directory and ensure it exists
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "$LOG_DIR"

# Validate the FFMPEG binary path
if [ ! -x $FFMPEG_BIN_PATH ]; then
    echo "FFMPEG binary does not exist at path: $FFMPEG_BIN_PATH"
    exit 1
fi

# Configuration
ffmpegCmd=$FFMPEG_BIN_PATH
maxIterations=5
breakLoop=0

# Define function for executing FFMPEG command
runFFMPEGCommand() {
    local startInstant=$(date '+%s')
    echo -n "Execution Start Time=$startInstant  "
    $ffmpegCmd -i "$VIDEO_PATH" -c:v libx264 -preset veryslow -b:v 5M -maxrate 5M -bufsize 15M -threads 4 -x264opts bframes=12:keyint=24:min-keyint=24:nal-hrd=cbr:force-cfr=1:bframes=8:no-scenecut -f null - -benchmark -stats
}

# Main loop for executing jobs
executeMainLoop() {
    iterationCount=0
    while true; do
        [[ $breakLoop -eq 1 ]] && break
        runFFMPEGCommand
        ((iterationCount++))
        [[ $iterationCount -ge $maxIterations ]] && breakLoop=1
    done
}

# Set environment variables
export ffmpegCmd
export maxIterations

# Redirect output to log file in log directory
LOG_FILE="${LOG_DIR}/${BASH_SOURCE[0]##*/}-${TIME_STAMP}.log"
exec > >(tee -ia "$LOG_FILE")
exec 2> >(tee -ia "$LOG_FILE" >&2)

# Execute main loop and calculate execution time
startTime=$(date +%s%3N)
executeMainLoop
endTime=$(date +%s%3N)
executionDuration=$((endTime - startTime))

# Log execution duration
echo "Script executed in $executionDuration milliseconds."
