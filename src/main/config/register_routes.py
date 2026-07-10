import importlib
from pathlib import Path
from fastapi import FastAPI, APIRouter


def register_routes(app: FastAPI, routes_dir: str = "src/main/routes"):
    """
    Importa dinamicamente todos os arquivos de rotas dentro de src/main/routes
    e os registra na instância do FastAPI.
    """
    base_path = Path(routes_dir)

    if not base_path.exists():
        raise FileNotFoundError(f"O diretório de rotas '{routes_dir}' não foi encontrado. Verifique o caminho.")

    package_prefix = routes_dir.replace('/', '.').strip('.')

    for file in base_path.rglob('*.py'):
        if file.name.startswith('__'):
            continue

        relative_path = file.relative_to(base_path)
        module_parts = list(relative_path.with_suffix('').parts)
        module_name = f"{package_prefix}.{'.'.join(module_parts)}"

        try:
            module = importlib.import_module(module_name)

            if hasattr(module, 'router'):
                router = getattr(module, 'router')

                if isinstance(router, APIRouter):
                    app.include_router(router)
                    print(f'✅ Rota registrada: {module_name}')

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f'❌ Falha ao carregar o módulo {module_name}: {e}')
