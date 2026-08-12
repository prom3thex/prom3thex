"""Build publication-ready PROM3THEX profile images from supplied portraits."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


BANNER_SIZE = (1600, 450)
AVATAR_SIZE = (640, 640)


def _rgb(image: Image.Image) -> Image.Image:
    """Return a metadata-free RGB copy with a consistent orientation."""
    return ImageOps.exif_transpose(image).convert("RGB")


def _cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)


def build_banner(source_path: Path, output_path: Path) -> None:
    with Image.open(source_path) as opened:
        source = _rgb(opened)

    width, height = source.size

    # The backdrop reuses only the source photograph, with enough blur and
    # darkening to create clean negative space without synthesizing scenery.
    background_crop = source.crop((0, 0, width, round(height * 0.55)))
    background = _cover(background_crop, BANNER_SIZE)
    background = background.filter(ImageFilter.GaussianBlur(radius=24))
    background = ImageEnhance.Color(background).enhance(0.82)
    background = ImageEnhance.Contrast(background).enhance(1.08)
    background = ImageEnhance.Brightness(background).enhance(0.46)

    canvas = background.convert("RGBA")

    # Keep the human likeness untouched apart from crop, resize, and restrained
    # tonal grading. The crop is normalized so the recipe scales with the input.
    portrait_crop = source.crop(
        (
            round(width * 0.12),
            round(height * 0.045),
            round(width * 0.96),
            round(height * 0.51),
        )
    )
    portrait_crop = ImageEnhance.Color(portrait_crop).enhance(0.94)
    portrait_crop = ImageEnhance.Contrast(portrait_crop).enhance(1.04)
    portrait = ImageOps.contain(
        portrait_crop,
        (540, BANNER_SIZE[1]),
        method=Image.Resampling.LANCZOS,
    ).convert("RGBA")

    # Feather only the rectangular source boundary; no subject segmentation or
    # generative fill is used.
    mask = Image.new("L", portrait.size, 0)
    inset_x = max(12, round(portrait.width * 0.06))
    inset_y = max(8, round(portrait.height * 0.025))
    ImageDraw.Draw(mask).rounded_rectangle(
        (inset_x, inset_y, portrait.width - inset_x, portrait.height - inset_y),
        radius=28,
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(radius=22))
    portrait.putalpha(mask)
    portrait_x = BANNER_SIZE[0] - portrait.width - 78
    portrait_y = (BANNER_SIZE[1] - portrait.height) // 2
    canvas.alpha_composite(portrait, (portrait_x, portrait_y))

    # A near-black left-to-right veil preserves readable negative space and the
    # restrained emerald/gold identity of the supplied references.
    veil = Image.new("RGBA", BANNER_SIZE, (0, 0, 0, 0))
    veil_pixels = veil.load()
    for x in range(BANNER_SIZE[0]):
        position = x / (BANNER_SIZE[0] - 1)
        alpha = round(188 * max(0.0, 1.0 - position / 0.78))
        for y in range(BANNER_SIZE[1]):
            veil_pixels[x, y] = (2, 6, 4, alpha)
    canvas = Image.alpha_composite(canvas, veil)

    # Minimal architectural accents: no pseudo-telemetry or baked-in microcopy.
    accents = Image.new("RGBA", BANNER_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(accents)
    gold = (192, 140, 75, 150)
    green = (87, 219, 125, 95)
    draw.line([(46, 54), (520, 54), (548, 82)], fill=gold, width=2)
    draw.line([(46, 396), (760, 396), (788, 368)], fill=gold, width=2)
    draw.line([(46, 72), (46, 160)], fill=green, width=1)
    draw.ellipse((41, 49, 51, 59), fill=(221, 182, 116, 185))
    draw.ellipse((41, 391, 51, 401), fill=(87, 219, 125, 150))
    canvas = Image.alpha_composite(canvas, accents)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(
        output_path,
        format="WEBP",
        quality=88,
        method=6,
        exif=b"",
        icc_profile=None,
    )


def build_avatar(source_path: Path, output_path: Path) -> None:
    with Image.open(source_path) as opened:
        source = _rgb(opened)

    width, height = source.size
    crop = source.crop(
        (
            round(width * 0.16),
            round(height * 0.045),
            round(width * 0.87),
            round(height * 0.445),
        )
    )
    avatar = _cover(crop, AVATAR_SIZE)
    avatar = ImageEnhance.Color(avatar).enhance(0.96)
    avatar = ImageEnhance.Contrast(avatar).enhance(1.03)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    avatar.save(
        output_path,
        format="WEBP",
        quality=92,
        method=6,
        exif=b"",
        icc_profile=None,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("banner_source", type=Path, help="Portrait used for the wide banner")
    parser.add_argument("avatar_source", type=Path, help="Portrait used for the square avatar")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets",
        help="Destination directory (default: repository assets directory)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_banner(args.banner_source, args.output_dir / "prom3thex-banner.webp")
    build_avatar(args.avatar_source, args.output_dir / "prom3thex-avatar-square.webp")


if __name__ == "__main__":
    main()
