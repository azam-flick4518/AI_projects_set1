from __future__ import annotations

from pathlib import Path

from kg_rag.models import Chunk, Document


class DocumentLoader:
    def load_directory(self, directory: str | Path) -> list[Document]:
        root = Path(directory)
        documents = []
        for path in sorted(root.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = self._title_from_markdown(text) or path.stem.replace("-", " ").title()
            documents.append(
                Document(
                    id=path.stem,
                    path=str(path),
                    title=title,
                    text=text,
                )
            )
        return documents

    def chunk(self, document: Document) -> list[Chunk]:
        sections = []
        current_title = document.title
        current_lines: list[str] = []

        for line in document.text.splitlines():
            if line.startswith("## "):
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines).strip()))
                    current_lines = []
                current_title = line.replace("## ", "", 1).strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_title, "\n".join(current_lines).strip()))

        chunks = []
        for index, (title, text) in enumerate(sections, start=1):
            if text:
                chunks.append(
                    Chunk(
                        id=f"{document.id}#{index}",
                        document_id=document.id,
                        source_path=document.path,
                        title=title,
                        text=text,
                    )
                )
        return chunks

    def _title_from_markdown(self, text: str) -> str | None:
        for line in text.splitlines():
            if line.startswith("# "):
                return line.replace("# ", "", 1).strip()
        return None
