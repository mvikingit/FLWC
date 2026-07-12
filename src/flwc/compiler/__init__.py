"""Compiler placeholders. No real source ingestion is authorized in B0."""
from .claim_event_fixtures import (
    build_valid_atomic_claim,
    build_valid_atomic_claim_ledger,
    build_valid_claim_event_compiler_output,
    build_valid_claim_event_pair,
    build_valid_financial_event,
    build_valid_financial_event_table,
)
from .raw_evidence_fixtures import (
    build_valid_raw_evidence_index_pair,
    build_valid_raw_evidence_record,
    build_valid_raw_evidence_vault_manifest,
    build_valid_source_document_index,
)
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
    "build_valid_atomic_claim",
    "build_valid_atomic_claim_ledger",
    "build_valid_claim_event_compiler_output",
    "build_valid_claim_event_pair",
    "build_valid_financial_event",
    "build_valid_financial_event_table",
    "build_valid_raw_evidence_index_pair",
    "build_valid_raw_evidence_record",
    "build_valid_raw_evidence_vault_manifest",
    "build_valid_license_manifest",
    "build_valid_source_license_pair",
    "build_valid_source_manifest",
    "build_valid_source_document_index",
]
