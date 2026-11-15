"""Synthetic repository fixture. Never a real customer repository."""

from __future__ import annotations

from pathlib import Path

CANARY = "CANARY-7f3a-not-a-real-secret"
FILES = {
    "app.py": 'import os\n\nAPI_TOKEN = "' + CANARY + '"\n\n\ndef run() -> str:\n    return os.environ.get("MODE", "safe")\n',
    "requirements.txt": "requests\n",
    "README.md": "# synthetic repo\n\nFixture for static review. No real credentials.\n",
}


def build_repo(root: Path) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for name, content in FILES.items():
        (root / name).write_text(content, encoding="utf-8")
    return root
