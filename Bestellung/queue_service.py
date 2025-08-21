from __future__ import annotations

from collections import deque
from typing import Deque, List, Optional

from .models import Bestellung
from .repository import BestellungsRepository


class BestellungsQueue:
    def __init__(self, repo: BestellungsRepository) -> None:
        self._repo = repo
        initial = self._repo.load()
        self.queue: Deque[Bestellung] = deque(initial)

    def bestellung_hinzufuegen(self, bestellung: Bestellung) -> None:
        self.queue.append(bestellung)
        self._repo.save(list(self.queue))

    def bestellung_abarbeiten(self) -> Optional[Bestellung]:
        if not self.queue:
            return None
        bearbeitete_bestellung = self.queue.popleft()
        self._repo.save(list(self.queue))
        return bearbeitete_bestellung

    def aktuelle_bestellungen(self) -> List[Bestellung]:
        return list(self.queue)


