"""Generate a shareable 'quote card' still image from a drama scene: a strong
frame + its best exchange (both speakers' lines, each in that character's
own color), styled like a speaker-labeled caption card, for standalone
social posts separate from the video itself.

General-purpose tool for ANY series, not scoped to one. Each character's
label color should be defined once (e.g. in that series' bible.json under
characters.<name>.quote_card_color) and reused consistently across every
card for that series.

Currently renders ONE panel (one frame + its exchange). Designed so a future
multi-panel card is just calling render_panel() per exchange and stacking
the results vertically — not a redesign.
"""
import sys
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
BAR_RGBA = (20, 20, 20, 205)
LINE_TEXT_COLOR = (255, 255, 255, 255)
DEFAULT_SPEAKER_COLOR = (255, 209, 102, 255)  # warm gold fallback


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        box = draw.textbbox((0, 0), trial, font=font)
        if box[2] - box[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_panel(image_path, exchange, out_path):
    """exchange: list of (speaker_name, line, rgba_color_or_None) tuples,
    rendered in order as speaker-labeled lines stacked in one bar at the
    bottom of image_path. A None color falls back to DEFAULT_SPEAKER_COLOR."""
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    pad_x = int(width * 0.08)
    max_text_w = width - 2 * pad_x
    speaker_font_size = max(16, int(width * 0.044))
    line_font_size = max(18, int(width * 0.05))
    speaker_font = ImageFont.truetype(FONT_PATH, speaker_font_size)
    line_font = ImageFont.truetype(FONT_PATH, line_font_size)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    lh_speaker = speaker_font.getbbox("Ag")[3] - speaker_font.getbbox("Ag")[1]
    lh_line = line_font.getbbox("Ag")[3] - line_font.getbbox("Ag")[1]
    spacing = int(lh_line * 0.3)
    gap_after_speaker = int(lh_speaker * 0.35)
    gap_between_turns = int(lh_line * 0.55)

    # Pre-wrap every turn's line so we know the total block height up front.
    wrapped_turns = []
    for speaker, line, color in exchange:
        wrapped = _wrap(draw, line, line_font, max_text_w)
        wrapped_turns.append((speaker, wrapped, color or DEFAULT_SPEAKER_COLOR))

    text_block_h = 0
    for _, wrapped, _ in wrapped_turns:
        text_block_h += lh_speaker + gap_after_speaker
        text_block_h += len(wrapped) * lh_line + (len(wrapped) - 1) * spacing
    text_block_h += gap_between_turns * (len(wrapped_turns) - 1)

    pad_y = int(line_font_size * 0.65)
    bar_h = text_block_h + 2 * pad_y
    # Anchor the TOP of the bar at the vertical center rather than pinning
    # the bottom to the very edge — sitting flush against the bottom (or
    # even at 3/4) read as too cramped/low. Half keeps faces fully visible
    # above the bar while still landing as a bold, clean 50/50 split.
    bar_top = int(height * 0.50)
    bar_bottom = bar_top + bar_h

    draw.rectangle([0, bar_top, width, bar_bottom], fill=BAR_RGBA)

    y = bar_top + pad_y
    for i, (speaker, wrapped, color) in enumerate(wrapped_turns):
        # Alternating alignment, like a message thread: first speaker left,
        # second speaker right, and so on — makes a back-and-forth exchange
        # easier to read at a glance than two lines stacked flush-left.
        align_right = i % 2 == 1

        def x_for(text, font):
            if not align_right:
                return pad_x
            box = draw.textbbox((0, 0), text, font=font)
            return width - pad_x - (box[2] - box[0])

        speaker_label = speaker.upper()
        draw.text((x_for(speaker_label, speaker_font), y), speaker_label, font=speaker_font, fill=color)
        y += lh_speaker + gap_after_speaker
        for l in wrapped:
            draw.text((x_for(l, line_font), y), l, font=line_font, fill=LINE_TEXT_COLOR)
            y += lh_line + spacing
        if i < len(wrapped_turns) - 1:
            y += gap_between_turns

    out = Image.alpha_composite(img, overlay).convert("RGB")
    out.save(out_path, quality=95)
    return out_path


def render_quote_card(image_path, exchange, out_path):
    """Single-panel quote card (today's default). `exchange` is a list of
    (speaker, line, color) tuples for one frame's exchange. Multi-panel
    cards will call render_panel() per exchange and vstack the results —
    not implemented yet, kept for when panel_count > 1 is needed."""
    return render_panel(image_path, exchange, out_path)


# Facebook feed photo posts: 1080x1350 (4:5 portrait) is the current
# recommendation — it fills more of the mobile feed than our native 9:16
# video frame would, which Facebook instead shrinks/crops. Confirmed via
# search (Buffer/Hootsuite/SocialSizes, Sept 2026 guides) rather than assumed.
FB_FEED_SIZE = (1080, 1350)


def resize_for_facebook_feed(image_path, out_path, target=FB_FEED_SIZE):
    """Fit a (typically 9:16) image into the 4:5 Facebook feed ratio without
    cropping any of the actual content: scale the source to fit the target
    HEIGHT, center it, and fill the leftover side space with a blurred,
    cover-scaled copy of the same image as a backdrop — the common
    letterbox-without-black-bars technique, rather than plain black/solid
    bars or a crop that would cut off the subjects or the caption bar."""
    src = Image.open(image_path).convert("RGB")
    tw, th = target
    sw, sh = src.size

    # Foreground: scale to fit target height, preserving aspect ratio.
    fg_h = th
    fg_w = round(sw * (fg_h / sh))
    fg = src.resize((fg_w, fg_h), Image.LANCZOS)

    # Backdrop: scale to COVER the full target (may overflow), then blur.
    cover_scale = max(tw / sw, th / sh)
    bg_w, bg_h = round(sw * cover_scale), round(sh * cover_scale)
    bg = src.resize((bg_w, bg_h), Image.LANCZOS)
    bg = bg.crop((
        (bg_w - tw) // 2, (bg_h - th) // 2,
        (bg_w - tw) // 2 + tw, (bg_h - th) // 2 + th,
    ))
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    # Darken slightly so the sharp foreground reads as clearly primary.
    bg = Image.blend(bg, Image.new("RGB", bg.size, (0, 0, 0)), 0.25)

    canvas = bg.copy()
    canvas.paste(fg, ((tw - fg_w) // 2, (th - fg_h) // 2))
    canvas.save(out_path, quality=95)
    return out_path


def generate_quote_card(image_path, exchange, out_path):
    """Default entry point going forward: renders the quote card at native
    resolution AND a Facebook-feed-ready 4:5 version, since a Reels/Stories-
    style 9:16 post and a feed photo post want different crops of the same
    card. `out_path` names the native file; the feed version is saved
    alongside it with an '-fb' suffix before the extension. Returns
    (native_path, fb_path)."""
    render_quote_card(image_path, exchange, out_path)
    root, ext = out_path.rsplit(".", 1)
    fb_path = f"{root}-fb.{ext}"
    resize_for_facebook_feed(out_path, fb_path)
    return out_path, fb_path


def load_character_colors(bible_path):
    """Read characters.<name>.quote_card_color (an [r,g,b] or [r,g,b,a] list)
    from a series bible.json, returning {name: rgba_tuple}."""
    with open(bible_path) as fh:
        bible = json.load(fh)
    colors = {}
    for name, c in bible.get("characters", {}).items():
        rgb = c.get("quote_card_color")
        if rgb:
            colors[name] = tuple(rgb) if len(rgb) == 4 else tuple(rgb) + (255,)
    return colors


if __name__ == "__main__":
    # CLI demo: quote_card.py <image> <speaker1> <line1> <speaker2> <line2> <out>
    src, s1, l1, s2, l2, out = sys.argv[1:7]
    native, fb = generate_quote_card(src, [(s1, l1, None), (s2, l2, None)], out)
    print("saved native (9:16-ish, as generated):", native)
    print("saved Facebook feed-ready (1080x1350):", fb)
