from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from sunnyvale.api.google_maps import distance_matrix

Address: TypeAlias = str
LatLong: TypeAlias = tuple[float, float]
Location: TypeAlias = LatLong | Address


@dataclass(frozen=True)
class TravelTime:
    meters: int
    seconds: int  # seconds

    @classmethod
    def from_api_element(cls, element: distance_matrix.Element):
        return cls(
            meters=element["distance"]["value"],
            seconds=element["duration"]["value"],
        )
