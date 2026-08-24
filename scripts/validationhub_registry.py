#!/usr/bin/env python3
"""CLI helpers for ValidationHub Registry v0.

Output is intentionally hash/metadata only. It never prints FASTA sequence
contents or private collaborator identifiers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validationhub.registry_v0 import (
    initialize_registry,
    register_fasta_artifact,
    register_registry_constants,
    registry_constants_hash,
    registry_summary,
    verify_event_chain,
)


def print_json(data: object) -> None:
    print(json.dumps(data, sort_keys=True, indent=2))


def cmd_init(args: argparse.Namespace) -> None:
    head = initialize_registry(Path(args.db))
    print_json({"ok": True, "head": head, "db": str(args.db)})


def cmd_register_fasta(args: argparse.Namespace) -> None:
    result = register_fasta_artifact(
        Path(args.db), Path(args.fasta), role=args.role, label=args.label
    )
    print_json(
        {
            "artifact_id": result.artifact_id,
            "role": result.role,
            "label": result.label,
            "sha256": result.sha256,
            "size_bytes": result.size_bytes,
            "event_hash": result.event_hash,
        }
    )


def cmd_constants_hash(args: argparse.Namespace) -> None:
    result = registry_constants_hash(Path(args.root))
    print_json({"constants_hash": result.constants_hash, "files": result.files})


def cmd_register_constants(args: argparse.Namespace) -> None:
    result = register_registry_constants(Path(args.db), Path(args.root))
    print_json(
        {
            "artifact_id": result.artifact_id,
            "role": result.role,
            "label": result.label,
            "sha256": result.sha256,
            "size_bytes": result.size_bytes,
            "event_hash": result.event_hash,
        }
    )


def cmd_self_test(args: argparse.Namespace) -> None:
    db = Path(args.db)
    initialize_registry(db)
    ok = verify_event_chain(db)
    summary = registry_summary(db)
    print_json({"ok": ok, "summary": summary})
    if not ok:
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ValidationHub Registry v0 local helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize a local Registry v0 SQLite database")
    p_init.add_argument("--db", required=True)
    p_init.set_defaults(func=cmd_init)

    p_fasta = sub.add_parser("register-fasta", help="Register an input/output FASTA by hash only")
    p_fasta.add_argument("--db", required=True)
    p_fasta.add_argument("--fasta", required=True)
    p_fasta.add_argument("--role", required=True, choices=["input_fasta", "output_fasta"])
    p_fasta.add_argument("--label", required=True)
    p_fasta.set_defaults(func=cmd_register_fasta)

    p_hash = sub.add_parser(
        "constants-hash",
        help="Compute deterministic Registry v0 constants hash",
    )
    p_hash.add_argument("--root", default=".")
    p_hash.set_defaults(func=cmd_constants_hash)

    p_constants = sub.add_parser("register-constants", help="Register Registry v0 constants hash")
    p_constants.add_argument("--db", required=True)
    p_constants.add_argument("--root", default=".")
    p_constants.set_defaults(func=cmd_register_constants)

    p_self = sub.add_parser("self-test", help="Verify append-only event linkage")
    p_self.add_argument("--db", required=True)
    p_self.set_defaults(func=cmd_self_test)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
