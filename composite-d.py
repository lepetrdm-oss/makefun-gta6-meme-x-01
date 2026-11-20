"""Version D: "200 GB" — composite the exact vector ghost (ghost.png)
beside an overflowing bin of deleted game cases in a generated gamer-room
scene whose monitor shows a Vice City sunset scene and a barely-started
download bar. A vector game case is mid-toss into the bin. Captions are
rendered crisply on top. Drawn at 2x supersample, downscaled at the end.

    ~/workspace/airdrop-agent/.venv/bin/python composite-d.py
"""
import glob
import pathlib

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
BG = HERE / "media-generation-bg-d-download-0-018d4db8-3287-4178-9684-5a37e06023c9.webp"
OUT = HERE / "meme-d.png"
POST = HERE / "meme-d-post.jpg"
PREVIEW = pathlib.Path("/tmp/meme-d-480.png")

SS = 2  # supersample factor
W, H = 1920, 1280

INK = (13, 13, 18)
WHITE = (255, 255, 255)
YELLOW = (255, 210, 63)
MAGENTA = (214, 0, 109)
NEON = (255, 43, 150)
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

    def _p(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def ellipse(self, box, **kw):
        if "width" in kw:
            kw["width"] *= SS
        self.d.ellipse(self._b(box), **kw)

    def rounded_rectangle(self, box, radius, **kw):
        if "width" in kw:
            kw["width"] *= SS
        self.d.rounded_rectangle(self._b(box), radius=radius * SS, **kw)

    def rectangle(self, box, **kw):
        if "width" in kw:
            kw["width"] *= SS
        self.d.rectangle(self._b(box), **kw)

    def polygon(self, pts, **kw):
        if "width" in kw:
            kw["width"] *= SS
        self.d.polygon(self._p(pts), **kw)

    def line(self, pts, width=1, **kw):
        self.d.line(self._p(pts), width=width * SS, **kw)

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


def make_game_case(w=150, h=195):
    """One generic game case on its own transparent layer (final-res units)."""
    layer = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    pen = Pen(layer)
    pen.rounded_rectangle([4, 4, w - 4, h - 4], radius=10,
                          fill=(24, 78, 160), outline=INK, width=6)
    pen.rounded_rectangle([16, 16, w - 16, h - 60], radius=6,
                          fill=MAGENTA)
    # simple white star on the cover, no text
    cx, cy, r = w / 2, 62, 30
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    pen.polygon(pts, fill=WHITE)
    pen.rectangle([16, h - 44, w - 16, h - 30], fill=(230, 230, 235))
    return layer


def paste_rotated(base, layer, cx, cy, angle):
    rot = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(rot, (round((cx - rot.width / SS / 2) * SS),
                               round((cy - rot.height / SS / 2) * SS)))


def main() -> None:
    img = Image.open(BG).convert("RGB").resize((W * SS, H * SS), Image.LANCZOS)
    img = img.convert("RGBA")
    pen = Pen(img)

    # --- sharpen the joke on the monitor: a download bar that has
    #     barely moved (the painted bar in the art is an empty outline) ---
    pen.rounded_rectangle([376, 594, 740, 624], radius=8,
                          fill=(8, 8, 14), outline=WHITE, width=3)
    pen.rounded_rectangle([382, 600, 412, 618], radius=5, fill=NEON)

    # --- a game case mid-toss, arcing into the overflowing bin ------------
    paste_rotated(img, make_game_case(), 1315, 652, -22)
    pen = Pen(img)

    # --- soft shadow under the ghost ---------------------------------------
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([1400 * SS, 1200 * SS, 1900 * SS, 1262 * SS], fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10 * SS // 2))
    img = Image.alpha_composite(img, shadow)
    pen = Pen(img)

    # --- the ghost, exact drawing from ghost.png, standing by the bin -----
    ghost = Image.open(HERE / "ghost.png").convert("RGBA")
    ghost = ghost.crop(ghost.getchannel("A").getbbox())
    target_h = 545 * SS
    scale = target_h / ghost.height
    ghost = ghost.resize((round(ghost.width * scale), target_h), Image.LANCZOS)
    gx = round((1615 - ghost.width / SS / 2) * SS)
    gy = round((1268 - 545) * SS)
    # magenta rim light on the ghost's left edge (screen-side glow)
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
    pen = Pen(img)

    # --- top caption ----------------------------------------------------------
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, 0, W * SS, 185 * SS], fill=(5, 3, 12, 85))
    band = band.filter(ImageFilter.GaussianBlur(6 * SS // 2))
    img = Image.alpha_composite(img, band)
    pen = Pen(img)
    cap = fit_font(pen, "GTA 6 NEEDS 200 GB", W - 120, 118)
    draw_mixed(pen, W // 2, 30,
               [("GTA 6 NEEDS ", WHITE), ("200 GB", YELLOW)], cap, 11)

    # --- bottom caption over a soft dark band ---------------------------------
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, 1150 * SS, W * SS, H * SS], fill=(5, 3, 12, 115))
    band = band.filter(ImageFilter.GaussianBlur(6 * SS // 2))
    img = Image.alpha_composite(img, band)
    pen = Pen(img)
    bot = fit_font(pen, "SO I DELETED EVERYTHING ELSE", W - 120, 104)
    draw_mixed(pen, W // 2, 1172,
               [("SO I DELETED ", WHITE), ("EVERYTHING ELSE", YELLOW)], bot, 10)

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
