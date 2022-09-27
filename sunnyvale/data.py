from __future__ import annotations

import csv
import math
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd

from sunnyvale.datatypes import TravelTime, LatLong


class DistanceTable:
    INDEX = ["lat", "long"]
    COLUMNS = ["lat", "long", "distance", "duration"]

    def __init__(self, data: pd.DataFrame):
        self.data = data

    @classmethod
    def from_file(cls, path: Path) -> DistanceTable:
        if not path.exists():
            return cls.from_empty()
        else:
            dataframe = pd.read_csv(
                filepath_or_buffer=path,
                index_col=["lat", "long"],
                header=0,
                dtype={
                    "lat": float,
                    "long": float,
                    "distance": int,
                    "duration": int,
                }
            )

        return cls(dataframe)

    @classmethod
    def from_empty(cls) -> DistanceTable:
        dataframe = pd.DataFrame(columns=cls.COLUMNS)
        dataframe = dataframe.set_index(cls.INDEX)

        return cls(dataframe)

    def adjust(self, adjustment: TravelTime) -> DistanceTable:
        adjusted = self.data.add({
            "distance": adjustment.meters,
            "duration": adjustment.seconds,
        })

        return DistanceTable(adjusted)

    def min(self, other: DistanceTable) -> DistanceTable:
        shorter = (
            pd.concat([self.data, other.data]).groupby(level=tuple(self.INDEX)).min()
        )
        return DistanceTable(shorter)

    def save(self, path: Path) -> None:
        self.data.to_csv(
            path_or_buf=path,
            quoting=csv.QUOTE_NONNUMERIC,
        )

    def subtract(self, other: DistanceTable):
        return DistanceTable(self.data.subtract(other.data))


class AddressTable:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    @classmethod
    def from_file(cls, path: Path) -> AddressTable:
        dataframe = pd.read_csv(
            filepath_or_buffer=path,
            index_col=None,
            header=0,
            dtype={
                "lat": float,
                "long": float,
            }
        )

        return cls(dataframe)

    def get_distance_via(
            self,
            prior_output: DistanceTable,
            func: Callable[[list[LatLong]], dict[LatLong, TravelTime]],
    ) -> DistanceTable:

        output = DistanceTable.from_empty()

        num_sections = math.ceil(self.data.shape[0] / 25)
        for i, chunk in enumerate(np.array_split(self.data, num_sections)):
            print(f"calculating {i}/{num_sections}")

            to_query: list[LatLong] = []
            for _, (lat, long) in chunk.iterrows():
                try:
                    prior = prior_output.data.loc[(lat, long), ["distance", "duration"]]
                except KeyError:
                    to_query.append((lat, long))
                else:
                    output.data.loc[(lat, long), ["distance", "duration"]] = prior

            if not to_query:
                continue

            results = func(to_query)

            for (lat, long), travel_time in results.items():
                dist = travel_time.meters
                dur = travel_time.seconds
                output.data.loc[(lat, long), ["distance", "duration"]] = dist, dur

        return output
