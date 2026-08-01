#!/usr/bin/env node
/**
 * Regression suite for assets/deck.html.
 *
 * Every case here is a bug that actually shipped once. Run this after any edit to
 * the template — the widget has no other safety net, and its failures are silent
 * (a dead deck looks exactly like a deck waiting for the user).
 *
 *   npm install playwright && node tests/run.js
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const TPL = fs.readFileSync(path.join(__dirname, '..', 'assets', 'deck.html'), 'utf8');
const TMP = fs.mkdtempSync('/tmp/swipe-deck-test-');
let pass = 0, fail = 0;

const card = (id, facet, extra = {}) =>
  Object.assign({ id, q: `Question ${id}`, facet, depth: 1, style: 'preference' }, extra);

// Decks are 20-28 cards in real use and the handoff fires with 5 left, so anything
// smaller transmits almost immediately and stops exercising the mid-deck paths.
const bulk = (prefix, n) =>
  Array.from({ length: n }, (_, i) => card(`${prefix}${i}`, i % 2 ? 'a' : 'b'));

function page(decks) {
  const body = decks.map(d => TPL.replace('__DECK_JSON__', JSON.stringify(d))).join('\n');
  const file = path.join(TMP, `p${Math.abs(JSON.stringify(decks).length)}-${decks.length}-${Date.now()}.html`);
  fs.writeFileSync(file,
    `<!doctype html><html><head><meta charset="utf-8"></head><body>` +
    `<script>window.__sent=[];window.sendPrompt=function(t){window.__sent.push(t)};</script>` +
    `${body}</body></html>`);
  return 'file://' + file;
}

const deck = (round, cards, facets) => ({
  round, topic: 'test topic', facets: facets || ['a', 'b'],
  carry: { swiped: 0, coverage: {} }, cards,
});

function check(name, cond, detail) {
  if (cond) { pass++; console.log(`  \x1b[32mPASS\x1b[0m ${name}`); }
  else { fail++; console.log(`  \x1b[31mFAIL\x1b[0m ${name}${detail ? ' — ' + detail : ''}`); }
}

async function swipeAll(p, key = 'ArrowRight', max = 40) {
  for (let i = 0; i < max; i++) {
    if (!(await p.locator('.sd-card.top').count())) break;
    await p.keyboard.press(key);
    await p.waitForTimeout(300);
  }
}

(async () => {
  const browser = await chromium.launch();
  const errors = [];
  const open = async url => {
    const p = await browser.newPage();
    p.on('pageerror', e => errors.push(`${url.split('/').pop()}: ${e.message}`));
    await p.goto(url); await p.waitForTimeout(400);
    return p;
  };

  console.log('\nsyntax');
  {
    // A literal closing script tag anywhere in the inline JS silently truncates it.
    const start = TPL.indexOf('<script>\n(function()');
    const bodyStart = TPL.indexOf('\n', start) + 1;
    const end = TPL.indexOf('</script', bodyStart);
    check('inline script is not truncated by a nested closing tag',
      end - bodyStart > 10000, `browser sees only ${end - bodyStart} chars`);
  }

  console.log('\nmulti-instance (round 2 renders below round 1)');
  {
    const p = await open(page([
      deck(1, bulk('x', 20)),
      deck(2, bulk('y', 20)),
    ]));
    const init = await p.evaluate(() => [...document.querySelectorAll('#sd-root')].map(r => r.dataset.on || 'NO'));
    const stacks = await p.evaluate(() => [...document.querySelectorAll('#sd-stack')].map(s => s.children.length));
    check('both decks initialise', init.every(v => v === '1'), JSON.stringify(init));
    check('both decks render cards', stacks.every(n => n === 3), JSON.stringify(stacks));
    await p.keyboard.press('ArrowRight'); await p.waitForTimeout(350);
    const counts = await p.evaluate(() => [...document.querySelectorAll('#sd-count')].map(c => c.textContent));
    check('one keypress swipes exactly one deck',
      counts.filter(c => c !== '0 swiped').length === 1, JSON.stringify(counts));
    await p.close();
  }

  console.log('\nhandoff / tail boundary');
  {
    // A `needs` gate collapses the queue by more than one, which used to make the
    // tail message re-report a card the main handoff already sent.
    const p = await open(page([deck(1, [
      card('p1', 'a'), card('p2', 'b'), card('X', 'a'),
      card('g1', 'b', { needs: 'X' }), card('g2', 'a', { needs: 'X' }),
      card('g3', 'b', { needs: 'X' }), card('z1', 'a'),
    ])]));
    for (let i = 0; i < 8; i++) {
      if (!(await p.locator('.sd-card.top').count())) break;
      const q = (await p.locator('.sd-card.top .sd-q').textContent()).trim();
      await p.keyboard.press(q === 'Question X' ? 'ArrowLeft' : 'ArrowRight');
      await p.waitForTimeout(310);
    }
    const sent = await p.evaluate(() => window.__sent);
    const lines = s => (s || '').split('\n').filter(l => l.startsWith('- ['))
      .map(l => l.replace(/^- \[[^\]]*\] /, '').replace(/ → .*$/, ''));
    const dupes = sent[1] ? lines(sent[1]).filter(q => lines(sent[0]).includes(q)) : [];
    check('no card is reported in both handoff and tail', dupes.length === 0, dupes.join(', '));
    check('in-flight count is pluralised correctly',
      !/\(1 cards still/.test(sent[0] || ''), 'says "1 cards"');
    await p.close();
  }

  console.log('\ndegenerate decks');
  {
    const p = await open(page([deck(1, [])]));
    const sent = await p.evaluate(() => window.__sent);
    check('empty deck reports instead of hanging', sent.length === 1, `${sent.length} messages`);
    check('empty deck says so on screen',
      /No cards/.test(await p.locator('#sd-end').textContent()));
    await p.close();
  }
  {
    // A literal closing script tag in card text truncates the JSON block.
    const bad = deck(1, [card('b1', 'a', { q: 'Inline a <' + '/script> tag' })]);
    const p = await open(page([bad]));
    const sent = await p.evaluate(() => window.__sent);
    check('unparseable deck asks Claude to re-emit',
      sent.length === 1 && /FAILED TO LOAD/.test(sent[0]), sent[0] ? sent[0].slice(0, 40) : 'nothing sent');
    await p.close();
  }

  console.log('\ninput fidelity');
  {
    const p = await open(page([deck(1, bulk('a', 20))]));
    await p.keyboard.press('ArrowRight'); await p.waitForTimeout(40);
    await p.keyboard.press('ArrowRight'); await p.waitForTimeout(40);
    await p.keyboard.press('ArrowRight'); await p.waitForTimeout(600);
    check('rapid keypresses cannot rate unseen cards',
      (await p.locator('#sd-count').textContent()) === '1 swiped',
      await p.locator('#sd-count').textContent());
    // The end card sets display:flex in CSS, which silently overrides the `hidden`
    // attribute unless [hidden] is re-asserted — it then peeks out behind the stack.
    check('closing card stays hidden while the stack is live',
      !(await p.locator('#sd-end').isVisible()));
    await p.close();
  }

  console.log('\nundo');
  {
    const p = await open(page([deck(1, bulk('u', 20))]));
    const first = (await p.locator('.sd-card.top .sd-q').textContent()).trim();
    await p.keyboard.press('ArrowRight'); await p.waitForTimeout(320);
    await p.keyboard.press('ArrowRight'); await p.waitForTimeout(320);
    await p.keyboard.press('z'); await p.waitForTimeout(300);
    check('undo restores the last untransmitted swipe',
      (await p.locator('#sd-count').textContent()) === '1 swiped');
    // one step only — a second undo must not keep rewinding the deck
    await p.keyboard.press('z'); await p.waitForTimeout(250);
    check('undo is a single step, not a rewind',
      (await p.locator('#sd-count').textContent()) === '1 swiped' &&
      !(await p.locator('#sd-undo').isVisible()));
    await p.keyboard.press('ArrowRight'); await p.waitForTimeout(320);
    check('a fresh swipe re-surfaces the take-back button',
      await p.locator('#sd-undo').isVisible());
    await swipeAll(p);
    check('take-back disappears once swipes have been sent to Claude',
      !(await p.locator('#sd-undo').isVisible()));
    await p.close();
  }

  console.log('\nword edit (counter-offer)');
  {
    const cards = bulk('e', 20);
    cards[0] = card('e0', 'a', { q: 'Under $5k all in', predict: 'yes' });
    const p = await open(page([deck(1, cards)]));
    await p.locator('.sd-card.top .sd-w').nth(1).click();  // tap "$5k"
    await p.waitForTimeout(150);
    check('tapping a word opens an inline input',
      (await p.locator('.sd-card.top .sd-wIn').count()) === 1);
    await p.keyboard.type('$15k'); await p.keyboard.press('Enter'); await p.waitForTimeout(200);
    const q = (await p.locator('.sd-card.top .sd-q').textContent()).replace(/\s+/g, ' ').trim();
    check('the card now says what the user meant', q === 'Under $15k all in', q);
    check('the rewritten word is highlighted',
      (await p.locator('.sd-card.top .sd-w.m').textContent()).trim() === '$15k');
    await swipeAll(p);
    const sent = await p.evaluate(() => window.__sent);
    check('the handoff carries the before and after',
      /EDITED CARDS/.test(sent[0]) && /"Under \$5k all in" → "Under \$15k all in" → YES/.test(sent[0]));
    // I predicted about a statement the user rewrote — that prediction must count as a miss
    check('an edit voids the prediction as a miss',
      /predicted correctly: 0\/1/.test(sent[0]),
      (sent[0].match(/predicted correctly.*/) || [''])[0]);
    await p.close();
  }

  console.log('\nsaturation meter');
  {
    const meter = async p => parseInt((await p.locator('#sd-mlabel').textContent()).match(/(\d+)%/)[1], 10);
    const facets = ['a', 'b'];
    const predicted = v => bulk('m', 24).map(c => Object.assign({}, c, { predict: v, depth: 2 }));

    // Claude guessed every card right and both facets got depth — the meter should fill.
    let p = await open(page([deck(1, predicted('yes'), facets)]));
    check('meter starts empty', (await meter(p)) === 0, `${await meter(p)}%`);
    await swipeAll(p, 'ArrowRight');
    const hit = await meter(p);
    check('meter fills when predictions hold and facets are covered', hit >= 85, `${hit}%`);
    const sent = await p.evaluate(() => window.__sent);
    check('a full meter tells Claude to stop', /METER IS FULL/.test(sent[0]), sent[0].slice(-90));
    await p.close();

    // Same deck, every prediction wrong — still learning, so the meter must stay down.
    p = await open(page([deck(1, predicted('no'), facets)]));
    await swipeAll(p, 'ArrowRight');
    const miss = await meter(p);
    check('meter stays low while swipes keep surprising Claude', miss < 85 && miss < hit, `${miss}% vs ${hit}%`);
    const sent2 = await p.evaluate(() => window.__sent);
    check('an unfilled meter asks for more cards, not a new round',
      /Send ONE more batch/.test(sent2[0]) && /"hits":/.test(sent2[0]), sent2[0].slice(-90));
    // The deck is one continuous run. Any "round" language leaking into a message the
    // user can see in the transcript is the bug this whole design exists to avoid.
    check('no round language reaches the user',
      !/\bround\b/i.test(sent.concat(sent2).join('\n')),
      sent.concat(sent2).join('\n').match(/.{0,40}round.{0,40}/i));
    await p.close();

    // A whole facet left untouched must cap the meter no matter how good the predictions are.
    p = await open(page([deck(1, predicted('yes'), ['a', 'b', 'untouched-facet'])]));
    await swipeAll(p, 'ArrowRight');
    const capped = await meter(p);
    check('an uncovered facet caps the meter below full', capped <= 70, `${capped}%`);
    await p.close();

    // Being wrong about a third of the swipes is not "I've got it", however well the
    // other terms score. A weighted average alone would let coverage paper over this.
    const mixed = bulk('k', 30).map((c, i) =>
      Object.assign({}, c, { depth: 2, predict: i % 3 === 0 ? 'no' : 'yes' }));
    p = await open(page([deck(1, mixed, facets)]));
    await swipeAll(p, 'ArrowRight');   // every third prediction misses → ~67% correct
    const surprised = await meter(p);
    check('sustained wrong predictions cap the meter below full', surprised <= 80, `${surprised}%`);
    await p.close();
  }

  console.log('\nescaping');
  {
    const evil = '<img src=x onerror="window.__pwn=1">';
    const p = await open(page([deck(1, [
      card('e1', 'a', { q: evil, hint: '<svg onload="window.__pwn=1">' }),
      card('e2', evil), card('e3', 'b'),
    ], ['a', 'b', evil])]));
    check('card content cannot execute script', (await p.evaluate(() => window.__pwn || 0)) === 0);
    check('markup renders as literal text',
      (await p.locator('.sd-card.top .sd-q').textContent()).includes('<img'));
    await p.close();
  }

  console.log('\nnotes');
  {
    const p = await open(page([deck(1, bulk('n', 20))]));
    await p.keyboard.press('n'); await p.waitForTimeout(150);
    await p.keyboard.type('a typed aside'); await p.keyboard.press('Enter'); await p.waitForTimeout(250);
    await swipeAll(p);
    const sent = await p.evaluate(() => window.__sent);
    check('a typed note reaches the handoff', /a typed aside/.test(sent.join('\n')));
    await p.close();
  }

  check('no uncaught page errors', errors.length === 0, errors.join(' | '));

  await browser.close();
  fs.rmSync(TMP, { recursive: true, force: true });
  console.log(`\n${pass} passed, ${fail} failed\n`);
  process.exit(fail ? 1 : 0);
})();
