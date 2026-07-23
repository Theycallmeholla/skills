#!/usr/bin/env python3
"""Build the UI Review report: a self-contained HTML file organized section-by-section,
with numbered severity pins overlaid on a screenshot crop of each page section,
a repeated-message summary table up top, and click-to-expand images.

Usage:
  python3 build_report.py page.png findings.json [--out ui-review-acme.html]

If --out is omitted the file is named ui-review-<business-slug>-<date>.html.
NEVER deliver this as "report.html"/"review.html" — the name should identify the site.

findings.json:
{
  "meta": {
    "business": "OnSite Garage Doors",          // used in the H1 and the file name
    "source":  "https://... or file name",
    "date":    "2026-07-18",
    "subject": "Local garage-door repair company; primary action: call now",
    "pattern_intro": "1-2 sentences naming the pattern behind most findings.",
    "repeats": [                                  // the repeated-message table (can be [])
      {"count": "7x", "message": "Phone number", "where": "top bar, header, hero button, footer"}
    ],
    "recommendation": "The one structural change that fixes most of it.",
    "lens": ""                                    // optional override of the default lens line
  },
  "sections": [                                   // in page order, top to bottom
    {
      "title": "Header + Hero",
      "region": [y0, y1],                         // vertical page-pixel range to crop (full width)
      "working_well": false,                      // true => green "working well" tag
      "findings": [
        {
          "severity": "high" | "medium" | "low" | "good",
          "text": "What is odd, quoting the exact copy.",
          "fix":  "One structural sentence.",     // omit for severity "good"
          "pin":  [x, y]                          // page coords to pin; omit for section-wide/good notes
        }
      ]
    }
  ]
}

Numbered pins restart at 1 per section and match the numbered notes below the image.
"good" findings render with a green check, no number. Also writes crops/<section>.png.
Requires: pip install pillow
"""
import argparse, base64, io, json, os, re
from PIL import Image

COLORS = {"high": "#d92d20", "medium": "#e07000", "low": "#b58a00", "good": "#1f9d55"}
PAD_Y = 24


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "page"


def b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("screenshot")
    ap.add_argument("findings")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    with open(args.findings) as fh:
        data = json.load(fh)
    meta = data.get("meta", {})
    out = args.out or f"ui-review-{slug(meta.get('business'))}-{meta.get('date', '')}".rstrip("-") + ".html"

    img = Image.open(args.screenshot).convert("RGB")
    crops_dir = os.path.join(os.path.dirname(os.path.abspath(out)) or ".", "crops")
    os.makedirs(crops_dir, exist_ok=True)

    lens = meta.get("lens") or ("Lens: does it <b>look</b> right, is it <b>structured</b> right, and does the "
                                "<b>copy repeat itself</b>? — not links / SEO / UX flow. Numbered pins on each "
                                "screenshot match the numbered notes. Click any image to expand.")

    # summary table
    rows = "".join(
        f'<tr><td class="n">{esc(r.get("count"))}</td><td>{esc(r.get("message"))}</td><td>{esc(r.get("where"))}</td></tr>'
        for r in meta.get("repeats", []))
    table = f"<table>{rows}</table>" if rows else ""
    rec = (f'<p class="rec"><b>The one change that fixes most of it:</b> {esc(meta.get("recommendation"))}</p>'
           if meta.get("recommendation") else "")
    summary = ""
    if meta.get("pattern_intro") or table or rec:
        summary = (f'<div class="summary"><h2>The pattern behind most of this</h2>'
                   f'<p>{esc(meta.get("pattern_intro"))}</p>{table}{rec}</div>')

    cards = []
    for sec in data.get("sections", []):
        y0, y1 = sec.get("region", [0, img.height])
        y0 = max(0, int(y0) - PAD_Y)
        y1 = min(img.height, int(y1) + PAD_Y)
        crop = img.crop((0, y0, img.width, y1))
        crop.save(os.path.join(crops_dir, f"{slug(sec.get('title'))}.png"))
        ch = max(1, y1 - y0)

        pins, notes, n = [], [], 0
        for f in sec.get("findings", []):
            sev = str(f.get("severity", "medium")).lower()
            color = COLORS.get(sev, COLORS["medium"])
            if sev == "good":
                mark = '<span class="mk good">&#10003;</span>'
            else:
                n += 1
                mark = f'<span class="mk" style="background:{color}">{n}</span>'
                if f.get("pin"):
                    px = min(99, max(1, round(f["pin"][0] / img.width * 100)))
                    py = min(99, max(1, round((f["pin"][1] - y0) / ch * 100)))
                    pins.append(f'<span class="pin" style="left:{px}%;top:{py}%;background:{color}">{n}</span>')
            fix = f'<div class="fix"><b>Fix:</b> {esc(f["fix"])}</div>' if f.get("fix") else ""
            notes.append(f'<li>{mark}<div class="ftext">{esc(f.get("text"))}{fix}</div></li>')

        ok = ' <span class="secok">&#10003; working well</span>' if sec.get("working_well") else ""
        cards.append(f'''
<section class="card">
  <figure class="shot" tabindex="0">
    <img loading="lazy" src="data:image/png;base64,{b64(crop)}" alt="{esc(sec.get("title"))}">
    {"".join(pins)}
    <figcaption>click to expand</figcaption>
  </figure>
  <div class="findings"><h2>{esc(sec.get("title"))}{ok}</h2><ul>{"".join(notes)}</ul></div>
</section>''')

    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>UI Review — {esc(meta.get("business"))}</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#1a2233;background:#f4f6f9}}
.wrap{{max-width:900px;margin:0 auto;padding:32px 20px 90px}}
header.top h1{{font-size:26px;margin:0 0 4px}}
header.top .meta{{color:#66707e;font-size:13px}}
header.top .lens{{margin-top:12px;padding:10px 14px;background:#eaf0fb;border-left:3px solid #2f6bd6;border-radius:6px;font-size:14px}}
header.top .subject{{margin-top:8px;padding:8px 14px;background:#fdf3e7;border-left:3px solid #e07000;border-radius:6px;font-size:13.5px;color:#4a4030}}
.summary{{background:#fff;border:1px solid #e3e8ef;border-radius:12px;padding:22px 24px;margin:20px 0 28px}}
.summary h2{{margin:0 0 10px;font-size:19px}}
.summary table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:14px}}
.summary td{{border-top:1px solid #eef1f5;padding:8px 10px;vertical-align:top}}
.summary td.n{{font-weight:700;color:#d92d20;white-space:nowrap;width:44px}}
.summary td:nth-child(2){{font-weight:600;width:32%}}
.summary td:nth-child(3){{color:#66707e}}
.summary .rec{{background:#f0f9f2;border-left:3px solid #1f9d55;padding:10px 14px;border-radius:6px;margin-top:14px}}
.card{{background:#fff;border:1px solid #e3e8ef;border-radius:12px;padding:16px;margin-bottom:20px}}
.shot{{position:relative;margin:0 0 14px;cursor:zoom-in;line-height:0}}
.shot img{{width:100%;border:1px solid #dfe4ea;border-radius:8px;display:block}}
.shot figcaption{{position:absolute;right:8px;bottom:8px;background:rgba(20,28,40,.65);color:#fff;font-size:11px;padding:3px 8px;border-radius:10px;line-height:1.4}}
.pin{{position:absolute;transform:translate(-50%,-50%);width:26px;height:26px;border-radius:50%;color:#fff;font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 3px #fff,0 2px 6px rgba(0,0,0,.4);line-height:1}}
.findings h2{{font-size:17px;margin:2px 0 12px}}
.findings ul{{list-style:none;margin:0;padding:0}}
.findings li{{display:flex;gap:10px;padding:7px 0;border-top:1px solid #f0f2f6}}
.findings li:first-child{{border-top:0}}
.mk{{flex:none;width:24px;height:24px;border-radius:50%;color:#fff;font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;margin-top:1px}}
.good{{background:#1f9d55}}
.secok{{font-size:12px;color:#1f9d55;font-weight:600;margin-left:6px}}
.ftext{{flex:1}}
.fix{{margin-top:4px;color:#3a4657;font-size:13.5px}}
#lb{{display:none;position:fixed;inset:0;background:rgba(12,18,28,.88);z-index:50;overflow:auto;padding:30px}}
#lb.open{{display:block}}
#lb figure{{position:relative;max-width:1200px;margin:0 auto;line-height:0}}
#lb img{{width:100%;border-radius:8px}}
#lb figcaption{{display:none}}
#lbx{{position:fixed;top:14px;right:22px;color:#fff;font-size:34px;cursor:pointer;z-index:51}}
</style></head>
<body><div class="wrap">
<header class="top"><h1>UI Review — {esc(meta.get("business"))}</h1>
<div class="meta">{esc(meta.get("source"))} · reviewed {esc(meta.get("date"))}</div>
<div class="lens">{lens}</div>
<div class="subject"><b>Read as:</b> {esc(meta.get("subject"))} — correct me if that premise is wrong.</div></header>
{summary}
{"".join(cards)}
</div>
<div id="lb"><span id="lbx">&times;</span><figure></figure></div>
<script>
var lb=document.getElementById('lb'),lbf=lb.querySelector('figure');
document.querySelectorAll('.shot').forEach(function(s){{
  s.addEventListener('click',function(){{lbf.innerHTML=s.innerHTML;lb.classList.add('open');document.body.style.overflow='hidden';}});
}});
function close(){{lb.classList.remove('open');document.body.style.overflow='';}}
lb.addEventListener('click',function(e){{if(e.target===lb||e.target.id==='lbx')close();}});
document.addEventListener('keydown',function(e){{if(e.key==='Escape')close();}});
</script>
</body></html>'''

    with open(out, "w") as fh:
        fh.write(html)
    nsec = len(data.get("sections", []))
    print(f"Report: {out} ({nsec} section(s), crops in {crops_dir}/)")


if __name__ == "__main__":
    main()
