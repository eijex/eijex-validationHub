"""Compatibility import for the explicitly optional PostgreSQL adapter."""

from validationhub.intake.postgres_ingest import ingest_wetlab_csv

__all__ = ["ingest_wetlab_csv"]
