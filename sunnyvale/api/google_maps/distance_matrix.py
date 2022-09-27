from __future__ import annotations

from typing import TypedDict, Any


class Result(TypedDict):
    origin_addresses: list[Any]
    destination_addresses: list[Any]
    rows: list[Row]
    status: str


class Row(TypedDict):
    elements: list[Element]


class Element(TypedDict):
    distance: Distance
    duration: Duration


class Distance(TypedDict):
    text: str
    value: int


class Duration(TypedDict):
    text: str
    value: int
