# Skill cards

Every skill folder has a `README.md` that GitHub shows when you open the folder. It opens with
a trading card, front and back. The images live here, one folder per skill, so they never ship
inside an installed skill.

**Art you supply is a PNG or JPEG picture.** Every `.svg` here is produced by the build script;
nobody needs to make an SVG by hand. Prompts for the pictures: `prompts.json` (for an API script)
and `PROMPTS.md` (to copy by hand).

```
docs/media/<skill>/
  card.json        card text, stats, colours          (you edit)
  front-art.webp   a hand-made front, if there is one  (you add)
  art.svg          art for a generated front           (you edit, 420 x 468 canvas)
  *.src.svg        example output, charts              (you edit)
  front.svg        the finished front                  (generated)
  back.svg         the finished back                   (generated)
  <name>.svg       each *.src.svg, fonts embedded      (generated)
  *.gif            recordings                          (added as-is)
```

Rebuild after any change:

```bash
pip install fonttools brotli          # once
python3 scripts/build_skill_cards.py  # all skills, or name some: ... slop-scan hot-seat
```

## The front

- **Hand-made:** a 1024 x 1536 card in the collection style (cream border, `SKILL COLLECTION`
  header, name in the bottom band). Leave the top-right corner empty: the build stamps the card
  number there. Convert to WebP (`ffmpeg -i card.png -c:v libwebp -quality 80 front-art.webp`)
  and point `front` in card.json at it.
- **Generated:** without `front`, the build draws one in the same frame around `art.svg`.

## card.json

The card number comes from the skill's position in the main README index.

| Field | What it is |
|---|---|
| `title` | Skill name as it should read on the card |
| `category` | `discovery`, `code`, `ux`, `docs`, `content` or `meta`; sets default colours |
| `set` | Small label under `SKILL COLLECTION`, e.g. `Visual audit` |
| `type` | The back's type line, e.g. `Audit · rendered site` |
| `tagline` | One line for a generated front |
| `ability` | The back's main text, the TL;DR |
| `flavor` | A real line from the skill's `SKILL.md`, never invented |
| `stats` | Four `[label, value]` pairs; facts from the SKILL.md only |
| `palette` | Optional `panel`, `accent`, `tint` colours, matched to a hand-made front |
| `front` | Optional: `art` (file), `number_box` `[x, y, w, h]` for the stamp, `patch` (colour under it), `number_color`, `number_size` |

## Rules

- **Public repo.** Example output uses fictional businesses and data, and says so.
- **Formats are real.** An example follows the skill's own template or reference, not a guess.
- **Fonts.** Montserrat (cards), Big Shoulders Display and Atkinson Hyperlegible (example
  images), all SIL OFL; licences in `_fonts/`.
