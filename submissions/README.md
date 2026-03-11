# Approved Submissions

This directory stores the reviewed app records that are allowed to reach devices.

Rules:

- One JSON file per app
- File names should be stable and predictable, for example `org.videolan.vlc.json`
- Only approved apps belong here
- `apps/app-list.json` must be regenerated after any change in this directory

Run:

```bash
python3 scripts/sync_registry.py --check
python3 scripts/sync_registry.py --write
```
