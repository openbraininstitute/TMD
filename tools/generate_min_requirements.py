#!/usr/bin/env python3
"""Generate minimum pinned requirements from pyproject.toml."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from packaging.requirements import Requirement


def _min_pin(requirement: Requirement) -> str:
    name = requirement.name
    if not requirement.specifier:
        return name

    for spec in requirement.specifier:
        if spec.operator == ">=":
            return f"{name}=={spec.version}"
        if spec.operator == "==":
            return f"{name}=={spec.version}"

    return str(requirement)


def generate_min_requirements(pyproject: Path, extras: list[str]) -> list[str]:
    """Return minimum pinned requirements for project and optional extras."""
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    requirements = list(data["project"]["dependencies"])
    optional = data["project"].get("optional-dependencies", {})
    for extra in extras:
        requirements.extend(optional[extra])

    seen: set[str] = set()
    pins: list[str] = []
    for req_str in requirements:
        pin = _min_pin(Requirement(req_str))
        if pin not in seen:
            seen.add(pin)
            pins.append(pin)
    return pins


def main() -> None:
    """Generate a requirements file with minimum dependency pins."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("-e", "--extra", action="append", default=[])
    parser.add_argument("pyproject", type=Path, nargs="?", default=Path("pyproject.toml"))
    args = parser.parse_args()

    lines = generate_min_requirements(args.pyproject, args.extra)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
