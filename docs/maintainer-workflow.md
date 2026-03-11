# Maintainer Workflow

## Intake

1. Review new app request Issues.
2. Confirm the Issue includes app name, package name, version, APK URL, source URL, and description.
3. Reject incomplete or suspicious requests early.

## Verification

1. Download the APK from the submitted source.
2. Confirm the package name and version match the request.
3. Install and smoke-test on a reference device.
4. Compute and record the APK `sha256`.

## Approval

1. Create or update `submissions/approved/<package>.json`.
2. Run `python3 scripts/sync_registry.py --check`.
3. Run `python3 scripts/sync_registry.py --write`.
4. Review the generated diff in `apps/app-list.json`.
5. Commit the approved submission file and generated registry together.

## Operating Rules

- Do not edit `apps/app-list.json` manually.
- Keep one approved JSON file per package.
- Prefer removing an app from `submissions/approved/` and regenerating the registry over hand-editing the generated file.
