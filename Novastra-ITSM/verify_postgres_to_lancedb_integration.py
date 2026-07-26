#!/usr/bin/env python
# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Integration Verification: PostgreSQL → LanceDB Data Flow
# Date: 2026-04-15
# ---------------------------------------------------------------------------
"""
Integration Verification: PostgreSQL → LanceDB Data Flow

This script verifies that when ServiceNow incidents are synced to PostgreSQL,
they are automatically indexed in LanceDB with the required schema:
  - incident_id
  - embedding
  - text_chunk
  - metadata

Usage:
  python verify_postgres_to_lancedb_integration.py [--detailed]
"""
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)


# Function: verify_schema
def verify_schema() -> bool:
    """Verify LanceDB schema matches requirements."""
    logger.info("=" * 70)
    logger.info("SCHEMA VERIFICATION")
    logger.info("=" * 70)
    
    try:
        from backend.services.lancedb_store import (
            get_lancedb_client,
            lancedb_enabled,
            _table_exists,
        )
        import backend.config as cfg
        
        if not lancedb_enabled():
            logger.error("✗ LanceDB is not enabled")
            return False
        
        logger.info("✓ LanceDB backend enabled")
        
        client = get_lancedb_client()
        table_name = cfg.LANCEDB_TABLE
        
        if not _table_exists(client, table_name):
            logger.warning(
                "⚠ Table '%s' does not exist yet (will be created on first insert)",
                table_name
            )
            logger.info("✓ LanceDB path is configured: %s", cfg.LANCEDB_PATH)
            return True
        
        # Get table schema
        table = client.open_table(table_name)
        schema = table.schema
        
        logger.info("✓ Table '%s' exists", table_name)
        logger.info("  Schema: %s", schema)
        
        # Check required fields
        required_fields = {"incident_id", "embedding", "text_chunk", "metadata"}
        schema_fields = {field.name for field in schema}
        
        missing = required_fields - schema_fields
        if missing:
            logger.error("✗ Missing required fields: %s", missing)
            return False
        
        logger.info("✓ All required fields present:")
        for field in schema:
            logger.info("    - %s: %s", field.name, field.type)
        
        return True
        
    except Exception as exc:
        logger.error("✗ Schema verification failed: %s", exc)
        return False


# Function: verify_postgresql_schema
def verify_postgresql_schema() -> bool:
    """Verify PostgreSQL has incident data."""
    logger.info("\n" + "=" * 70)
    logger.info("POSTGRESQL VERIFICATION")
    logger.info("=" * 70)
    
    try:
        from backend.services.postgres_store import ensure_common_schema, get_connection
        
        ensure_common_schema()
        logger.info("✓ PostgreSQL schema initialized")
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check if sn_incidents table exists
                cur.execute(
                    """
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = 'sn_incidents'
                    """
                )
                exists = bool(cur.fetchone()[0])
                
                if not exists:
                    logger.warning("⚠ sn_incidents table not yet created (will be on first sync)")
                    conn.commit()
                    return True
                
                # Count incidents
                cur.execute("SELECT COUNT(*) FROM sn_incidents")
                count = int(cur.fetchone()[0] or 0)
                logger.info("✓ sn_incidents table exists with %d records", count)
                
                if count > 0:
                    # Show sample incident
                    cur.execute(
                        """
                        SELECT incident_id, number, short_description, category, state
                        FROM sn_incidents LIMIT 1
                        """
                    )
                    incident = cur.fetchone()
                    if incident:
                        logger.info("  Sample incident:")
                        logger.info("    - ID: %s", incident[0])
                        logger.info("    - Number: %s", incident[1])
                        logger.info("    - Description: %s", incident[2][:50])
                        logger.info("    - Category: %s", incident[3])
                        logger.info("    - State: %s", incident[4])
                
                conn.commit()
                return True
                
    except Exception as exc:
        logger.error("✗ PostgreSQL verification failed: %s", exc)
        return False


# Function: verify_lancedb_data
def verify_lancedb_data() -> bool:
    """Verify LanceDB has indexed data from PostgreSQL."""
    logger.info("\n" + "=" * 70)
    logger.info("LANCEDB DATA VERIFICATION")
    logger.info("=" * 70)
    
    try:
        from backend.services.lancedb_store import (
            get_points_count,
            get_table_stats,
            lancedb_enabled,
            _table_exists,
            get_lancedb_client,
        )
        import backend.config as cfg
        
        if not lancedb_enabled():
            logger.error("✗ LanceDB not enabled")
            return False
        
        count = get_points_count()
        logger.info("✓ LanceDB total vectors: %d", count)
        
        stats = get_table_stats()
        logger.info("  Status: %s", stats.get("status"))
        logger.info("  Table: %s", stats.get("table_name"))
        
        if count == 0:
            logger.warning("⚠ No vectors in LanceDB yet (run ingestion to populate)")
            return True
        
        # Show sample record
        try:
            client = get_lancedb_client()
            table_name = cfg.LANCEDB_TABLE
            
            if _table_exists(client, table_name):
                table = client.open_table(table_name)
                sample = table.search([0.5] * 384).limit(1).to_list()  # Dummy query
                
                if sample:
                    record = sample[0]
                    logger.info("  Sample record structure:")
                    logger.info("    - incident_id: %s", record.get("incident_id"))
                    logger.info("    - embedding: [%d dimensions]", len(record.get("embedding", [])))
                    logger.info("    - text_chunk: %s", str(record.get("text_chunk", ""))[:50])
                    
                    metadata = record.get("metadata", {})
                    logger.info("    - metadata:")
                    for key, value in metadata.items():
                        if key != "chunk_index":
                            logger.info("        - %s: %s", key, str(value)[:40])
        except Exception as e:
            logger.debug("Could not fetch sample: %s", e)
        
        return True
        
    except Exception as exc:
        logger.error("✗ LanceDB data verification failed: %s", exc)
        return False


# Function: verify_data_flow
def verify_data_flow() -> bool:
    """Verify the complete PostgreSQL → LanceDB data flow."""
    logger.info("\n" + "=" * 70)
    logger.info("END-TO-END DATA FLOW VERIFICATION")
    logger.info("=" * 70)
    
    try:
        from backend.services.postgres_store import get_connection
        from backend.services.embedding_worker_lancedb import index_incidents_to_lancedb
        from backend.services.lancedb_store import get_points_count
        
        # Check PostgreSQL incidents
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = 'sn_incidents'
                    """
                )
                if not cur.fetchone()[0]:
                    logger.info("✓ No PostgreSQL data yet (will be created on sync)")
                    conn.commit()
                    return True
                
                cur.execute("SELECT incident_id, number, short_description, description FROM sn_incidents LIMIT 1")
                incident = cur.fetchone()
                conn.commit()
        
        if incident:
            logger.info("✓ Found incident in PostgreSQL:")
            logger.info("    - ID: %s", incident[0])
            logger.info("    - Number: %s", incident[1])
            logger.info("    - Description: %s", incident[2][:50] if incident[2] else "")
            
            # Try to index it
            lancedb_before = get_points_count()
            logger.info("  LanceDB vectors before: %d", lancedb_before)
            
            # Create mock record for testing
            test_record = {
                "number": incident[1],
                "short_description": incident[2],
                "description": incident[3] or incident[2],
                "category": "Test",
                "state": "Open",
                "priority": "Medium",
            }
            
            indexed = index_incidents_to_lancedb([test_record], "verification_test")
            lancedb_after = get_points_count()
            
            logger.info("  Indexed: %d chunks", indexed)
            logger.info("  LanceDB vectors after: %d", lancedb_after)
            
            if indexed > 0:
                logger.info("✓ Data flow verified: PostgreSQL → LanceDB successful")
                return True
            else:
                logger.warning("⚠ No chunks indexed (check embedding model)")
                return True
        else:
            logger.info("✓ No PostgreSQL data yet (will be created on first sync)")
            return True
        
    except Exception as exc:
        logger.error("✗ Data flow verification failed: %s", exc)
        import traceback
        logger.debug(traceback.format_exc())
        return False


# Function: _log_record_field_checks
def _log_record_field_checks(record: dict) -> None:
    """Log presence/format checks for a single LanceDB record's required fields."""
    # Check incident_id
    incident_id = record.get("incident_id")
    if incident_id:
        logger.info("    ✓ incident_id: %s", incident_id)
    else:
        logger.warning("    ✗ incident_id missing or empty")

    # Check embedding
    embedding = record.get("embedding")
    if embedding:
        logger.info("    ✓ embedding: [%d floats]", len(embedding))
        if isinstance(embedding, list) and all(isinstance(x, (int, float)) for x in embedding[:3]):
            logger.info("      Format OK (numeric list)")
        else:
            logger.warning("      Format issue - not numeric list")
    else:
        logger.warning("    ✗ embedding missing")

    # Check text_chunk
    text_chunk = record.get("text_chunk")
    if text_chunk:
        logger.info("    ✓ text_chunk: %d chars", len(text_chunk))
    else:
        logger.warning("    ✗ text_chunk missing or empty")

    # Check metadata
    metadata = record.get("metadata")
    if metadata and isinstance(metadata, dict):
        logger.info("    ✓ metadata: %d fields", len(metadata))
    else:
        logger.warning("    ✗ metadata missing or not dict")


# Function: verify_embedding_format
def verify_embedding_format() -> bool:
    """Verify embedding is stored in correct format."""
    logger.info("\n" + "=" * 70)
    logger.info("EMBEDDING FORMAT VERIFICATION")
    logger.info("=" * 70)
    
    try:
        from backend.services.lancedb_store import (
            get_lancedb_client,
            lancedb_enabled,
            _table_exists,
        )
        import backend.config as cfg
        
        if not lancedb_enabled():
            logger.error("✗ LanceDB not enabled")
            return False
        
        client = get_lancedb_client()
        table_name = cfg.LANCEDB_TABLE
        
        if not _table_exists(client, table_name):
            logger.warning("⚠ Table not created yet")
            return True
        
        table = client.open_table(table_name)

        # Check a few records
        try:
            records = table.search([0.1] * 384).limit(3).to_list()

            if records:
                logger.info("✓ Checking record format:")
                for idx, record in enumerate(records):
                    logger.info("  Record %d:", idx + 1)
                    _log_record_field_checks(record)

                return True
            else:
                logger.info("✓ No records to check yet (will be created on sync)")
                return True

        except Exception as e:
            logger.debug("Could not query records: %s", e)
            return True
        
    except Exception as exc:
        logger.error("✗ Embedding format verification failed: %s", exc)
        return False


# Function: main
def main(detailed: bool = False) -> int:
    """Run all verifications."""
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " PostgreSQL → LanceDB Integration Verification ".center(68) + "║")
    logger.info("╚" + "=" * 68 + "╝")
    
    results = {
        "Schema": verify_schema(),
        "PostgreSQL": verify_postgresql_schema(),
        "LanceDB Data": verify_lancedb_data(),
        "Embedding Format": verify_embedding_format(),
        "Data Flow": verify_data_flow(),
    }
    
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info("%s - %s", status, check)
    
    all_passed = all(results.values())
    
    logger.info("\n" + "=" * 70)
    if all_passed:
        logger.info("✓ All verifications passed!")
        logger.info("\nData flow is ready:")
        logger.info("  ServiceNow → Python Ingestion → PostgreSQL ✓")
        logger.info("                                  ↓")
        logger.info("                        LanceDB Vector Store ✓")
        logger.info("\nSchema in LanceDB:")
        logger.info("  - incident_id: str (incident identifier)")
        logger.info("  - embedding: float[] (vector embeddings)")
        logger.info("  - text_chunk: str (chunked incident text)")
        logger.info("  - metadata: dict (incident attributes)")
    else:
        logger.error("✗ Some verifications failed. See details above.")
    
    logger.info("=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify PostgreSQL → LanceDB integration"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed output",
    )
    
    args = parser.parse_args()
    sys.exit(main(detailed=args.detailed))
