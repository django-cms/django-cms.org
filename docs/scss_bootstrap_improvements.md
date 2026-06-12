# SCSS / Bootstrap 5 — Customization Review & Improvement Plan

This document reviews how the theme in `backend/static/scss/` customizes its
vendored copy of **Bootstrap 5.3** (`scss/theme/`) and identifies where the
customization fights Bootstrap instead of using it.

The short version of the finding confirms the original hunch:

> The "design tokens" layer (`_variables.scss`, `_bootstrap_overrides.scss`) is
> done correctly — variables are set *before* Bootstrap compiles. But almost
> every component partial imported *after* `theme/bootstrap` (`_buttons.scss`,
> `_table.scss`, `_links.scss`, `_class_overrides.scss`, `_forms.scss`, …)
> re-declares finished rules and leans on `!important` to win the cascade,
> rather than feeding values into the variables and CSS custom properties that
> Bootstrap already exposes for exactly this purpose.

`!important` is the symptom. There are **~150 `!important` declarations** across
the custom partials (47 in `_table.scss` alone). Each one is a place where a
later, higher-specificity rule is overriding an earlier Bootstrap rule that
could instead have been *configured* not to emit the unwanted value at all.

---

## How the build is wired (what's already right)

`main.scss` imports in this order:

```scss
@import "./typography";
@import "./bootstrap_overrides";   // <-- variables & map merges
@import "./theme/bootstrap";       // <-- Bootstrap compiles HERE
@import "./navbar";                // \
@import "./cards";                 //  >  component partials
@import "./buttons";               //  /   (run AFTER bootstrap)
...
```

`_bootstrap_overrides.scss` is the model to follow. It:

- imports `theme/functions` first,
- sets brand variables (`$primary`, `$secondary`, …) **before** `theme/variables`,
- merges `$spacers`, `$theme-colors`, and the `-text/-bg-subtle/-border-subtle`
  color maps so custom colors get the **full** Bootstrap treatment
  (`alert-*`, `btn-*`, `bg-*-subtle`, `text-bg-*`, etc.).

This is the correct extension pattern. **The problem is that the partials after
`theme/bootstrap` largely ignore that this layer exists** and re-style
components from scratch.

Two things make the override approach especially wasteful here:

1. **This is Bootstrap 5.3.** Every component is driven by **CSS custom
   properties** (`--bs-btn-bg`, `--bs-table-bg`, `--bs-accordion-*`,
   `--bs-breadcrumb-*`, …). You can re-theme a component instance by setting a
   couple of `--bs-*` variables on a selector — no `!important`, no
   reimplementation.
2. The Sass variables that *generate* those defaults (`$btn-*`, `$table-*`,
   `$accordion-*`, `$input-*`, `$link-*`) are all present and `!default` in
   `theme/_variables.scss`, so they can be set from `_bootstrap_overrides.scss`
   for free.

---

## Findings by component

### 1. Buttons — `_buttons.scss` (reimplements `.btn` from scratch)

`.btn`, `.btn-sm`, `.btn-lg` redefine `border-radius`, `padding`, `font-size`,
`line-height`, `letter-spacing`, `font-weight` as literal values. `.btn-primary`,
`.btn-secondary`, `.btn-outline-secondary` re-declare every state
(`:hover/:focus/:active/.active`) by hand.

Bootstrap already generates all of this from variables and the
`button-variant()` / `button-outline-variant()` mixins (the vendored
`theme/_buttons.scss` calls them at lines 134–159).

**Better:** push the shape into variables (in `_bootstrap_overrides.scss`):

```scss
$btn-border-radius:        40px;
$btn-border-radius-sm:     40px;
$btn-border-radius-lg:     40px;
$btn-padding-y:            16px;
$btn-padding-x:            24px;
$btn-font-size:            14px;
$btn-font-weight:          500;
$btn-line-height:          1.15;
```

`letter-spacing`, `text-transform`, and the flex/gap layout aren't variables, so
they remain a small base rule — but a *one-time* one, not per-variant:

```scss
.btn {
  letter-spacing: 0.15em;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  --bs-btn-hover-bg: transparent;   // instead of hand-writing :hover blocks
}
```

For the *colors*, define the variants through the map / mixin instead of literal
selectors. The hover-to-transparent inversion is the same shape for every
variant, so it can be one mixin call per color rather than three duplicated
state blocks each. This removes the `.btn-primary {…}` / `.btn-secondary {…}` /
`.btn-outline-secondary {…}` duplication entirely.

**Net:** ~140 lines → ~30, and `.btn-mid-grey`, `.btn-gold`, etc. (the custom
colors) get correct buttons automatically instead of being undefined.

---

### 2. Tables — `_table.scss` (the worst offender: 47 × `!important`)

The whole file restyles bare `table` and `.table` with literal borders, radii,
striping, and per-`:nth-child` background colors, every line `!important`.

Bootstrap 5.3 tables are entirely CSS-variable driven
(`--bs-table-bg`, `--bs-table-color`, `--bs-table-border-color`,
`--bs-table-striped-bg`, `--bs-table-striped-color`, …) and there are Sass
variables for all of it (`$table-*` at `theme/_variables.scss:733+`).

Problems this causes:

- **Styling bare `table`** (not just `.table`) means every table in
  rich-text/CMS content is forced into the comparison-card look, which is why
  `.table-comparison` then needs *another* 47-on-top overrides to undo it.
- The `!important` walls mean utilities like `.table-borderless`,
  `.table-sm`, `.table-dark`, responsive variants, etc. **cannot** be used —
  they're outgunned.

**Better:**

```scss
// design tokens (compile-time)
$table-border-color:   $mid-grey;
$table-striped-bg:     $light;
$table-cell-padding-y: 1rem;
$table-cell-padding-x: 1rem;

// per-instance theming (runtime CSS vars, no !important)
.table {
  --bs-table-bg: #{$white};
  --bs-table-striped-bg: #{$light};
  --bs-table-color: #{$body-color};
  border-radius: $border-radius;          // the rounded shell
  border-collapse: separate;
  overflow: hidden;                         // clips children to the radius
}
```

The rounded-corner shell (radius on the outer table + clipping) is the one piece
Bootstrap genuinely doesn't provide, so it stays — but it becomes ~10 lines
applied once, not 115 lines of per-cell corner math. Crucially, scope it to
`.table` (and a `.table-bordered-rounded` modifier for the fancy variant) so
plain content tables are left alone, which deletes the entire `.table-comparison`
counter-override block.

---

### 3. Links — `_links.scss` (global `a {}` + `!important` on every variant)

`a { … }` restyles **every anchor on the site**, then `.nav-link`,
`.link-light`, `.link-primary`, `.link-white` re-fight it with `!important`. The
`background-color: $primary` hover is a genuine custom behavior, but the rest
duplicates Bootstrap's link system.

Bootstrap exposes `$link-color`, `$link-decoration`, `$link-hover-color`
(`theme/_variables.scss:455`) and generates `.link-*` helpers from
`$utilities-links` / the theme color map. `.link-light`/`.link-primary` already
exist — overriding them with `!important` defeats their purpose.

**Better:**

```scss
$link-color:        $secondary;
$link-decoration:   none;
$link-hover-color:  $secondary;
```

Then a *single* small rule for the brand hover-highlight, applied through a
class rather than the bare `a` element so it doesn't leak into buttons, cards,
nav, etc.:

```scss
.link-highlight:hover { background-color: $primary; }
```

Let Bootstrap keep generating `.link-primary`/`.link-light`/etc. from the color
map (you already merged the maps), instead of redefining each one.

---

### 4. Headings & text — `_class_overrides.scss` (every line `!important`)

`h1–h4`, `.small`, `blockquote` set `font-weight`/`line-height`/`letter-spacing`
with `!important`. These map directly to existing Sass variables:

| Hand-written rule | Bootstrap variable |
|---|---|
| `h1 { font-weight: 400 }` | `$headings-font-weight: 400;` |
| `h1 { line-height: 100% }` | `$headings-line-height: 1;` |
| `.small { font-size: .75rem }` | `$small-font-size: .75rem;` |
| `blockquote { font-size: 1.5rem }` | `$blockquote-font-size: 1.5rem;` |

Per-level heading weights that genuinely differ (h2/h4 = 500 vs h1/h3 = 400) are
the one case a small explicit rule is justified — but **without `!important`**,
because once `$headings-font-weight` isn't being fought, normal specificity wins.

> Note: `font-style: light` (in `_class_overrides.scss:42` and the `@font-face`
> blocks) is **invalid CSS** — `font-style` takes `normal | italic | oblique`.
> The light weight is selected by `font-weight: 250`, so `font-style: light`
> should simply be removed.

---

### 5. Accordion — `_accordion.scss` (already close; finish the job)

This file is **the second-best example in the codebase** — it correctly sets
`--bs-accordion-*` custom properties (lines 8–13) and uses `var(--bs-primary)`
etc. Good. Two cleanups:

- Lines 2–9 set `--bs-accordion-border-radius: 0` *and* `border-radius: 0px`
  *and* `border: none` — the CSS var alone is enough; drop the literal duplicates.
- The five `.accordion-header-{primary,secondary,white,muted,default}` blocks are
  identical except for one color. That's a Sass `@each` loop over a small map —
  ~80 lines → ~15 — and `muted`/`default` can pull from `--bs-secondary-color` /
  `--bs-emphasis-color` instead of hardcoded `#6c757d` / `#000`.

---

### 6. Forms — `_forms.scss` (mostly legitimate; a few token leaks)

The custom checkbox/radio/switch SVGs and the 24px sizing are real bespoke
design — fine to keep as rules. But:

- `.form-control:focus { border-color: $primary }` duplicates
  `$input-focus-border-color` / `$input-focus-box-shadow`.
- The focus-ring `box-shadow` pattern (`0 0 0 .25rem rgba($x, .25)`) is repeated
  ~6 times across forms/buttons; that's `$focus-ring-*` /
  `$input-btn-focus-box-shadow`, set once.
- Label sizing (`.form-label`) → `$form-label-font-size`/`-font-weight`.

---

### 7. Breadcrumbs — `_breadcrumbs.scss`

`--bs-breadcrumb-item-padding-x: 0` (line 2) is the right instinct. The rest
(uppercase, letter-spacing, separator weight) is custom and fine, but the
`!important` on every property isn't needed once you're not also being
overridden by a global `a {}` rule — fixing finding #3 lets these drop
`!important` too. The separator character itself is `$breadcrumb-divider`.

---

## Cross-cutting issues

1. **`!important` as the default tool.** ~150 occurrences. Almost all exist only
   to beat a Bootstrap rule that should have been configured off. They're
   contagious: each one forces the *next* override to also be `!important`
   (see how `.table-comparison` must `!important` its way out of `_table.scss`).

2. **Styling bare elements (`a`, `table`, `h1`) globally** instead of Bootstrap
   classes. This is what makes the `!important` necessary and breaks utility
   classes. Prefer configuring the variable (affects the element *and* the
   class consistently) or scoping to a class.

3. **Duplicated state/color blocks** that should be `@each` loops over a map:
   button variants, accordion header colors, link variants, the `.rounded-6`
   family in `main.scss` (which duplicates what extending `$utilities`
   "rounded" with a `6: .625rem` entry would generate, including responsive
   variants).

4. **Repeated literal magic numbers** that are already tokens:
   `box-shadow: 0 0 10px 2px rgba(0,0,0,.10)` appears in `_table`, `_cards`,
   `main`, and `_variables` (as `$box-shadow-sm`). `border-radius: 20px` is
   `$border-radius` (set to `1.25rem` = 20px). Reference the token.

5. **`$custom-colors` map in `_variables.scss` is dead** — `_bootstrap_overrides`
   merges colors into `$theme-colors` directly and never uses `$custom-colors`.
   Remove it or wire it in, but don't keep both.

---

## Priority / effort

| # | Area | Impact | Effort | `!important` removed |
|---|------|--------|--------|----------------------|
| 1 | Tables → `$table-*` vars + `--bs-table-*`, scope to `.table` | **High** | Med | ~47 |
| 2 | Headings/text → `$headings-*`, `$small-font-size`, … | High | Low | ~32 |
| 3 | Links → `$link-*` + scoped highlight class | High | Low | ~9 |
| 4 | Buttons → `$btn-*` vars + variant mixin/`@each` | High | Med | 0 (dedupe ~110 lines) |
| 5 | Breadcrumbs → drop `!important` after #3 | Med | Low | ~13 |
| 6 | Accordion → `@each` the 5 color variants | Med | Low | 0 |
| 7 | Forms → focus-ring / label / focus-border tokens | Low | Low | 0 |
| 8 | `main.scss` `.rounded-6*` → extend `$utilities` | Low | Low | ~9 |
| 9 | Remove dead `$custom-colors`, fix `font-style: light` | Low | Low | — |

**Suggested order:** do #2 and #3 first (highest ratio, they unlock dropping
`!important` in breadcrumbs/links and are low-risk), then #1 (largest single
win), then #4, then the loops/cleanups.

## Guiding rule going forward

> Before writing a rule in a partial that runs after `theme/bootstrap`, ask:
> **(a)** Is there a `$component-*` Sass variable? → set it in
> `_bootstrap_overrides.scss`.
> **(b)** No variable, but is it a one-instance tweak? → set the `--bs-*` custom
> property on the selector (no `!important`).
> **(c)** Only if neither applies, write a plain rule — scoped to a class, and
> still without `!important`.
