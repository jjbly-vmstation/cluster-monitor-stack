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
DOLLAR_VAR_RE = re.compile(r"^\$[A-Za-z0-9_]+$")


def _default_datasource_name_for_placeholder(placeholder: str) -> str:
    # Prefer Prometheus as the default because the majority of community dashboards
    # in this repo are Prometheus-based, and our provisioned data source name is stable.
    p = placeholder.strip("${}")
    p_lower = p.lower()
    if "loki" in p_lower:
        return "Loki"
    return "Prometheus"


def _normalize_templating_var(var_obj: dict[str, Any]) -> dict[str, Any]:
    # Many grafana.com exports ship with datasource template variables that default
    # to a datasource name that doesn't exist in our cluster (e.g. Prometheus-DevTest).
    # We normalize these to our provisioned datasource names.
    var_type = var_obj.get("type")

    # Constant datasource vars commonly appear in dashboards that used grafana.com __inputs.
    # Example: {"name": "datasource", "type": "constant", "query": "${VAR_DATASOURCE}"}
    if var_type == "constant" and isinstance(var_obj.get("name"), str) and var_obj.get("name").lower() in {
        "datasource",
        "var_datasource",
    }:
        ds_name = "Prometheus"
        var_obj["query"] = ds_name
        var_obj["options"] = [{"text": ds_name, "value": ds_name, "selected": False}]
        var_obj["current"] = {"text": ds_name, "value": ds_name, "selected": False}
        return var_obj

    if var_type != "datasource":
        return var_obj

    query = var_obj.get("query")
    if isinstance(query, str) and query.lower() == "loki":
        ds_name = "Loki"
    else:
        # Default to Prometheus for "prometheus" and other/unknown values.
        ds_name = "Prometheus"

    current = var_obj.get("current")
    if not isinstance(current, dict):
        current = {}

    current["text"] = ds_name
    current["value"] = ds_name
    current.setdefault("selected", False)
    var_obj["current"] = current

    # Some dashboards keep an options list that includes non-existent datasource names.
    # Grafana's variable editor can behave poorly when current.value doesn't exist in options.
    options = var_obj.get("options")
    if isinstance(options, list):
        has_ds = any(isinstance(o, dict) and o.get("value") == ds_name for o in options)
        if not has_ds:
            options = [{"text": ds_name, "value": ds_name, "selected": False}]
        var_obj["options"] = options

    return var_obj


def _sanitize_dashboard_uid(filename_base: str) -> str:
    # Grafana UID constraints: <= 40 chars, URL-safe-ish.
    uid = re.sub(r"[^a-zA-Z0-9_-]+", "-", filename_base).strip("-")
    if not uid:
        uid = "dashboard"
    uid = uid.lower()
    if len(uid) > 40:
        uid = uid[:40].rstrip("-")
    return uid


def _rewrite_value(value: Any, parent_key: str | None = None) -> Any:
    if isinstance(value, str):
        if value == "${DS_PROMETHEUS}" or PROM_DS_RE.match(value):
            return "Prometheus"
        if value == "${DS_LOKI}" or LOKI_DS_RE.match(value):
            return "Loki"
        # Common pattern in newer dashboards: ${datasource} is usually used as a datasource UID.
        if value == "${datasource}":
            if parent_key == "uid":
                return "prometheus"
            if parent_key == "datasource":
                return "Prometheus"
            return value

        # Common patterns in older dashboards
        if parent_key == "datasource" and value in {"$datasource", "$Datasource"}:
            return "Prometheus"
        if parent_key == "datasource" and value == "${VAR_DATASOURCE}":
            return "Prometheus"

        # Best-effort: handle placeholder-like datasource values only when we're inside a datasource field.
        if parent_key == "datasource" and (ANY_VAR_RE.match(value) or DOLLAR_VAR_RE.match(value)):
            return _default_datasource_name_for_placeholder(value)

        # Best-effort: some exports use other placeholder spellings.
        if ANY_VAR_RE.match(value) or DOLLAR_VAR_RE.match(value):
            # Do NOT rewrite non-datasource variables (like $namespace) here.
            # We only rewrite known datasource placeholders above, and leave
            # other variables intact.
            return value
        return value

    if isinstance(value, list):
        return [_rewrite_value(v, None) for v in value]

    if isinstance(value, dict):
        new_obj = {k: _rewrite_value(v, k) for k, v in value.items()}

        # Normalize templating datasource variables to known datasources.
        try:
            if isinstance(new_obj.get("type"), str) and "name" in new_obj and "current" in new_obj:
                new_obj = _normalize_templating_var(new_obj)
        except Exception:
            # Keep rendering robust even if dashboards contain unexpected types.
            pass

        # Migrate deprecated pie chart panel plugin id to the built-in panel type.
        if new_obj.get("type") == "grafana-piechart-panel":
            new_obj["type"] = "piechart"

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
