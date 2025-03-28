from pathlib import Path
import mkdocs_gen_files

list_of_files = ["database.py", "main.py"]

src_root = Path("app")
for path in src_root.glob("**/*.py"):
    if path.name in list_of_files:
        continue
    
    doc_path = Path("Docs", path.relative_to(src_root)).with_suffix(".md")

    with mkdocs_gen_files.open(doc_path, "w") as f:
        ident = ".".join(path.with_suffix("").parts)
        print("::: " + ident, file=f)