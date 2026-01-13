#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from typing import Any


PROM_DS_RE = re.compile(r"^\$\{DS_.*PROMETHEUS\}$")
LOKI_DS_RE = re.compile(r"^\$\{DS_.*LOKI\}$")
ANY_VAR_RE = re.compile(r"^\$\{[^}]+\}$")


def _sanitize_dashboard_uid(filename_base: str) -> str:
    # Grafana UID constraints: <= 40 chars, URL-safe-ish.
    uid = re.sub(r"[^a-zA-Z0-9_-]+", "-", filename_base).strip("-")
    if not uid:
        uid = "dashboard"
    uid = uid.lower()
    if len(uid) > 40:
        uid = uid[:40].rstrip("-")
    return uid


def _rewrite_value(value: Any) -> Any:
    if isinstance(value, str):
        if value == "${DS_PROMETHEUS}" or PROM_DS_RE.match(value):
            return "Prometheus"
        if value == "${DS_LOKI}" or LOKI_DS_RE.match(value):
            return "Loki"
        # Common pattern in newer dashboards
        if value == "${datasource}":
            return "prometheus"
        return value

    if isinstance(value, list):
        return [_rewrite_value(v) for v in value]

    if isinstance(value, dict):
        new_obj = {k: _rewrite_value(v) for k, v in value.items()}

        # Datasource objects often look like: {"type": "prometheus", "uid": "${datasource}"}
        ds_type = new_obj.get("type")
        ds_uid = new_obj.get("uid")
        if isinstance(ds_type, str) and isinstance(ds_uid, str) and ANY_VAR_RE.match(ds_uid):
            if ds_type == "prometheus":
                new_obj["uid"] = "prometheus"
            elif ds_type == "loki":
                new_obj["uid"] = "loki"
        return new_obj

    return value


def render_dashboard(src_path: str, dest_path: str) -> None:
    with open(src_path, "r", encoding="utf-8") as f:
        dashboard = json.load(f)

    if not isinstance(dashboard, dict):
        raise ValueError(f"Dashboard JSON must be an object: {src_path}")

    # Strip grafana.com export-only metadata; provisioning does not support interactive inputs.
    for key in ["__inputs", "__requires", "__elements"]:
        dashboard.pop(key, None)

    # Ensure ID is not pinned.
    dashboard["id"] = None

    filename_base = os.path.splitext(os.path.basename(src_path))[0]
    dashboard.setdefault("uid", _sanitize_dashboard_uid(filename_base))

    dashboard = _rewrite_value(dashboard)

    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Grafana dashboards for file provisioning")
    parser.add_argument("--src", required=True, help="Source directory containing *.json dashboards")
    parser.add_argument("--dest", required=True, help="Destination directory to write rendered *.json dashboards")
    parser.add_argument("--clean", action="store_true", help="Delete existing *.json in destination first")
    args = parser.parse_args()

    src_dir = args.src
    dest_dir = args.dest

    if not os.path.isdir(src_dir):
        print(f"ERROR: source directory not found: {src_dir}", file=sys.stderr)
        return 2

    os.makedirs(dest_dir, exist_ok=True)

    if args.clean:
        for name in os.listdir(dest_dir):
            if name.endswith(".json"):
                try:
                    os.unlink(os.path.join(dest_dir, name))
                except OSError as e:
                    print(f"WARN: failed to delete {name}: {e}", file=sys.stderr)

    src_files = sorted([f for f in os.listdir(src_dir) if f.endswith(".json")])
    if not src_files:
        print(f"ERROR: no dashboard JSON files found in {src_dir}", file=sys.stderr)
        return 3

    rendered = 0
    for name in src_files:
        src_path = os.path.join(src_dir, name)
        dest_path = os.path.join(dest_dir, name)
        try:
            render_dashboard(src_path, dest_path)
            rendered += 1
        except Exception as e:
            print(f"ERROR: failed to render {src_path}: {e}", file=sys.stderr)
            return 4

    print(f"Rendered dashboards: {rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
