# Quality Gates

## Source and Intent

- Are all input images labeled as edit targets or references?
- Are user-provided faces, locations, architecture, and wording preserved when required?
- Have accidental screenshot controls and counters been excluded?

## Sequence

- Does every panel have a distinct narrative role?
- Are shot sizes and subject placement varied?
- Is identity, wardrobe, time, weather, and location consistent?
- Does the final panel leave a visual afterimage rather than repeat the first?

## Color and Texture

- Is one color direction applied consistently?
- Are skin tones, sky, water, and vegetation believable?
- Are highlights protected and shadows textured?
- Is grain fine and restrained?
- Is the image free of generic orange-teal, HDR, neon, light-leak, and fake-vintage effects?

## Layout

- Is the master canvas the requested ratio, defaulting to 9:16?
- Are travel frames near 1.9:1 unless another ratio was requested?
- Are gutters and margins consistent?
- Is the stack visually centered with sufficient black breathing room?

## Subtitles

- Is Chinese above English?
- When the user requested a fully captioned triptych, does every panel have its own subtitle pair?
- Is all supplied text reproduced verbatim?
- Is the English natural and semantically faithful?
- Are subtitles legible at phone size?
- Do they avoid faces, hands, and key objects?
- Are long lines wrapped without awkward breaks?

## Technical

- Is the image RGB or RGBA and saved as PNG/JPEG as requested?
- Did `validate_collage.py` pass the aspect and dimension checks?
- Was the final image visually inspected after composition?
- Does the filename follow the date-topic-status archive rule?
