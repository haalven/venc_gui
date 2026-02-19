# venc

FFmpeg command builder for VideoToolbox (Apple Silicon hardware)

![example screenshot](screenshot.png)

Syntax:
`ffmpeg
  -hwaccel videotoolbox
  -hwaccel_output_format videotoolbox_vld
  -i input.mkv
  -vf "scale_vt=w=1280:h=720"
  -c:v hevc_videotoolbox
  -q:v 66
  -tag:v hvc1
  -c:a aac_at
  output.mp4`
