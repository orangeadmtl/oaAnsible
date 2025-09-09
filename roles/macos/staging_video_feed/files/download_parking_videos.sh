#!/bin/bash

# Download parking lot surveillance videos for staging environment
# This script searches and downloads suitable parking lot footage from YouTube

set -euo pipefail

# Check if required tools are available
if ! command -v yt-dlp &> /dev/null; then
    echo "[ERROR] yt-dlp is not installed"
    echo "Install with: brew install yt-dlp"
    exit 1
fi

if ! command -v ffprobe &> /dev/null; then
    echo "[ERROR] ffprobe is not installed (required for video validation)"
    echo "Install with: brew install ffmpeg"
    exit 1
fi

# Configuration
STORAGE_DIR="${STORAGE_DIR:-$HOME/orangead/staging-video-feed/videos}"
LOG_FILE="${LOG_FILE:-$HOME/orangead/staging-video-feed/logs/video_download.log}"
MAX_DURATION=1800  # 30 minutes max
MIN_DURATION=300   # 5 minutes min
QUALITY="best[height<=1080]"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Create directories
mkdir -p "$STORAGE_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log "Starting parking lot video download process"

# Search queries for parking lot surveillance footage
declare -a SEARCH_QUERIES=(
    "parking lot security camera footage 1080p"
    "empty parking lot surveillance camera"
    "mall parking lot security camera overhead"
    "airport parking surveillance footage"
    "parking garage security camera view"
    "outdoor parking lot surveillance 1080p"
    "commercial parking lot security footage"
    "surveillance camera parking lot day time"
)

# Download function
download_parking_video() {
    local query="$1"
    local filename_template="$2"
    local filename_base="${filename_template%.%(ext)s}"  # Remove %(ext)s suffix
    
    log "Searching for: $query"
    
    # Search and download with specific criteria
    # Note: yt-dlp may return non-zero even on successful single download due to --max-downloads behavior
    yt-dlp \
        --format "$QUALITY" \
        --output "$STORAGE_DIR/$filename_template" \
        --match-filter "duration > $MIN_DURATION & duration < $MAX_DURATION" \
        --max-downloads 1 \
        --no-playlist \
        --write-info-json \
        --embed-subs \
        --write-auto-subs \
        --no-flat-playlist \
        "ytsearch1:$query" 2>&1 | tee -a "$LOG_FILE"
    
    # Don't fail immediately on yt-dlp exit code - check if files were actually downloaded instead
    
    # Check for actual downloaded video files (exclude .info.json and .vtt files)
    if find "$STORAGE_DIR" -name "${filename_base}.*" -type f \( -name "*.mp4" -o -name "*.webm" -o -name "*.mkv" -o -name "*.avi" -o -name "*.mov" -o -name "*.flv" \) | head -1 | grep -q .; then
        local actual_file=$(find "$STORAGE_DIR" -name "${filename_base}.*" -type f \( -name "*.mp4" -o -name "*.webm" -o -name "*.mkv" -o -name "*.avi" -o -name "*.mov" -o -name "*.flv" \) | head -1)
        log "Successfully downloaded: $(basename "$actual_file")"
        
        # First, wait a moment for the file to fully close
        sleep 1
        
        # Verify video properties with improved error handling and debugging
        log "Attempting to analyze video: $actual_file"
        log "File exists: $(test -f "$actual_file" && echo "yes" || echo "no")"
        log "File size: $(stat -f%z "$actual_file" 2>/dev/null || echo "unknown") bytes"
        
        # Try to get video properties with more detailed error handling
        local duration_raw=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$actual_file" 2>&1)
        local duration=$(echo "$duration_raw" | grep -E '^[0-9]+(\.[0-9]+)?$' | cut -d. -f1 || echo "0")
        local width=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$actual_file" 2>/dev/null || echo "0")
        local height=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$actual_file" 2>/dev/null || echo "0")
        
        # Debug ffprobe output if it fails
        if [[ "$duration" == "0" ]] || [[ -z "$duration" ]]; then
            log "ffprobe duration failed. Raw output: $duration_raw"
            log "Trying alternative ffprobe command..."
            local alt_duration=$(ffprobe -i "$actual_file" 2>&1 | grep Duration | cut -d ' ' -f 4 | sed s/,// | awk -F: '{print ($1 * 3600) + ($2 * 60) + $3}' | cut -d. -f1 || echo "0")
            if [[ "$alt_duration" != "0" ]] && [[ -n "$alt_duration" ]]; then
                duration="$alt_duration"
                log "Alternative ffprobe succeeded: ${duration}s"
            fi
        fi
        
        # Handle decimal durations and empty values
        if [[ -z "$duration" ]] || [[ "$duration" == "N/A" ]] || ! [[ "$duration" =~ ^[0-9]+$ ]]; then
            duration="0"
        fi
        
        log "Video properties - Duration: ${duration}s, Resolution: ${width}x${height}"
        
        # Check file size and use heuristic if ffprobe fails completely
        local file_size=$(stat -f%z "$actual_file" 2>/dev/null || echo "0")
        
        # For valid-looking video files (>10MB), be more permissive
        if [[ "$file_size" -gt 10485760 ]]; then
            if [[ "$duration" == "0" ]]; then
                log "Large video file (${file_size} bytes) with ffprobe issues - assuming valid video"
                return 0
            elif [[ "$duration" -ge "$MIN_DURATION" ]]; then
                log "Video meets duration requirement: ${duration}s >= ${MIN_DURATION}s"
                return 0
            else
                log "Video too short (${duration}s < ${MIN_DURATION}s) but file is large - keeping anyway"
                return 0
            fi
        else
            log "Small file (${file_size} bytes) and duration ${duration}s - likely invalid"
            rm -f "$actual_file"
            return 1
        fi
        
        return 0
    else
        log "Download failed for: $query"
        log "No file found matching pattern: $STORAGE_DIR/${filename_base}.*"
        log "Check if yt-dlp is working correctly and YouTube is accessible"
        return 1
    fi
}

# Download videos for different scenarios
log "Downloading parking lot surveillance videos..."

# Try to download videos for different scenarios
downloaded_count=0
scenario_names=("empty-lot" "half-full" "full-lot" "general-1" "general-2" "general-3")

for i in "${!SEARCH_QUERIES[@]}"; do
    if [[ $i -lt ${#scenario_names[@]} ]]; then
        scenario="${scenario_names[$i]}"
    else
        scenario="parking-video-$((i+1))"
    fi
    
    filename="${scenario}.%(ext)s"
    
    if download_parking_video "${SEARCH_QUERIES[$i]}" "$filename"; then
        ((downloaded_count++))
    fi
    
    # Small delay between downloads
    sleep 2
done

# Check if we have at least one video
if [[ $downloaded_count -eq 0 ]]; then
    log "ERROR: No videos were successfully downloaded"
    
    # Try alternative approach with more general search
    log "Attempting fallback download with general search..."
    
    if download_parking_video "security camera parking lot" "fallback-parking.%(ext)s"; then
        downloaded_count=1
        log "Fallback download successful"
    else
        log "CRITICAL: All download attempts failed"
        exit 1
    fi
fi

# Create a playlist file for cycling
PLAYLIST_FILE="$STORAGE_DIR/playlist.txt"
log "Creating video playlist..."

find "$STORAGE_DIR" -name "*.mp4" -o -name "*.mkv" -o -name "*.webm" | sort > "$PLAYLIST_FILE"

if [[ -s "$PLAYLIST_FILE" ]]; then
    log "Playlist created with $(wc -l < "$PLAYLIST_FILE") videos"
    log "Videos available:"
    while IFS= read -r video; do
        log "  - $(basename "$video")"
    done < "$PLAYLIST_FILE"
else
    log "ERROR: No videos found for playlist"
    exit 1
fi

# Set permissions
chmod 644 "$STORAGE_DIR"/*.{mp4,mkv,webm} 2>/dev/null || true
chmod 644 "$PLAYLIST_FILE"

log "Video download process completed successfully"
log "Downloaded $downloaded_count videos to: $STORAGE_DIR"

# Display summary
log "=== Download Summary ==="
log "Total videos: $downloaded_count"
log "Storage location: $STORAGE_DIR"
log "Playlist file: $PLAYLIST_FILE"
log "Ready for staging video feed service"