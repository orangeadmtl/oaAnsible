#!/bin/bash

# Download parking lot surveillance videos for staging environment
# This script searches and downloads suitable parking lot footage from YouTube

set -euo pipefail

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
    local filename="$2"
    local output_path="$STORAGE_DIR/$filename"
    
    log "Searching for: $query"
    
    # Search and download with specific criteria
    yt-dlp \
        --quiet \
        --no-warnings \
        --format "$QUALITY" \
        --output "$output_path" \
        --match-filter "duration > $MIN_DURATION & duration < $MAX_DURATION" \
        --max-downloads 1 \
        --no-playlist \
        --write-info-json \
        --embed-subs \
        --write-auto-subs \
        --extract-flat false \
        "ytsearch1:$query" || {
            log "Failed to download video for query: $query"
            return 1
        }
    
    if [[ -f "$output_path" ]]; then
        log "Successfully downloaded: $filename"
        
        # Verify video properties
        local duration=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$output_path" 2>/dev/null || echo "0")
        local width=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width -of csv=p=0 "$output_path" 2>/dev/null || echo "0")
        local height=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=height -of csv=p=0 "$output_path" 2>/dev/null || echo "0")
        
        log "Video properties - Duration: ${duration}s, Resolution: ${width}x${height}"
        
        # Check if video meets quality requirements
        if (( $(echo "$duration < $MIN_DURATION" | bc -l) )); then
            log "Video too short, removing: $filename"
            rm -f "$output_path"
            return 1
        fi
        
        return 0
    else
        log "Download failed for: $query"
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