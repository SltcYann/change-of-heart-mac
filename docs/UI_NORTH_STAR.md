# UI NORTH STAR — Executable Design Spec for 1:1 P5R Fidelity

**Created:** 2026-08-24 · **Status:** ACTIVE NORTH STAR
**Ground truth:** 146 official P5R UI screens (Game UI Database) — pixel-sampled, in `design/reference/`
**Contact sheets:** `design/reference/contact_sheets/sheet_01..08.png` (categorized views)
**Supersedes:** ad-hoc UI styling decisions; complements `docs/superpowers/specs/2026-08-19-authentic-p5r-ui-design.md` (Stage Director vision)

> **How to use this doc:** any UI change MUST cite a reference screenshot from
> `design/reference/` and a rule from this spec. "Make it look like P5R" is not
> a task; "active nav = cyan banner per 12558.jpg main menu" is.

---

## 1. The Palette (pixel-sampled from official screens — DO NOT GUESS)

### Core (every screen)
| Token | Hex | Sampled from | Role |
|---|---|---|---|
| `--p5-black` | `#000000` | dominant across all 146 screens | Canvas |
| `--p5-white` | `#FDFDFD` | menu text, banners | Text, lists, positive states |
| `--p5-red` | `#FD1700` | flat UI red (brighter than photo-sampled `#E31500`) | Brand, environment, danger |
| `--p5-red-deep` | `#C41001` | red shadow/dark variant | Red gradients/shadows |
| `--p5-cyan` | `#00C4FE` | main-menu "NEW GAME" selection banner | **Selection / active state** |
| `--p5-blue-deep` | `#005AFE` | offset shadow behind cyan banners | Cyan's shadow partner |
| Grey scale | `#D2D2D2` `#B6B6B6` `#989898` `#3A3A3A` `#1D1D1D` | supporting text/dividers | Muted hierarchy |

### Per-context accents (the game themes LOCATIONS, not features)
| Token | Hex | In-game context | Our stage |
|---|---|---|---|
| `--acc-lime` | `#CBE337` | Iwai's military shop | **Inventory / Item Studio** |
| `--acc-blue` | `#0086E9` | Takemi clinic, Velvet Room tones | **Velvet Room / Compendium** |
| `--acc-gold` | `#FED023` | battle rewards, rank stars | **Confidants, God-Tier, rewards** |
| `--acc-green` | `#5ADE00` | rare positive accent | sparingly (success toasts) |

### BANNED (measured: zero occurrences in official UI)
- ❌ Smooth multi-color gradients (the rainbow bar sin)
- ❌ Emoji as icons
- ❌ Dashboard green `#22c55e` / admin-panel styling
- ❌ Rounded-corner pill buttons (P5R is parallelograms + clipped corners)
- ❌ Hex IDs / engineering terms in user-facing text

## 2. The Design System Laws (from 146 screens)

1. **White does the work.** Lists, banners, values = white on black. Color is punctuation, not paint.
2. **Cyan = you are here.** The selected/active element gets the cyan parallelogram + `#005AFE` offset shadow (main menu: 12558.jpg).
3. **Red = the world.** Environment panels, brand moments, danger. Never the selection color.
4. **Every stage owns an accent** (law of location theming: shop=lime, clinic=blue, rewards=gold). Stage headers/tabs tint with their accent; base stays black/white.
5. **Parallelograms only.** All interactive geometry is skewed (`skew(-12deg)`) or hard-clipped (`clip-path` polygon corners). Zero border-radius on primary controls.
6. **Hard offset shadows, one direction.** `box-shadow: Npx Npx 0 <color>` — never soft blurs.
7. **Ransom-note typography for command words.** Headers mix 2-3 display fonts per word (Bebas/Oswald/Permanent Marker), white or yellow on black banners, always with the red slash bar.
8. **Body text is quiet.** Regular weight, grey-white (`#D2D2D2`), sentence case, no shadow.
9. **Lists are white panels on black** (item screen 63559.jpg, compendium register 228140.jpg).
10. **Diagonal composition.** Panels, dividers and transitions use shard/slash geometry, never straight symmetric grids.

## 3. Reference Inventory (categorized)

| Category | Files (in `design/reference/`) | Key layout lessons |
|---|---|---|
| Title / main menu | 12558, 63559, 77734 | cyan selection banner; white idle text; black bg |
| Save/Load slots | 95615 | white/red diagonal shards, slot list = our save selector |
| Daily HUD / calendar | 26388, 88967 | black HUD, white text, red accents |
| Party / status | 27809, 76684, 34920, 4313, 69687, 79589 | white stat text on black shards, red halftone character art, TOTAL EXP numerals |
| Config (light theme!) | 19207 | white bg + black text exists for system screens |
| Battle commands | 96158, 96120, 5233, 56008 | black shard banners, kinetic red typography |
| Shop (Iwai) | 89783, 10620, 26113, 33616, 26713 | **lime theme**, BUY/SELL/CUSTOMIZE pills, ¥ ledger |
| Clinic (Takemi) | 26070 | **blue theme** |
| Rewards | 1097, 45565, 55736, 84879 | **gold stars on night-sky**, EXP/Money/Item rows |
| Map | 67148, 33758 | red map, white node labels |
| Compendium register | 228140 | black list, red selected banner, white text |
| Velvet Room | 41845, 62484 | deep blue tones |

## 4. Current-State Gap Analysis (post R1/R1.9, 2026-08-24)

Done: sampled palette, cyan selection nav, white chips/progress, SVG nav icons, no hex in cards, horizontal star meters, type hierarchy.

| Gap | Priority | Reference |
|---|---|---|
| Emoji still in section headlines/buttons/topbar | HIGH | replace w/ SVG set (nav icons prove the pattern) |
| Stage accents not themed (all red) | HIGH | law #4 — Inventory=lime, Velvet/Compendium=blue, Confidants=gold |
| Geometry: inputs/search rounded rects | MED | law #5 — skew or clip everything |
| Two stacked search boxes | MED | consolidate (law: ≤5 controls before content) |
| Background collage muddy | MED | use real extracted collage art or clean flat + halftone |
| Ransom-note header typography | MED | law #7 — mixed-font command words |
| Battle-style kinetic transitions | LOW (Phase 4) | Stage Director spec |
| Official fonts/textures | LOW (blocked on DDS crypto) | see §6 |

## 5. Phase Roadmap (each phase = 1 session, screenshot-verified)

- **P2 — Accent theming + SVG completion.** Stage accent tokens wired (law 4); all remaining emoji → SVG; consolidate searches. *Accept: 10 captures show per-stage accents; zero emoji in DOM.*
- **P3 — Geometry pass.** All inputs/buttons parallelogram or clipped; kill border-radius on primary controls; single-direction offset shadows only. *Accept: zero rounded primary controls in captures.*
- **P4 — Asset unlock (research gate).** Find P5R DDS decryption (Amicitia wiki / Persona Merger / community tools — likely documented, not novel RE). Extract: fonts, UI icon sheets, halftone textures, collage backgrounds. *Accept: one real game texture renders in-app.*
- **P5 — Stage Director.** Per 2026-08-19 spec: 5 environments, slash transitions, kinetic headers. *Accept: capture script drives stage switch with transition.*
- **P6 — Motion + sound.** Elastic hover (existing `--ease-p5-snap`), transition audio snaps. *Accept: manual review.*

## 6. Blocked / Future RE

**DDS decryption — RESEARCHED 2026-08-24, WALL CONFIRMED (see research/RESEARCH.md §6):**
- Files = [0x800 prefix][CRILAYLA @0x800][trailing raw header]; `header_off` is file-coordinate; compressed stream itself is encrypted (first 1024 bytes from 0x20 — matches our `p5r_xor` footprint, but application detail differs; CRI's own CpkMaker.dll AccessViolates too).
- **No public solution exists** (ZenHax t=17557 archived unsolved; modding community uses loose-file loaders and never needed it).
- Remaining path = novel RE of p5r.exe read path (out of autonomous scope) OR texture-dump the running game (RenderDoc/SpecialK — user homework, zero decryption needed).
- Until then: icons/textures = hand-built SVGs in sampled style; fonts = free lookalikes (already wired).

## 7. Workflow Law (why this doc exists)

Every UI session: (1) pick a gap from §4/§5, (2) cite the reference screenshot,
(3) implement, (4) `python tools/capture_ui_state.py`, (5) compare captures vs
reference, (6) commit with before/after. No freeform "make it look better."
