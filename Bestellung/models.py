from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Bestellung:
    tisch_nummer: int
    getraenke_bestellung: Dict[str, int]

    def __repr__(self) -> str:
        if not self.getraenke_bestellung:
            return f"Tisch {self.tisch_nummer}: <leer>"
        parts = ", ".join(
            f"{drink}: {anzahl}" for drink, anzahl in sorted(self.getraenke_bestellung.items())
        )
        return f"Tisch {self.tisch_nummer}: {parts}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tisch_nummer": self.tisch_nummer,
            "getraenke_bestellung": self.getraenke_bestellung,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Bestellung":
        return Bestellung(
            int(data["tisch_nummer"]),
            {str(k): int(v) for k, v in dict(data["getraenke_bestellung"]).items()},
        )


