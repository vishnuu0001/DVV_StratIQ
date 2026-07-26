# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Fixed Qdrant backfill script that works around postgres connection issues.
# Date: 2025-10-29
# ---------------------------------------------------------------------------
"""Fixed Qdrant backfill script that works around postgres connection issues."""
import sys
import time
import requests
import psycopg
from typing import Any, Optional

# Configuration
POSTGRES_CONN = "postgresql://postgres:Ganesha%402008@localhost:5432/postgres"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "ki_incidents"
BATCH_SIZE = 500
MAX_ROWS = 350000  # Set to 0 for all rows

# Function: parse_vector_text
def parse_vector_text(vec_text: str) -> list[float]:
    """Parse postgres vector text format '[0.1,0.2,...]' to list."""
    if not vec_text:
        return []
    cleaned = vec_text.strip().strip('[]')
    if not cleaned:
        return []
    try:
        return [float(x.strip()) for x in cleaned.split(',')]
    except Exception:
        return []

# Function: _ensure_qdrant_collection
def _ensure_qdrant_collection() -> bool:
    """Step 1: Check/create collection. Returns True on success."""
    print("1. Checking Qdrant collection...")
    try:
        resp = requests.get(f"{QDRANT_URL}/collections/{COLLECTION_NAME}")
        if resp.status_code == 200:
            coll_data = resp.json()["result"]
            print(f"   Existing collection: {coll_data['points_count']} points")

            # Delete and recreate to start fresh
            print("   Deleting existing collection...")
            requests.delete(f"{QDRANT_URL}/collections/{COLLECTION_NAME}")
            time.sleep(1)

        # Create collection
        create_payload = {
            "vectors": {
                "size": 768,
                "distance": "Cosine"
            }
        }
        resp = requests.put(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}",
            json=create_payload
        )
        if resp.status_code in (200, 201):
            print("   Collection created successfully\n")
            return True

        print(f"   ERROR creating collection: {resp.status_code} - {resp.text}")
        return False

    except Exception as e:
        print(f"   ERROR: {e}\n")
        return False


# Function: _connect_postgres
def _connect_postgres() -> Optional[Any]:
    """Step 2: Connect to postgres with simple connection (not pooled)."""
    print("2. Connecting to PostgreSQL...")
    try:
        conn = psycopg.connect(POSTGRES_CONN, autocommit=True)
        print("   Connected\n")
        return conn
    except Exception as e:
        print(f"   ERROR: {e}\n")
        return None


# Function: _count_total_rows
def _count_total_rows(conn) -> Optional[int]:
    """Step 3: Count total rows."""
    print("3. Counting rows...")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM vector_chunks WHERE collection_name = 'kg_support'")
            total_rows = cur.fetchone()[0]
        print(f"   Total rows in postgres: {total_rows:,}\n")
        return total_rows
    except Exception as e:
        print(f"   ERROR: {e}\n")
        conn.close()
        return None


# Function: _build_points_from_rows
def _build_points_from_rows(rows) -> tuple:
    """Build Qdrant points for a batch of postgres rows. Returns (points, processed, skipped)."""
    points = []
    processed = 0
    skipped = 0
    for row in rows:
        row_id = str(row[0])
        document = str(row[1] or "")
        metadata = row[2] or {}
        vector = parse_vector_text(row[3])

        processed += 1

        if not vector or len(vector) != 768:
            skipped += 1
            continue

        # Build payload
        payload = {
            "ticket_id": metadata.get("incident_number", row_id),
            "source_type": metadata.get("type", "servicenow_incident"),
            "short_description": metadata.get("short_description", ""),
            "description_chunk": document,
            "category": metadata.get("category", ""),
            "state": metadata.get("state", ""),
            "group": metadata.get("assignment_group", ""),
            "source_name": metadata.get("source", "pgvector_backfill"),
            "chunk_index": metadata.get("chunk_index", 0),
        }

        points.append({
            "id": row_id,
            "vector": vector,
            "payload": payload
        })
    return points, processed, skipped


# Function: _upsert_qdrant_points
def _upsert_qdrant_points(points: list, offset: int, inserted: int, total_rows: int) -> Optional[int]:
    """Upsert a batch of points via HTTP. Returns the new inserted count, or None to signal a stop."""
    if not points:
        return inserted

    upsert_payload = {"points": points}
    resp = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points",
        json=upsert_payload,
        headers={"Content-Type": "application/json"}
    )

    if resp.status_code == 200:
        inserted += len(points)
        print(f"   Batch {offset // BATCH_SIZE + 1}: Inserted {len(points)} points | Total: {inserted:,}/{total_rows:,} ({100*inserted/total_rows:.1f}%)")
        return inserted

    print(f"   ERROR upserting batch: {resp.status_code} - {resp.text[:200]}")
    return None


# Function: _run_backfill_batches
def _fetch_batch_rows(conn, offset: int, processed: int) -> list:
    limit = BATCH_SIZE
    if MAX_ROWS:
        limit = min(limit, MAX_ROWS - processed)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, document, metadata_json, embedding::text
            FROM vector_chunks
            WHERE collection_name = 'kg_support'
            ORDER BY created_at ASC
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )
        return cur.fetchall()


# Function: _print_backfill_progress
def _print_backfill_progress(offset: int, inserted: int, total_rows: int, start_time: float) -> None:
    # Progress update every 10 batches
    if (offset // BATCH_SIZE) % 10 != 0:
        return
    elapsed = time.time() - start_time
    rate = inserted / elapsed if elapsed > 0 else 0
    eta_seconds = (total_rows - inserted) / rate if rate > 0 else 0
    print(f"   Progress: {inserted:,} points in {elapsed:.1f}s ({rate:.0f} pts/s) | ETA: {eta_seconds/60:.1f} min")


# Function: _run_backfill_batches
def _run_backfill_batches(conn, total_rows: int) -> tuple:
    """Step 4: Backfill in batches. Returns (processed, inserted, skipped)."""
    print("4. Starting backfill...")
    start_time = time.time()
    processed = 0
    inserted = 0
    skipped = 0
    offset = 0

    try:
        while True:
            if MAX_ROWS and processed >= MAX_ROWS:
                break

            rows = _fetch_batch_rows(conn, offset, processed)
            if not rows:
                break

            batch_points, batch_processed, batch_skipped = _build_points_from_rows(rows)
            processed += batch_processed
            skipped += batch_skipped

            new_inserted = _upsert_qdrant_points(batch_points, offset, inserted, total_rows)
            if new_inserted is None:
                break
            inserted = new_inserted

            offset += len(rows)
            _print_backfill_progress(offset, inserted, total_rows, start_time)

    except Exception as e:
        print(f"\n   ERROR during backfill: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

    # Step 5: Summary
    elapsed = time.time() - start_time
    print("\n5. Backfill complete!")
    print(f"   Processed: {processed:,} rows")
    print(f"   Inserted: {inserted:,} points")
    print(f"   Skipped: {skipped:,} (invalid vectors)")
    print(f"   Time: {elapsed:.1f}s ({inserted/elapsed:.0f} pts/s)")

    return processed, inserted, skipped


# Function: _verify_qdrant_backfill
def _verify_qdrant_backfill() -> None:
    """Step 6: Verify."""
    print("\n6. Verifying...")
    try:
        resp = requests.get(f"{QDRANT_URL}/collections/{COLLECTION_NAME}")
        if resp.status_code == 200:
            coll_data = resp.json()["result"]
            print(f"   Collection points: {coll_data['points_count']:,}")
            print(f"   Indexed vectors: {coll_data['indexed_vectors_count']:,}")

            # Check sample point
            scroll_resp = requests.post(
                f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/scroll",
                json={"limit": 1, "with_payload": True, "with_vectors": False}
            )
            if scroll_resp.status_code == 200:
                points = scroll_resp.json()["result"]["points"]
                if points and points[0].get("payload"):
                    payload_keys = list(points[0]["payload"].keys())
                    print(f"   Sample payload keys: {payload_keys}")
                    if "description_chunk" in points[0]["payload"]:
                        chunk = points[0]["payload"]["description_chunk"]
                        print(f"   Sample text: {chunk[:100]}...")
                        print("\n✅ SUCCESS: Payloads are correctly stored!")
                    else:
                        print("\n❌ WARNING: description_chunk missing from payload")
                else:
                    print("\n❌ WARNING: Sample point has empty payload")
    except Exception as e:
        print(f"   Verification error: {e}")


# Function: backfill_qdrant
def backfill_qdrant():
    """Backfill Qdrant from postgres using direct HTTP API."""
    print("=== QDRANT BACKFILL (FIXED VERSION) ===\n")

    if not _ensure_qdrant_collection():
        return

    conn = _connect_postgres()
    if conn is None:
        return

    total_rows = _count_total_rows(conn)
    if total_rows is None:
        return

    _run_backfill_batches(conn, total_rows)

    _verify_qdrant_backfill()

    print("\n=== BACKFILL COMPLETE ===")
    print("Next steps:")
    print("1. Update .env: VECTOR_BACKEND=qdrant")
    print("2. Restart backend")
    print("3. Test query: 'database connection timeout error'")

if __name__ == "__main__":
    backfill_qdrant()
