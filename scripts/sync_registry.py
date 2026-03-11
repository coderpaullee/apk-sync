#!/usr/bin/env python3

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_FIELDS = {
    "name",
    "package",
    "version",
    "apk_url",
    "source_url",
    "description",
    "sha256",
    "approved_at",
}
OPTIONAL_FIELDS = {"tested_on"}


@dataclass(frozen=True)
class AppRecord:
    name: str
    package: str
    version: str
    apk_url: str
    source_url: str
    description: str
    sha256: str
    approved_at: str
    tested_on: list[str]

    def to_registry_entry(self) -> dict[str, Any]:
        entry = {
            "name": self.name,
            "package": self.package,
            "version": self.version,
            "apk_url": self.apk_url,
            "source_url": self.source_url,
            "description": self.description,
            "sha256": self.sha256,
        }
        if self.tested_on:
            entry["tested_on"] = self.tested_on
        return entry


def validate_url(value: str, field_name: str, file_path: Path) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{file_path}: invalid {field_name}: {value}")


def require_string(data: dict[str, Any], field_name: str, file_path: Path) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{file_path}: field '{field_name}' must be a non-empty string")
    return value.strip()


def load_submission(file_path: Path) -> AppRecord:
    try:
        data = json.loads(file_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"{file_path}: invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"{file_path}: top-level JSON value must be an object")

    unknown_fields = sorted(set(data) - REQUIRED_FIELDS - OPTIONAL_FIELDS)
    if unknown_fields:
        raise ValueError(f"{file_path}: unsupported fields: {', '.join(unknown_fields)}")

    missing_fields = sorted(REQUIRED_FIELDS - set(data))
    if missing_fields:
        raise ValueError(f"{file_path}: missing required fields: {', '.join(missing_fields)}")

    name = require_string(data, "name", file_path)
    package = require_string(data, "package", file_path)
    version = require_string(data, "version", file_path)
    apk_url = require_string(data, "apk_url", file_path)
    source_url = require_string(data, "source_url", file_path)
    description = require_string(data, "description", file_path)
    sha256 = require_string(data, "sha256", file_path).lower()
    approved_at = require_string(data, "approved_at", file_path)

    if not PACKAGE_RE.match(package):
        raise ValueError(f"{file_path}: invalid package name: {package}")

    validate_url(apk_url, "apk_url", file_path)
    validate_url(source_url, "source_url", file_path)

    if not SHA256_RE.match(sha256):
        raise ValueError(f"{file_path}: sha256 must be 64 lowercase hex characters")

    if not DATE_RE.match(approved_at):
        raise ValueError(f"{file_path}: approved_at must use YYYY-MM-DD format")

    tested_on_value = data.get("tested_on", [])
    if not isinstance(tested_on_value, list) or any(
        not isinstance(item, str) or not item.strip() for item in tested_on_value
    ):
        raise ValueError(f"{file_path}: tested_on must be a list of non-empty strings")

    tested_on = [item.strip() for item in tested_on_value]

    return AppRecord(
        name=name,
        package=package,
        version=version,
        apk_url=apk_url,
        source_url=source_url,
        description=description,
        sha256=sha256,
        approved_at=approved_at,
        tested_on=tested_on,
    )


def load_all_submissions(approved_dir: Path) -> list[AppRecord]:
    records: list[AppRecord] = []
    seen_packages: dict[str, Path] = {}

    for file_path in sorted(approved_dir.glob("*.json")):
        record = load_submission(file_path)
        if record.package in seen_packages:
            raise ValueError(
                f"duplicate package '{record.package}' in {seen_packages[record.package]} and {file_path}"
            )
        seen_packages[record.package] = file_path
        records.append(record)

    return sorted(records, key=lambda item: (item.name.lower(), item.package))


def build_registry(records: list[AppRecord], existing_registry_path: Path) -> dict[str, Any]:
    config_version = 1
    if existing_registry_path.exists():
        current_data = json.loads(existing_registry_path.read_text())
        if isinstance(current_data, dict) and isinstance(current_data.get("config_version"), int):
            config_version = current_data["config_version"]

    return {
        "config_version": config_version,
        "updated": date.today().isoformat(),
        "apps": [record.to_registry_entry() for record in records],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate approved app submissions and build app-list.json")
    parser.add_argument("--check", action="store_true", help="validate only; do not write files")
    parser.add_argument("--write", action="store_true", help="write apps/app-list.json")
    args = parser.parse_args()

    if args.check == args.write:
        parser.error("choose exactly one of --check or --write")

    repo_root = Path(__file__).resolve().parent.parent
    approved_dir = repo_root / "submissions" / "approved"
    registry_path = repo_root / "apps" / "app-list.json"

    if not approved_dir.exists():
        raise ValueError(f"approved submissions directory does not exist: {approved_dir}")

    records = load_all_submissions(approved_dir)
    registry = build_registry(records, registry_path)

    if args.check:
        print(f"Validated {len(records)} approved submission(s)")
        return 0

    registry_path.write_text(json.dumps(registry, indent=2) + "\n")
    print(f"Wrote {registry_path} with {len(records)} app(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
