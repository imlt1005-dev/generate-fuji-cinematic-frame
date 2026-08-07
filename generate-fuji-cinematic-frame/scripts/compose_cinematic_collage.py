#!/usr/bin/env python3
"""Compose cinematic photo collages with optional grading and bilingual subtitles."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "This script requires Pillow and NumPy. Use the Codex workspace Python runtime "
        "or install them with: python -m pip install pillow numpy"
    ) from exc


ZH_FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

EN_FONT_CANDIDATES = [
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def parse_size(value: str) -> tuple[int, int]:
    try:
        width, height = (int(part) for part in value.lower().split("x", 1))
    except Exception as exc:
        raise argparse.ArgumentTypeError("Size must be WIDTHxHEIGHT, e.g. 1080x1920") from exc
    if width < 320 or height < 320:
        raise argparse.ArgumentTypeError("Both dimensions must be at least 320 px")
    return width, height


def choose_font(explicit: str | None, candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    paths = [explicit] if explicit else []
    paths.extend(candidates)
    for candidate in paths:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default(size=size)


def fit_crop(image: Image.Image, size: tuple[int, int], anchor: tuple[float, float]) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    target_w, target_h = size
    source_ratio = image.width / image.height
    target_ratio = target_w / target_h
    ax = min(1.0, max(0.0, anchor[0]))
    ay = min(1.0, max(0.0, anchor[1]))
    if source_ratio > target_ratio:
        crop_w = round(image.height * target_ratio)
        left = round((image.width - crop_w) * ax)
        box = (left, 0, left + crop_w, image.height)
    else:
        crop_h = round(image.width / target_ratio)
        top = round((image.height - crop_h) * ay)
        box = (0, top, image.width, top + crop_h)
    return image.crop(box).resize(size, Image.Resampling.LANCZOS)


def lift_blacks(image: Image.Image, amount: float) -> Image.Image:
    if amount <= 0:
        return image
    arr = np.asarray(image).astype(np.float32) / 255.0
    arr = amount + (1.0 - amount) * arr
    return Image.fromarray(np.clip(arr * 255.0, 0, 255).astype(np.uint8), "RGB")


def tone_matrix(image: Image.Image, matrix: np.ndarray, offset: np.ndarray) -> Image.Image:
    arr = np.asarray(image).astype(np.float32) / 255.0
    arr = arr @ matrix.T + offset
    return Image.fromarray(np.clip(arr * 255.0, 0, 255).astype(np.uint8), "RGB")


def apply_grade(image: Image.Image, preset: str, strength: float) -> Image.Image:
    strength = min(1.0, max(0.0, strength))
    if preset == "none" or strength == 0:
        return image

    base = image.convert("RGB")
    graded = base
    if preset == "soft-eterna":
        graded = ImageEnhance.Color(graded).enhance(0.84)
        graded = ImageEnhance.Contrast(graded).enhance(0.93)
        graded = lift_blacks(graded, 0.025)
        matrix = np.array([[1.015, 0.005, 0.0], [0.0, 1.0, 0.0], [0.0, 0.01, 0.985]])
        graded = tone_matrix(graded, matrix, np.array([0.002, 0.0, 0.003]))
    elif preset == "documentary-chrome":
        graded = ImageEnhance.Color(graded).enhance(0.78)
        graded = ImageEnhance.Contrast(graded).enhance(1.06)
        graded = lift_blacks(graded, 0.012)
        matrix = np.array([[1.025, 0.0, 0.0], [0.0, 0.99, 0.0], [0.0, 0.015, 0.965]])
        graded = tone_matrix(graded, matrix, np.array([0.002, 0.0, 0.0]))
    elif preset == "warm-negative":
        graded = ImageEnhance.Color(graded).enhance(0.94)
        graded = ImageEnhance.Contrast(graded).enhance(1.11)
        graded = lift_blacks(graded, 0.01)
        matrix = np.array([[1.04, 0.01, 0.0], [0.0, 0.99, 0.0], [0.0, 0.0, 0.96]])
        graded = tone_matrix(graded, matrix, np.array([0.004, 0.0, 0.008]))
    elif preset == "vivid-summer":
        graded = ImageEnhance.Color(graded).enhance(1.08)
        graded = ImageEnhance.Contrast(graded).enhance(1.04)
        matrix = np.array([[1.01, 0.0, 0.0], [0.0, 1.015, 0.0], [0.0, 0.005, 1.025]])
        graded = tone_matrix(graded, matrix, np.array([0.0, 0.0, 0.0]))
    elif preset == "monochrome-humanist":
        gray = ImageOps.grayscale(graded)
        gray = ImageEnhance.Contrast(gray).enhance(1.06)
        graded = Image.merge("RGB", (gray, gray, gray))
        graded = lift_blacks(graded, 0.012)
    else:
        raise ValueError(f"Unknown grade preset: {preset}")
    return Image.blend(base, graded, strength)


def add_grain(image: Image.Image, amount: float, seed: int) -> Image.Image:
    if amount <= 0:
        return image
    rng = np.random.default_rng(seed)
    arr = np.asarray(image).astype(np.float32)
    noise = rng.normal(0.0, amount, (image.height, image.width, 1))
    luminance = arr.mean(axis=2, keepdims=True) / 255.0
    mask = np.clip(1.15 - luminance, 0.3, 1.0)
    arr = np.clip(arr + noise * mask, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def load_subtitles(path: str | None) -> list[dict[str, Any]]:
    if not path:
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Subtitle JSON must contain a list")
    for entry in data:
        if not isinstance(entry, dict) or "panel" not in entry:
            raise ValueError("Each subtitle must be an object with a 1-based panel number")
        entry.setdefault("zh", "")
        entry.setdefault("en", "")
        entry.setdefault("placement", "overlay")
    return data


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int, chinese: bool) -> list[str]:
    if not text:
        return []
    units = list(text) if chinese else text.split()
    lines: list[str] = []
    current = ""
    for unit in units:
        candidate = current + unit if chinese else (f"{current} {unit}".strip())
        bbox = draw.textbbox((0, 0), candidate, font=font, stroke_width=1)
        if current and bbox[2] - bbox[0] > max_width:
            lines.append(current)
            current = unit
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines[:2]


def draw_bilingual(
    canvas: Image.Image,
    rect: tuple[int, int, int, int],
    zh: str,
    en: str,
    font_zh_path: str | None,
    font_en_path: str | None,
    scale: float,
) -> None:
    draw = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = rect
    width = x1 - x0
    zh_size = max(18, round(31 * scale))
    en_size = max(12, round(19 * scale))
    font_zh = choose_font(font_zh_path, ZH_FONT_CANDIDATES, zh_size)
    font_en = choose_font(font_en_path, EN_FONT_CANDIDATES, en_size)
    max_width = round(width * 0.86)
    zh_lines = wrap_text(draw, zh, font_zh, max_width, chinese=True)
    en_lines = wrap_text(draw, en, font_en, max_width, chinese=False)
    line_gap = max(3, round(4 * scale))
    blocks: list[tuple[str, ImageFont.ImageFont, int]] = []
    for line in zh_lines:
        blocks.append((line, font_zh, max(1, round(2 * scale))))
    for line in en_lines:
        blocks.append((line, font_en, max(1, round(1.5 * scale))))
    heights = [draw.textbbox((0, 0), text, font=font, stroke_width=stroke)[3] for text, font, stroke in blocks]
    total_h = sum(heights) + line_gap * max(0, len(blocks) - 1)
    cursor_y = y0 + max(0, (y1 - y0 - total_h) // 2)
    for (text, font, stroke), height in zip(blocks, heights):
        draw.text(
            ((x0 + x1) / 2, cursor_y),
            text,
            font=font,
            anchor="ma",
            fill=(245, 245, 240),
            stroke_width=stroke,
            stroke_fill=(15, 15, 15),
        )
        cursor_y += height + line_gap


def vertical_layout(
    count: int,
    canvas_size: tuple[int, int],
    margin: int,
    gap: int,
    frame_aspect: float,
    subtitles: list[dict[str, Any]],
    band_height: int,
) -> tuple[list[tuple[int, int, int, int]], dict[int, tuple[int, int, int, int]]]:
    canvas_w, canvas_h = canvas_size
    frame_w = canvas_w - 2 * margin
    band_panels = {int(s["panel"]) for s in subtitles if s.get("placement") == "band-after"}
    total_band = band_height * len(band_panels)
    natural_h = round(frame_w / frame_aspect)
    max_frame_h = max(80, (canvas_h - 2 * margin - gap * (count - 1) - total_band) // count)
    frame_h = min(natural_h, max_frame_h)
    total_h = frame_h * count + gap * (count - 1) + total_band
    y = max(margin, (canvas_h - total_h) // 2)
    rects: list[tuple[int, int, int, int]] = []
    bands: dict[int, tuple[int, int, int, int]] = {}
    for index in range(1, count + 1):
        rects.append((margin, y, margin + frame_w, y + frame_h))
        y += frame_h
        if index in band_panels:
            bands[index] = (margin, y, margin + frame_w, y + band_height)
            y += band_height
        if index < count:
            y += gap
    return rects, bands


def grid_layout(count: int, canvas_size: tuple[int, int], margin: int, gap: int) -> list[tuple[int, int, int, int]]:
    canvas_w, canvas_h = canvas_size
    cols = 2 if count <= 4 else 3
    rows = math.ceil(count / cols)
    cell_w = (canvas_w - 2 * margin - gap * (cols - 1)) // cols
    cell_h = round(cell_w / 1.5)
    total_h = rows * cell_h + gap * (rows - 1)
    start_y = max(margin, (canvas_h - total_h) // 2)
    rects = []
    for i in range(count):
        row, col = divmod(i, cols)
        x = margin + col * (cell_w + gap)
        y = start_y + row * (cell_h + gap)
        rects.append((x, y, x + cell_w, y + cell_h))
    return rects


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", nargs="+", required=True, help="Input images in narrative order")
    parser.add_argument("--output", required=True, help="Output PNG or JPEG path")
    parser.add_argument(
        "--layout",
        choices=["triptych-vertical", "diptych-vertical", "four-grid", "contact-sheet"],
        default="triptych-vertical",
    )
    parser.add_argument("--canvas", type=parse_size, default=(1080, 1920), help="WIDTHxHEIGHT")
    parser.add_argument("--frame-aspect", type=float, default=1.9)
    parser.add_argument("--margin", type=int, default=16)
    parser.add_argument("--gap", type=int, default=12)
    parser.add_argument("--background", default="#000000")
    parser.add_argument(
        "--grade",
        choices=["none", "soft-eterna", "documentary-chrome", "warm-negative", "vivid-summer", "monochrome-humanist"],
        default="soft-eterna",
    )
    parser.add_argument("--grade-strength", type=float, default=0.55)
    parser.add_argument("--grain", type=float, default=2.2, help="Fine luminance noise sigma; 0 disables")
    parser.add_argument("--seed", type=int, default=27)
    parser.add_argument("--anchors", help="Comma-separated crop anchors x:y, e.g. 0.5:0.4,0.7:0.5")
    parser.add_argument("--subtitles-json")
    parser.add_argument("--subtitle-band-height", type=int, default=108)
    parser.add_argument("--font-zh")
    parser.add_argument("--font-en")
    args = parser.parse_args()

    expected_counts = {
        "triptych-vertical": 3,
        "diptych-vertical": 2,
        "four-grid": 4,
    }
    if args.layout in expected_counts and len(args.images) != expected_counts[args.layout]:
        parser.error(f"{args.layout} requires exactly {expected_counts[args.layout]} images")
    if args.layout == "contact-sheet" and not 4 <= len(args.images) <= 9:
        parser.error("contact-sheet requires 4 to 9 images")
    if args.frame_aspect <= 0:
        parser.error("--frame-aspect must be positive")

    anchors = [(0.5, 0.5)] * len(args.images)
    if args.anchors:
        parsed = []
        for item in args.anchors.split(","):
            x, y = item.split(":", 1)
            parsed.append((float(x), float(y)))
        if len(parsed) not in (1, len(args.images)):
            parser.error("--anchors must contain one anchor or one per image")
        anchors = parsed * len(args.images) if len(parsed) == 1 else parsed

    subtitles = load_subtitles(args.subtitles_json)
    for entry in subtitles:
        panel = int(entry["panel"])
        if panel < 1 or panel > len(args.images):
            parser.error(f"Subtitle panel {panel} is outside the available image range")
        if entry.get("placement") not in ("overlay", "band-after", "none"):
            parser.error("Subtitle placement must be overlay, band-after, or none")

    canvas = Image.new("RGB", args.canvas, args.background)
    bands: dict[int, tuple[int, int, int, int]] = {}
    if args.layout in ("triptych-vertical", "diptych-vertical"):
        rects, bands = vertical_layout(
            len(args.images), args.canvas, args.margin, args.gap, args.frame_aspect, subtitles, args.subtitle_band_height
        )
    else:
        rects = grid_layout(len(args.images), args.canvas, args.margin, args.gap)

    for index, (path, anchor, rect) in enumerate(zip(args.images, anchors, rects), start=1):
        with Image.open(path) as source:
            size = (rect[2] - rect[0], rect[3] - rect[1])
            frame = fit_crop(source, size, anchor)
        frame = apply_grade(frame, args.grade, args.grade_strength)
        frame = add_grain(frame, args.grain, args.seed + index)
        canvas.paste(frame, (rect[0], rect[1]))

    scale = args.canvas[0] / 1080.0
    for entry in subtitles:
        panel = int(entry["panel"])
        placement = entry.get("placement", "overlay")
        if placement == "none":
            continue
        if placement == "band-after" and panel in bands:
            text_rect = bands[panel]
        else:
            x0, y0, x1, y1 = rects[panel - 1]
            overlay_h = max(round((y1 - y0) * 0.27), round(104 * scale))
            gradient = Image.new("L", (1, overlay_h), 0)
            gradient.putdata([round(150 * (i / max(1, overlay_h - 1)) ** 1.6) for i in range(overlay_h)])
            shade = Image.new("RGB", (x1 - x0, overlay_h), "black")
            canvas.paste(shade, (x0, y1 - overlay_h), gradient.resize((x1 - x0, overlay_h)))
            text_rect = (x0, y1 - overlay_h + round(8 * scale), x1, y1 - round(8 * scale))
        draw_bilingual(
            canvas,
            text_rect,
            str(entry.get("zh", "")),
            str(entry.get("en", "")),
            args.font_zh,
            args.font_en,
            scale,
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() in (".jpg", ".jpeg"):
        canvas.save(output, quality=94, subsampling=0)
    else:
        canvas.save(output)
    print(json.dumps({"output": str(output.resolve()), "size": list(canvas.size), "layout": args.layout}, ensure_ascii=False))


if __name__ == "__main__":
    main()
