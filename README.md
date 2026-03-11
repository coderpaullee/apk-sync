# apk-test

This repository stores the APK registry used by Android devices.

Devices only read [`apps/app-list.json`](./apps/app-list.json). Maintainers do not edit that file by hand. The source of truth is `submissions/approved/*.json`, and the registry is generated from those approved submissions.

## For Users

Need an app on the device:

- Open a GitHub Issue with the app name, package name, version, APK link, source website, and usage description.
- Read the detailed submission guide in [`docs/submit-app.md`](./docs/submit-app.md).

## For Maintainers

Review and publish apps:

- Follow the review and sync process in [`docs/maintainer-workflow.md`](./docs/maintainer-workflow.md).
- Apply the acceptance and removal rules in [`docs/policy.md`](./docs/policy.md).
- Store approved apps in [`submissions/approved`](./submissions/approved).
- Rebuild the registry with `python3 scripts/sync_registry.py --write`.

## For Devices

Use these files:

- [`apps/app-list.json`](./apps/app-list.json): generated app registry
- [`apps/changelog.md`](./apps/changelog.md): manual release notes

## Validation

Check approved submissions without rewriting files:

```bash
python3 scripts/sync_registry.py --check
```

Generate the device registry:

```bash
python3 scripts/sync_registry.py --write
```
