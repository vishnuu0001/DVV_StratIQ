from pathlib import Path
from services.build_runner import run_build
from services.artifact_store import load_output_artifact

root = Path(r'E:\stratIQ_VA-main\stratIQ_VA-main\Modernization\data\projects\APP-001\outputs\v001\CreateAFullStackSolutionForABank')
# Build an output dict matching the generated project relative layout.
output = {}
for path in root.rglob('*'):
    if path.is_file():
        try:
            output[path.relative_to(root).as_posix()] = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            pass
result = run_build(output, 'csharp', Path(r'E:\stratIQ_VA-main\stratIQ_VA-main\Modernization\tmp_build_runner_repro_out'))
print('passed=', result.passed)
print('checker=', result.checker)
print('remaining_errors=', result.remaining_errors)
print('raw_output=', result.raw_output[-8000:] if result.raw_output else '')
