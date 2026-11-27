# Skill cards

Every skill folder has a `README.md` that GitHub shows when you open the folder. The images
it uses live here, one folder per skill, so they never ship inside an installed skill.

```
docs/media/<skill>/
  card.json      card text and stats            (you edit)
  art.svg        the art-window illustration     (you edit, 420 x 468 canvas)
  *.src.svg      example output, charts          (you edit)
  card.svg       the finished card               (generated)
  <name>.svg     each *.src.svg, fonts embedded  (generated)
  *.gif          recordings                      (added as-is)
```

Rebuild after any change:

```bash
pip install fonttools brotli          # once
python3 scripts/build_skill_cards.py  # all skills, or name some: ... code-audit hot-seat
```

## card.json

| Field | What it is |
|---|---|
| `title` | Skill name as it should read on the card |
| `no`, `of` | Card number: the skill's position in the README index, and the total |
| `category` | `discovery`, `code`, `ux`, `docs`, `content` or `meta`; sets the frame colour |
| `type` | The type line, e.g. `Audit · whole repository` |
| `ability` | The TL;DR, max four lines on the card |
| `flavor` | A real line from the skill's `SKILL.md`, never invented |
| `stats` | Up to four `[label, value]` pairs; facts from the SKILL.md only |

## Swapping in your own art

Draw on a 420 x 468 canvas, save as `art.svg`, rebuild. Keep text out of it or use the card
fonts by name (`Display900`, `Display700`, `Body400`, `Body700`, `BodyItalic`) so the build
embeds them. Anything else falls back to a system font on GitHub.

## Rules

- **Public repo.** Example output uses fictional businesses and data, and says so on the image.
- **Formats are real.** An example follows the skill's own template or reference, not a guess.
- **Fonts.** Big Shoulders Display and Atkinson Hyperlegible, both SIL OFL (licences in `_fonts/`).
