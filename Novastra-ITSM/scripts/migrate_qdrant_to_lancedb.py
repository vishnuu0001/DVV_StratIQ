#!/usr/bin/env python
# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Migration script: Qdrant → LanceDB
# Date: 2026-02-05
# ---------------------------------------------------------------------------
"""
Migration script: Qdrant → LanceDB

Migrates all vector embeddings and metadata from Qdrant to LanceDB.
Usage: python migrate_qdrant_to_lancedb.py [--batch-size 100] [--verbose]
"""
import argparse
import json
import logging
import sys
from pathlib import Path

import backend.config as cfg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# Function: _convert_qdrant_point
def _convert_qdrant_point(point) -> dict | None:
    """Convert one Qdrant point to LanceDB's point format, or None if it has no vector."""
    point_id = str(point.id)
    vector = list(point.vector) if hasattr(point, 'vector') else point.get('vector', [])
    payload = dict(point.payload) if hasattr(point, 'payload') else point.get('payload', {})

    if not vector:
        return None

    return {
        "id": point_id,
        "vector": [float(x) for x in vector],
        "payload": payload,
    }


# Function: _convert_qdrant_points
def _convert_qdrant_points(points) -> tuple[list, int]:
    """Convert a batch of Qdrant points to LanceDB format. Returns (converted_points, failed_count)."""
    lancedb_points = []
    failed = 0
    for point in points:
        try:
            converted = _convert_qdrant_point(point)
        except Exception as e:
            logger.warning("Failed to convert point %s: %s", point.id, e)
            failed += 1
            continue
        if converted is None:
            failed += 1
            continue
        lancedb_points.append(converted)
    return lancedb_points, failed


# Function: migrate_qdrant_to_lancedb
def migrate_qdrant_to_lancedb(batch_size: int = 100, verbose: bool = False) -> dict:
    """
    Migrate all vectors from Qdrant to LanceDB.
    
    Returns:
        Dictionary with migration statistics
    """
    try:
        from backend.services.qdrant_store import qdrant_enabled, get_qdrant_client, get_points_count
        from backend.services.lancedb_store import lancedb_enabled, upsert_points as lancedb_upsert
    except ImportError as exc:
        logger.error("Failed to import storage modules: %s", exc)
        return {"success": False, "error": "Import failed", "migrated": 0}

    if not qdrant_enabled():
        logger.warning("Qdrant is not enabled. No migration needed.")
        return {"success": True, "message": "Qdrant not enabled", "migrated": 0}

    if not lancedb_enabled():
        logger.error("LanceDB is not enabled. Cannot proceed with migration.")
        return {"success": False, "error": "LanceDB not enabled", "migrated": 0}

    try:
        client = get_qdrant_client()
        collection_name = cfg.QDRANT_COLLECTION
        total_points = get_points_count()
        
        logger.info("Starting migration: %s points from Qdrant collection '%s' to LanceDB", total_points, collection_name)
        
        if total_points == 0:
            logger.info("No points to migrate.")
            return {"success": True, "migrated": 0, "message": "No points found"}

        migrated = 0
        failed = 0
        offset = 0

        while offset < total_points:
            try:
                # Scroll through Qdrant points
                points, _ = client.scroll(
                    collection_name=collection_name,
                    limit=batch_size,
                    offset=offset,
                    with_payload=True,
                    with_vectors=True,
                )
                
                if not points:
                    break

                # Convert Qdrant points to LanceDB format
                lancedb_points, batch_failed = _convert_qdrant_points(points)
                failed += batch_failed

                # Upsert to LanceDB
                if lancedb_points:
                    inserted = lancedb_upsert(lancedb_points)
                    migrated += inserted
                    
                    if verbose:
                        logger.debug("Migrated batch of %d points (total: %d)", len(lancedb_points), migrated)

                offset += batch_size

            except Exception as exc:
                logger.error("Error processing batch at offset %d: %s", offset, exc)
                failed += batch_size

        logger.info(
            "Migration complete: %d points migrated, %d failed",
            migrated,
            failed,
        )
        
        return {
            "success": True,
            "migrated": migrated,
            "failed": failed,
            "total": total_points,
        }

    except Exception as exc:
        logger.error("Migration failed: %s", exc)
        return {"success": False, "error": str(exc), "migrated": 0}


# Function: verify_migration
def verify_migration() -> dict:
    """Verify migration was successful."""
    try:
        from backend.services.qdrant_store import qdrant_enabled, get_points_count as qdrant_count
        from backend.services.lancedb_store import lancedb_enabled, get_points_count as lancedb_count
    except ImportError:
        return {"error": "Import failed"}

    qdrant_total = qdrant_count() if qdrant_enabled() else 0
    lancedb_total = lancedb_count() if lancedb_enabled() else 0

    return {
        "qdrant_points": qdrant_total,
        "lancedb_points": lancedb_total,
        "match": qdrant_total == lancedb_total,
    }


# Function: main
def main():
    parser = argparse.ArgumentParser(
        description="Migrate vectors from Qdrant to LanceDB"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for migration (default: 100)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing migration, don't perform it",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 70)
    logger.info("Qdrant → LanceDB Migration Tool")
    logger.info("=" * 70)

    if args.verify_only:
        logger.info("Verifying migration status...")
        result = verify_migration()
        logger.info("Migration Status: %s", json.dumps(result, indent=2))
        return 0

    # Perform migration
    result = migrate_qdrant_to_lancedb(
        batch_size=args.batch_size,
        verbose=args.verbose,
    )
    
    logger.info("Migration Result: %s", json.dumps(result, indent=2))

    if result["success"]:
        logger.info("Verifying...")
        verify = verify_migration()
        logger.info("Verification: %s", json.dumps(verify, indent=2))
        
        if verify.get("match"):
            logger.info("✓ Migration successful and verified!")
            return 0
        else:
            logger.warning("✗ Point count mismatch after migration")
            return 1
    else:
        logger.error("✗ Migration failed: %s", result.get("error"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
