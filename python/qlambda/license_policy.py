"""Array-backed tri-license policy engine.

This keeps repository language metrics aligned with the actual Python/Lean
package.
"""

from __future__ import annotations

import argparse
from typing import Dict, Tuple

LICENSES: Tuple[str, ...] = ("bsl_1_1", "agpl_3_0", "mpl_2_0", "commercial")

USE_CASES: Dict[str, str] = {
    "saas_wrapper": "agpl_3_0",
    "enterprise_restricted": "bsl_1_1",
    "file_level_mod": "mpl_2_0",
    "copyleft_bypass": "commercial",
    "open_source_redistribution": "agpl_3_0",
}

COMPATIBILITY: Tuple[Tuple[str, str], ...] = (
    ("mpl_2_0", "proprietary"),
    ("mpl_2_0", "mpl_2_0"),
    ("bsl_1_1", "source_available"),
    ("agpl_3_0", "agpl_3_0"),
    ("commercial", "proprietary"),
)


def select_license(use_case: str) -> str:
    try:
        return USE_CASES[use_case]
    except KeyError as exc:
        raise ValueError(f"unknown use case: {use_case}") from exc


def is_compatible(license_name: str, dependency_type: str) -> bool:
    return (license_name, dependency_type) in COMPATIBILITY


def main() -> None:
    parser = argparse.ArgumentParser(description="Select or check the tri-license policy.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    select = sub.add_parser("select")
    select.add_argument("use_case")

    check = sub.add_parser("check")
    check.add_argument("license")
    check.add_argument("dependency")

    sub.add_parser("matrix")
    args = parser.parse_args()

    if args.cmd == "select":
        print(f"Recommended License: {select_license(args.use_case)}")
    elif args.cmd == "check":
        ok = is_compatible(args.license, args.dependency)
        label = "compatible" if ok else "INCOMPATIBLE"
        print(f"{args.license} is {label} with {args.dependency}.")
        raise SystemExit(0 if ok else 1)
    elif args.cmd == "matrix":
        for license_name, dependency in COMPATIBILITY:
            print(f"{license_name} <-> {dependency}")


if __name__ == "__main__":
    main()
