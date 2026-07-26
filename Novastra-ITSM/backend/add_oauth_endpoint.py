#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Add OAuth providers endpoint to auth.py
# Date: 2026-04-07
# ---------------------------------------------------------------------------
"""Add OAuth providers endpoint to auth.py"""
import re

with open('api/auth.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position to insert after the /me endpoint
pattern = r'(@router\.get\("/me"\)\s+async def get_me\(current_user: dict = Depends\(get_current_user\)\):\s+return _user_public\(current_user\))'
match = re.search(pattern, content, re.DOTALL)

if match:
    insert_pos = match.end()
    
    new_endpoint = '''


@router.get("/oauth/providers")
async def get_oauth_providers():
    """List available OAuth providers and their configuration status."""
    return {
        "providers": [
            {
                "id": "github",
                "name": "GitHub",
                "enabled": bool(cfg.GITHUB_CLIENT_ID),
                "icon": "github",
            },
            {
                "id": "google",
                "name": "Google",
                "enabled": bool(cfg.GOOGLE_CLIENT_ID),
                "icon": "google",
            },
        ]
    }'''
    
    new_content = content[:insert_pos] + new_endpoint + content[insert_pos:]
    
    with open('api/auth.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('✓ OAuth providers endpoint added successfully')
else:
    print('✗ Pattern not found - please manually add the endpoint')
