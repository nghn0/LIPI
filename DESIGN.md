---
name: Lipi
description: An everyday bilingual writing studio for local Hindi inference.
colors:
  forest: "#183e31"
  primary: "#254e38"
  primary-hover: "#183b29"
  text: "#263b34"
  canvas: "#f6f8f6"
  surface: "#ffffff"
  output: "#fafcf8"
  border: "#e2e8e2"
  navigation-active: "#315644"
  caution-bg: "#fff6ee"
  caution-text: "#795236"
typography:
  display:
    fontFamily: '"Manrope Variable", sans-serif'
    fontSize: "44px"
    fontWeight: 620
    lineHeight: 1.18
    letterSpacing: "-1.8px"
  body:
    fontFamily: '"Manrope Variable", sans-serif'
    fontSize: "17px"
    lineHeight: 1.95
    letterSpacing: "-0.3px"
  hindi:
    fontFamily: '"Noto Sans Devanagari", sans-serif'
    fontSize: "20px"
    lineHeight: 2.05
  label:
    fontFamily: '"Manrope Variable", sans-serif'
    fontSize: "11px"
    fontWeight: 650
rounded:
  control: "7px"
  secondary: "6px"
  studio: "12px"
  draft: "9px"
  chip: "20px"
spacing:
  panel-inline: "23px"
  desktop-inline: "44px"
  compact-inline: "24px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#f4f8ed"
    rounded: "{rounded.control}"
    padding: "13px 17px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "#5d7252"
    rounded: "{rounded.secondary}"
    padding: "10px 13px"
  studio:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.studio}"
---

# Design System: Lipi

## Overview

**Creative North Star: "The Bilingual Writing Studio"**

An everyday bilingual writing studio. The user's words are the focal point. A forest-green navigation rail, white writing surface and pale sage output distinguish working areas without decorative imagery. A type specimen pairs a Roman a with Devanagari अ.

The bright canvas serves laptop use in classroom light. Quiet borders and restrained depth keep writing, inference state and inspectable results legible.

**Key Characteristics:**
- Forest navigation anchors a bright workspace.
- Roman and Devanagari text have dedicated self-hosted fonts.
- Working surfaces distinguish input, output and generated revision.

## Colors

### Primary
Forest anchors navigation. Primary green identifies deliberate conversion and evaluation actions; its darker hover communicates readiness. Active navigation uses a lighter forest surface.

### Neutral
Canvas surrounds white writing and card surfaces. Pale sage marks the Hindi output work area. Green-tinted ink, muted supporting text and fine borders preserve continuity across the studio, drafts, model details and evaluation.

### Secondary
Warm ochre is reserved for review, missing setup and error status; it is not a decorative accent.

## Typography

Manrope Variable serves the interface and Roman text; Noto Sans Devanagari serves Hindi. Both are self-hosted through bundled Fontsource imports. Hindi weights 400 and 500 are loaded.

The main desktop heading uses the display role; secondary page headings use 38px. The studio heading scales to 50px above 1500px and 39px/35px at narrower breakpoints. Working Roman input remains 17px after the final readability overrides; Hindi output uses 20px, reducing to 18px at the 800px breakpoint. Supporting copy is typically 10–12px, with compact mobile status labels at 8–10px. Source and target labels use modest tracking. The oversized Roman a and Devanagari अ are decorative type, not text-entry sizes.

## Layout

The desktop shell has a sticky full-height 224px navigation rail and a flexible content column. Main content is capped at 1450px with 44px horizontal padding. The editor uses equal input/output columns; the output has a left divider. Toolbars and action bars frame the writing area. Drafts and model details use two-column grids; evaluation uses horizontally scrollable tables.

At 1100px the rail narrows to 195px and content padding to 30px. At 800px it becomes a 72px icon rail with accessible navigation names and 24px content padding; drafts and model details stack. At 540px navigation becomes a top strip and the editor stacks input above output. The large-screen breakpoint is 1500px. Content wraps within writing and result areas.

## Elevation & Depth

Tonal layering and thin borders provide most separation. The studio has a nearly imperceptible resting shadow (`0 4px 20px #35513c05`). Alternative-word popovers lift above text (`0 9px 28px #28452322`); toast feedback uses `0 7px 24px #2f4b3422`. The input panel receives an inset focus outline rather than lifting.

## Shapes

Controls use gently curved 6–7px corners. The studio uses 12px corners, drafts 9px and generated results 8px. Example chips and model pills use 20px rounding. One-pixel green-tinted borders delineate controls and containers. Circular status dots and the avatar remain small supporting shapes.

## Components

### Buttons
Primary actions are compact green filled controls with pale text, 7px corners and a darker hover. Secondary and save actions use bordered white or transparent surfaces with 6px corners. Icon actions use small unobtrusive hit areas. Buttons shift down 1px while pressed; disabled actions reduce opacity and use a disabled cursor. Keyboard focus has a visible 3px outline with a 4px offset.

### Inputs / Fields
The borderless Roman writing area lives inside the white panel with a panel-wide inset focus treatment. Hindi editing uses the output type role. Selects are white bordered controls. The preserve-English switch visibly changes track and thumb state and exposes a keyboard focus ring.

### Navigation
Forest sidebar links use muted pale text; the active item has a lighter forest fill. Hover and active states remain visible as the navigation collapses to icons and then a top strip.

### Chips / Status
Example chips have a thin border, pale background and pill corners; hover adds sage fill and a stronger border. Model and result badges describe readiness, match or review with text as well as color.

### Cards / Containers
The studio groups toolbar, two writing panels and action bar. Drafts, generated revisions and model details use white bordered containers. Evaluation aligns compact metrics above the test bench and detailed result table.

### Word Alternatives and Results
Dotted-underlined Hindi words are keyboard-focusable alternative selectors. A white anchored popover lists options, with sage hover/selected treatment. Conversion runs explicitly; input changes invalidate prior output. Original output and generated revision stay visually separate. Draft save feedback appears in a toast. Skeletons indicate active inference; button transitions run for 0.16s, switches for 0.2s. Reduced-motion removes animations and transitions.

## Do's and Don'ts

### Do:
- Do preserve the white input and pale sage output distinction.
- Do use Noto Sans Devanagari for Hindi working text.
- Do keep inference status, generated revisions and evaluation results explicit.
- Do retain keyboard focus and reduced-motion behavior.

### Don't:
- Don't use decorative imagery in place of the bilingual type specimen.
- Don't silently replace original output with a generated revision.
- Don't present unavailable models or unrun evaluation as successful results.
