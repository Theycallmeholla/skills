#!/usr/bin/env node
/**
 * Website audit crawler — deterministic layer of the website-audit skill.
 * Usage: node audit.mjs <url> [--max-pages=10] [--out=./audit-out]
 * Output: <out>/audit.json + <out>/screenshots/*.png
 */
import { chromium } from 'playwright';
import { mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const argUrl = process.argv[2];
if (!argUrl) { console.error('Usage: node audit.mjs <url> [--max-pages=N] [--out=dir]'); process.exit(1); }
const opts = Object.fromEntries(process.argv.slice(3).map(a => { const m = a.match(/^--([^=]+)=(.*)$/); return m ? [m[1], m[2]] : [a, true]; }));
const MAX_PAGES = parseInt(opts['max-pages'] || '10', 10);
const START = new URL(argUrl.startsWith('http') ? argUrl : 'https://' + argUrl);
const ORIGIN_HOST = START.hostname.replace(/^www\./, '');
const OUT = opts.out || `./audit-${ORIGIN_HOST}`;
const SHOTS = join(OUT, 'screenshots');
mkdirSync(SHOTS, { recursive: true });

const sameSite = (u) => { try { return new URL(u).hostname.replace(/^www\./, '') === ORIGIN_HOST; } catch { return false; } };
const norm = (u) => { try { const x = new URL(u); x.hash = ''; return x.href; } catch { return null; } };
const slug = (u) => (new URL(u).pathname.replace(/\/$/, '') || 'home').replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').slice(0, 60) || 'home';

// Prefer playwright's own resolution; fall back to a preinstalled chromium binary if versions mismatch.
// Honor env proxies (sandboxed environments often route egress via a local MITM proxy that
// Chromium won't pick up from env vars — pass it explicitly and relax cert checks only then).
const PROXY = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || null;
// MITM proxies often can't negotiate Chromium's TLS 1.3 handshake — cap at 1.2 when proxied.
const launchOpts = PROXY ? { proxy: { server: PROXY }, args: ['--ssl-version-max=tls1.2'] } : {};
const ctxExtra = PROXY ? { ignoreHTTPSErrors: true } : {};
let browser;
try { browser = await chromium.launch(launchOpts); }
catch {
  const fallback = ['/opt/pw-browsers/chromium', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome'].find(p => existsSync(p));
  if (!fallback) throw new Error('No Chromium found. Run: npx playwright install chromium');
  browser = await chromium.launch({ ...launchOpts, executablePath: fallback });
}
const result = {
  start_url: START.href, host: ORIGIN_HOST, crawled_at: new Date().toISOString(),
  site_checks: {}, pages: [], broken_internal_links: [], broken_external_links: [],
  errors: [],
};

// ---------- site-level checks ----------
async function headOrGet(url, timeout = 12000) {
  try {
    const ctl = AbortSignal.timeout(timeout);
    let r = await fetch(url, { method: 'HEAD', redirect: 'follow', signal: ctl }).catch(() => null);
    if (!r || r.status === 405 || r.status === 403) r = await fetch(url, { method: 'GET', redirect: 'follow', signal: AbortSignal.timeout(timeout) });
    return r;
  } catch { return null; }
}

{
  // http -> https redirect
  try {
    const r = await fetch(`http://${START.hostname}/`, { redirect: 'manual', signal: AbortSignal.timeout(12000) });
    const loc = r.headers.get('location') || '';
    result.site_checks.http_redirects_to_https = r.status >= 300 && r.status < 400 && loc.startsWith('https');
  } catch { result.site_checks.http_redirects_to_https = null; }

  const robots = await headOrGet(`${START.origin}/robots.txt`);
  result.site_checks.robots_txt = !!(robots && robots.ok);
  const sitemap = await headOrGet(`${START.origin}/sitemap.xml`);
  result.site_checks.sitemap_xml = !!(sitemap && sitemap.ok);
  const r404 = await headOrGet(`${START.origin}/definitely-not-a-real-page-zq9x`);
  result.site_checks.returns_404_for_missing = r404 ? r404.status === 404 : null;
  const fav = await headOrGet(`${START.origin}/favicon.ico`);
  result.site_checks.favicon_ico = !!(fav && fav.ok);
}

// ---------- crawl ----------
const queue = [norm(START.href)];
const seen = new Set(queue);
const externalLinks = new Set();
let homepageShotDone = false;

while (queue.length && result.pages.length < MAX_PAGES) {
  const url = queue.shift();
  const ctx = await browser.newContext({ ...ctxExtra, viewport: { width: 1440, height: 900 }, userAgent: 'Mozilla/5.0 (compatible; SiteAuditBot/1.0)' });
  const page = await ctx.newPage();
  const consoleErrors = [];
  const failedRequests = [];
  page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text().slice(0, 300)); });
  page.on('pageerror', e => consoleErrors.push('pageerror: ' + String(e).slice(0, 300)));
  page.on('requestfailed', rq => { const f = rq.failure()?.errorText || ''; if (!/ERR_ABORTED/.test(f)) failedRequests.push({ url: rq.url().slice(0, 200), error: f }); });

  const rec = { url, status: null, load_ms: null, console_errors: [], failed_requests: [], seo: {}, links_internal: 0, links_external: 0, screenshot: null, mixed_content: false };
  try {
    const t0 = Date.now();
    const resp = await page.goto(url, { waitUntil: 'load', timeout: 45000 });
    rec.load_ms = Date.now() - t0;
    rec.status = resp ? resp.status() : null;
    await page.waitForTimeout(1500);

    rec.seo = await page.evaluate(() => {
      const q = (s) => document.querySelector(s);
      const imgs = [...document.images];
      return {
        title: document.title || '',
        title_length: (document.title || '').length,
        meta_description: q('meta[name="description"]')?.content || '',
        meta_description_length: (q('meta[name="description"]')?.content || '').length,
        h1_count: document.querySelectorAll('h1').length,
        h1_text: q('h1')?.innerText?.trim().slice(0, 150) || '',
        viewport_meta: !!q('meta[name="viewport"]'),
        canonical: q('link[rel="canonical"]')?.href || null,
        og_title: !!q('meta[property="og:title"]'),
        og_image: !!q('meta[property="og:image"]'),
        schema_jsonld: document.querySelectorAll('script[type="application/ld+json"]').length,
        images_total: imgs.length,
        images_missing_alt: imgs.filter(i => !i.alt?.trim()).length,
        images_broken: imgs.filter(i => i.complete && i.naturalWidth === 0 && i.src).length,
        tel_links: document.querySelectorAll('a[href^="tel:"]').length,
        forms: document.querySelectorAll('form').length,
        word_count: (document.body?.innerText || '').split(/\s+/).filter(Boolean).length,
        copyright_year: (document.body?.innerText.match(/(?:©|copyright)\s*(\d{4})/i) || [])[1] || null,
        lorem_ipsum: /lorem ipsum/i.test(document.body?.innerText || ''),
      };
    });

    rec.mixed_content = failedRequests.some(f => f.url.startsWith('http://')) ||
      await page.evaluate(() => location.protocol === 'https:' && [...document.querySelectorAll('img,script,link,iframe')].some(el => (el.src || el.href || '').startsWith('http://')));

    const links = await page.evaluate(() => [...document.querySelectorAll('a[href]')].map(a => a.href));
    for (const l of links) {
      const n = norm(l);
      if (!n || !/^https?:/.test(n)) continue;
      if (sameSite(n)) {
        rec.links_internal++;
        if (!seen.has(n) && !/\.(pdf|jpg|jpeg|png|gif|zip|docx?)($|\?)/i.test(n)) { seen.add(n); queue.push(n); }
      } else { rec.links_external++; externalLinks.add(n); }
    }

    const s = slug(url);
    rec.screenshot = `screenshots/${s}-desktop.png`;
    await page.screenshot({ path: join(SHOTS, `${s}-desktop.png`), fullPage: result.pages.length === 0 }).catch(() => { rec.screenshot = null; });

    if (!homepageShotDone) {
      homepageShotDone = true;
      const mctx = await browser.newContext({ ...ctxExtra, viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
      const mp = await mctx.newPage();
      try {
        await mp.goto(url, { waitUntil: 'load', timeout: 45000 });
        await mp.waitForTimeout(1500);
        await mp.screenshot({ path: join(SHOTS, 'home-mobile.png'), fullPage: true });
        rec.mobile_screenshot = 'screenshots/home-mobile.png';
        rec.mobile_horizontal_scroll = await mp.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 5);
      } catch (e) { result.errors.push('mobile shot: ' + String(e).slice(0, 200)); }
      await mctx.close();
    }
  } catch (e) {
    rec.error = String(e).slice(0, 300);
    result.errors.push(`${url}: ${rec.error}`);
  }
  rec.console_errors = consoleErrors.slice(0, 15);
  rec.failed_requests = failedRequests.slice(0, 15);
  result.pages.push(rec);
  await ctx.close();
  console.log(`crawled ${result.pages.length}/${MAX_PAGES}: ${url} [${rec.status}]`);
}

// ---------- link checking ----------
const crawledOk = new Set(result.pages.filter(p => p.status && p.status < 400).map(p => p.url));
for (const p of result.pages) if (p.status && p.status >= 400) result.broken_internal_links.push({ url: p.url, status: p.status });
// internal links queued but never crawled (over page budget): spot-check up to 30
const uncrawled = [...seen].filter(u => !result.pages.some(p => p.url === u)).slice(0, 30);
for (const u of uncrawled) {
  const r = await headOrGet(u);
  if (!r || r.status >= 400) result.broken_internal_links.push({ url: u, status: r ? r.status : 'unreachable' });
}
// external links: check up to 40
for (const u of [...externalLinks].slice(0, 40)) {
  const r = await headOrGet(u, 10000);
  if (!r || r.status >= 400) result.broken_external_links.push({ url: u, status: r ? r.status : 'unreachable' });
}

result.summary = {
  pages_crawled: result.pages.length,
  pages_with_console_errors: result.pages.filter(p => p.console_errors.length).length,
  broken_internal: result.broken_internal_links.length,
  broken_external: result.broken_external_links.length,
  pages_missing_meta_description: result.pages.filter(p => p.seo && !p.seo.meta_description).length,
  pages_bad_h1: result.pages.filter(p => p.seo && p.seo.h1_count !== 1).length,
  avg_load_ms: Math.round(result.pages.reduce((a, p) => a + (p.load_ms || 0), 0) / Math.max(1, result.pages.length)),
};

writeFileSync(join(OUT, 'audit.json'), JSON.stringify(result, null, 2));
console.log(`\nDone. ${result.pages.length} pages -> ${OUT}/audit.json`);
await browser.close();
