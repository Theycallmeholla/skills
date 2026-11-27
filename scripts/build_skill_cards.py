#!/usr/bin/env python3
"""Build the trading-card images that illustrate each skill's README.

Inputs live in docs/media/<skill>/:
  card.json       card text and stats (see docs/media/README.md for the fields)
  art.svg         the art-window illustration, drawn on a 420x468 canvas
  *.src.svg       any other image (example output, charts); text uses the card fonts

Outputs, written next to the inputs:
  card.svg        the finished card
  <name>.svg      each *.src.svg with its fonts embedded

Fonts are subset to the characters each file uses and embedded as base64 WOFF2, because
GitHub shows README images through <img>, which cannot load external fonts.

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
}

INK = "#1D1A16"
INK_SOFT = "#5B544A"
STOCK = "#F6F1E7"

# Category colours: frame (strong) and tint (art window, type line).
CATEGORIES = {
    "discovery": ("Requirements &amp; discovery", "#6B4FD8", "#E9E3FB"),
    "code": ("Code quality &amp; testing", "#0F7C8C", "#DCEFF1"),
    "ux": ("Site, UX &amp; conversion", "#C96F1A", "#FBEAD5"),
    "docs": ("Documentation", "#2F8F4E", "#DFF1E3"),
    "content": ("Content", "#C2367A", "#F9DFEA"),
    "meta": ("Prompting, workflow &amp; repo ops", "#3E4C66", "#E3E7EE"),
}

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


def wrap(s, family, size, width):
    lines, line = [], ""
    for word in s.split():
        trial = f"{line} {word}".strip()
        if line and text_width(trial, family, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def fit_size(s, family, start, width, spacing=0.0, floor=10):
    size = start
    while size > floor and text_width(s, family, size, spacing) > width:
        size -= 1
    return size


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
    used = [fam for fam in FONTS if re.search(rf"font-family=\"{fam}\"|font-family:\s*{fam}", svg)]
    if not used:
        return svg
    plain = re.sub(r"<[^>]+>", " ", svg)
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


def t(x, y, s, family, size, fill=INK, anchor="start", spacing=0, extra=""):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}"'
            f' text-anchor="{anchor}"{ls}{extra}>{escape(s)}</text>')


def build_card(skill_dir):
    data = json.loads((skill_dir / "card.json").read_text())
    cat_label, frame, tint = CATEGORIES[data["category"]]
    art_path = skill_dir / "art.svg"
    art = strip_svg_wrapper(art_path.read_text()) if art_path.exists() else ""

    W, H = 1200, 560
    col_x, col_w = 500, 640
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W + 12} {H + 12}" '
           f'width="{W + 12}" height="{H + 12}" role="img" '
           f'aria-label="{escape(data["title"])}: {escape(data["ability"])}">']
    # Card body: offset print shadow, coloured frame, card stock.
    out.append(f'<rect x="22" y="22" width="{W - 10}" height="{H - 10}" rx="30" fill="{INK}"/>')
    out.append(f'<rect x="10" y="10" width="{W - 10}" height="{H - 10}" rx="30" fill="{frame}"/>')
    out.append(f'<rect x="26" y="26" width="{W - 42}" height="{H - 42}" rx="18" fill="{STOCK}"/>')

    # Art window.
    out.append(f'<rect x="46" y="46" width="420" height="468" rx="10" fill="{tint}"/>')
    out.append(f'<svg x="46" y="46" width="420" height="468" viewBox="0 0 420 468" overflow="hidden">'
               f'{art}</svg>')
    out.append(f'<rect x="46" y="46" width="420" height="468" rx="10" fill="none" '
               f'stroke="{INK}" stroke-width="2"/>')

    # Header: category stamp + card number.
    out.append(t(col_x, 84, cat_label.replace("&amp;", "&").upper(), "Display700", 20, frame, spacing=3))
    out.append(t(col_x + col_w, 84, f'No. {data["no"]:02d} / {data["of"]}', "Display700", 20,
                 INK_SOFT, "end", spacing=2))

    # Name, shrunk to fit the column.
    name = data["title"].upper()
    size = fit_size(name, "Display900", 104, col_w, spacing=1)
    out.append(t(col_x - 3, 180, name, "Display900", size, INK, spacing=1))

    # Type line.
    out.append(f'<rect x="{col_x}" y="200" width="{col_w}" height="42" fill="{tint}"/>')
    out.append(f'<rect x="{col_x}" y="200" width="6" height="42" fill="{frame}"/>')
    out.append(t(col_x + 20, 228, data["type"], "Body700", 20, INK))

    # Ability text (the TL;DR).
    y = 288
    for line in wrap(data["ability"], "Body400", 25, col_w)[:4]:
        out.append(t(col_x, y, line, "Body400", 25, INK))
        y += 34

    # Flavor text: a real line from the SKILL.md.
    if data.get("flavor"):
        y += 8
        for line in wrap(f'“{data["flavor"]}”', "BodyItalic", 19, col_w)[:2]:
            out.append(t(col_x, y, line, "BodyItalic", 19, INK_SOFT))
            y += 26

    # Stat bar.
    stats = data["stats"][:4]
    out.append(f'<line x1="{col_x}" y1="430" x2="{col_x + col_w}" y2="430" stroke="{INK}" stroke-width="2"/>')
    cell = col_w / len(stats)
    for i, (label, value) in enumerate(stats):
        cx = col_x + i * cell
        if i:
            out.append(f'<line x1="{cx}" y1="446" x2="{cx}" y2="510" stroke="{INK}" stroke-opacity=".25"/>')
        pad = 0 if i == 0 else 16
        out.append(t(cx + pad, 462, label.upper(), "Display700", 17, frame, spacing=2))
        vsize = fit_size(value.upper(), "Display900", 40, cell - pad - 10, spacing=0.5)
        out.append(t(cx + pad, 506, value.upper(), "Display900", vsize, INK, spacing=0.5))

    out.append("</svg>")
    svg = embed_fonts("\n".join(out))
    (skill_dir / "card.svg").write_text(svg)
    return skill_dir / "card.svg"


def build_sources(skill_dir):
    built = []
    for src in sorted(skill_dir.glob("*.src.svg")):
        dest = src.with_name(src.name.replace(".src.svg", ".svg"))
        dest.write_text(embed_fonts(src.read_text()))
        built.append(dest)
    return built


def main(argv):
    names = argv or sorted(p.name for p in MEDIA.iterdir()
                           if p.is_dir() and (p / "card.json").exists())
    for name in names:
        skill_dir = MEDIA / name
        if not (skill_dir / "card.json").exists():
            raise SystemExit(f"{name}: no docs/media/{name}/card.json")
        outputs = [build_card(skill_dir)] + build_sources(skill_dir)
        for path in outputs:
            print(f"{path.relative_to(ROOT)}  {path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
