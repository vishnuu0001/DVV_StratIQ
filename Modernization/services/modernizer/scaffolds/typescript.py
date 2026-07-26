# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/scaffolds (typescript.py)
# Date: 2025-11-01
# ---------------------------------------------------------------------------
from __future__ import annotations

import functools
import hashlib
import json
import logging
import os
import re
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)



# ─── TypeScript / JavaScript component generation ─────────────────────────────
# Function: _gen_ts_component
def _gen_ts_component(output: Dict[str, str], root_ns: str, domain: str, target_stack: str):
    base = f"ModernizedApp/src/components/{domain}"
    fw = "React"
    if "angular" in target_stack.lower():
        fw = "Angular"
    elif "vue" in target_stack.lower():
        fw = "Vue"
    output[f"{base}/{domain}Page.tsx"] = _ts_page_template(domain, fw)
    output[f"{base}/{domain}Service.ts"] = _ts_service(domain)


# Function: _ts_page_template
def _ts_page_template(domain: str, framework: str) -> str:
    if framework == "React":
        return textwrap.dedent(f"""\
            import React, {{ useState, useEffect }} from 'react';
            import {{ {domain}Service }} from './{domain}Service';

            interface {domain}Item {{
              id: number;
              name: string;
              isActive: boolean;
              createdAt: string;
            }}

            export const {domain}Page: React.FC = () => {{
              const [items, setItems] = useState<{domain}Item[]>([]);
              const [loading, setLoading] = useState(true);
              const [error, setError] = useState('');

              useEffect(() => {{
                {domain}Service.getAll()
                  .then(setItems)
                  .catch(e => setError(e.message))
                  .finally(() => setLoading(false));
              }}, []);

              if (loading) return <div className="loading">Loading {domain}...</div>;
              if (error)   return <div className="error">Error: {{error}}</div>;

              return (
                <div className="{domain.lower()}-page">
                  <h1>{domain}</h1>
                  <table>
                    <thead>
                      <tr><th>ID</th><th>Name</th><th>Active</th><th>Created</th></tr>
                    </thead>
                    <tbody>
                      {{items.map(item => (
                        <tr key={{item.id}}>
                          <td>{{item.id}}</td>
                          <td>{{item.name}}</td>
                          <td>{{item.isActive ? '✓' : '✗'}}</td>
                          <td>{{new Date(item.createdAt).toLocaleDateString()}}</td>
                        </tr>
                      ))}}
                    </tbody>
                  </table>
                </div>
              );
            }};

            export default {domain}Page;
        """)
    return f"// {domain}Page component — generated for {framework}\nexport default {{}}"


# Function: _ts_service
def _ts_service(domain: str) -> str:
    return textwrap.dedent(f"""\
        const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8080';

        export const {domain}Service = {{
          async getAll() {{
            const res = await fetch(`${{API_BASE}}/api/{domain.lower()}`);
            if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
            return res.json();
          }},
          async getById(id: number) {{
            const res = await fetch(`${{API_BASE}}/api/{domain.lower()}/${{id}}`);
            if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
            return res.json();
          }},
          async create(data: object) {{
            const res = await fetch(`${{API_BASE}}/api/{domain.lower()}`, {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/json' }},
              body: JSON.stringify(data),
            }});
            if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
            return res.json();
          }},
          async delete(id: number) {{
            const res = await fetch(`${{API_BASE}}/api/{domain.lower()}/${{id}}`, {{ method: 'DELETE' }});
            if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
          }},
        }};
    """)


# Function: _npm_root_package
def _npm_root_package(root_ns: str, target_stack: str) -> str:
    import json as _json
    framework = "react" if "react" in target_stack else \
                "angular" if "angular" in target_stack else "vue"
    deps: Dict[str, str] = {}
    dev_deps: Dict[str, str] = {
        "typescript": "^5.3.0",
        "vite": "^5.0.0",
        "@types/node": "^20.0.0",
    }
    if framework == "react":
        deps.update({"react": "^18.2.0", "react-dom": "^18.2.0", "react-router-dom": "^6.0.0"})
        dev_deps.update({"@vitejs/plugin-react": "^4.0.0", "@types/react": "^18.2.0"})
    elif framework == "angular":
        deps.update({"@angular/core": "^17.0.0", "@angular/common": "^17.0.0",
                     "rxjs": "^7.8.0", "zone.js": "^0.14.0"})
    else:  # vue
        deps.update({"vue": "^3.3.0", "vue-router": "^4.0.0", "pinia": "^2.0.0"})
        dev_deps["@vitejs/plugin-vue"] = "^4.0.0"
    return _json.dumps({
        "name": root_ns.lower().replace(" ", "-") + "-modernized",
        "version": "1.0.0",
        "scripts": {"dev": "vite", "build": "tsc && vite build", "preview": "vite preview"},
        "dependencies": deps,
        "devDependencies": dev_deps,
    }, indent=2)


# Function: _tsconfig
def _tsconfig() -> str:
    import json as _json
    return _json.dumps({
        "compilerOptions": {
            "target": "ES2022", "module": "ESNext", "moduleResolution": "bundler",
            "jsx": "react-jsx", "strict": True, "noUnusedLocals": True,
            "noUnusedParameters": True, "noFallthroughCasesInSwitch": True
        },
        "include": ["src"], "references": [{"path": "./tsconfig.node.json"}]
    }, indent=2)


# Function: _vite_config
def _vite_config() -> str:
    return textwrap.dedent("""\
        import { defineConfig } from 'vite'
        import react from '@vitejs/plugin-react'

        export default defineConfig({
          plugins: [react()],
          server: {
            proxy: {
              '/api': { target: 'http://localhost:8080', changeOrigin: true }
            }
          }
        })
    """)
