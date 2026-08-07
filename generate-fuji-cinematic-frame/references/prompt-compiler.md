# Cinematic Prompt Compiler

Write one prompt per frame. Keep shared continuity fields identical and vary only the shot-specific fields.

## Shared Fields

1. **Story fact:** place, time, weather, character identity, wardrobe, and ongoing action.
2. **Photographic behavior:** candid documentary still, natural texture, plausible optics.
3. **Light:** source, direction, softness, exposure, and reflections.
4. **Color behavior:** describe saturation, contrast, highlights, shadows, skin, blue, and green.
5. **Continuity:** repeat character, clothing, location, season, weather, and grade.
6. **Avoids:** no text, watermark, UI, commercial pose, HDR, orange-teal excess, plastic skin, malformed anatomy.

## Shot-Specific Fields

- narrative role: context, action, detail, reaction, or afterimage;
- shot size and camera position;
- subject placement and gaze;
- foreground/background layers;
- one decisive environmental detail.

## Prompt Shape

Use this compact order:

```text
Use case: photorealistic-natural
Asset type: cinematic still for a vertical film-diary collage
Scene/backdrop: ...
Subject and action: ...
Narrative role: ...
Composition/framing: ...
Lighting/mood: ...
Film-inspired color behavior: ...
Continuity constraints: ...
Avoid: any text, subtitles, logo, watermark, UI, gallery counter, close icon, commercial pose, HDR halos, exaggerated orange-teal grading, plastic skin, malformed anatomy
```

Do not ask the image model to create the final collage or bilingual typography. Generate clean frames and compose afterward.

## Triptych Example Logic

- Frame 1: wide context; show the place and weather.
- Frame 2: medium human action or meaningful object.
- Frame 3: environmental afterimage with the person absent or small.

The three prompts must not merely change camera zoom. Each must reveal a different part of the same visual sentence.
