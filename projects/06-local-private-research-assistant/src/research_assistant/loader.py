from __future__ import annotations

from pathlib import Path

from research_assistant.models import Chunk, Document


class DocumentLoader:
    def load_directory(self, directory: str | Path) -> list[Document]:
        root = Path(directory)
        documents = []
        for path in sorted(root.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = self._title(text) or path.stem.replace("-", " ").title()
            documents.append(Document(id=path.stem, path=str(path), title=title, text=text))
        return documents

    def chunk(self, document: Document) -> list[Chunk]:
        sections: list[tuple[str, list[str]]] = [(document.title, [])]
        for line in document.text.splitlines():
            if line.startswith("## "):
                sections.append((line.replace("## ", "", 1).strip(), []))
            else:
                sections[-1][1].append(line)

        chunks = []
        for index, (title, lines) in enumerate(sections, start=1):
            text = "\n".join(lines).strip()
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

    def _title(self, text: str) -> str | None:
        for line in text.splitlines():
            if line.startswith("# "):
                return line.replace("# ", "", 1).strip()
        return None
