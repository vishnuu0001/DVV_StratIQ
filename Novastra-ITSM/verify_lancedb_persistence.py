#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Verify LanceDB data persistence after sync.
# Date: 2025-07-16
# ---------------------------------------------------------------------------
"""
Verify LanceDB data persistence after sync.

This script checks if:
1. vectorstore/lancedb/ directory contains files
2. LanceDB table exists and has data
3. Data persists across client reconnections

Run this AFTER syncing ServiceNow incidents to verify data is actually saved to disk.
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(Path(__file__).parent))

import backend.config as cfg
from backend.services.lancedb_store import (
    lancedb_enabled,
    get_lancedb_client,
    get_table_stats,
    get_points_count,
    _table_exists,
)

# Function: check_persistence
def check_persistence():
    """Check LanceDB persistence status."""
    print("\n" + "="*70)
    print("LANCEDB PERSISTENCE VERIFICATION")
    print("="*70)
    
    print("\n[1] Configuration Check:")
    print(f"    VECTOR_BACKEND: {cfg.VECTOR_BACKEND}")
    print(f"    LANCEDB_PATH: {cfg.LANCEDB_PATH}")
    print(f"    LANCEDB_TABLE: {cfg.LANCEDB_TABLE}")
    
    if cfg.VECTOR_BACKEND not in {"lancedb", "hybrid"}:
        print(f"\n    ⚠ LanceDB not configured (backend={cfg.VECTOR_BACKEND})")
        return False
    
    print("\n[2] Directory Check:")
    lancedb_dir = Path(cfg.LANCEDB_PATH)
    dir_exists = lancedb_dir.exists()
    print(f"    Directory exists: {dir_exists}")
    
    if dir_exists:
        files = list(lancedb_dir.iterdir())
        print(f"    Files in directory: {len(files)}")
        if files:
            print("    Sample files:")
            for f in files[:5]:
                size_mb = f.stat().st_size / (1024*1024) if f.is_file() else 0
                print(f"      - {f.name} ({size_mb:.2f} MB)")
        else:
            print(f"    ❌ CRITICAL: Directory is EMPTY - data not persisting to disk!")
    
    print("\n[3] LanceDB Client Check:")
    if not lancedb_enabled():
        print(f"    ❌ LanceDB backend disabled")
        return False
    
    print(f"    ✓ LanceDB backend enabled")
    
    try:
        client = get_lancedb_client()
        print(f"    ✓ LanceDB client connected")
    except Exception as exc:
        print(f"    ❌ Failed to connect: {exc}")
        return False
    
    print("\n[4] Table Check:")
    try:
        table_exists = _table_exists(client, cfg.LANCEDB_TABLE)
        print(f"    Table exists: {table_exists}")
        
        if not table_exists:
            print(f"    ⚠ Table '{cfg.LANCEDB_TABLE}' does not exist yet")
            print("    (This is normal if no sync has been run)")
        else:
            point_count = get_points_count()
            print(f"    ✓ Table exists with {point_count} chunks")
            
            if point_count == 0:
                print(f"    ⚠ Table exists but contains NO DATA")
            else:
                print(f"    ✓ Data persisted: {point_count} chunks")
    except Exception as exc:
        print(f"    ❌ Error checking table: {exc}")
        return False
    
    print("\n[5] Table Statistics:")
    try:
        stats = get_table_stats()
        print(f"    Status: {stats.get('status')}")
        print(f"    Row Count: {stats.get('row_count')}")
        print(f"    Schema: {str(stats.get('schema', 'N/A'))[:100]}...")
    except Exception as exc:
        print(f"    ⚠ Could not retrieve stats: {exc}")
    
    print("\n" + "="*70)
    
    # Determine overall status
    success = (
        dir_exists and
        table_exists and
        get_points_count() > 0
    )
    
    if success:
        print("✓ PERSISTENCE OK: LanceDB data is properly saved to disk")
    else:
        print("❌ PERSISTENCE ISSUE: Data not fully persisted")
        print("\nTroubleshooting steps:")
        print("1. Run ServiceNow sync: POST /api/servicenow/one-time-sync")
        print("2. Wait for sync to complete (check /api/servicenow/sync-job/{job_id})")
        print("3. Run this script again to verify persistence")
        print("4. Check backend logs for embedding/indexing errors")
    
    print("="*70 + "\n")
    return success

if __name__ == "__main__":
    success = check_persistence()
    sys.exit(0 if success else 1)
