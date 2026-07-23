# UI Oddity Checklist

The full checklist, with concrete examples of each oddity and of near-misses that should NOT be flagged. Work through it category by category against your Step-3 inventories. Remember the scope: UI, visual design, and copy structure — no link/href auditing, no SEO, no accessibility audits, no rewording suggestions.

## Contents

1. [Repetition & redundancy](#1-repetition--redundancy)
2. [Copy oddities](#2-copy-oddities)
3. [CTA oddities (visual/copy only)](#3-cta-oddities-visualcopy-only)
4. [Layout & alignment](#4-layout--alignment)
5. [Imagery fit](#5-imagery-fit)
6. [Consistency](#6-consistency)
7. [Severity guide](#7-severity-guide)

---

## 1. Repetition & redundancy

The headline category. The unit of repetition is the **fact or message**, not the exact string — the same information counts as repeated even when every instance is worded differently.

**1a. Repeated facts.** A phone number, availability claim ("24/7"), rating, service area, or offer appearing multiple times within a screenful. Each fact earns one home per screenful.
- Flag: phone number in the top bar ("Call today: 555-0142"), again directly below it, and a third time inside the hero button — three homes for one fact within one viewport.
- Flag: "24/7 Emergency Repairs" as a top banner AND again lower on the page as "emergency service around the clock" — same fact, different words, still a repeat.
- Flag: the star-rating/review count shown twice in the same hero.
- Don't flag: the phone number in the header AND the footer (opposite ends of a long page — convention); the primary CTA repeating once per major scroll section.
- `page.json → repeated_facts` precomputes phone-number repeats with bounding boxes. Everything else — badges, taglines, availability, ratings — you map yourself in the fact map.

**1b. Verbatim duplicated copy too close together.** The same sentence or block appearing twice within a screen's height. Usually a copy-paste or CMS artifact.
- Flag: hero subheading repeated word-for-word as the first feature card's body text.
- `page.json → duplicates` precomputes exact pairs with pixel distance; treat < ~900px as "too close" by default. Also hunt near-duplicates yourself (the same sentence lightly reworded back-to-back).

**1c. Restatement.** An element that re-says what its neighbor just said, adding no new information — most often a bullet list or chip row under a paragraph covering the identical ground.
- Flag: paragraph says "we fix broken springs, doors that won't open, off-track doors, and noisy openers" and directly below it sits a chip list "Broken springs · Won't open · Off track · Opener issues · Noisy door". One of the two should carry that information; the other should either go or say something new (prices, timeframes, guarantees).
- Flag: two sections that are near-clones — same structure, same points, slightly different phrasing (usually a template block pasted twice and half-edited).
- Don't flag: a heading and its body (headings summarize by design); a legitimate summary ("in short, ...") at the end of a long section.

**1d. Overcrowding through duplication.** When repeats concentrate in one region — especially the hero/above-the-fold — call out the *density* as its own finding: many competing messages, several of them the same fact re-said. The fix framing is structural: each message appears once, biggest where it matters most.
- Flag: a hero containing the phone number twice, an emergency badge that also runs in the top banner, a review widget, a service chip row restating the subheading, and three CTAs — no single element can win attention.

## 2. Copy oddities

**2a. Orphaned / stray text, especially around CTAs.** Fragments that belong to nothing: a half-sentence below a button, a label with no field, a lone word between sections. Often a deleted element left its caption behind.
- Flag: "and start saving today" sitting alone under a "Get Started" button whose heading doesn't lead into it.
- Don't flag: intentional microcopy ("No credit card required" under a signup CTA is convention, not an orphan).

**2b. Placeholder / debug text.** `Lorem ipsum`, `TODO`, `TBD`, `[INSERT ...]`, `xxx`, `asdf`, `{{variable}}`, `${var}`, `undefined`, `null`, `NaN`, `[object Object]`, unrendered markdown shown literally.
- Always at least medium severity; `undefined`/`NaN`/`{{...}}` are high — they signal a live rendering bug.

**2c. Copy not matching the subject.** Body text that contradicts or ignores its own heading, or content about a different business entirely (template reuse artifact). Judge against the subject you stated in Step 1.
- Flag: section headed "Security" whose paragraph talks about pricing tiers.
- Flag: a garage-door repair page with a testimonial praising "the best pizza in town".
- Flag: labels that don't parse for this business — judge each chip/label row against what a first-time visitor would understand ("Repair · Emergency · Commercial" reads as three different kinds of thing: a service, a situation, a customer type).
- Don't flag: loosely-related content (a Features section mentioning pricing once is normal cross-selling).

**2d. Typos and mechanical errors.** Misspellings, doubled words ("the the"), wrong homophones, sentences that stop mid-
- Flag only what you're confident about; brand names and jargon are often intentionally odd.

## 3. CTA oddities (visual/copy only)

Judge CTAs by what they look and read like. Do NOT audit or report where they navigate — hrefs, dead links, and target mismatches are out of scope.

**3a. Identical CTAs stacked too close.** Two buttons with the same label in the same visual group; one is redundant and dilutes the click.
- Flag: "Start free trial" twice inside one hero.
- Don't flag: the same primary CTA repeating once per major scroll section.

**3b. Vague labels.** "Click here", "Submit", "Go", "More" — or "Learn more" used 4+ times so destinations can't be told apart by their labels.

**3c. CTA text conflicting with nearby copy.** The button promises something the surrounding text contradicts.
- Flag: copy says "No signup needed" next to a "Sign up to continue" button.

## 4. Layout & alignment

Judge these from the screenshot; `page.json → overflow_elements` and `broken_images` give deterministic help for two of them.

**4a. Overlapping elements** — text over text, a badge covering a word, a sticky header eating a heading.
**4b. Cut-off / truncated text** — ellipsis where it shouldn't be, text clipped mid-letter or mid-sentence by its container.
**4c. Misalignment.** Elements that visibly should share a baseline, edge, or center but don't: star icons floating above or below their "4.9 · 212 reviews" text, icons not centered with their labels, one card's button sitting lower than its siblings'. These read as sloppiness fast — flag them even when small.
**4d. Broken images** — alt text or broken-image icon showing; zero-size images that collapsed a layout slot.
**4e. Horizontal overflow** — content wider than the viewport.
**4f. Spacing incoherence** — comparable sections with wildly different vertical rhythm. Only flag when it looks accidental, not designed.
**4g. Contrast** — text a sighted visitor visibly struggles to read (light gray on white body copy, text over a busy image with no overlay). This is a visual finding, not a WCAG audit — no ratios needed.
**4h. Overcrowding.** A region — almost always the hero — packed with more competing elements than a visitor can parse: multiple badges, repeated facts, chip rows, review widgets, several CTAs. Pairs with 1d when the crowding comes from duplication.

## 5. Imagery fit

Every prominent image should earn its place: right business, right section, right feel. Judge against the subject stated in Step 1.

**5a. Subject mismatch.** The image shows something other than what the business does or the section discusses.
- Flag: a garage-door repair hero whose background photo is just a house with no garage door in frame.
- Flag: a "Meet the team" section using an obvious generic stock photo of different people than the testimonials name.
**5b. Placeholder/artifact imagery.** Visible stock watermarks, gray placeholder boxes, the same photo used twice in different sections, an image clearly cropped wrong (heads cut off, product half out of frame).
**5c. Text-over-image legibility** — belongs to 4g, but check it per image: busy imagery behind headline text with no overlay.
- Don't flag: abstract/decorative backgrounds (gradients, patterns) — those aren't claiming to depict the business.

## 6. Consistency

**6a. Naming drift.** The product/brand written multiple ways: "QuickBooks" / "Quickbooks" / "Quick Books" on one page.
**6b. Tone whiplash.** Formal corporate copy in one section, slang in the next — unless the page is clearly playing that for effect.
**6c. Heading style drift.** Title Case for some section headings, sentence case for others, ALL CAPS for one random section.
**6d. Person/voice drift.** Switching between "you", "we", and third person across comparable copy slots (three feature cards: two say "You get...", one says "Customers receive...").
**6e. Format drift.** "$10/mo" and "10 dollars monthly" in the same table; dates in two formats; "email"/"e-mail".

## 7. Severity guide

- **HIGH** — a visitor will notice quickly and it damages trust or blocks conversion: rendering bugs (`undefined`, `{{var}}`), lorem ipsum, copy about the wrong business, a hero image that doesn't match the business, unreadable overlapping text, a hero so crowded/duplicated the main message is lost.
- **MEDIUM** — noticeable on a careful read: a fact repeated 2–3× in one screenful, verbatim duplicated paragraph, restating list, orphaned fragment, misaligned stars/icons, truncation in a secondary area, naming drift.
- **LOW** — polish: heading-case drift, minor spacing incoherence, "Learn more" overuse, format drift.

When unsure between two severities, pick the lower one — an inflated report costs you credibility on the findings that matter.
