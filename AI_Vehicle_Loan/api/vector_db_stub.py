# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AI_Vehicle_Loan — api (vector_db_stub.py)
# Date: 2025-10-28
# ---------------------------------------------------------------------------
import random

try:
    from .data_service import VEHICLE_DATABASE
except ImportError:
    from data_service import VEHICLE_DATABASE


class VectorDBStub:
    """Simulated Semantic Search across the Vehicle Database."""

    # Function: search_vehicles
    def search_vehicles(self, query_text, top_k=3):
        query_tokens = set(query_text.lower().split())
        results = []

        for v in VEHICLE_DATABASE:
            search_blob = f"{v['make']} {v['model']} {v['type']} {' '.join(v['tags'])}".lower()
            overlap = len(query_tokens.intersection(set(search_blob.split())))

            if overlap > 0:
                # Fake a similarity score (0.0 to 1.0)
                score = 0.75 + (overlap / len(query_tokens)) * 0.2 + random.uniform(-0.02, 0.02)
                results.append({**v, "similarity_score": round(min(score, 0.99), 4)})

        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]


vector_db = VectorDBStub()