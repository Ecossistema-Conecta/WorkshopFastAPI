from importlib import import_module
from pathlib import Path


def auto_import_entities() -> None:
    src_dir = Path(__file__).parent.parent.parent

    for entities_dir in src_dir.glob('*/infra/entities'):
        if entities_dir.is_dir():
            parts = entities_dir.parts[entities_dir.parts.index('src') :]
            module_path = '.'.join(parts)

            try:
                import_module(module_path)
                print(f'{module_path} importado')
            except ModuleNotFoundError:
                print(f'Pulando: {module_path} não encontrado.')
