# GAMESVERSE

**ONE APP. EVERY GENERATION.**

GAMESVERSE is an open-source Windows desktop frontend for organizing a personal
multi-console game library, browsing franchise metadata, tracking user-entered
license/purchase information, and launching emulators configured by the user.

> Status: early prototype. The repository is not yet a finished, production-ready
> commercial launcher. Emulator management, automatic updates, cloud saves,
> online accounts, and a hosted game store are not implemented.

## Features currently present
- PySide6 desktop interface with dark gaming theme.
- Multi-console catalogue and franchise metadata (catalogue entries do not include game files).
- Local library backed by SQLite.
- Add locally stored game files and associate them with a console/franchise.
- User-managed artwork and favorites.
- Manually associate an emulator executable with a console and launch imported games.
- Store/collections/licence pages as prototype UI.

## Download for Windows users
Open the repository's **Releases** page and download `GAMESVERSE-Setup-0.5.0.exe`
from the latest successful release. Run the installer; Python is not required on
the end user's PC.

The installer is produced by GitHub Actions when a maintainer pushes a version tag
such as `v0.5.0`. The workflow also attaches the portable `GAMESVERSE.exe`.

## Build locally on Windows
Requirements:
- Windows 10/11 64-bit
- Python 3.12
- Inno Setup 6

1. Install Python 3.12 and Inno Setup 6.
2. Extract/clone this repository.
3. Double-click `build_windows.bat`.
4. Find the installer in `installer-output/` and the portable executable in `dist/`.

## Publish on GitHub (maintainer)
1. Create a **public** repository named `GAMESVERSE` on GitHub.
2. Upload/push the contents of this folder to the repository root (not the enclosing ZIP folder).
3. In GitHub, open **Actions** and confirm workflows are enabled.
4. Push a version tag from a terminal in the repository:
   ```bash
   git tag v0.5.0
   git push origin v0.5.0
   ```
5. Open **Releases**. GitHub Actions builds the Windows installer and creates a release with both `.exe` files attached.

For subsequent versions, update `VERSION`, `GAMESVERSE.iss`, and the workflow's installer filename before tagging.

## Catalogue and intellectual property
The catalogue contains game titles and metadata only; it does not bundle ROMs, BIOS,
firmware, copyrighted cover art, or commercial game files. Users are responsible for
ensuring they have the rights to use any files they add. The GAMESVERSE code license
does not grant rights to third-party games, trademarks, logos, music, or artwork.

## Privacy
The prototype stores its library database and artwork locally under
`%APPDATA%\\GAMESVERSE`. It does not require an account or cloud service.

## Contributing
Read [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md),
and [SECURITY.md](SECURITY.md) before contributing.

## License
GAMESVERSE source code is licensed under GPL-3.0-or-later. See [LICENSE](LICENSE).
Third-party assets and intellectual property remain subject to their respective owners.
