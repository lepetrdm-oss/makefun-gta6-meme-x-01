"""Version C: "we both called in sick" — composite the exact vector ghost
and a flat-vector boss onto a generated living-room background, both
holding controllers in front of a TV showing a Vice City game scene with
a neon make.fun sign. Captions and the speech bubble are rendered crisply
on top. Drawn at 2x supersample and downscaled for smooth vector edges.

    ~/workspace/airdrop-agent/.venv/bin/python composite-c.py
"""
import glob
import pathlib

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
BG = HERE / "media-generation-bg-c-livingroom-0-c14343b9-d298-484b-8a4a-35ef521c989e.webp"
OUT = HERE / "meme-c.png"

SS = 2  # supersample factor
W, H = 1920, 1280

INK = (13, 13, 18)
DARK = (20, 16, 31)
WHITE = (255, 255, 255)
YELLOW = (255, 210, 63)
MAGENTA = (214, 0, 109)
NEON = (255, 43, 150)
RIM = (255, 46, 136)

SUIT = (43, 47, 64)
SUIT_DARK = (33, 36, 49)
SHIRT = (238, 240, 244)
TIE = (163, 22, 33)
SKIN = (238, 189, 147)
SKIN_SHADOW = (217, 160, 111)
HAIR = (38, 34, 31)
PAD = (32, 34, 44)
PAD_DARK = (20, 21, 28)


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
        if draw.textlength(text, f) <= max_w:
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

    def pieslice(self, box, start, end, **kw):
        if "width" in kw:
            kw["width"] *= SS
        self.d.pieslice(self._b(box), start, end, **kw)

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


def make_controller(width=260):
    """A gamepad on its own transparent layer (final-res units)."""
    h = 170
    layer = Image.new("RGBA", (width * SS, h * SS), (0, 0, 0, 0))
    pen = Pen(layer)
    sx = width / 260  # design is 260 wide; scale x coords
    def X(v):
        return v * sx
    # grips
    pen.ellipse([X(6), 82, X(80), 162], fill=PAD, outline=INK, width=6)
    pen.ellipse([X(180), 82, X(254), 162], fill=PAD, outline=INK, width=6)
    # body
    pen.rounded_rectangle([X(18), 28, X(242), 122], radius=42,
                          fill=PAD, outline=INK, width=6)
    # left stick
    pen.ellipse([X(58), 52, X(96), 90], fill=(52, 55, 67), outline=INK, width=4)
    pen.ellipse([X(69), 63, X(85), 79], fill=PAD_DARK)
    # d-pad
    pen.rectangle([X(112), 62, X(140), 76], fill=PAD_DARK)
    pen.rectangle([X(119), 55, X(133), 83], fill=PAD_DARK)
    # buttons (one magenta brand accent)
    for (bx, by, col) in [(188, 50, (224, 33, 138)), (208, 68, YELLOW),
                          (188, 86, (45, 200, 190)), (168, 68, (230, 230, 235))]:
        pen.ellipse([X(bx - 8), by - 8, X(bx + 8), by + 8], fill=col,
                    outline=INK, width=3)
    # centre pill
    pen.rounded_rectangle([X(118), 36, X(142), 46], radius=5, fill=(52, 55, 67))
    return layer


def paste_rotated(base, layer, cx, cy, angle):
    rot = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(rot, (round((cx - rot.width / SS / 2) * SS),
                               round((cy - rot.height / SS / 2) * SS)))


def draw_boss(pen):
    """Flat-vector boss, deadpan, seated at centre x=1230, bottom=1280."""
    cx = 1230
    # neck
    pen.rectangle([cx - 30, 845, cx + 30, 912], fill=SKIN_SHADOW)
    # torso (suit)
    pen.rounded_rectangle([1010, 890, 1450, 1305], radius=95,
                          fill=SUIT, outline=INK, width=6)
    # shirt
    pen.polygon([(cx - 34, 892), (cx + 34, 892), (cx + 62, 1052),
                 (cx, 1122), (cx - 62, 1052)], fill=SHIRT)
    # lapels
    pen.polygon([(cx - 34, 892), (cx, 1002), (cx - 58, 1052), (cx - 72, 918)],
                fill=SUIT_DARK)
    pen.polygon([(cx + 34, 892), (cx, 1002), (cx + 58, 1052), (cx + 72, 918)],
                fill=SUIT_DARK)
    # tie
    pen.polygon([(cx - 13, 894), (cx + 13, 894), (cx + 7, 928), (cx - 7, 928)],
                fill=TIE)
    pen.polygon([(cx - 7, 928), (cx + 7, 928), (cx + 19, 1030),
                 (cx, 1088), (cx - 19, 1030)], fill=TIE)
    # arms: ink underlay then suit, shoulders -> elbows -> wrists
    arm_l = [(1052, 952), (1085, 1062), (1152, 1112)]
    arm_r = [(1408, 952), (1375, 1062), (1308, 1112)]
    for arm in (arm_l, arm_r):
        pen.line(arm, width=84, fill=INK, joint="curve")
    for arm in (arm_l, arm_r):
        pen.line(arm, width=66, fill=SUIT, joint="curve")
    # head: ears, face, hair
    pen.ellipse([cx - 106, 762, cx - 76, 792], fill=SKIN, outline=INK, width=4)
    pen.ellipse([cx + 76, 762, cx + 106, 792], fill=SKIN, outline=INK, width=4)
    pen.ellipse([cx - 88, 682, cx + 88, 866], fill=SKIN, outline=INK, width=6)
    pen.pieslice([cx - 94, 662, cx + 94, 818], 180, 360, fill=HAIR,
                 outline=INK, width=5)
    pen.pieslice([cx - 77, 686, cx + 77, 820], 180, 360, fill=SKIN)
    # deadpan face: flat brows, half-lidded eyes, straight mouth
    pen.line([(cx - 54, 758), (cx - 9, 754)], width=7, fill=HAIR)
    pen.line([(cx + 9, 754), (cx + 54, 758)], width=7, fill=HAIR)
    for ex in (cx - 50, cx + 13):
        pen.line([(ex, 778), (ex + 36, 778)], width=6, fill=INK)
        pen.pieslice([ex + 5, 770, ex + 31, 790], 0, 180, fill=INK)
    pen.line([(cx, 786), (cx - 4, 808), (cx + 4, 810)], width=4,
             fill=(201, 143, 95))
    pen.line([(cx - 34, 832), (cx - 25, 836), (cx + 25, 836), (cx + 34, 832)],
             width=7, fill=(74, 50, 38))


def main() -> None:
    img = Image.open(BG).convert("RGB").resize((W * SS, H * SS), Image.LANCZOS)
    img = img.convert("RGBA")
    pen = Pen(img)

    # --- neon make.fun sign worked into the TV's game scene ----------------
    sign = Image.new("RGBA", (760 * SS, 180 * SS), (0, 0, 0, 0))
    spen = Pen(sign)
    sf = font(76)
    tw = spen.textlength("make.fun", sf)
    glow = Image.new("RGBA", sign.size, (0, 0, 0, 0))
    gpen = Pen(glow)
    gpen.text(((760 - tw) / 2, 42), "make.fun", sf, fill=NEON + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(16 * SS // 2))
    sign.alpha_composite(glow)
    sign.alpha_composite(glow)
    spen.text(((760 - tw) / 2, 42), "make.fun", sf, fill=(255, 236, 248),
              stroke_width=1, stroke_fill=MAGENTA)
    sign = sign.rotate(-2, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(sign, (round((810 - sign.width / SS / 2) * SS),
                               round((355 - sign.height / SS / 2) * SS)))

    # --- soft shadows on the couch ------------------------------------------
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([545 * SS, 1195 * SS, 1055 * SS, 1258 * SS], fill=(0, 0, 0, 95))
    sd.ellipse([1035 * SS, 1200 * SS, 1425 * SS, 1258 * SS], fill=(0, 0, 0, 95))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10 * SS // 2))
    img = Image.alpha_composite(img, shadow)
    pen = Pen(img)

    # --- boss (behind the ghost's shoulder) ----------------------------------
    draw_boss(pen)
    paste_rotated(img, make_controller(235), 1230, 1128, 4)
    pen = Pen(img)
    # boss hands over the controller grips + white cuffs
    pen.line([(1136, 1102), (1168, 1122)], width=30, fill=SHIRT)
    pen.line([(1324, 1102), (1292, 1122)], width=30, fill=SHIRT)
    pen.ellipse([1118, 1094, 1178, 1146], fill=SKIN, outline=INK, width=5)
    pen.ellipse([1282, 1094, 1342, 1146], fill=SKIN, outline=INK, width=5)

    # --- the ghost, exact drawing from ghost.png ------------------------------
    ghost = Image.open(HERE / "ghost.png").convert("RGBA")
    ghost = ghost.crop(ghost.getchannel("A").getbbox())
    target_h = 600 * SS
    scale = target_h / ghost.height
    ghost = ghost.resize((round(ghost.width * scale), target_h), Image.LANCZOS)
    gx = round((800 - ghost.width / SS / 2) * SS)
    gy = round((1270 - 600) * SS)
    # magenta rim light on the ghost's left edge (TV-side glow)
    alpha = ghost.getchannel("A")
    rim = Image.new("RGBA", ghost.size, RIM + (255,))
    rim.putalpha(alpha)
    glow = rim.resize((rim.width + 80 * SS // 2, rim.height + 80 * SS // 2),
                      Image.LANCZOS)
    glow.putalpha(glow.getchannel("A").point(lambda a: int(a * 0.22)))
    glow = glow.filter(ImageFilter.GaussianBlur(24 * SS // 2))
    img.alpha_composite(glow, (gx - 24 * SS, gy - 24 * SS))
    img.alpha_composite(rim, (gx - 7 * SS, gy - 2 * SS))
    img.alpha_composite(ghost, (gx, gy))
    pen = Pen(img)

    # ghost's controller, low on its body, clear of the coin (right side)
    paste_rotated(img, make_controller(245), 790, 1100, -6)
    pen = Pen(img)

    # --- boss speech bubble -----------------------------------------------------
    bx0, by0, bx1, by1 = 1065, 320, 1795, 520
    tip = (1252, 650)
    base_l, base_r = 1150, 1290
    pen.polygon([(base_l, by1 - 6), (base_r, by1 - 6), tip], fill=WHITE)
    pen.rounded_rectangle([bx0, by0, bx1, by1], radius=36,
                          fill=WHITE, outline=INK, width=8)
    pen.line([(base_l, by1 - 2), tip], fill=INK, width=8)
    pen.line([(base_r, by1 - 2), tip], fill=INK, width=8)
    pen.rectangle([base_l + 5, by1 - 5, base_r - 5, by1 + 5], fill=WHITE)
    bub = fit_font(pen, "Now pass me a controller.", bx1 - bx0 - 70, 56)
    bcx = (bx0 + bx1) // 2
    draw_mixed(pen, bcx, 356, [("You're fired.", DARK)], bub, 0)
    draw_mixed(pen, bcx, 428, [("Now pass me a controller.", DARK)], bub, 0)

    # --- top captions -------------------------------------------------------------
    cap = font(118)
    draw_mixed(pen, W // 2, 26, [("CALLED IN SICK FOR", WHITE)], cap, 11)
    draw_mixed(pen, W // 2, 158,
               [("GTA 6", YELLOW), (" LAUNCH DAY", WHITE)], cap, 11)

    # --- bottom caption over a soft dark band --------------------------------------
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, 1155 * SS, W * SS, H * SS], fill=(5, 3, 12, 110))
    band = band.filter(ImageFilter.GaussianBlur(6 * SS // 2))
    img = Image.alpha_composite(img, band)
    pen = Pen(img)
    bot = font(104)
    draw_mixed(pen, W // 2, 1180,
               [("HE CALLED IN SICK ", WHITE), ("TOO.", YELLOW)], bot, 10)

    img = img.resize((W, H), Image.LANCZOS).convert("RGB")
    img.save(OUT)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
