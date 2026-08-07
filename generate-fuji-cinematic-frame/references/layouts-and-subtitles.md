# Layouts and Bilingual Subtitles

## Default Geometry

- Canvas: 1080 × 1920, vertical 9:16.
- Background: pure or near black.
- Side margin: 16 px.
- Frame aspect: 1.9:1 for the default travel triptych; optional 2.25:1 for a wider letterboxed treatment.
- Inter-frame gap: 12 px.
- Stack: vertically centered, leaving generous black space above and below.

These values are calibrated against `reference-triptych-imlt1005-dev.jpg`, in which three equal panels fill most of a tall black mobile canvas while retaining visible top and bottom breathing room.

## Layout Modes

### triptych-vertical

Use three equally wide frames. Default narrative roles: context, human/detail, afterimage. When subtitles are requested, give every panel its own concise Chinese-over-English pair unless the user asks for selective captions.

### diptych-vertical

Use two wide frames for contrast, before/after, near/far, or two points of view.

### four-grid

Use four equal cells for a denser sequence. Preserve a single location, person, or motif across the set.

### contact-sheet

Use up to nine small frames for travel diaries, observational studies, or editing-room selections. Do not add subtitles to every cell.

## Subtitle Hierarchy

- Chinese first, English second.
- Chinese size: approximately 28–34 px on a 1080 px canvas.
- English size: 55–70% of the Chinese size.
- Color: warm white or white.
- Add a restrained black stroke or shadow for legibility.
- Center by default; left-align only when negative space clearly supports it.
- Keep subtitles inside the title-safe area.
- Prefer one short Chinese line and one short English line.

## Placement

### overlay

Place both lines near the lower part of the selected frame. Use when the underlying area is visually calm. Add a subtle dark gradient or shadow only when needed.

### band-after

Insert a black band immediately after the selected panel and center both lines within it. Use when the image is busy, when dialogue should behave as an editorial pause, or when matching the reference style.

### none

Keep a clean frame. Not every panel needs text.

## Translation Rules

- Preserve exact supplied bilingual text.
- When translating Chinese, preserve cinematic intent and emotional temperature.
- Avoid literal word order when it sounds unnatural in English.
- Keep English concise; contractions are acceptable for dialogue.
- Do not add quotation marks or punctuation not present in the source without a reason.
- Avoid generic captions such as “Life is a journey” unless the user explicitly requests them.

## Continuity Rules

- Maintain consistent typeface, stroke, size, and vertical rhythm.
- Do not place subtitles over faces, hands, or the narrative object.
- Do not add page counters, playback controls, timecodes, or close icons.
- If a generated frame contains unintended text, regenerate or remove it before compositing.
