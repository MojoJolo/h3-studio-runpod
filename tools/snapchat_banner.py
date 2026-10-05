"""Burn a Snapchat-style caption bar onto any video: a full-width translucent
dark bar with centered bold white text, upper-third of the frame.

This matches gui/server.py's render_caption_bar()/burn_caption() exactly —
the same style already used by the Auto loop's caption step — so manual
captioning and the automated pipeline stay visually identical. Rendered as
a transparent PNG via PIL and composited with ffmpeg's overlay filter,
since this system's ffmpeg build has no drawtext/libfreetype support.

General-purpose tool, not scoped to any one series.

Usage:
    python3 tools/snapchat_banner.py <input_video> "<caption text>" <output_video> [--position top|middle|bottom]
"""
import argparse
import subprocess
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
BAR_RGBA = (45, 45, 45, 190)
TEXT_COLOR = (255, 255, 255, 255)

POSITIONS = {
    "top": 0.12,
    "middle": 0.46,
    "bottom": 0.80,
}


def _probe_dims(input_video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", input_video],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    w, h = out.split(",")
    return int(w), int(h)


def render_banner_png(caption, width, height, position="top", out_png=None):
    """Render the Snapchat-style caption bar as an RGBA PNG the same size
    as the video — identical style to gui/server.py's render_caption_bar()."""
    if position not in POSITIONS:
        raise ValueError(f"position must be one of {list(POSITIONS)}")

    pad_x = int(width * 0.06)
    max_text_w = width - 2 * pad_x
    font_size = max(16, int(width * 0.042))
    font = ImageFont.truetype(FONT_PATH, font_size)

    scratch = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scratch)

    def line_width(s):
        box = draw.textbbox((0, 0), s, font=font)
        return box[2] - box[0]

    words = caption.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if line_width(trial) <= max_text_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lines = lines[:3]  # hard cap — a caption this long isn't "a few words" anymore

    line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
    line_spacing = int(line_h * 0.35)
    text_block_h = len(lines) * line_h + (len(lines) - 1) * line_spacing
    pad_y = int(font_size * 0.6)
    bar_h = text_block_h + 2 * pad_y
    bar_top = int(height * POSITIONS[position])

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, bar_top, width, bar_top + bar_h], fill=BAR_RGBA)

    y = bar_top + pad_y
    for line in lines:
        w = line_width(line)
        x = (width - w) // 2
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += line_h + line_spacing

    if out_png:
        img.save(out_png)
    return img


def apply_banner(input_video, caption, output_video, position="top"):
    width, height = _probe_dims(input_video)
    png_path = output_video.rsplit(".", 1)[0] + "_banner.png"
    render_banner_png(caption, width, height, position, png_path)

    cmd = [
        "ffmpeg", "-y", "-i", input_video, "-i", png_path,
        "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
        "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-c:a", "copy",
        output_video,
    ]
    subprocess.run(cmd, check=True)
    return output_video


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_video")
    parser.add_argument("caption")
    parser.add_argument("output_video")
    parser.add_argument("--position", choices=list(POSITIONS), default="top")
    args = parser.parse_args()
    out = apply_banner(args.input_video, args.caption, args.output_video, args.position)
    print("saved:", out)
