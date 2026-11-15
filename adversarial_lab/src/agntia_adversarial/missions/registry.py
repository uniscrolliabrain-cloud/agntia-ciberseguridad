"""Versioned mission library loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .validator import validate_mission


class MissionRegistry:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.missions: Dict[str, dict] = {}

    def load(self) -> Dict[str, dict]:
        missions: Dict[str, dict] = {}
        for path in sorted(self.root.glob("*/mission.json")):
            mission = json.loads(path.read_text(encoding="utf-8"))
            validate_mission(mission)
            if mission["id"] in missions:
                raise ValueError(f"duplicate mission id: {mission['id']}")
            missions[mission["id"]] = mission
        self.missions = missions
        return missions

    def get(self, mission_id: str) -> dict:
        if mission_id not in self.missions:
            self.load()
        if mission_id not in self.missions:
            raise KeyError(mission_id)
        return self.missions[mission_id]
