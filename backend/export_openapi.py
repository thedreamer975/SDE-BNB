import json
from pathlib import Path
from app.main import app

docs_dir = Path(__file__).resolve().parent.parent / "docs"
docs_dir.mkdir(parents=True, exist_ok=True)
openapi_path = docs_dir / "openapi.json"

openapi_schema = app.openapi()
with open(openapi_path, "w", encoding="utf-8") as f:
    json.dump(openapi_schema, f, indent=2)

print(f"Exported OpenAPI schema to {openapi_path}")
