# Profile image assets

Only publication-ready derived assets are stored here. The supplied PNG source images remain outside the repository.

## Files

- `prom3thex-banner.webp` — 1600 × 450 WebP, used by all three profile READMEs. Derived from `ChatGPT Image 12. Aug. 2026, 03_50_30 (2).png`, the same source as the avatar candidate, using a tighter avatar-aligned crop, horizontal portrait mirroring so the subject faces the open left side, restrained clarity and tonal grading, a blurred extension of the supplied background, feathered source boundaries, and minimal geometric accents.
- `prom3thex-avatar-square.webp` — 640 × 640 WebP, prepared for manual GitHub avatar upload. Derived from `ChatGPT Image 12. Aug. 2026, 03_50_30 (2).png` by square cropping, resizing, and restrained tonal grading.

The dense poster source `ChatGPT Image 12. Aug. 2026, 03_56_34.png` was used only as an art-direction reference and is not published here.

Both WebP files are saved as fresh RGB images without EXIF or embedded ICC profiles.

## Regeneration

The recipe requires Python 3 and Pillow. From the repository root, place the two private source files somewhere outside the repository and pass their paths explicitly:

```text
python tools/build_assets.py banner-source.png avatar-source.png
```

The script writes the two stable filenames above into `assets/` by default. Use `--output-dir` to render review copies elsewhere.
Use `--only banner` to rebuild the banner without writing the avatar file.
