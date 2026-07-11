"""Compiler placeholders. No real source ingestion is authorized in B0."""
from .source_license_fixtures import (
    build_derived_only_license_manifest,
    build_human_review_required_license_manifest,
    build_metadata_only_license_manifest,
    build_valid_license_manifest,
    build_valid_source_license_pair,
    build_valid_source_manifest,
)

__all__ = [
    "build_derived_only_license_manifest",
    "build_human_review_required_license_manifest",
    "build_metadata_only_license_manifest",
    "build_valid_license_manifest",
    "build_valid_source_license_pair",
    "build_valid_source_manifest",
]
