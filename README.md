# venc_gui

FFmpeg command builder for VideoToolbox.

## Run from Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python venc_gui.py
```

## Build a standalone macOS app

The easiest option is **PyInstaller**, which creates a native `.app` bundle.

### Quick build

```bash
./scripts/build_macos_app.sh
```

This generates:

- `dist/venc_gui.app`

You can launch it from Finder or run:

```bash
open dist/venc_gui.app
```

### Manual build command (without script)

```bash
python3 -m pip install -r requirements.txt pyinstaller
python3 -m PyInstaller --windowed --name venc_gui venc_gui.py
```

## Notes for macOS distribution

- If you distribute outside your own machine, you usually need **code signing** (and optionally notarization) so Gatekeeper will trust the app.
- The app still requires `ffmpeg` to be installed and available in `PATH` (for example with Homebrew: `brew install ffmpeg`).
