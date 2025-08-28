# Staging Video Feed Role

## Purpose
Provides virtual camera feed for parking monitor testing in staging environments. This role automatically:
- Downloads parking lot surveillance footage
- Creates V4L2 virtual camera device
- Streams video content as fake camera feed
- Integrates seamlessly with parking monitor service

## Deployment Scope
- **Environment**: Staging environments only
- **Detection**: Automatically deployed when `parking_monitor.enabled: true` AND `oa_environment.stage == "staging"`
- **Service**: `com.orangead.staging-video-feed`
- **Virtual Device**: `/dev/video1` (leaves `/dev/video0` for future real cameras)

## Dependencies
- v4l2loopback (virtual camera kernel module)
- ffmpeg (video processing and streaming)
- yt-dlp (YouTube video download)
- parking monitor service (coordination)

## Integration
- Creates virtual camera before parking monitor starts
- Parking monitor uses `camera.source: 1` in staging
- Automatic service lifecycle management
- Health monitoring and recovery

## Video Content
- 1080p parking lot surveillance footage
- Multiple scenario videos (empty, half-full, full lots)
- Angled overhead perspectives
- Auto-cycling through different scenarios