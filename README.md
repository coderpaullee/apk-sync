# apk-test

This repository stores the APK registry consumed by our Android devices.

Devices only read `apps/app-list.json`. Maintainers do not edit that file by hand. The source of truth is `submissions/approved/*.json`, and the registry is generated from those approved submissions.

## Workflow

1. Users submit an app request through a GitHub Issue.
2. Maintainers verify the APK link, package name, version, and installation safety.
3. Approved apps are recorded as JSON files in `submissions/approved/`.
4. Run `python3 scripts/sync_registry.py --write` to validate approved submissions and rebuild `apps/app-list.json`.
5. Commit the submission file and generated registry together.

## Repository Layout

- `apps/app-list.json`: generated device-facing registry
- `apps/changelog.md`: high-level manual changelog
- `submissions/approved/`: approved app records, one JSON file per app
- `scripts/sync_registry.py`: validation and sync script
- `docs/`: operator-facing workflow and policy docs

## Approved Submission Format

Each file in `submissions/approved/` must include:

- `name`
- `package`
- `version`
- `apk_url`
- `source_url`
- `description`
- `sha256`
- `approved_at`

Optional:

- `tested_on`

Example:

```json
{
  "name": "VLC",
  "package": "org.videolan.vlc",
  "version": "3.7.0",
  "apk_url": "https://get.videolan.org/vlc-android/3.7.0/VLC-Android-3.7.0-arm64-v8a.apk",
  "source_url": "https://www.videolan.org/vlc/download-android.html",
  "description": "Open source video player",
  "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "approved_at": "2026-03-11",
  "tested_on": [
    "Reference Device A"
  ]
}
```

## Commands

Validate approved submissions without changing files:

```bash
python3 scripts/sync_registry.py --check
```

Rebuild the device registry:

```bash
python3 scripts/sync_registry.py --write
```
