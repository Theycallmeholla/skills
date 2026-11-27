#!/usr/bin/env python3
"""Build the trading cards (front + back) and example images for each skill's README.

Inputs live in docs/media/<skill>/ (field reference: docs/media/README.md):
  card.json        card text, stats, colours, and where the front comes from
  front-art.webp   a hand-made front (optional); the card number is stamped onto it
  art.svg          illustration for a generated front, 420x468 canvas (used when no front-art)
  *.src.svg        other images (example output, charts) that use the card fonts

Outputs, written next to the inputs:
  front.svg, back.svg, and <name>.svg for each *.src.svg

Fonts are subset to the characters each file uses and embedded as base64 WOFF2, and
front art is embedded as base64 WebP, because GitHub shows README images through <img>,
which cannot load anything external.

Dev-only dependency:  pip install fonttools brotli
Usage:  python3 scripts/build_skill_cards.py [skill ...]
"""
import base64
import io
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "docs" / "media"
FONT_DIR = MEDIA / "_fonts"

FONTS = {  # family name used in SVGs -> (file, weight, style)
    "Display900": ("big-shoulders-display-latin-900-normal.woff2", 900, "normal"),
    "Display700": ("big-shoulders-display-latin-700-normal.woff2", 700, "normal"),
    "Body400": ("atkinson-hyperlegible-latin-400-normal.woff2", 400, "normal"),
    "Body700": ("atkinson-hyperlegible-latin-700-normal.woff2", 700, "normal"),
    "BodyItalic": ("atkinson-hyperlegible-latin-400-italic.woff2", 400, "italic"),
    "Card500": ("montserrat-latin-500-normal.woff2", 500, "normal"),
    "Card500i": ("montserrat-latin-500-italic.woff2", 500, "italic"),
    "Card600": ("montserrat-latin-600-normal.woff2", 600, "normal"),
    "Card800": ("montserrat-latin-800-normal.woff2", 800, "normal"),
    "Card900i": ("montserrat-latin-900-italic.woff2", 900, "italic"),
}

CREAM = "#F6EFE3"

# Category -> (label, dark panel, accent, light tint for generated art windows).
CATEGORIES = {
    "discovery": ("Requirements & discovery", "#2A1D5A", "#FFC94A", "#E9E3FB"),
    "code": ("Code quality & testing", "#0D3940", "#FFB627", "#DCEFF1"),
    "ux": ("Site, UX & conversion", "#3D2410", "#FF9F43", "#FBEAD5"),
    "docs": ("Documentation", "#12371F", "#8BE3A8", "#DFF1E3"),
    "content": ("Content", "#3B1630", "#F2C230", "#F9DFEA"),
    "meta": ("Prompting, workflow & repo ops", "#1D2433", "#9DB4E0", "#E3E7EE"),
}

W, H = 1024, 1536
PAD = 84                       # text inset from the card edge
TEXT_W = W - 2 * PAD

_fonts = {}


def font(family):
    if family not in _fonts:
        _fonts[family] = TTFont(FONT_DIR / FONTS[family][0])
    return _fonts[family]


def text_width(s, family, size, spacing=0.0):
    f = font(family)
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    upm = f["head"].unitsPerEm
    total = 0
    for ch in s:
        glyph = cmap.get(ord(ch))
        total += hmtx[glyph][0] if glyph else upm * 0.5
    return total * size / upm + spacing * max(len(s) - 1, 0)


def wrap(s, family, size, width, spacing=0.0):
    lines, line = [], ""
    for word in s.split():
        trial = f"{line} {word}".strip()
        if line and text_width(trial, family, size, spacing) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def fit_lines(s, family, start, width, max_lines, spacing=0.0, floor=24):
    """Largest size (<= start) at which s wraps into max_lines lines that fit width."""
    size = start
    while size > floor:
        lines = wrap(s, family, size, width, spacing)
        if len(lines) <= max_lines and all(text_width(l, family, size, spacing) <= width for l in lines):
            return size, lines
        size -= 2
    return size, wrap(s, family, size, width, spacing)[:max_lines]


def subset_b64(family, chars):
    f = TTFont(FONT_DIR / FONTS[family][0])
    opts = Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    sub = Subsetter(opts)
    sub.populate(text="".join(sorted(set(chars))) + " ")
    sub.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def embed_fonts(svg):
    """Insert @font-face rules for every font family the SVG mentions."""
    used = [fam for fam in FONTS if re.search(rf"font-family=\"{fam}\"|font-family:\s*{fam}\b", svg)]
    if not used:
        return svg
    plain = re.sub(r"<image[^>]*>", " ", svg)
    plain = re.sub(r"<[^>]+>", " ", plain)
    plain = (plain.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&#39;", "'"))
    rules = []
    for fam in used:
        _, weight, style = FONTS[fam]
        rules.append(
            f"@font-face{{font-family:{fam};font-weight:{weight};font-style:{style};"
            f"src:url(data:font/woff2;base64,{subset_b64(fam, plain)}) format('woff2')}}"
        )
    style_el = "<style>" + "".join(rules) + "</style>"
    return re.sub(r"(<svg[^>]*>)", lambda m: m.group(1) + style_el, svg, count=1)


def strip_svg_wrapper(art):
    art = re.sub(r"<\?xml[^>]*\?>", "", art)
    inner = re.search(r"<svg[^>]*>(.*)</svg>", art, re.S)
    if not inner:
        raise SystemExit("art.svg has no <svg> root")
    return inner.group(1)


def t(x, y, s, family, size, fill, anchor="start", spacing=0, opacity=None):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}"'
            f' text-anchor="{anchor}"{ls}{op}>{escape(s)}</text>')


def index_order():
    """Skill names in the order of the main README's skill index."""
    text = (ROOT / "README.md").read_text()
    section = text.split("## Skill index", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"^- \*\*([a-z0-9-]+)\*\*", section, re.M)


def _hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c * 255))) for c in rgb)


def sample_palette(image_path):
    """Panel, accent and tint taken from an illustration (needs Pillow).

    Panel: the hue of the picture's bottom band, pushed dark so cream text reads on it.
    Accent: the most vivid bright colour in the picture, lifted if it is dull.
    """
    import colorsys
    from PIL import Image

    with Image.open(image_path) as im:
        small = im.convert("RGB").resize((48, 72))
    raw = small.tobytes()
    px = [tuple(c / 255 for c in raw[i:i + 3]) for i in range(0, len(raw), 3)]

    bottom = px[48 * 50:]
    avg = [sum(p[i] for p in bottom) / len(bottom) for i in range(3)]
    h, l, s = colorsys.rgb_to_hls(*avg)
    panel = colorsys.hls_to_rgb(h, min(l, 0.13), min(max(s, 0.25), 0.65))
    tint = colorsys.hls_to_rgb(h, 0.92, min(s, 0.45))

    with Image.open(image_path) as im:
        quant = im.convert("RGB").resize((96, 144)).quantize(colors=12)
    pal = quant.getpalette()[:36]
    counts = dict((idx, n) for n, idx in quant.getcolors())
    best, best_score = None, -1.0
    for i in range(12):
        rgb = tuple(c / 255 for c in pal[i * 3:i * 3 + 3])
        hh, ss, vv = colorsys.rgb_to_hsv(*rgb)
        share = counts.get(i, 0) / (96 * 144)
        if share < 0.004:
            continue
        score = ss * vv * (0.6 + min(share, 0.25))
        if score > best_score:
            best, best_score = (hh, ss, vv), score
    hh, ss, vv = best
    accent = colorsys.hsv_to_rgb(hh, max(ss, 0.6), max(vv, 0.88))
    # Small labels use the accent on the dark panel, so keep it light enough to read.
    lum = 0.2126 * accent[0] + 0.7152 * accent[1] + 0.0722 * accent[2]
    if lum < 0.38:
        ah, al, as_ = colorsys.rgb_to_hls(*accent)
        accent = colorsys.hls_to_rgb(ah, min(0.72, al + (0.38 - lum) * 1.2), as_)
    return {"panel": _hex(panel), "accent": _hex(accent), "tint": _hex(tint)}


def load(skill_dir):
    data = json.loads((skill_dir / "card.json").read_text())
    order = index_order()
    if skill_dir.name not in order:
        raise SystemExit(f"{skill_dir.name}: not in the README skill index")
    data["no"] = order.index(skill_dir.name) + 1
    if "illustration" not in data and (skill_dir / "illustration.webp").exists():
        data["illustration"] = {"art": "illustration.webp"}
    label, panel, accent, tint = CATEGORIES[data["category"]]
    if "palette" not in data and "illustration" in data:
        data["palette"] = sample_palette(skill_dir / data["illustration"]["art"])
    pal = data.get("palette", {})
    data["_panel"] = pal.get("panel", panel)
    data["_accent"] = pal.get("accent", accent)
    data["_tint"] = pal.get("tint", tint)
    data.setdefault("set", label)
    return data


def frame(d, label):
    """Cream card border, coloured panel, header, accent slice with the card number."""
    panel, accent = d["_panel"], d["_accent"]
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{escape(label)}">',
        '<defs><clipPath id="panel"><rect x="32" y="32" width="960" height="1472" rx="44"/></clipPath></defs>',
        f'<rect width="{W}" height="{H}" rx="64" fill="{CREAM}"/>',
        f'<rect x="32" y="32" width="960" height="1472" rx="44" fill="{panel}"/>',
        f'<polygon clip-path="url(#panel)" points="760,32 1000,32 1000,236 676,236" fill="{accent}"/>',
        t(PAD, 128, "SKILL COLLECTION", "Card600", 40, CREAM, spacing=10),
        f'<rect x="{PAD}" y="160" width="90" height="9" fill="{accent}"/>',
        t(PAD + 112, 172, d["set"].upper(), "Card600", 23, CREAM, spacing=7, opacity=0.85),
        t(944, 192, f'{d["no"]:02d}', "Card900i", 124, panel, "end"),
    ]


def build_back(skill_dir, d):
    accent = d["_accent"]
    out = frame(d, f'{d["title"]}, card back: {d["ability"]}')

    size, lines = fit_lines(d["title"].upper(), "Card800", 96, TEXT_W, 2)
    y = 300 + size * 0.8
    for line in lines:
        out.append(t(PAD - 4, round(y), line, "Card800", size, CREAM))
        y += size * 1.04
    y += 18
    out.append(t(PAD, round(y), d["type"].upper(), "Card600", 27, accent, spacing=4))
    y += 40
    out.append(f'<rect x="{PAD}" y="{round(y)}" width="{TEXT_W}" height="2" fill="{CREAM}" fill-opacity=".25"/>')

    # Ability + flavor: the largest size that still ends above the stat grid.
    flavor = f'“{d["flavor"]}”' if d.get("flavor") else ""
    start = y
    for size in range(48, 33, -2):
        a_lines = wrap(d["ability"], "Card500", size, TEXT_W)
        f_size = round(size * 0.8)
        f_lines = wrap(flavor, "Card500i", f_size, TEXT_W) if flavor else []
        end = (start + size * 1.9 + len(a_lines) * size * 1.45
               + (24 + len(f_lines) * f_size * 1.42 if f_lines else 0))
        if end <= 1090:
            break
    y = start + size * 1.9
    for line in a_lines:
        out.append(t(PAD, round(y), line, "Card500", size, CREAM))
        y += size * 1.45
    if f_lines:
        y += 24
        for line in f_lines:
            out.append(t(PAD, round(y), line, "Card500i", f_size, CREAM, opacity=0.7))
            y += f_size * 1.42
    if y > 1110:
        raise SystemExit(f"{skill_dir.name}: back text runs into the stats; shorten ability/flavor")

    # 2x2 stat grid.
    cell_w, top = TEXT_W / 2, 1140
    out.append(f'<rect x="{PAD}" y="{top - 30}" width="{TEXT_W}" height="2" fill="{CREAM}" fill-opacity=".25"/>')
    for i, (label, value) in enumerate(d["stats"][:4]):
        cx = PAD + (i % 2) * cell_w + (24 if i % 2 else 0)
        cy = top + (i // 2) * 150
        out.append(t(cx, cy + 22, label.upper(), "Card600", 24, accent, spacing=5))
        vsize = 60
        while vsize > 30 and text_width(value.upper(), "Card800", vsize) > cell_w - 40:
            vsize -= 2
        out.append(t(cx, cy + 90, value.upper(), "Card800", vsize, CREAM))
    out.append(f'<rect x="{PAD + cell_w}" y="{top - 6}" width="2" height="270" fill="{CREAM}" fill-opacity=".25"/>')
    out.append(f'<rect x="{PAD}" y="1446" width="110" height="10" fill="{accent}"/>')
    out.append(t(940, 1456, "BACK", "Card600", 22, CREAM, "end", spacing=8, opacity=0.5))
    out.append("</svg>")
    return "\n".join(out)


THUMB_W = 360   # art width inside gallery thumbnails


def _thumb_art(path):
    """The art shrunk for the README gallery, animation kept (needs Pillow)."""
    from PIL import Image

    size = (THUMB_W, THUMB_W * 3 // 2)
    buf = io.BytesIO()
    with Image.open(path) as im:
        if getattr(im, "is_animated", False):
            # Keep the motion: shrink every frame, keep each frame's timing.
            frames, durations = [], []
            for i in range(im.n_frames):
                im.seek(i)
                frame = im.convert("RGB")
                frame.thumbnail(size)
                frames.append(frame)
                durations.append(im.info.get("duration", 100))
            frames[0].save(buf, "WEBP", save_all=True, append_images=frames[1:],
                           duration=durations, loop=0, quality=60)
        else:
            frame0 = im.convert("RGB")
            frame0.thumbnail(size)
            frame0.save(buf, "WEBP", quality=68)
    return "webp", base64.b64encode(buf.getvalue()).decode()


def build_illustrated_front(skill_dir, d, thumb=False):
    """A text-free illustration set behind the card: header, number and title band sit on top."""
    panel, accent = d["_panel"], d["_accent"]
    spec = d["illustration"]
    if thumb:
        ext, data = _thumb_art(skill_dir / spec["art"])
    else:
        ext = Path(spec["art"]).suffix.lstrip(".").replace("jpg", "jpeg")
        data = base64.b64encode((skill_dir / spec["art"]).read_bytes()).decode()
    align = spec.get("align", "xMidYMid")
    out = frame(d, f'{d["title"]}: {d.get("tagline", d["ability"])}')
    art = [
        '<defs>'
        f'<linearGradient id="topfade" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{panel}" stop-opacity=".92"/>'
        f'<stop offset="1" stop-color="{panel}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="lowfade" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{panel}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{panel}" stop-opacity=".85"/></linearGradient>'
        '</defs>',
        f'<image clip-path="url(#panel)" href="data:image/{ext};base64,{data}" '
        f'x="32" y="32" width="960" height="1180" preserveAspectRatio="{align} slice"/>',
        f'<rect clip-path="url(#panel)" x="32" y="32" width="960" height="270" fill="url(#topfade)"/>',
        f'<rect x="32" y="900" width="960" height="250" fill="url(#lowfade)"/>',
        # Title band with a slanted top edge, drawn over the art.
        f'<polygon clip-path="url(#panel)" points="32,1150 992,1060 992,1504 32,1504" fill="{panel}"/>',
        f'<polygon clip-path="url(#panel)" points="32,1150 992,1060 992,1070 32,1160" fill="{accent}"/>',
    ]
    out[4:4] = art   # after the panel background, before the accent slice and header text

    # Lay out bottom-up: tagline ends above the accent bar, title sits on top of it,
    # and both shrink until the title clears the band's slanted edge.
    tagline = d.get("tagline", d["type"])
    for title_max, tag_size in ((104, 34), (92, 32), (84, 30), (76, 28)):
        size, lines = fit_lines(d["title"].upper(), "Card800", title_max, TEXT_W, 2)
        tag_lines = wrap(tagline, "Card500", tag_size, TEXT_W)[:2]
        tag_top = 1412 - (len(tag_lines) - 1) * tag_size * 1.35
        first_baseline = tag_top - tag_size * 1.5 - (len(lines) - 1) * size * 1.02
        if first_baseline - size * 0.75 >= 1170:
            break
    y = first_baseline
    for line in lines:
        out.append(t(PAD - 4, round(y), line, "Card800", size, CREAM))
        y += size * 1.02
    y = tag_top
    for line in tag_lines:
        out.append(t(PAD, round(y), line, "Card500", tag_size, CREAM, opacity=0.9))
        y += tag_size * 1.35
    out.append(f'<rect x="{PAD}" y="1446" width="110" height="10" fill="{accent}"/>')
    out.append("</svg>")
    return "\n".join(out)


def build_generated_front(skill_dir, d):
    accent, tint = d["_accent"], d["_tint"]
    out = frame(d, f'{d["title"]}: {d.get("tagline", d["ability"])}')
    art_path = skill_dir / "art.svg"
    art = strip_svg_wrapper(art_path.read_text()) if art_path.exists() else ""
    out.append(f'<rect x="{PAD}" y="256" width="{TEXT_W}" height="820" rx="28" fill="{tint}"/>')
    out.append(f'<svg x="{PAD}" y="256" width="{TEXT_W}" height="820" viewBox="0 0 420 468" '
               f'preserveAspectRatio="xMidYMid meet">{art}</svg>')

    size, lines = fit_lines(d["title"].upper(), "Card800", 104, TEXT_W, 2)
    y = 1130 + size * 0.85
    for line in lines:
        out.append(t(PAD - 4, round(y), line, "Card800", size, CREAM))
        y += size * 1.02
    y += 22
    for line in wrap(d.get("tagline", d["type"]), "Card500", 40, TEXT_W)[:3]:
        out.append(t(PAD, round(y), line, "Card500", 40, CREAM, opacity=0.9))
        y += 54
    out.append(f'<rect x="{PAD}" y="1446" width="110" height="10" fill="{accent}"/>')
    out.append("</svg>")
    return "\n".join(out)


def build_art_front(skill_dir, d):
    """A hand-made front, with the card number stamped into its corner."""
    spec = d["front"]
    data = base64.b64encode((skill_dir / spec["art"]).read_bytes()).decode()
    x, y, w, h = spec["number_box"]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{escape(d["title"])}: {escape(d.get("tagline", d["ability"]))}">',
        f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="64"/></clipPath></defs>',
        f'<image clip-path="url(#card)" href="data:image/webp;base64,{data}" width="{W}" height="{H}"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{spec["patch"]}"/>',
        t(x + w - 6, y + h - 22, f'{d["no"]:02d}', "Card900i", spec.get("number_size", 104),
          spec["number_color"], "end"),
        "</svg>",
    ])


def build_sources(skill_dir):
    built = []
    for src in sorted(skill_dir.glob("*.src.svg")):
        dest = src.with_name(src.name.replace(".src.svg", ".svg"))
        dest.write_text(embed_fonts(src.read_text()))
        built.append(dest)
    return built


def build(skill_dir):
    d = load(skill_dir)
    if "illustration" in d:
        front = build_illustrated_front(skill_dir, d)
    elif "front" in d:
        front = build_art_front(skill_dir, d)
    else:
        front = build_generated_front(skill_dir, d)
    front_svg = embed_fonts(front)
    (skill_dir / "front.svg").write_text(front_svg)
    thumb_svg = embed_fonts(build_illustrated_front(skill_dir, d, thumb=True)) \
        if "illustration" in d else front_svg
    (skill_dir / "thumb.svg").write_text(thumb_svg)
    (skill_dir / "back.svg").write_text(embed_fonts(build_back(skill_dir, d)))
    return ([skill_dir / "front.svg", skill_dir / "thumb.svg", skill_dir / "back.svg"]
            + build_sources(skill_dir))


GALLERY_START = "<!-- skill-gallery:start -->"
GALLERY_END = "<!-- skill-gallery:end -->"
GALLERY_COLS, GALLERY_W = 4, 180


def _card(name):
    path = MEDIA / name / "card.json"
    return json.loads(path.read_text()) if path.exists() else {}


def families():
    """Index order plus {parent: [children]} from each card.json's optional "parent"."""
    order = index_order()
    kids = {}
    for name in order:
        parent = _card(name).get("parent")
        if parent:
            if parent not in order:
                raise SystemExit(f"{name}: parent '{parent}' is not a skill in the README index")
            kids.setdefault(parent, []).append(name)
    return order, kids


def _thumb(name, width, href_prefix="", src_prefix=""):
    src = f"{src_prefix}docs/media/{name}/thumb.svg"
    if not (MEDIA / name / "thumb.svg").exists():
        src = f"{src_prefix}docs/media/{name}/front.svg"
    title = escape(_card(name).get("title", name))
    return (f'<a href="{href_prefix}skills/{name}/"><img src="{src}" width="{width}" '
            f'align="top" alt="{title}"></a>')


def write_gallery():
    """Staggered card wall in the root README, between the gallery markers, in index order.

    Skills with a "parent" don't get their own slot: they sit under the parent card as
    half-size cards, two to a row.
    """
    readme = ROOT / "README.md"
    text = readme.read_text()
    if GALLERY_START not in text or GALLERY_END not in text:
        return False
    order, kids = families()
    tops = [n for n in order if not _card(n).get("parent")]
    columns = [[] for _ in range(GALLERY_COLS)]
    for i, name in enumerate(tops):
        columns[i % GALLERY_COLS].append(name)
    cells = []
    for c, names in enumerate(columns):
        parts = []
        if c % 2:   # every other column starts half a card lower
            parts.append(f'<img src="docs/media/_spacer.svg" width="{GALLERY_W}" '
                         f'height="{GALLERY_W * 3 // 4}" align="top" alt="">')
        for name in names:
            parts.append(_thumb(name, GALLERY_W))
            children = kids.get(name, [])
            for i in range(0, len(children), 2):
                parts.append("".join(_thumb(k, GALLERY_W // 2) for k in children[i:i + 2]))
        # align=top + <br> with no whitespace stacks cards flush (measured on github.com);
        # GitHub's own table-cell padding sets the column gap.
        cells.append('<td valign="top" align="center">' + "<br>".join(parts) + "</td>")
    block = (f"{GALLERY_START}\n<table>\n<tr>\n" + "\n".join(cells)
             + f"\n</tr>\n</table>\n{GALLERY_END}")
    start, end = text.index(GALLERY_START), text.index(GALLERY_END) + len(GALLERY_END)
    new = text[:start] + block + text[end:]
    if new != text:
        readme.write_text(new)
    return True


FAMILY_START = "<!-- skill-family:start -->"
FAMILY_END = "<!-- skill-family:end -->"


def write_families():
    """Fill the family block in each skill README that has the markers."""
    order, kids = families()
    changed = []
    for name in order:
        readme = ROOT / "skills" / name / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text()
        if FAMILY_START not in text or FAMILY_END not in text:
            continue
        parent = _card(name).get("parent")
        if parent:
            ptitle = _card(parent).get("title", parent)
            body = (f"> **Part of [{ptitle}](../{parent}/).** It works alongside {ptitle} "
                    "and can also be installed on its own.")
        elif kids.get(name):
            cards = "".join(_thumb(k, 140, "../../", "../../") for k in kids[name])
            body = ("**The family:** these skills are parts of this one, each also installable "
                    f"on its own.\n\n<p>{cards}</p>")
        else:
            body = ""
        block = f"{FAMILY_START}\n{body}\n{FAMILY_END}" if body else f"{FAMILY_START}\n{FAMILY_END}"
        start, end = text.index(FAMILY_START), text.index(FAMILY_END) + len(FAMILY_END)
        new = text[:start] + block + text[end:]
        if new != text:
            readme.write_text(new)
            changed.append(name)
    return changed


def main(argv):
    names = argv or sorted(p.name for p in MEDIA.iterdir()
                           if p.is_dir() and (p / "card.json").exists())
    for name in names:
        skill_dir = MEDIA / name
        if not (skill_dir / "card.json").exists():
            raise SystemExit(f"{name}: no docs/media/{name}/card.json")
        for path in build(skill_dir):
            print(f"{path.relative_to(ROOT)}  {path.stat().st_size // 1024} KB")
    if write_gallery():
        print("README.md gallery updated")
    for name in write_families():
        print(f"skills/{name}/README.md family block updated")


if __name__ == "__main__":
    main(sys.argv[1:])
