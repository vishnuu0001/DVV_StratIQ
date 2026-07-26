# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — diagnose_rag (diagnose_rag.py)
# Date: 2026-03-22
# ---------------------------------------------------------------------------
import sys
sys.path.insert(0, '.')

from backend.rag.vectorstore import similarity_search, fetch_solution_chunks, keyword_search
from backend.rag.pipeline import _annotate_solutions, _extract_solution_text

question = "When the data is replicating from MDG to MABAS. The replication message failed due to error during data replication from MDG to MABAS system."

print("=== VECTOR SIMILARITY RESULTS ===")
results = similarity_search(question, provider='ollama')
for doc, score in results:
    src = doc.metadata.get("source", "?")
    print(f"  score={score:.2f}  src={src}")
    print(f"  preview: {doc.page_content[:250].replace(chr(10), ' | ')}")
    print()

print("=== KEYWORD SEARCH RESULTS ===")
kw = keyword_search(question, provider='ollama')
for doc, score in kw:
    src = doc.metadata.get("source", "?")
    print(f"  kw_score={score}  src={src}")
    print(f"  preview: {doc.page_content[:250].replace(chr(10), ' | ')}")
    print()

print("=== SOLUTION-CHUNK AUGMENTATION ===")
all_results = list(results)
seen = {d.page_content for d, _ in results}
for d, s in kw:
    if d.page_content not in seen:
        all_results.append((d, s))
        seen.add(d.page_content)

matched_sources = list({d.metadata.get("source","") for d, _ in all_results})
sol_chunks = fetch_solution_chunks(matched_sources, provider='ollama')
print(f"  Found {len(sol_chunks)} solution chunks from {matched_sources}")
for sc in sol_chunks:
    print(f"  -> {sc.page_content[:200].replace(chr(10), ' | ')}")
    print()

for sc in sol_chunks:
    if sc.page_content not in seen:
        all_results.append((sc, 1.0))
        seen.add(sc.page_content)

print("=== REGEX EXTRACTION (all_results) ===")
extracted = _extract_solution_text(all_results)
print(extracted if extracted else "EMPTY - regex found NO solution text")

print()
print("=== ANNOTATED TOP CHUNK ===")
if all_results:
    print(_annotate_solutions(all_results[0][0].page_content))
