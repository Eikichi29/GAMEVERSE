# Contributing to GAMESVERSE

Thanks for considering a contribution!

## Before opening an issue
- Search existing issues to avoid duplicates.
- Include your Windows version, GAMESVERSE version, and clear reproduction steps.
- Never attach commercial game ROMs, BIOS files, copyrighted artwork, passwords, or personal data.

## Pull requests
1. Fork the repository and create a focused branch.
2. Keep changes small and explain the user-visible impact.
3. Run `python -m py_compile main.py`.
4. Validate the catalogue with `python -m json.tool catalogue.json`.
5. Describe manual tests and known limitations.

## Catalogue contributions
Catalogue entries are metadata only. Do not commit game images, ROMs, BIOS files,
firmware, or copyrighted assets unless you have documented permission to redistribute them.
Include a source/reference for factual metadata where practical.

## Code style
- Prefer clear names and small functions.
- Preserve compatibility with Python 3.12 and the supported PySide6 range.
- Do not add telemetry or network behavior without documenting it and obtaining user consent.
