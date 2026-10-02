#!/usr/bin/env node
// slop-scan renderer: loads the page in Chromium, measures visual AI fingerprints
// from computed styles and visible text, and saves screenshots.
// Usage (via render.sh): node render-scan.cjs <url> <outdir>
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [url, outDir = "./slop-shots"] = process.argv.slice(2);
if (!url) { console.error("usage: render-scan.cjs <url> <outdir>"); process.exit(1); }
fs.mkdirSync(outDir, { recursive: true });

function measure() {
  const SCRIPT = /caveat|dancing|pacifico|great vibes|kalam|sacramento|satisfy|parisienne|allura|homemade apple|shadows into light|permanent marker|indie flower|yellowtail|kaushan|lobster|courgette|alex brush|reenie|gochi|patrick hand|cursive/i;
  const vis = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none"; };
  const all = [...document.querySelectorAll("body *")].filter(vis);
  const px = (v) => parseFloat(v) || 0;
  const rgb = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[\s,/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const hue = ({ r, g, b }) => { r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn; if (!d) return { h: 0, s: 0, l: (mx + mn) / 2 }; let h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h = (h * 60 + 360) % 360; const l = (mx + mn) / 2; return { h, s: d / (1 - Math.abs(2 * l - 1)), l }; };
  const isPurple = (c) => { const x = rgb(c); if (!x || x.a === 0) return false; const h = hue(x); return h.s > 0.35 && h.h >= 235 && h.h <= 300; };
  const short = (t) => (t || "").replace(/\s+/g, " ").trim().slice(0, 70);
  const out = {};

  // Em dashes in visible text
  const text = document.body.innerText || "";
  const words = (text.match(/\S+/g) || []).length;
  const dashes = (text.match(/\u2014/g) || []).length;
  const dashSpots = [...document.querySelectorAll("h1,h2,h3,h4,button,a,p,li,figcaption,span")].filter(vis)
    .filter((e) => [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.includes("\u2014"))).slice(0, 6).map((e) => `${e.tagName.toLowerCase()}: ${short(e.innerText)}`);
  out.emDash = { count: dashes, words, per1000: words ? +(dashes / words * 1000).toFixed(1) : 0, examples: dashSpots };

  // Highlighted words inside headings
  const hl = [];
  for (const h of document.querySelectorAll("h1,h2,h3")) {
    if (!vis(h)) continue;
    const hs = getComputedStyle(h);
    const htxt = (h.innerText || "").trim();
    for (const c of h.querySelectorAll("*")) {
      if (!vis(c) || !c.innerText || !c.innerText.trim()) continue;
      if (c.closest("button,a,summary,label") && c.closest("button,a,summary,label") !== h) continue;
      if (c.innerText.trim().length >= htxt.length * 0.8) continue;
      const cs = getComputedStyle(c);
      if (px(cs.fontSize) < px(hs.fontSize) * 0.85) continue;
      const why = [];
      if (cs.fontFamily !== hs.fontFamily) why.push(SCRIPT.test(cs.fontFamily) ? "script font" : "different font");
      if (cs.fontStyle === "italic" && hs.fontStyle !== "italic") why.push("italic");
      if (cs.color !== hs.color) why.push("different color");
      if ((cs.backgroundClip === "text" || cs.webkitBackgroundClip === "text") && cs.backgroundImage.includes("gradient")) why.push("gradient text");
      if (cs.textDecorationLine.includes("underline") || cs.backgroundImage.includes("url(")) why.push("underline/mark");
      if (why.length) { hl.push(`${h.tagName.toLowerCase()} "${short(h.innerText)}" -> "${short(c.innerText)}" (${why.join(", ")})`); break; }
    }
  }
  out.headingHighlights = hl.slice(0, 8);
  out.headingHighlightCount = hl.length;

  // Gradients: classify
  const grad = { text: [], decorative: [], fades: 0, purple: 0 };
  for (const e of all) {
    const s = getComputedStyle(e); const bi = s.backgroundImage;
    if (!bi || !bi.includes("gradient")) continue;
    const isText = s.backgroundClip === "text" || s.webkitBackgroundClip === "text";
    if (isText) { grad.text.push(short(e.innerText)); continue; }
    const stops = bi.match(/rgba?\([^)]+\)/g) || [];
    const fade = /transparent/.test(bi) || stops.some((c) => { const x = rgb(c); return x && x.a < 0.05; });
    if (fade) { grad.fades++; continue; }
    if (stops.some(isPurple)) grad.purple++;
    const r = e.getBoundingClientRect();
    grad.decorative.push(`${e.tagName.toLowerCase()}.${(e.className || "").toString().split(" ")[0]} ${Math.round(r.width)}x${Math.round(r.height)}`);
  }
  out.gradients = { textCount: grad.text.length, text: grad.text.slice(0, 4), decorativeCount: grad.decorative.length, decorative: grad.decorative.slice(0, 5), photoFades: grad.fades, purpleish: grad.purple };

  // Glow blobs and glass
  let glow = 0, glass = 0; const glowEx = [];
  for (const e of all) {
    const s = getComputedStyle(e);
    const m = s.filter.match(/blur\(([\d.]+)px\)/);
    if (m && +m[1] >= 20) { glow++; glowEx.push(`${Math.round(e.getBoundingClientRect().width)}px blob, blur ${m[1]}px`); }
    const sh = s.boxShadow; if (sh && sh !== "none" && /0px 0px (\d+)px/.test(sh) && +RegExp.$1 >= 24 && !/rgba\(0, 0, 0/.test(sh)) { glow++; glowEx.push("colored glow shadow"); }
    if (s.backdropFilter && s.backdropFilter !== "none") glass++;
  }
  out.glow = { count: glow, examples: glowEx.slice(0, 3) };
  out.glass = glass;

  // Pills and eyebrow labels
  let pills = 0, eyebrowPills = 0, capsLabels = 0; const pillEx = [];
  for (const e of all) {
    const s = getComputedStyle(e); const r = e.getBoundingClientRect();
    const hasBox = (s.backgroundColor !== "rgba(0, 0, 0, 0)" || px(s.borderTopWidth) > 0);
    if (hasBox && r.height > 14 && r.height <= 44 && r.width < 360 && r.width >= r.height * 1.5 && px(s.borderTopLeftRadius) >= r.height / 2 - 1 && e.innerText && e.innerText.trim()) {
      pills++;
      const tag = e.tagName.toLowerCase();
      if (!["button", "input", "select", "label"].includes(tag) && !e.closest("button,label") && pillEx.length < 5) pillEx.push(short(e.innerText));
      let n = e.nextElementSibling; for (let i = 0; i < 2 && n && !/H[1-3]/.test(n.tagName); i++) n = n.nextElementSibling;
      if (n && /H[1-3]/.test(n.tagName) && !["button", "a"].includes(tag)) eyebrowPills++;
    }
    if (s.textTransform === "uppercase" && px(s.letterSpacing) >= px(s.fontSize) * 0.05 && px(s.fontSize) <= 15 && e.children.length === 0 && e.innerText && e.innerText.trim().length > 2) capsLabels++;
  }
  out.pills = { total: pills, eyebrowPills, examples: pillEx };
  out.capsLabels = capsLabels;

  // Icon tiles
  let tiles = 0, lucide = document.querySelectorAll("svg.lucide, svg[class*='lucide']").length;
  for (const e of all) {
    const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    if (r.width >= 28 && r.width <= 72 && Math.abs(r.width - r.height) < 4 && px(s.borderTopLeftRadius) >= 6 &&
        s.backgroundColor !== "rgba(0, 0, 0, 0)" && e.querySelector("svg") && (e.innerText || "").trim().length === 0) tiles++;
  }
  const lineIcons = [...document.querySelectorAll("svg")].filter((v) => vis(v) && v.getAttribute("fill") === "none" && v.getAttribute("stroke")).length;
  out.icons = { tiles, lucide, lineIcons };

  // Cards, rounding, hairlines
  const boxes = all.filter((e) => { const s = getComputedStyle(e); const r = e.getBoundingClientRect(); return r.width >= 140 && r.height >= 80 && (px(s.borderTopWidth) > 0 || s.boxShadow !== "none" || s.backgroundColor !== "rgba(0, 0, 0, 0)") && e !== document.body; });
  const radii = boxes.map((e) => Math.round(px(getComputedStyle(e).borderTopLeftRadius)));
  const rounded = radii.filter((r) => r >= 12).length;
  const radCount = {}; radii.filter((r) => r > 0).forEach((r) => radCount[r] = (radCount[r] || 0) + 1);
  const topRad = Object.entries(radCount).sort((a, b) => b[1] - a[1])[0];
  const cards = boxes.filter((e) => { const s = getComputedStyle(e); return px(s.borderTopLeftRadius) >= 6 && (px(s.borderTopWidth) === 1 || s.boxShadow !== "none"); });
  out.rounding = { boxes: boxes.length, roundedOver12px: rounded, share: boxes.length ? +(rounded / boxes.length).toFixed(2) : 0, mostCommonRadius: topRad ? `${topRad[0]}px x${topRad[1]}` : "none", hairlineOrShadowCards: cards.length };

  // Repeated card rows (3-up) and bento
  let threeUp = 0, repeatedSets = 0, bento = 0; const rowsEx = [];
  for (const p of all) {
    const kids = [...p.children].filter(vis); if (kids.length < 2) continue;
    const ps = getComputedStyle(p);
    const sizes = kids.map((k) => { const r = k.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), Math.round(r.top)]; });
    if (ps.display.includes("grid")) {
      const spans = kids.filter((k) => { const s = getComputedStyle(k); return /span [2-9]/.test(s.gridColumnEnd) || /span [2-9]/.test(s.gridRowEnd); }).length;
      const widths = new Set(sizes.map((s) => s[0])); 
      if (spans && kids.length >= 4 && widths.size >= 2 && kids.every((k) => px(getComputedStyle(k).borderTopLeftRadius) > 0)) bento++;
    }
    if (kids.length >= 3 && sizes[0][0] >= 140) {
      const first = sizes[0]; const same = sizes.filter((s) => Math.abs(s[0] - first[0]) <= 2 && Math.abs(s[1] - first[1]) <= 4);
      if (same.length === kids.length) {
        repeatedSets++;
        const perRow = sizes.filter((s) => Math.abs(s[2] - first[2]) <= 2).length;
        if (perRow === 3) { threeUp++; rowsEx.push(`${kids.length} x ${first[0]}x${first[1]} (${(p.className || p.tagName).toString().split(" ")[0]})`); }
      }
    }
  }
  out.cardRows = { threeUp, identicalSets: repeatedSets, bento, examples: rowsEx.slice(0, 4) };

  // Section rhythm
  const sections = [...document.querySelectorAll("body > section, main > section, body > div > section, main > div > section, section")].filter(vis)
    .filter((s, i, arr) => !arr.some((o) => o !== s && o.contains(s)));
  const pads = sections.map((s) => { const c = getComputedStyle(s); return `${Math.round(px(c.paddingTop))}/${Math.round(px(c.paddingBottom))}`; });
  const padCount = {}; pads.forEach((p) => padCount[p] = (padCount[p] || 0) + 1);
  const topPad = Object.entries(padCount).sort((a, b) => b[1] - a[1])[0];
  const maxW = sections.map((s) => { const inner = s.firstElementChild; return inner ? Math.round(inner.getBoundingClientRect().width) : 0; });
  const wCount = {}; maxW.forEach((w) => wCount[w] = (wCount[w] || 0) + 1);
  const topW = Object.entries(wCount).sort((a, b) => b[1] - a[1])[0];
  const bgs = sections.map((s) => getComputedStyle(s).backgroundColor);
  let alternating = 0; for (let i = 2; i < bgs.length; i++) if (bgs[i] === bgs[i - 2] && bgs[i] !== bgs[i - 1]) alternating++;
  const centeredHeads = [...document.querySelectorAll("h2")].filter(vis).filter((h) => getComputedStyle(h).textAlign === "center").length;
  out.rhythm = { sections: sections.length, mostCommonPadding: topPad ? `${topPad[0]} on ${topPad[1]}/${sections.length}` : "n/a", padShare: topPad && sections.length ? +(topPad[1] / sections.length).toFixed(2) : 0,
    sameInnerWidth: topW && sections.length ? `${topW[0]}px on ${topW[1]}/${sections.length}` : "n/a", widthShare: topW && sections.length ? +(topW[1] / sections.length).toFixed(2) : 0,
    alternatingBackgrounds: alternating, centeredH2s: centeredHeads, totalH2s: document.querySelectorAll("h2").length };

  // Hero formula and typography
  const h1 = document.querySelector("h1");
  const body = getComputedStyle(document.body);
  if (h1) {
    const s = getComputedStyle(h1);
    const hero = h1.closest("section,header,div[class*='hero']") || h1.parentElement;
    const btns = [...hero.querySelectorAll("a,button")].filter(vis).filter((b) => { const c = getComputedStyle(b); return px(c.paddingLeft) >= 12 && (c.backgroundColor !== "rgba(0, 0, 0, 0)" || px(c.borderTopWidth) > 0); });
    const ghost = btns.filter((b) => getComputedStyle(b).backgroundColor === "rgba(0, 0, 0, 0)").length;
    out.hero = { centered: s.textAlign === "center", buttons: btns.length, ghostButtons: ghost, fontPx: Math.round(px(s.fontSize)), letterSpacingEm: +(px(s.letterSpacing) / px(s.fontSize)).toFixed(3), weight: s.fontWeight };
    out.type = { h1Font: s.fontFamily.split(",")[0].replace(/["']/g, ""), bodyFont: body.fontFamily.split(",")[0].replace(/["']/g, "") };
  }
  out.type = out.type || { bodyFont: body.fontFamily.split(",")[0].replace(/["']/g, "") };
  out.type.defaultSans = /^(inter|geist|ui-sans-serif|system-ui|-apple-system|arial|helvetica)/i.test(out.type.bodyFont);
  out.emoji = (text.match(/[\u{1F680}\u{2728}\u{26A1}\u{1F3AF}\u{1F4A1}\u{1F525}\u{1F31F}\u{1F4C8}\u{1F4AA}\u{1F389}]/gu) || []).length;
  out.arrows = (text.match(/\u2192/g) || []).length;
  out.middleDots = (text.match(/\s\u00b7\s/g) || []).length;

  // Colors for clusters
  const bodyBg = rgb(getComputedStyle(document.body).backgroundColor) || { r: 255, g: 255, b: 255 };
  out.palette = { purpleElements: all.filter((e) => { const s = getComputedStyle(e); return isPurple(s.backgroundColor) || isPurple(s.color); }).length,
    darkBase: hue(bodyBg).l < 0.12, creamBase: bodyBg.r > 240 && bodyBg.g > 232 && bodyBg.b > 215 && bodyBg.r - bodyBg.b > 10 };

  // Motion: hidden-until-scroll content, hover lift rules
  const vh = innerHeight;
  out.motion = { hiddenBelowFold: all.filter((e) => e.getBoundingClientRect().top > vh && getComputedStyle(e).opacity === "0").length, hoverLiftRules: 0 };
  for (const sh of document.styleSheets) { let rules; try { rules = sh.cssRules; } catch { continue; }
    for (const r of rules || []) { const t = r.cssText || ""; if (/:hover/.test(t) && /translateY\(-|translate3d\(0px?, -|box-shadow/.test(t)) out.motion.hoverLiftRules++; } }
  return out;
}

function grade(m) {
  const F = [];
  const add = (big, name, state, detail) => F.push({ big, name, state, detail });
  const st = (v, part, pres) => (v >= pres ? "Present" : v >= part ? "Partial" : "Absent");
  add(true, "Em dashes in visible text", m.emDash.count >= 4 || m.emDash.per1000 >= 3 ? "Present" : m.emDash.count >= 2 ? "Partial" : "Absent", `${m.emDash.count} (${m.emDash.per1000}/1000 words)`);
  add(true, "Script/italic/colored accent word in headings", st(m.headingHighlightCount, 1, 2), `${m.headingHighlightCount} heading(s)`);
  add(true, "Gradient text", st(m.gradients.textCount, 1, 1), `${m.gradients.textCount}`);
  add(true, "Decorative gradient backgrounds", st(m.gradients.decorativeCount, 1, 3), `${m.gradients.decorativeCount} (${m.gradients.purpleish} purple-ish; ${m.gradients.photoFades} photo fades ignored)`);
  add(true, "Blurred glow blobs", st(m.glow.count, 1, 2), `${m.glow.count}`);
  add(false, "Glassmorphism", st(m.glass, 1, 2), `${m.glass} backdrop-filter elements`);
  add(true, "Pill/eyebrow overload", m.pills.eyebrowPills >= 2 || m.capsLabels >= 4 || m.pills.total >= 10 ? "Present" : m.pills.eyebrowPills || m.capsLabels >= 2 || m.pills.total >= 5 ? "Partial" : "Absent", `${m.pills.total} pills, ${m.pills.eyebrowPills} above headings, ${m.capsLabels} caps labels`);
  add(true, "Icons in rounded tiles", st(m.icons.tiles, 2, 3), `${m.icons.tiles} tiles, ${m.icons.lucide} Lucide svgs`);
  add(false, "Excessive rounding + hairline cards", m.rounding.share >= 0.6 && m.rounding.hairlineOrShadowCards >= 4 ? "Present" : m.rounding.share >= 0.4 ? "Partial" : "Absent", `${Math.round(m.rounding.share * 100)}% of boxes radius>=12px; most common ${m.rounding.mostCommonRadius}; ${m.rounding.hairlineOrShadowCards} bordered/shadowed cards`);
  add(true, "Repeated 3-card rows", st(m.cardRows.threeUp, 1, 2), `${m.cardRows.threeUp} rows of 3 identical cards; ${m.cardRows.identicalSets} identical sets`);
  add(false, "Bento grid", st(m.cardRows.bento, 1, 1), `${m.cardRows.bento}`);
  add(true, "Mechanical spacing rhythm", m.rhythm.padShare >= 0.75 && m.rhythm.widthShare >= 0.6 ? "Present" : m.rhythm.padShare >= 0.6 || m.rhythm.alternatingBackgrounds >= 2 ? "Partial" : "Absent", `padding ${m.rhythm.mostCommonPadding}; inner width ${m.rhythm.sameInnerWidth}; ${m.rhythm.alternatingBackgrounds} alternating bg`);
  if (m.hero) add(true, "Centered hero + two-button formula", m.hero.centered && m.hero.buttons === 2 ? "Present" : m.hero.centered || (m.hero.buttons === 2 && m.hero.ghostButtons === 1) ? "Partial" : "Absent", `centered=${m.hero.centered}, ${m.hero.buttons} buttons (${m.hero.ghostButtons} ghost)`);
  if (m.hero) add(false, "Oversized clean sans headline", m.type.defaultSans && m.hero.fontPx >= 48 && m.hero.letterSpacingEm < 0 ? "Present" : m.hero.fontPx >= 56 && m.hero.letterSpacingEm < -0.01 ? "Partial" : "Absent", `${m.type.h1Font} ${m.hero.fontPx}px, tracking ${m.hero.letterSpacingEm}em; body ${m.type.bodyFont}`);
  add(false, "Fade-up / hover-lift motion", m.motion.hiddenBelowFold >= 5 && m.motion.hoverLiftRules >= 2 ? "Present" : m.motion.hiddenBelowFold >= 3 || m.motion.hoverLiftRules >= 3 ? "Partial" : "Absent", `${m.motion.hiddenBelowFold} hidden-until-scroll elements, ${m.motion.hoverLiftRules} hover lift/shadow rules`);
  add(false, "Emoji / arrows / middle dots", m.emoji >= 2 || m.arrows >= 5 || m.middleDots >= 3 ? "Present" : m.emoji || m.arrows >= 3 || m.middleDots ? "Partial" : "Absent", `${m.emoji} emoji, ${m.arrows} arrows, ${m.middleDots} middle dots`);

  const clusters = [];
  const gradientish = m.gradients.textCount + m.gradients.decorativeCount + m.glow.count;
  if (m.palette.purpleElements >= 3 && gradientish >= 2) clusters.push("Lovable/Bolt purple-gradient SaaS");
  if (m.type.defaultSans && m.rounding.hairlineOrShadowCards >= 4 && m.icons.lucide >= 3) clusters.push("v0/shadcn kit (Inter/Geist, hairline rounded cards, Lucide)");
  if (m.palette.creamBase && !m.type.defaultSans && (m.headingHighlightCount || m.capsLabels >= 2)) clusters.push("Claude-style cream editorial (cream, serif, accent words)");
  if (m.palette.darkBase && (m.glow.count || m.gradients.textCount)) clusters.push("Dark glow SaaS");
  if (m.cardRows.bento) clusters.push("Bento product page");

  const present = F.filter((f) => f.state === "Present");
  const big = present.filter((f) => f.big).length;
  const verdict = present.length >= 6 || big >= 3 ? "YES: strong AI-generated fingerprint" : present.length >= 3 || big >= 2 ? "SOME: a few AI fingerprints" : "NO: few AI fingerprints";
  return { verdict, present: present.length, bigSixPresent: big, fingerprints: F, clusters };
}

(async () => {
  let browser;
  try { browser = await chromium.launch(); } catch (e) { console.error("LAUNCH_FAILED " + e.message); process.exit(3); }
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(url, { waitUntil: "networkidle", timeout: 45000 }).catch(() => page.goto(url, { waitUntil: "load", timeout: 45000 }));
  await page.waitForTimeout(800);
  const m = await page.evaluate(measure);
  await page.screenshot({ path: path.join(outDir, "desktop-top.png") });
  // scroll to trigger reveal animations, then full page
  const h = await page.evaluate(() => document.body.scrollHeight);
  for (let y = 0; y < h; y += 700) { await page.evaluate((yy) => scrollTo(0, yy), y); await page.waitForTimeout(120); }
  await page.evaluate(() => scrollTo(0, 0)); await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(outDir, "desktop-full.png"), fullPage: true });
  const mob = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  await mob.goto(url, { waitUntil: "load", timeout: 45000 });
  const mh = await mob.evaluate(() => document.body.scrollHeight);
  for (let y = 0; y < mh; y += 700) { await mob.evaluate((yy) => scrollTo(0, yy), y); await mob.waitForTimeout(100); }
  await mob.evaluate(() => scrollTo(0, 0)); await mob.waitForTimeout(400);
  await mob.screenshot({ path: path.join(outDir, "mobile-full.png"), fullPage: true });
  await browser.close();

  const g = grade(m);
  fs.writeFileSync(path.join(outDir, "render-scan.json"), JSON.stringify({ url, grade: g, measurements: m }, null, 2));
  console.log(`\n=== ${url}`);
  console.log(`RENDERED VERDICT: ${g.verdict}  (${g.present} present, ${g.bigSixPresent} of the big tells)`);
  if (g.clusters.length) console.log(`CLUSTERS: ${g.clusters.join("; ")}`);
  for (const s of ["Present", "Partial"]) {
    const rows = g.fingerprints.filter((f) => f.state === s); if (!rows.length) continue;
    console.log(`\n${s.toUpperCase()}`);
    rows.forEach((f) => console.log(` ${f.big ? "*" : " "} ${f.name}: ${f.detail}`));
  }
  const ex = [];
  if (m.emDash.examples.length) ex.push("Em dashes: " + m.emDash.examples.join(" | "));
  if (m.headingHighlights.length) ex.push("Heading accents: " + m.headingHighlights.join(" | "));
  if (m.gradients.decorative.length) ex.push("Gradients: " + m.gradients.decorative.join(", "));
  if (m.pills.examples.length) ex.push("Pills: " + m.pills.examples.join(" | "));
  if (m.cardRows.examples.length) ex.push("3-up rows: " + m.cardRows.examples.join(", "));
  if (ex.length) { console.log("\nWHERE"); ex.forEach((e) => console.log("  " + e)); }
  console.log(`\n* = big tell. Screenshots + render-scan.json in ${outDir}. Confirm by viewing the screenshots.`);
})().catch((e) => { console.error(e); process.exit(1); });
