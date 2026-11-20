"""Version E: "13 years vs 6" — composite the exact vector ghost
(ghost.png) onto the free left cushion of a generated living-room scene,
as the third player on the couch next to a tearful dad and his puzzled
6-year-old son, both holding controllers in front of a Vice City sunset
TV. Captions are rendered crisply on top. Drawn at 2x supersample,
downscaled at the end.

    ~/workspace/airdrop-agent/.venv/bin/python composite-e.py
"""
import glob
import pathlib

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
BG = sorted(HERE.glob("media-generation-*bg-e-dadson*.webp"))[0]
OUT = HERE / "meme-e.png"
POST = HERE / "meme-e-post.jpg"
PREVIEW = pathlib.Path("/tmp/meme-e-480.png")

SS = 2  # supersample factor
W, H = 1920, 1280

WHITE = (255, 255, 255)
YELLOW = (255, 210, 63)
RIM = (255, 46, 136)


def font(size: int) -> ImageFont.FreeTypeFont:
    paths = glob.glob("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
    if not paths:
        paths = glob.glob("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    return ImageFont.truetype(paths[0], size * SS)


def fit_font(draw, text, max_w, start):
    """Largest font (<= start) whose text fits max_w (final-res units)."""
    size = start
    while size > 10:
        f = font(size)
        if draw.textlength(text, f) / SS <= max_w:
            return f
        size -= 2
    return font(size)


class Pen:
    """ImageDraw wrapper that takes final-res coordinates."""

    def __init__(self, img):
        self.d = ImageDraw.Draw(img)

    def _b(self, box):
        return [v * SS for v in box]

    def ellipse(self, box, **kw):
        if "width" in kw:
            kw["width"] *= SS
        self.d.ellipse(self._b(box), **kw)

    def text(self, xy, text, fnt, **kw):
        if "stroke_width" in kw:
            kw["stroke_width"] *= SS
        self.d.text((xy[0] * SS, xy[1] * SS), text, font=fnt, **kw)

    def textlength(self, text, fnt):
        return self.d.textlength(text, font=fnt) / SS


def draw_mixed(pen, cx, y, parts, fnt, stroke_w):
    """Draw a line of (text, fill) parts centred on cx. Returns height."""
    widths = [pen.textlength(t, fnt) for t, _ in parts]
    x = cx - sum(widths) / 2
    for (text, fill), w in zip(parts, widths):
        pen.text((x, y), text, fnt, fill=fill,
                 stroke_width=stroke_w, stroke_fill=(13, 5, 24))
        x += w
    return fnt.size // SS


def main() -> None:
    img = Image.open(BG).convert("RGB").resize((W * SS, H * SS), Image.LANCZOS)
    img = img.convert("RGBA")

    # --- soft shadow on the cushion under the ghost -------------------------
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([25 * SS, 985 * SS, 485 * SS, 1050 * SS], fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10 * SS // 2))
    img = Image.alpha_composite(img, shadow)

    # --- the ghost, exact drawing from ghost.png, sitting on the free
    #     left cushion as the third player on the couch ----------------------
    ghost = Image.open(HERE / "ghost.png").convert("RGBA")
    ghost = ghost.crop(ghost.getchannel("A").getbbox())
    target_h = 480 * SS
    scale = target_h / ghost.height
    ghost = ghost.resize((round(ghost.width * scale), target_h), Image.LANCZOS)
    gx = round((282 - ghost.width / SS / 2) * SS)
    gy = round((1025 - 480) * SS)
    # magenta rim light on the ghost (TV-side glow), as in versions C/D
    alpha = ghost.getchannel("A")
    rim = Image.new("RGBA", ghost.size, RIM + (255,))
    rim.putalpha(alpha)
    glow = rim.resize((rim.width + 40 * SS, rim.height + 40 * SS),
                      Image.LANCZOS)
    glow.putalpha(glow.getchannel("A").point(lambda a: int(a * 0.22)))
    glow = glow.filter(ImageFilter.GaussianBlur(12 * SS))
    img.alpha_composite(glow, (gx - 24 * SS, gy - 24 * SS))
    img.alpha_composite(rim, (gx - 7 * SS, gy - 2 * SS))
    img.alpha_composite(ghost, (gx, gy))

    # --- top caption ---------------------------------------------------------
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, 0, W * SS, 185 * SS], fill=(5, 3, 12, 85))
    band = band.filter(ImageFilter.GaussianBlur(6 * SS // 2))
    img = Image.alpha_composite(img, band)
    pen = Pen(img)
    cap = fit_font(pen, "WAITED 13 YEARS FOR GTA 6", W - 120, 118)
    draw_mixed(pen, W // 2, 30,
               [("WAITED ", WHITE), ("13 YEARS", YELLOW),
                (" FOR GTA 6", WHITE)], cap, 11)

    # --- bottom caption over a soft dark band --------------------------------
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, 1150 * SS, W * SS, H * SS], fill=(5, 3, 12, 115))
    band = band.filter(ImageFilter.GaussianBlur(6 * SS // 2))
    img = Image.alpha_composite(img, band)
    pen = Pen(img)
    bot = fit_font(pen, "MY SON HAS ONLY EXISTED FOR 6", W - 120, 104)
    draw_mixed(pen, W // 2, 1172,
               [("MY SON HAS ONLY EXISTED FOR ", WHITE), ("6", YELLOW)],
               bot, 10)

    img = img.resize((W, H), Image.LANCZOS).convert("RGB")
    img.save(OUT)
    print("wrote", OUT, img.size)

    # brightened copy for posting
    post = ImageEnhance.Brightness(img).enhance(1.13)
    post = ImageEnhance.Color(post).enhance(1.05)
    post.save(POST, quality=90)
    print("wrote", POST, post.size)

    # small preview for the readability check (not committed)
    img.resize((480, 320), Image.LANCZOS).save(PREVIEW)
    print("wrote", PREVIEW)


if __name__ == "__main__":
    main()
