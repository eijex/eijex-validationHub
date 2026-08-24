"""Local SQLite Registry v0 for ValidationHub.

The registry stores hashes and coarse public-safe metadata only. It may hash
FASTA bytes, but it never stores or returns raw biological sequences.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REGISTRY_SCHEMA_VERSION = "registry_v0.1"
GENESIS_EVENT_TYPE = "registry_initialized"
PUBLIC_SEQUENCE_HASH_FIELD = "sequence_hash"
PUBLIC_WET_LAB_TEMPLATE_FIELD_ALIASES = {
    "version": "factorforge_version",
}

DEFAULT_CONSTANT_PATHS = (
    "schemas/prohibited_fields.json",
    "schemas/validation_survey_record.schema.json",
    "schemas/public_validation_summary.schema.json",
    "schemas/curated_validation_record.schema.json",
    "schemas/design_reference.schema.json",
    "schemas/benchmark_evidence_reference.schema.json",
    "docs/DATA_BOUNDARY.md",
)

PUBLIC_WET_LAB_REQUIRED_FIELDS = (
    "factorforge_version",
    "profile",
    "host",
    "protein_class",
    "assay_category",
    "comparison_result",
    "expression_result",
    "public_safe_confirmation",
)

PUBLIC_WET_LAB_OPTIONAL_FIELDS = (
    "replicate_category",
    "non_confidential_notes",
    "feedback_boundary_confirmation",
    "maintainer_review_confirmation",
)

PUBLIC_WET_LAB_ALLOWED_FIELDS = set(PUBLIC_WET_LAB_REQUIRED_FIELDS) | set(
    PUBLIC_WET_LAB_OPTIONAL_FIELDS
)

PROHIBITED_WET_LAB_FIELDS = {
    "raw_sequence",
    "sequence",
    "dna_sequence",
    "rna_sequence",
    "protein_sequence",
    "amino_acid_sequence",
    "construct_sequence",
    "customer_sequence",
    "proprietary_sequence",
    "construct_id",
    "internal_batch_id",
    "customer_construct_id",
    "protein_name",
    "submitter_name",
    "submitter_email",
    "respondent_email",
    "contact_email",
    "phone_number",
    "personal_identifier",
    "institution_name",
    "exact_process_parameters",
}

_FASTA_LINE = re.compile(r"^[A-Za-z*.-]+$")


class RegistryError(ValueError):
    """Raised when Registry v0 input violates a safety or schema rule."""


@dataclass(frozen=True)
class ArtifactRegistration:
    artifact_id: str
    role: str
    label: str
    sha256: str
    size_bytes: int
    event_hash: str


@dataclass(frozen=True)
class ConstantsHash:
    constants_hash: str
    files: tuple[tuple[str, str], ...]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def payload_hash(payload: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def file_sha256(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            total += len(chunk)
            digest.update(chunk)
    return digest.hexdigest(), total


def assert_public_label(label: str) -> None:
    if not label or not label.strip():
        raise RegistryError("artifact label is required")
    lowered = label.lower()
    forbidden_fragments = (
        "raw_sequence",
        "private",
        "collaborator",
        "construct_id",
        "internal_batch",
        "protein_name",
    )
    if any(fragment in lowered for fragment in forbidden_fragments):
        raise RegistryError("artifact label must be public-safe and non-identifying")


def assert_probable_fasta(path: Path) -> None:
    saw_header = False
    saw_sequence_line = False
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(">"):
                saw_header = True
                continue
            if _FASTA_LINE.fullmatch(stripped) is None:
                raise RegistryError("FASTA contains a non-sequence line")
            saw_sequence_line = True
    if not saw_header or not saw_sequence_line:
        raise RegistryError("FASTA must contain at least one header and one sequence line")


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaction(db_path: Path):
    conn = connect(db_path)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def initialize_registry(db_path: Path) -> str:
    """Create Registry v0 tables and return the current head event hash."""

    with transaction(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS registry_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS registry_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                prev_event_hash TEXT,
                event_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                CHECK (length(payload_hash) = 64),
                CHECK (prev_event_hash IS NULL OR length(prev_event_hash) = 64),
                CHECK (length(event_hash) = 64)
            );

            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                label TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                source_kind TEXT NOT NULL,
                content_type TEXT NOT NULL,
                supersedes_artifact_id TEXT,
                created_event_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                CHECK (role IN ('input_fasta', 'output_fasta', 'registry_constants')),
                CHECK (length(sha256) = 64),
                CHECK (size_bytes >= 0),
                FOREIGN KEY (supersedes_artifact_id) REFERENCES artifacts(artifact_id),
                FOREIGN KEY (created_event_hash) REFERENCES registry_events(event_hash)
            );

            CREATE TABLE IF NOT EXISTS wet_lab_feedback_public_safe (
                feedback_id TEXT PRIMARY KEY,
                record_json TEXT NOT NULL,
                record_sha256 TEXT NOT NULL,
                created_event_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                CHECK (length(record_sha256) = 64),
                FOREIGN KEY (created_event_hash) REFERENCES registry_events(event_hash)
            );
            """
        )
        conn.execute(
            "INSERT OR IGNORE INTO registry_meta(key, value) VALUES (?, ?)",
            ("schema_version", REGISTRY_SCHEMA_VERSION),
        )
        existing = conn.execute(
            "SELECT event_hash FROM registry_events ORDER BY rowid LIMIT 1"
        ).fetchone()
        if existing:
            return str(existing["event_hash"])
        event_hash = _append_event(
            conn,
            GENESIS_EVENT_TYPE,
            {"schema_version": REGISTRY_SCHEMA_VERSION},
        )
        return event_hash


def current_head_hash(conn: sqlite3.Connection) -> str | None:
    row = conn.execute(
        "SELECT event_hash FROM registry_events ORDER BY created_at DESC, rowid DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    return str(row["event_hash"])


def _append_event(conn: sqlite3.Connection, event_type: str, payload: dict[str, Any]) -> str:
    prev = current_head_hash(conn)
    phash = payload_hash(payload)
    created_at = utc_now_iso()
    event_id = str(uuid.uuid4())
    event_hash = sha256_bytes(
        canonical_json(
            {
                "event_id": event_id,
                "event_type": event_type,
                "payload_hash": phash,
                "prev_event_hash": prev,
                "created_at": created_at,
            }
        ).encode("utf-8")
    )
    conn.execute(
        """
        INSERT INTO registry_events(
            event_id, event_type, payload_hash, prev_event_hash, event_hash, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (event_id, event_type, phash, prev, event_hash, created_at),
    )
    return event_hash


def register_fasta_artifact(
    db_path: Path,
    fasta_path: Path,
    *,
    role: str,
    label: str,
    supersedes_artifact_id: str | None = None,
) -> ArtifactRegistration:
    if role not in {"input_fasta", "output_fasta"}:
        raise RegistryError("role must be input_fasta or output_fasta")
    assert_public_label(label)
    assert_probable_fasta(fasta_path)
    digest, size = file_sha256(fasta_path)
    artifact_id = str(uuid.uuid4())
    payload = {
        "artifact_id": artifact_id,
        "role": role,
        "label": label,
        "sha256": digest,
        "size_bytes": size,
        "source_kind": "local_file_hash_only",
        "content_type": "text/fasta",
        "supersedes_artifact_id": supersedes_artifact_id,
    }
    with transaction(db_path) as conn:
        initialize_registry(db_path)
        event_hash = _append_event(conn, "artifact_registered", payload)
        conn.execute(
            """
            INSERT INTO artifacts(
                artifact_id, role, label, sha256, size_bytes, source_kind, content_type,
                supersedes_artifact_id, created_event_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                artifact_id,
                role,
                label,
                digest,
                size,
                "local_file_hash_only",
                "text/fasta",
                supersedes_artifact_id,
                event_hash,
                utc_now_iso(),
            ),
        )
    return ArtifactRegistration(artifact_id, role, label, digest, size, event_hash)


def registry_constants_hash(
    root: Path,
    paths: tuple[str, ...] = DEFAULT_CONSTANT_PATHS,
) -> ConstantsHash:
    file_hashes: list[tuple[str, str]] = []
    for rel in paths:
        path = root / rel
        if not path.exists():
            raise RegistryError(f"registry constants path is missing: {rel}")
        digest, _size = file_sha256(path)
        file_hashes.append((rel.replace("\\", "/"), digest))
    payload = {"schema_version": REGISTRY_SCHEMA_VERSION, "files": file_hashes}
    return ConstantsHash(payload_hash(payload), tuple(file_hashes))


def register_registry_constants(
    db_path: Path, root: Path, paths: tuple[str, ...] = DEFAULT_CONSTANT_PATHS
) -> ArtifactRegistration:
    constants = registry_constants_hash(root, paths)
    artifact_id = str(uuid.uuid4())
    payload = {
        "artifact_id": artifact_id,
        "role": "registry_constants",
        "label": "registry-v0-policy-and-schema-constants",
        "sha256": constants.constants_hash,
        "size_bytes": len(canonical_json(constants.files).encode("utf-8")),
        "source_kind": "canonical_file_list_hash",
        "content_type": "application/json",
        "files": constants.files,
    }
    with transaction(db_path) as conn:
        initialize_registry(db_path)
        event_hash = _append_event(conn, "registry_constants_registered", payload)
        conn.execute(
            """
            INSERT INTO artifacts(
                artifact_id, role, label, sha256, size_bytes, source_kind, content_type,
                supersedes_artifact_id, created_event_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, ?)
            """,
            (
                artifact_id,
                "registry_constants",
                "registry-v0-policy-and-schema-constants",
                constants.constants_hash,
                payload["size_bytes"],
                "canonical_file_list_hash",
                "application/json",
                event_hash,
                utc_now_iso(),
            ),
        )
    return ArtifactRegistration(
        artifact_id,
        "registry_constants",
        "registry-v0-policy-and-schema-constants",
        constants.constants_hash,
        payload["size_bytes"],
        event_hash,
    )


def validate_public_wet_lab_feedback(record: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(record)
    for template_field, registry_field in PUBLIC_WET_LAB_TEMPLATE_FIELD_ALIASES.items():
        if template_field in normalized and registry_field in normalized:
            raise RegistryError(
                f"public wet-lab feedback contains both {template_field} and {registry_field}"
            )
        if template_field in normalized:
            normalized[registry_field] = normalized.pop(template_field)
    keys = set(normalized)
    prohibited = (keys & PROHIBITED_WET_LAB_FIELDS) | ({PUBLIC_SEQUENCE_HASH_FIELD} & keys)
    if prohibited:
        raise RegistryError(
            f"public wet-lab feedback contains prohibited fields: {sorted(prohibited)}"
        )
    unknown = keys - PUBLIC_WET_LAB_ALLOWED_FIELDS
    if unknown:
        raise RegistryError(f"public wet-lab feedback contains unknown fields: {sorted(unknown)}")
    missing = set(PUBLIC_WET_LAB_REQUIRED_FIELDS) - keys
    if missing:
        raise RegistryError(f"public wet-lab feedback missing required fields: {sorted(missing)}")
    for confirmation in (
        "public_safe_confirmation",
        "feedback_boundary_confirmation",
        "maintainer_review_confirmation",
    ):
        if confirmation in normalized and normalized.get(confirmation) is not True:
            raise RegistryError(f"{confirmation} must be true")
    clean: dict[str, Any] = {}
    for key in sorted(normalized):
        value = normalized[key]
        if isinstance(value, str):
            value = value.strip()
        clean[key] = value
    return clean


def register_public_wet_lab_feedback(db_path: Path, record: dict[str, Any]) -> str:
    clean = validate_public_wet_lab_feedback(record)
    record_text = canonical_json(clean)
    record_sha = sha256_bytes(record_text.encode("utf-8"))
    feedback_id = str(uuid.uuid4())
    payload = {"feedback_id": feedback_id, "record_sha256": record_sha}
    with transaction(db_path) as conn:
        initialize_registry(db_path)
        event_hash = _append_event(conn, "public_safe_wet_lab_feedback_registered", payload)
        conn.execute(
            """
            INSERT INTO wet_lab_feedback_public_safe(
                feedback_id, record_json, record_sha256, created_event_hash, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (feedback_id, record_text, record_sha, event_hash, utc_now_iso()),
        )
    return feedback_id


def verify_event_chain(db_path: Path) -> bool:
    with transaction(db_path) as conn:
        rows = conn.execute(
            """
            SELECT event_id, event_type, payload_hash, prev_event_hash, event_hash, created_at
            FROM registry_events
            ORDER BY created_at, rowid
            """
        ).fetchall()
    previous = None
    for row in rows:
        if row["prev_event_hash"] != previous:
            return False
        expected = sha256_bytes(
            canonical_json(
                {
                    "event_id": row["event_id"],
                    "event_type": row["event_type"],
                    "payload_hash": row["payload_hash"],
                    "prev_event_hash": row["prev_event_hash"],
                    "created_at": row["created_at"],
                }
            ).encode("utf-8")
        )
        if row["event_hash"] != expected:
            return False
        previous = row["event_hash"]
    return True


def registry_summary(db_path: Path) -> dict[str, int | str | None]:
    with transaction(db_path) as conn:
        initialize_registry(db_path)
        artifacts = conn.execute("SELECT COUNT(*) AS n FROM artifacts").fetchone()["n"]
        feedback = conn.execute(
            "SELECT COUNT(*) AS n FROM wet_lab_feedback_public_safe"
        ).fetchone()["n"]
        events = conn.execute("SELECT COUNT(*) AS n FROM registry_events").fetchone()["n"]
        head = current_head_hash(conn)
    return {"artifacts": artifacts, "public_feedback": feedback, "events": events, "head": head}
