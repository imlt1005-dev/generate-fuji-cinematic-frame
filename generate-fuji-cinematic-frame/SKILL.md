---
name: generate-fuji-cinematic-frame
description: Generate or assemble Fuji-film-inspired cinematic stills, vertical movie-frame collages, contact sheets, and bilingual Chinese-English subtitle images from a story, theme, existing photos, or reference images. Use when the user asks for 富士风格、胶片感、电影感、电影截图、电影拼图、三联画、组图、分镜、旅行照片排版、中英双语字幕、电影台词、日系纪实影像, or wants ordinary photos turned into a restrained cinematic sequence rather than a commercial poster.
---

# Generate Fuji Cinematic Frame

Create a restrained photographic sequence in which story, framing, light, and ordinary detail establish the cinematic feeling before color grading does. Treat “Fuji” as a family of film-inspired color directions, not as one universal filter and not as an exact proprietary simulation.

## Default Deliverable

Unless the user asks for another format, produce:

1. a clean vertical 9:16 triptych on black;
2. three consistent 1.9:1 cinematic frames for travel photos, with 2.25:1 available as a wider option;
3. one independent Chinese-over-English subtitle pair per panel by default, added deterministically after image generation;
4. the final prompt or editing specification;
5. a short recipe naming layout, color direction, light, framing, subtitle placement, and narrative arc.

When creating user-facing files, name them `YYYY-MM-DD_任务主题_已完成.ext`; use `正在继续` for drafts and `未完成` only when blocked.

## Route the Request

Choose one route before acting:

- **Existing-photo collage:** Preserve the supplied photos. Crop, grade, arrange, and subtitle them with `scripts/compose_cinematic_collage.py`. Do not regenerate faces or places unless the user asks.
- **Reference-guided generation:** Inspect every reference with `view_image`, label it as style/composition/mood reference, and use built-in image generation to create new clean frames. Do not reproduce gallery UI, counters, close icons, watermarks, or accidental screenshot chrome.
- **Story-to-stills generation:** Convert the story into 2–6 separate shot prompts, generate one frame per prompt, then compose them. Keep character identity, wardrobe, location, weather, time, and color direction consistent across prompts.
- **Single-frame mode:** Generate or grade one cinematic still; add subtitles only when requested.
- **Prompt-only mode:** Stop before generation only when the user explicitly asks for prompts only.

## Read the Relevant References

- Read `references/style-spec.md` for every generation or color-grading request.
- Read `references/layouts-and-subtitles.md` for every collage or subtitle request.
- Inspect `references/reference-triptych-imlt1005-dev.jpg` with `view_image` when choosing travel-triptych geometry, crop rhythm, or subtitle placement. Treat it as a visual target, not as a source image to copy into new outputs.
- Read `references/prompt-compiler.md` before writing image-generation prompts.
- Read `references/quality-gates.md` before delivery.

## Workflow

### 1. Parse the Brief

Identify:

- subject, place, time, weather, action, and emotional temperature;
- whether inputs are edit targets or visual references;
- desired frame count and platform;
- exact Chinese and English text, if supplied;
- invariants such as identity, clothing, architecture, or geography.

Ask only when missing information would materially change the result. Otherwise use these defaults:

- 1080 × 1920 vertical canvas;
- black background;
- three horizontally cropped frames;
- 1.9:1 frame ratio for travel triptychs; use 2.25:1 only when the user wants a wider, more letterboxed look;
- 12 px gutters and 16 px side margins;
- `soft-eterna` grade at restrained strength;
- fine grain, no fake scratches or light leaks;
- one concise Chinese-over-English subtitle pair per panel when subtitles are requested.

### 2. Build a Shot Sequence

Give each frame a distinct narrative job. Default triptych:

1. **Context:** establish place, season, or social environment.
2. **Human or detail:** reveal an action, object, texture, or relationship.
3. **Afterimage:** return to environment or end with an unresolved visual echo.

Vary shot size while preserving continuity. Prefer ordinary gestures, off-camera gaze, partial occlusion, layered depth, and meaningful empty space. Do not make every frame a centered portrait.

### 3. Choose One Color Direction

Select one direction from `references/style-spec.md` and keep it consistent across a sequence:

- `soft-eterna`: gentle contrast and saturation; quiet narrative default;
- `documentary-chrome`: restrained color and stronger documentary separation;
- `warm-negative`: warmer highlights and denser nostalgic contrast;
- `vivid-summer`: clean blue sky and vegetation without HDR excess;
- `monochrome-humanist`: nuanced black-and-white tonal range.

Describe the actual color behavior in prompts. A profile label alone is insufficient.

### 4. Generate or Prepare Clean Frames

For generated frames, use the built-in image-generation capability. Generate each distinct shot separately rather than asking one model image to contain a finished multi-panel layout. This improves continuity control and keeps text out of the generated pixels.

For edits, preserve invariants aggressively. If the user provides local images, inspect them first. Apply only the requested crop, grading, and composition changes unless the user authorizes generative alteration.

Never ask the image model to render long bilingual subtitles. Generate clean imagery, then add exact text locally.

### 5. Compose and Subtitle

Use `codex_app__load_workspace_dependencies` to locate the bundled workspace Python runtime when available. Otherwise use a Python environment with Pillow and NumPy:

```bash
WORKSPACE_PY="/path/returned/by/load_workspace_dependencies/python/bin/python3"
"$WORKSPACE_PY" scripts/compose_cinematic_collage.py \
  --images frame-1.png frame-2.png frame-3.png \
  --output final.png \
  --layout triptych-vertical \
  --grade soft-eterna \
  --subtitles-json subtitles.json
```

If no bundled runtime is available, set `WORKSPACE_PY="$(command -v python3)"` after confirming that Pillow and NumPy are installed. Run `--help` for all options.

Subtitle JSON example:

```json
[
  {
    "panel": 2,
    "zh": "生活就像一部电影。",
    "en": "Life is like a movie.",
    "placement": "overlay"
  },
  {
    "panel": 3,
    "zh": "有些答案留在风里。",
    "en": "Some answers remain in the wind.",
    "placement": "band-after"
  }
]
```

Preserve user-supplied wording verbatim. If only Chinese is supplied, translate for cinematic meaning rather than word order, then show the translation to the user in the final response. If text is invented, keep it short, specific, and non-clichéd.

### 6. Inspect and Revise

Render and inspect the final collage. Check it at full size and thumbnail size. Revise once when there is an obvious violation such as inconsistent characters, illegible subtitles, crushed shadows, excessive orange-teal grading, malformed anatomy, repeated compositions, or accidental UI elements.

Run the deterministic validator:

```bash
"$WORKSPACE_PY" scripts/validate_collage.py final.png --expected-aspect 0.5625
```

The validator complements visual inspection; it does not replace it.

## Hard Avoids

Avoid by default:

- gallery close icons, page counters, app chrome, watermarks, or screenshot residue;
- commercial-poster hierarchy, logos, CTA, or advertising copy;
- indiscriminate orange-teal grading, cyberpunk neon, HDR halos, plastic skin, or extreme clarity;
- fake film borders, sprocket holes, timestamps, dust, scratches, and light leaks unless requested;
- subtitles generated inside the source image;
- every subject looking at camera or every frame using the same shot size;
- heavy blur that removes environmental storytelling;
- claiming an exact Fujifilm film simulation match when only a visual approximation is being made.

## Output Format

Return:

```markdown
**成片**

![Cinematic collage](absolute-path)

**字幕**

- 中文：...
- English: ...

**配方**

- Layout: ...
- Color direction: ...
- Shot sequence: ...
- Subtitle placement: ...

**最终生成 Prompt**

```text
...
```
```

For multiple generated frames, list each shot prompt separately. Link only user-facing deliverables in the designated output folder.
