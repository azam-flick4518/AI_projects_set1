from __future__ import annotations

import re
from collections import defaultdict

from kg_rag.models import Document, Entity, GraphFact, Relationship


FIELD_PATTERN = re.compile(r"^(System|Owner|Depends-On|Policy|Data|SLO):\s*(.+)$", re.IGNORECASE)


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


class KnowledgeGraph:
    def __init__(self) -> None:
        self.entities: dict[str, Entity] = {}
        self.relationships: list[Relationship] = []
        self._adjacency: dict[str, list[Relationship]] = defaultdict(list)

    def add_entity(self, name: str, kind: str) -> Entity:
        entity_id = normalize(f"{kind}-{name}")
        entity = self.entities.get(entity_id)
        if entity is None:
            entity = Entity(id=entity_id, name=name, kind=kind)
            self.entities[entity_id] = entity
        return entity

    def add_relationship(
        self,
        source: Entity,
        target: Entity,
        kind: str,
        evidence: str,
        document_id: str,
    ) -> None:
        relationship = Relationship(
            source=source.id,
            target=target.id,
            kind=kind,
            evidence=evidence,
            document_id=document_id,
        )
        self.relationships.append(relationship)
        self._adjacency[source.id].append(relationship)
        self._adjacency[target.id].append(relationship)

    def facts_for_terms(self, terms: set[str], limit: int = 8) -> list[GraphFact]:
        facts: list[GraphFact] = []
        for relationship in self.relationships:
            source = self.entities[relationship.source]
            target = self.entities[relationship.target]
            haystack = " ".join([source.name, target.name, relationship.kind, relationship.evidence]).lower()
            if any(term in haystack for term in terms):
                facts.append(
                    GraphFact(
                        source=source,
                        relationship=relationship.kind,
                        target=target,
                        evidence=relationship.evidence,
                        document_id=relationship.document_id,
                    )
                )
        return facts[:limit]

    def related_entity_names(self, terms: set[str]) -> set[str]:
        names = set()
        for fact in self.facts_for_terms(terms):
            names.add(fact.source.name.lower())
            names.add(fact.target.name.lower())
        return names


class KnowledgeGraphBuilder:
    def build(self, documents: list[Document]) -> KnowledgeGraph:
        graph = KnowledgeGraph()
        for document in documents:
            fields = self._fields(document.text)
            system_name = fields.get("system", document.title)
            system = graph.add_entity(system_name, "system")

            for owner in self._split_values(fields.get("owner", "")):
                graph.add_relationship(
                    source=system,
                    target=graph.add_entity(owner, "team"),
                    kind="owned_by",
                    evidence=f"Owner: {owner}",
                    document_id=document.id,
                )

            for dependency in self._split_values(fields.get("depends-on", "")):
                graph.add_relationship(
                    source=system,
                    target=graph.add_entity(dependency, "system"),
                    kind="depends_on",
                    evidence=f"Depends-On: {dependency}",
                    document_id=document.id,
                )

            for policy in self._split_values(fields.get("policy", "")):
                graph.add_relationship(
                    source=system,
                    target=graph.add_entity(policy, "policy"),
                    kind="governed_by",
                    evidence=f"Policy: {policy}",
                    document_id=document.id,
                )

            for data_type in self._split_values(fields.get("data", "")):
                graph.add_relationship(
                    source=system,
                    target=graph.add_entity(data_type, "data"),
                    kind="handles",
                    evidence=f"Data: {data_type}",
                    document_id=document.id,
                )
        return graph

    def _fields(self, text: str) -> dict[str, str]:
        fields = {}
        for line in text.splitlines():
            match = FIELD_PATTERN.match(line.strip())
            if match:
                fields[match.group(1).lower()] = match.group(2).strip()
        return fields

    def _split_values(self, value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]
