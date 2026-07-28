from pathlib import Path
root = Path(r'E:\stratIQ_VA-main\stratIQ_VA-main\Modernization\data\projects\APP-001\outputs\v001\CreateAFullStackSolutionForABank\frontend')
for rel in ['tsconfig.json','src/index.html','src/main.ts','src/styles.css','src/environments/environment.ts','src/app/app-routing.module.ts','src/app/app.component.ts']:
    path = root / rel
    print(rel, path.exists())
