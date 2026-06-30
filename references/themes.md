# Themes Reference

Color token sets for every generated page. All themes share **one variable
contract** (Section 1), so any page styled against those variables can switch
themes by swapping only the `:root` / `[data-theme="dark"]` blocks — exactly what
`assets/md2html.js` does, and what the quiz / mock / cheat-sheet templates do.

Each theme below gives a **light block** (`:root, [data-theme="light"]`) and a
**dark block** (`[data-theme="dark"]`). Light is the default; the toggle and
anti-flash script (see [html-conventions.md](html-conventions.md)) flip
`data-theme` on `<html>` and persist to the shared key `esb-theme`.

---

## 1. The token contract

Every theme defines the same variables so components stay theme-agnostic.

| Token | Role |
|---|---|
| `--bg` | Page background |
| `--bg-soft` | Secondary page background / wells |
| `--surface` | Card / panel surface |
| `--surface-2` | Raised surface, table header, header bar |
| `--ink` | Primary text |
| `--ink-soft` | Secondary text |
| `--ink-faint` | Muted text / captions |
| `--line` | Borders, dividers |
| `--brand` | Primary accent (links, active state, headings) |
| `--brand-2` | Secondary accent |
| `--brand-soft` | Accent tint background |
| `--ok` | Success / correct |
| `--ok-bg` | Success tint background |
| `--warn` | Warning / incorrect |
| `--warn-bg` | Warning tint background |
| `--tip-bg` | Tip / callout background |
| `--code-bg` | Code block background |
| `--code-ink` | Code block text |
| `--chip` | Pill / tag background |
| `--shadow` | Elevation shadow (set `none` for flat themes) |

Shape / type tokens live in `:root` and are usually theme-independent, but a
theme may override them (Metro forces sharp corners; Material 3 rounds more):

```css
:root{
  --font-sans:  "Microsoft YaHei","PingFang SC","Segoe UI",system-ui,sans-serif;
  --font-serif: "Noto Serif SC","Source Han Serif SC","Songti SC",Georgia,serif;
  --font-mono:  "Cascadia Code","JetBrains Mono","Consolas",monospace;
  --radius: 14px; --radius-sm: 9px; --maxw: 1080px; --speed: .25s;
}
```

> [!tip] Keep contrast AA in both blocks
> After editing any palette, recheck `--ink` on `--bg` and accent-on-`--surface`
> for ≥ 4.5:1 (body) and ≥ 3:1 (large text). See html-conventions §6.

---

## 2. 素雅温暖 / warm  (default)

Paper-cream + warm-brown ink + terracotta/amber accents (米黄 / 暖棕 / 赤陶 /
琥珀). Low-glare, eye-friendly for late-night revision. This is the built-in
default of `md2html.js` and `assets/theme-tokens.css`.

```css
:root,
[data-theme="light"]{
  --bg:#f6efe3; --bg-soft:#efe5d4; --surface:#fffaf2; --surface-2:#f3ebdc;
  --ink:#4a3b2c; --ink-soft:#6f5e4c; --ink-faint:#9b8a76; --line:#e3d6c0;
  --brand:#c0612f; --brand-2:#b9892f; --brand-soft:#f0d9c4;
  --ok:#5b7c52; --ok-bg:#dde7d2; --warn:#b0552c; --warn-bg:#f3d9cb;
  --tip-bg:#f5ead2; --code-bg:#2f2722; --code-ink:#f3e7d6; --chip:#ecd9c2;
  --shadow:0 6px 24px rgba(90,64,40,.10),0 2px 6px rgba(90,64,40,.06);
}
[data-theme="dark"]{
  --bg:#211b15; --bg-soft:#1b1611; --surface:#2b2219; --surface-2:#332820;
  --ink:#f0e3d0; --ink-soft:#d4c3ac; --ink-faint:#a7937a; --line:#4a3c2d;
  --brand:#e8915a; --brand-2:#e6b85c; --brand-soft:#3c2c1d;
  --ok:#9cc081; --ok-bg:#2f3a26; --warn:#e8a06a; --warn-bg:#3e2a1d;
  --tip-bg:#3a2e1d; --code-bg:#15110d; --code-ink:#f0e0c8; --chip:#3a2d20;
  --shadow:0 8px 28px rgba(0,0,0,.45),0 2px 8px rgba(0,0,0,.3);
}
```

---

## 3. dark-tech

Cool slate + blue/cyan accents, IDE-like. The light block is a clean blue-gray;
the dark block is the headline look. Built into `md2html.js` as `--theme dark-tech`.

```css
:root,
[data-theme="light"]{
  --bg:#eef2f7; --bg-soft:#e4e9f0; --surface:#ffffff; --surface-2:#e4e9f0;
  --ink:#1b2330; --ink-soft:#45526a; --ink-faint:#7c8aa0; --line:#d2dae6;
  --brand:#2563eb; --brand-2:#0891b2; --brand-soft:#dbe7fb;
  --ok:#0f766e; --ok-bg:#d6f0ec; --warn:#b45309; --warn-bg:#fdecd2;
  --tip-bg:#e2ecfb; --code-bg:#0f172a; --code-ink:#e2e8f0; --chip:#dde6f2;
  --shadow:0 6px 22px rgba(30,41,59,.10),0 2px 6px rgba(30,41,59,.06);
}
[data-theme="dark"]{
  --bg:#0b1120; --bg-soft:#111a2e; --surface:#111a2e; --surface-2:#1b2742;
  --ink:#e6edf6; --ink-soft:#a9b6cc; --ink-faint:#6b7a94; --line:#26344f;
  --brand:#5b9dff; --brand-2:#22d3ee; --brand-soft:#13233f;
  --ok:#34d399; --ok-bg:#0f2e2a; --warn:#fbbf24; --warn-bg:#3a2a12;
  --tip-bg:#13233f; --code-bg:#060b16; --code-ink:#d6e2f2; --chip:#1d2b46;
  --shadow:0 10px 30px rgba(0,0,0,.55),0 2px 10px rgba(0,0,0,.4);
}
```

---

## 4. Material 3 (tonal)

Google Material Design 3 tonal palette, default violet seed (`#6750A4`). M3
favors larger radii and soft tonal elevation, so override the shape tokens too.

```css
/* M3 prefers rounder corners + soft tonal elevation */
:root{ --radius:16px; --radius-sm:12px; }

:root,
[data-theme="light"]{
  --bg:#fef7ff; --bg-soft:#f7f2fa; --surface:#ffffff; --surface-2:#e7e0ec;
  --ink:#1d1b20; --ink-soft:#49454f; --ink-faint:#79747e; --line:#cac4d0;
  --brand:#6750a4; --brand-2:#625b71; --brand-soft:#eaddff;   /* primary / secondary / primary-container */
  --ok:#386a20; --ok-bg:#d7f0c8; --warn:#b3261e; --warn-bg:#f9dedc; /* error / error-container */
  --tip-bg:#eaddff; --code-bg:#1d1b20; --code-ink:#f5eff7; --chip:#e8def8; /* secondary-container */
  --shadow:0 1px 3px rgba(0,0,0,.15),0 4px 8px rgba(0,0,0,.08);
}
[data-theme="dark"]{
  --bg:#141218; --bg-soft:#1d1b20; --surface:#211f26; --surface-2:#49454f;
  --ink:#e6e0e9; --ink-soft:#cac4d0; --ink-faint:#938f99; --line:#49454f;
  --brand:#d0bcff; --brand-2:#ccc2dc; --brand-soft:#4f378b;
  --ok:#9dd67d; --ok-bg:#28381b; --warn:#f2b8b5; --warn-bg:#8c1d18;
  --tip-bg:#4f378b; --code-bg:#0f0d13; --code-ink:#e6e0e9; --chip:#4a4458;
  --shadow:0 1px 3px rgba(0,0,0,.4),0 6px 12px rgba(0,0,0,.3);
}
```

To reskin to another M3 seed, regenerate a tonal palette (Material Theme Builder)
and remap: `primary→--brand`, `secondary→--brand-2`, `primary-container→--brand-soft`,
`surface→--bg`, `surface-variant→--surface-2`, `on-surface→--ink`, `outline→--line`,
`error/error-container→--warn/--warn-bg`.

---

## 5. Windows 10 Metro

Flat **Metro** design: accent `#0078D7`, Segoe UI, **sharp** corners, **no
shadows**, solid tiles. Override shape + font; set `--shadow: none`.

```css
/* Metro is flat and sharp — square tiles, Segoe UI, no elevation */
:root{
  --radius:0; --radius-sm:0;
  --font-sans:"Segoe UI","Microsoft YaHei",system-ui,sans-serif;
  --font-serif:"Segoe UI","Microsoft YaHei",sans-serif;  /* Metro avoids serifs */
}

:root,
[data-theme="light"]{
  --bg:#f2f2f2; --bg-soft:#e6e6e6; --surface:#ffffff; --surface-2:#e6e6e6;
  --ink:#1f1f1f; --ink-soft:#444444; --ink-faint:#767676; --line:#d1d1d1;
  --brand:#0078d7; --brand-2:#0063b1; --brand-soft:#cce4f7;
  --ok:#107c10; --ok-bg:#dff6dd; --warn:#d83b01; --warn-bg:#fdeee3;
  --tip-bg:#fff4ce; --code-bg:#1e1e1e; --code-ink:#f2f2f2; --chip:#e1e1e1;
  --shadow:none;
}
[data-theme="dark"]{
  --bg:#1f1f1f; --bg-soft:#171717; --surface:#2b2b2b; --surface-2:#333333;
  --ink:#ffffff; --ink-soft:#d6d6d6; --ink-faint:#a0a0a0; --line:#3f3f3f;
  --brand:#4894fe; --brand-2:#60a5e8; --brand-soft:#15324d;
  --ok:#6ccb5f; --ok-bg:#1b3a16; --warn:#ff8c00; --warn-bg:#3a2410;
  --tip-bg:#3a3320; --code-bg:#121212; --code-ink:#f2f2f2; --chip:#3a3a3a;
  --shadow:none;
}
```

**Metro accent palette** (swap `--brand` for a different tile color):
`#0078D7` blue · `#E81123` red · `#107C10` green · `#FF8C00` orange ·
`#5C2D91` purple · `#008272` teal · `#FFB900` amber.

Pair Metro with square tiles: `border-radius: var(--radius)` (= 0) and
`box-shadow: var(--shadow)` (= none) everywhere; use a solid `--brand` fill with
white text for "live tiles".

---

## 6. Custom accent from one hex

When a student gives a single brand color, derive the rest instead of hand-picking.

### 6.1 Runtime, pure-CSS (`color-mix`) — works under `file://`

Set one hex; mix toward white/black/ink for the related tints. `color-mix()` is
plain CSS (no fetch), so it is `file://`-safe in current browsers.

```css
:root,
[data-theme="light"]{
  --brand:#7c3aed;                                             /* the one hex */
  --brand-2:   color-mix(in srgb, var(--brand) 78%, #000);     /* deeper sibling */
  --brand-soft:color-mix(in srgb, var(--brand) 14%, #fff);     /* tint background */
  --line:      color-mix(in srgb, var(--brand) 22%, #ddd);
  --tip-bg:    color-mix(in srgb, var(--brand) 10%, #fff);
  /* keep neutral --bg/--surface/--ink from your base palette */
}
[data-theme="dark"]{
  --brand:#a78bfa;                                             /* lift accent for dark */
  --brand-2:   color-mix(in srgb, var(--brand) 80%, #fff);
  --brand-soft:color-mix(in srgb, var(--brand) 24%, #000);
  --tip-bg:    color-mix(in srgb, var(--brand) 16%, #000);
}
```

Choose **text-on-accent** by luminance, not by eye — for a filled accent button:

```css
/* fallback for engines without the contrast() color function */
.btn-accent{ background:var(--brand); color:#fff; }
@supports (color: contrast-color(white)) {
  .btn-accent{ color: contrast-color(var(--brand)); }
}
```

### 6.2 Precompute a full ramp (max compatibility)

To avoid relying on `color-mix`, generate hex values once at build time and paste
them in. Minimal luminance + mix helper (Node, no dependencies):

```js
function mix(hex, withHex, t){            // t = weight of `withHex` (0..1)
  const a=hex.match(/\w\w/g).map(h=>parseInt(h,16));
  const b=withHex.match(/\w\w/g).map(h=>parseInt(h,16));
  const c=a.map((v,i)=>Math.round(v*(1-t)+b[i]*t));
  return '#'+c.map(v=>v.toString(16).padStart(2,'0')).join('');
}
function onAccent(hex){                    // white or near-black for text
  const [r,g,b]=hex.match(/\w\w/g).map(h=>parseInt(h,16)/255)
    .map(v=>v<=.03928?v/12.92:((v+.055)/1.055)**2.4);
  const L=.2126*r+.7152*g+.0722*b;         // relative luminance
  return L>.4 ? '#1a1a1a' : '#ffffff';
}
const brand='#7c3aed';
const tokens={
  '--brand':       brand,
  '--brand-2':     mix(brand,'#000000',0.22),
  '--brand-soft':  mix(brand,'#ffffff',0.86),  // light tint
  '--on-brand':    onAccent(brand),
};
console.log(tokens);
```

Rules of thumb: `--brand-2` ≈ brand mixed 18–25% toward black; `--brand-soft` ≈
brand mixed ~86% toward white (light) or ~76% toward black (dark); pick on-accent
text by luminance threshold (~0.4). Keep neutrals (`--bg`, `--surface`, `--ink`)
from the warm or dark-tech base and only swap the accent family.

---

## 7. Wiring a theme into `md2html.js`

`md2html.js` ships `warm` (default) and `dark-tech` in its `THEMES` map and
selects via `--theme NAME`. To add Material 3, Metro, or a custom set, paste its
light/dark blocks (without the selectors) into that map:

```js
const THEMES = {
  warm:        { light: "…", dark: "…" },
  'dark-tech': { light: "…", dark: "…" },
  m3:          { light: "--bg:#fef7ff; …", dark: "--bg:#141218; …" },
  metro:       { light: "--bg:#f2f2f2; …", dark: "--bg:#1f1f1f; …" },
};
```

The template emits them as `:root,[data-theme="light"]{…}` and
`[data-theme="dark"]{…}`. For Metro/M3 also fold their shape/font overrides
(`--radius`, `--font-sans`) into the same string, or into the template's base
`:root`.
