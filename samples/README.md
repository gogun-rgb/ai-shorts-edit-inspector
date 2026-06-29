# Samples

Do not commit copyrighted videos or user videos here.

For local integration testing, generate a tiny MP4 with FFmpeg:

```powershell
ffmpeg -y -f lavfi -i "testsrc=size=540x960:rate=30:duration=4" -f lavfi -i "sine=frequency=880:duration=1" -filter_complex "[1:a]adelay=1000|1000,apad=pad_dur=3[a]" -map 0:v -map "[a]" -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac samples/test-short.mp4
```

