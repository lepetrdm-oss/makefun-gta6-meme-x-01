"""Version A: composite the vector ghost into the generated cinematic
background, with a ground shadow, a magenta rim light, the speech bubble
and the captions rendered on top as crisp text.

    ~/workspace/airdrop-agent/.venv/bin/python composite-a.py
"""
import glob
import pathlib

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
BG = HERE / "media-generation-bg-a-0-c52360b7-c752-4963-8c26-55fe8ff20f4d.webp"
OUT = HERE / "meme-a.png"

INK = (13, 5, 24)
DARK = (20, 16, 31)
YELLOW = (255, 210, 63)
MAGENTA = (214, 0, 109)
RIM = (255, 46, 136)


def font(size: int) -> ImageFont.FreeTypeFont:
    paths = glob.glob("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
    if not paths:
        paths = glob.glob("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    return ImageFont.truetype(paths[0], size)


def draw_mixed(draw, cx, y, parts, fnt, stroke_w):
    """Draw a line made of (text, fill) parts, centred on cx. Returns height."""
    widths = [draw.textlength(t, font=fnt) for t, _ in parts]
    x = cx - sum(widths) / 2
    for (text, fill), w in zip(parts, widths):
        draw.text((x, y), text, font=fnt, fill=fill,
                  stroke_width=stroke_w, stroke_fill=INK)
        x += w
    return fnt.size


def main() -> None:
    img = Image.open(BG).convert("RGB")
    W, H = img.size  # 1920 x 1280

    # --- ghost, trimmed to its alpha bbox ---------------------------------
    ghost = Image.open(HERE / "ghost.png").convert("RGBA")
    ghost = ghost.crop(ghost.getchannel("A").getbbox())
    target_h = 580
    scale = target_h / ghost.height
    ghost = ghost.resize((round(ghost.width * scale), target_h),
                         Image.LANCZOS)
    gx = 860 - ghost.width // 2          # ghost centre x
    gy = 1135 - ghost.height             # ghost top y (feet at 1135)
    cx = gx + ghost.width // 2

    # --- soft ground shadow ------------------------------------------------
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([cx - 250, 1118, cx + 250, 1168], fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img.convert("RGBA"), shadow)

    # --- magenta rim light: silhouette peeking on the ghost's left edge ---
    alpha = ghost.getchannel("A")
    rim = Image.new("RGBA", ghost.size, RIM + (255,))
    rim.putalpha(alpha)
    glow = rim.resize((rim.width + 200, rim.height + 200), Image.LANCZOS)
    glow.putalpha(glow.getchannel("A").point(lambda a: int(a * 0.30)))
    glow = glow.filter(ImageFilter.GaussianBlur(45))
    img.alpha_composite(glow, (gx - 108, gy - 100))
    img.alpha_composite(rim, (gx - 8, gy - 2))

    # --- the ghost itself ---------------------------------------------------
    img.alpha_composite(ghost, (gx, gy))

    draw = ImageDraw.Draw(img)

    # --- top captions --------------------------------------------------------
    cap = font(122)
    draw_mixed(draw, W // 2, 30, [("WAITED 13 YEARS", (255, 255, 255))], cap, 11)
    draw_mixed(draw, W // 2, 168,
               [("FOR ", (255, 255, 255)), ("GTA 6", YELLOW)], cap, 11)

    # --- speech bubble -------------------------------------------------------
    bx0, by0, bx1, by1 = 1000, 300, 1610, 545
    tip = (982, 590)
    base_l, base_r = 1062, 1202
    draw.polygon([(base_l, by1 - 6), (base_r, by1 - 6), tip],
                 fill=(255, 255, 255))
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=34,
                           fill=(255, 255, 255), outline=(13, 13, 18), width=8)
    # tail sides, then erase the bubble border where the tail joins
    draw.line([(base_l, by1 - 2), tip], fill=(13, 13, 18), width=8)
    draw.line([(base_r, by1 - 2), tip], fill=(13, 13, 18), width=8)
    draw.rectangle([base_l + 5, by1 - 5, base_r - 5, by1 + 5],
                   fill=(255, 255, 255))
    bub = font(54)
    bcx = (bx0 + bx1) // 2
    draw_mixed(draw, bcx, 330, [("I spent the wait", DARK)], bub, 0)
    draw_mixed(draw, bcx, 392, [("winning bounties", DARK)], bub, 0)
    draw_mixed(draw, bcx, 454,
               [("on ", DARK), ("make.fun", MAGENTA)], bub, 0)

    # --- bottom caption over a soft dark band --------------------------------
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, 1146, W, H], fill=(5, 3, 12, 110))
    band = band.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, band)
    draw = ImageDraw.Draw(img)
    bot = font(98)
    draw_mixed(draw, W // 2, 1162,
               [("LAUNCH DAY. ", (255, 255, 255)), ("FINALLY.", YELLOW)],
               bot, 10)

    img.convert("RGB").save(OUT)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
