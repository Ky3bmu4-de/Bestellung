from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import List

from .models import Bestellung


class BestellungsRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> List[Bestellung]:
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
        result: List[Bestellung] = []
        if isinstance(raw, list):
            for item in raw:
                try:
                    result.append(Bestellung.from_dict(item))
                except Exception:
                    # Skip invalid entries
                    continue
        return result

    def save(self, bestellungen: List[Bestellung]) -> None:
        data = [b.to_dict() for b in bestellungen]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.path.parent), prefix=self.path.name + ".", text=True
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.path)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass


