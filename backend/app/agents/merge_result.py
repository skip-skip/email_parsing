from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class MergeResult:
    ticket_id: uuid.UUID
    updated_fields: list[str] = field(default_factory=list)
    previous_values: dict[str, object] = field(default_factory=dict)
    new_values: dict[str, object] = field(default_factory=dict)
