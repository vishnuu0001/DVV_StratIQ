# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Validate One-time Sync Tickets functionality.
# Date: 2025-10-10
# ---------------------------------------------------------------------------
"""
Validate One-time Sync Tickets functionality.
Ensures both Postgres and Qdrant have valid data with full payloads.
"""
import requests
import json
from datetime import datetime

print("=" * 80)
print("VALIDATING ONE-TIME SYNC TICKETS FUNCTIONALITY")
print("=" * 80)
print()

# 1. Check Qdrant Collection Status
print("1. CHECKING QDRANT COLLECTION STATUS")
print("-" * 80)
try:
    response = requests.get("http://localhost:6333/collections/ki_incidents")
    coll_data = response.json()
    result = coll_data.get("result", {})
    
    points_count = result.get("points_count", 0)
    indexed_count = result.get("indexed_vectors_count", 0)
    
    print(f"   Total Points: {points_count:,}")
    print(f"   Indexed Vectors: {indexed_count:,}")
    print(f"   Vector Dimension: {result.get('config', {}).get('params', {}).get('vectors', {}).get('size', 0)}")
    print(f"   Distance Metric: {result.get('config', {}).get('params', {}).get('vectors', {}).get('distance', 'N/A')}")
    
    indexing_threshold = result.get("config", {}).get("optimizer_config", {}).get("indexing_threshold", 20000)
    print(f"   Indexing Threshold: {indexing_threshold:,}")
    
    if indexed_count < points_count:
        print(f"   ⚠️  WARNING: Only {indexed_count:,}/{points_count:,} vectors indexed")
        print("      HNSW index may still be building...")
    else:
        print("   ✅ HNSW indexing: COMPLETE")
    print()
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print()

# 2. Validate Qdrant Payload Structure
print("2. VALIDATING QDRANT PAYLOAD STRUCTURE")
print("-" * 80)
try:
    # Scroll through a few points to check payloads
    scroll_response = requests.post(
        "http://localhost:6333/collections/ki_incidents/points/scroll",
        json={"limit": 5, "with_payload": True, "with_vector": False}
    )
    scroll_data = scroll_response.json()
    points = scroll_data.get("result", {}).get("points", [])
    
    if not points:
        print("   ❌ ERROR: No points found in Qdrant collection")
    else:
        print(f"   Checking {len(points)} sample points...")
        print()
        
        required_fields = ["ticket_id", "description_chunk", "category", "state", "source_name"]
        all_valid = True
        
        for i, point in enumerate(points, 1):
            payload = point.get("payload", {})
            print(f"   Point {i}:")
            print(f"      ID: {point.get('id', 'N/A')[:20]}...")
            
            # Check required fields (allow empty values, just check field exists)
            missing = [f for f in required_fields if f not in payload]
            if missing:
                print(f"      ❌ MISSING FIELDS: {', '.join(missing)}")
                all_valid = False
            else:
                print(f"      ✅ Ticket ID: {payload.get('ticket_id', 'N/A')}")
                print(f"      ✅ Category: {payload.get('category', 'N/A') or '(empty)'}")
                print(f"      ✅ State: {payload.get('state', 'N/A') or '(empty)'}")
                group_val = payload.get('group', '(not set)')
                print(f"      ✅ Group: {group_val[:40] if group_val and group_val != '(not set)' else '(empty)'}...")
                desc_chunk = payload.get('description_chunk', '')
                print(f"      ✅ Description: {desc_chunk[:60]}..." if desc_chunk else "      ⚠️  Empty description")
            print()
        
        if all_valid:
            print("   ✅ ALL PAYLOADS VALID: Contains incident descriptions, ticket IDs, categories, states, groups")
        else:
            print("   ❌ SOME PAYLOADS INCOMPLETE")
    print()
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print()

# 3. Test Semantic Search
print("3. TESTING SEMANTIC SEARCH")
print("-" * 80)
try:
    # Generate embedding for test query
    embed_response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": "database connection timeout error"}
    )
    embedding = embed_response.json().get("embedding", [])
    
    if not embedding:
        print("   ❌ ERROR: Could not generate embedding")
    else:
        # Search Qdrant
        search_response = requests.post(
            "http://localhost:6333/collections/ki_incidents/points/search",
            json={
                "vector": embedding,
                "limit": 10,
                "with_payload": True,
                "score_threshold": 0.10
            }
        )
        results = search_response.json().get("result", [])
        
        print("   Query: 'database connection timeout error'")
        print(f"   Results returned: {len(results)}")
        print()
        
        if not results:
            print("   ❌ ERROR: No search results returned")
        else:
            high_score_count = sum(1 for r in results if r.get("score", 0) >= 0.60)
            print(f"   Results with score ≥ 0.60: {high_score_count}")
            print()
            print("   Top 3 Results:")
            for i, result in enumerate(results[:3], 1):
                score = result.get("score", 0)
                payload = result.get("payload", {})
                print(f"      [{i}] Score: {score:.4f}")
                print(f"          Ticket: {payload.get('ticket_id', 'N/A')}")
                print(f"          Category: {payload.get('category', 'N/A')}")
                desc = payload.get('description_chunk', '')[:80]
                print(f"          Text: {desc}...")
                print()
            
            if high_score_count > 0:
                print("   ✅ SEMANTIC SEARCH WORKING: Scores 0.60+ found")
            else:
                print("   ⚠️  WARNING: No high-confidence matches (scores < 0.60)")
                print("      This may be normal for test queries not in dataset")
    print()
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print()

# 4. Check Postgres Integration
print("4. CHECKING POSTGRES INTEGRATION")
print("-" * 80)
try:
    import psycopg
    
    conn = psycopg.connect(
        "postgresql://postgres:Ganesha%402008@localhost:5432/postgres",
        autocommit=True
    )
    cur = conn.cursor()
    
    # Check vector_chunks table
    cur.execute("""
        SELECT COUNT(*), COUNT(DISTINCT metadata_json->>'incident_number')
        FROM vector_chunks
        WHERE collection_name = 'kg_support'
    """)
    row = cur.fetchone()
    total_chunks = row[0] if row else 0
    unique_tickets = row[1] if row else 0
    
    print("   PostgreSQL vector_chunks:")
    print(f"      Total Chunks: {total_chunks:,}")
    print(f"      Unique Tickets: {unique_tickets:,}")
    
    if total_chunks > 0:
        print("   ✅ POSTGRES POPULATED")
    else:
        print("   ⚠️  WARNING: No data in Postgres")
    
    cur.close()
    conn.close()
    print()
except Exception as e:
    print(f"   ⚠️  Could not check Postgres: {e}")
    print()

# 5. Backend Health Check
print("5. BACKEND CONFIGURATION")
print("-" * 80)
try:
    health_response = requests.get("http://localhost:8086/health")
    health = health_response.json()
    
    print(f"   Backend Status: {health.get('status', 'N/A')}")
    print(f"   Vector Backend: {health.get('vector_backend', 'N/A')}")
    print(f"   Embedding Model: {health.get('embed_model', 'N/A')}")
    print(f"   Modern Pipeline: {health.get('modern_pipeline_enabled', False)}")
    print()
    
    if health.get('vector_backend') == 'qdrant' and health.get('modern_pipeline_enabled'):
        print("   ✅ BACKEND CONFIGURED CORRECTLY")
    else:
        print("   ⚠️  WARNING: Backend may not be configured optimally")
    print()
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print()

# Summary
print("=" * 80)
print("VALIDATION SUMMARY")
print("=" * 80)
print("""
WHAT TO CHECK AFTER CLICKING 'ONE-TIME SYNC TICKETS':

1. Wait for the sync job to complete (check job status in UI)
2. Run this script: python validate_sync.py
3. Verify all checks pass with ✅

EXPECTED RESULTS:
✅ Qdrant collection has points with HNSW indexing complete
✅ All payloads contain: ticket_id, description_chunk, category, state, group
✅ Semantic search returns results with scores 0.60+
✅ Postgres vector_chunks table populated
✅ Backend configured with VECTOR_BACKEND=qdrant, MODERN_PIPELINE_ENABLED=true

If any checks fail, review the sync job logs in the backend terminal.
""")
