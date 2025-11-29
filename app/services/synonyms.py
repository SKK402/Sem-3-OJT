from collections import defaultdict
from typing import Iterable, Set


class SynonymService:
    def __init__(self, mapping: dict[str, set[str]] | None = None) -> None:
        self.mapping = defaultdict(set)
        if mapping:
            for term, synonyms in mapping.items():
                normalized = term.lower()
                self.mapping[normalized].update({s.lower() for s in synonyms})

    def expand(self, term: str) -> set[str]:
        normalized = term.lower()
        expanded: Set[str] = {normalized}
        expanded.update(self.mapping.get(normalized, set()))
        return expanded

    def load_bulk(self, entries: Iterable[tuple[str, Iterable[str]]]) -> None:
        for base, synonyms in entries:
            self.mapping[base.lower()].update({s.lower() for s in synonyms})

