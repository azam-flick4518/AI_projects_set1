from __future__ import annotations

from pathlib import Path

from code_review_coach.models import SourceFile


class RepoScanner:
    def scan(self, repo_path: str | Path) -> list[SourceFile]:
        root = Path(repo_path)
        files = []
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            files.append(SourceFile(path=str(path), text=path.read_text(encoding="utf-8")))
        return files
