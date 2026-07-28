import json
from services.build_runner import toolchain_status
from api.server import target_stacks
import asyncio

status = toolchain_status()
keys = ["dotnet", "dart", "flutter", "swift", "jenkinsfile", "yaml_parser"]
print("TOOLS")
for key in keys:
    info = status["tools"].get(key, {})
    print(f"{key}: ready={info.get('ready')} path={info.get('path')}")

catalog = asyncio.run(target_stacks())
wanted = ["flutter_dotnet", "dart_server", "swift_vapor", "jenkins_pipeline", "github_actions_workflow"]
by_id = {s["id"]: s for s in catalog["stacks"]}
print("\nSTACKS")
for stack_id in wanted:
    s = by_id.get(stack_id)
    if not s:
        print(f"{stack_id}: MISSING")
        continue
    print(
        f"{stack_id}: available={s.get('available')} project_ready={s.get('project_ready')} full_generation={s.get('full_generation')} blocked={s.get('blocked_reason')}"
    )

with open("tmp_check_modernization_tools.json", "w", encoding="utf-8") as f:
    json.dump({"tools": status["tools"], "stacks": {k: by_id.get(k) for k in wanted}}, f, indent=2)
print("\nwritten tmp_check_modernization_tools.json")
