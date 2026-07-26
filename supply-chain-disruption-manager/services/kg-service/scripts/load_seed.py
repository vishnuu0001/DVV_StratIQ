#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: CLI script to load seed data into a running KG service.
# Date: 2026-07-07
# ---------------------------------------------------------------------------
"""CLI script to load seed data into a running KG service.

Usage::

    python scripts/load_seed.py --url http://localhost:8001 --api-key kg-dev-key-change-in-prod

Or via environment variables::

    KG_BASE_URL=http://localhost:8001 KG_API_KEY=kg-dev-key-change-in-prod python scripts/load_seed.py
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

import httpx


# Function: main
async def main(base_url: str, api_key: str) -> None:
    print(f"Loading seed data into KG service at {base_url} ...")
    async with httpx.AsyncClient(
        base_url=base_url,
        headers={"X-API-Key": api_key},
        timeout=120.0,
    ) as client:
        # Check health first
        try:
            health = await client.get("/health")
            health.raise_for_status()
            h = health.json()
            print(f"Neo4j connected. Current nodes: {h.get('node_count')}, edges: {h.get('edge_count')}")
        except Exception as exc:
            print(f"ERROR: Could not reach KG service: {exc}", file=sys.stderr)
            sys.exit(1)

        # Trigger seed
        try:
            resp = await client.post("/seed")
            resp.raise_for_status()
            data = resp.json()
            stats = data.get("stats", {})
            print(f"Seed complete. Nodes written: {stats.get('nodes')}, Edges written: {stats.get('edges')}")
        except httpx.HTTPStatusError as exc:
            print(f"ERROR: Seed failed ({exc.response.status_code}): {exc.response.text}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load seed data into KG service")
    parser.add_argument("--url", default=os.environ.get("KG_BASE_URL", "http://localhost:8001"), help="KG service base URL")
    parser.add_argument("--api-key", default=os.environ.get("KG_API_KEY", "kg-dev-key-change-in-prod"), help="API key")
    args = parser.parse_args()
    asyncio.run(main(args.url, args.api_key))
