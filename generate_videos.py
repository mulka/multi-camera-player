#!/usr/bin/env python3
"""Generate test videos for multi-camera player using PIL frames + ffmpeg."""
import subprocess, os, struct
from PIL import Image, ImageDraw, ImageFont

W, H = 320, 240
FPS = 15
DURATION = 60  # seconds per video
COLORS = [
    (26, 26, 46),   # cam1 - dark navy
    (22, 33, 62),   # cam2 - dark blue
    (15, 52, 96),   # cam3 - blue
    (83, 52, 131),  # cam4 - purple
    (43, 45, 66),   # cam5 - slate
    (0, 109, 119),  # cam6 - teal
]

os.makedirs("videos", exist_ok=True)

# Try to get a monospace font
try:
    font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 72)
    font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
    font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
except:
    font_big = ImageFont.load_default()
    font_med = ImageFont.load_default()
    font_sm = ImageFont.load_default()

def generate_video(seg, cam):
    color = COLORS[cam - 1]
    outfile = f"videos/seg{seg}_cam{cam}.mp4"
    seg_label = f"Segment {seg}"
    cam_label = f"Camera {cam}"

    proc = subprocess.Popen([
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "pipe:0",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "35",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        outfile
    ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    total_frames = FPS * DURATION
    for f in range(total_frames):
        t = f / FPS
        seconds = int(t)
        
        img = Image.new("RGB", (W, H), color)
        draw = ImageDraw.Draw(img)
        
        # Segment label at top
        bbox = draw.textbbox((0, 0), seg_label, font=font_med)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, 12), seg_label, fill=(255, 255, 0), font=font_med)
        
        # Big second counter in center
        count_text = str(seconds)
        bbox = draw.textbbox((0, 0), count_text, font=font_big)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((W - tw) // 2, (H - th) // 2 - 15), count_text, fill=(255, 255, 255), font=font_big)
        
        # Timestamp below counter
        ts_text = f"{seconds // 60:02d}:{seconds % 60:02d}.{int((t % 1) * 10)}"
        bbox = draw.textbbox((0, 0), ts_text, font=font_sm)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, H // 2 + 40), ts_text, fill=(200, 200, 200), font=font_sm)
        
        # Camera label at bottom
        bbox = draw.textbbox((0, 0), cam_label, font=font_med)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, H - 35), cam_label, fill=(0, 255, 255), font=font_med)
        
        proc.stdin.write(img.tobytes())
    
    proc.stdin.close()
    proc.wait()
    size = os.path.getsize(outfile)
    print(f"  {outfile} ({size // 1024}KB)")

for seg in [1, 2]:
    for cam in range(1, 7):
        generate_video(seg, cam)

print("Done! Generated 12 test videos.")
