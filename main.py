from __future__ import annotations

from pathlib import Path

import googlemaps

from sunnyvale import data
from sunnyvale.routing import Router

DESTINATION_MAP = {
    # Main surface parking lot south of Historic Murphy will serve as a common
    # destination for routing
    "murphy": (37.375404, -122.030125),

    # Because the Google Maps API has no clean way of getting travel times while
    # avoiding a street, we instead force the routing to take one of the two other
    # overpasses (Mathilda and Fair Oaks)
    "mathilda": (37.379009, -122.033777),
    "fair-oaks": (37.374664, -122.020863),
}

# These addresses were collected from
# https://sunnyvale-geohub-cityofsunnyvale.hub.arcgis.com/datasets/0975c44d98b645cfb04f3daae9d1e6da_0/explore
# and then pruned to fit the Area of Interest
ADDRESS_DATA = Path("data/input-address.csv")


def main() -> None:
    gmaps_client = googlemaps.Client(
        key=Path("google-maps-api-key.txt").read_text().strip()
    )
    router = Router(gmaps_client)

    # Collect travel times from each property to each destination
    for destination in DESTINATION_MAP:
        collect_data(router, destination)

    # Because we navigated to the overpasses instead of our end-goal parking lot, we
    # need to adjust each travel by the overpass->parking lot baseline
    for location in {"mathilda", "fair-oaks"}:
        adjust_baselines(router, location)

    # Take the short of each route. Properties closer to Mathilda will inherently have
    # shorter routes going over Mathilda than Fair Oaks, and vice versa
    shorter = calculate_shorter("mathilda", "fair-oaks")

    original = data.DistanceTable.from_file(Path("data/murphy-data.csv"))

    # Calculate how much longer the route will be if the crossing is left open to
    # vehicles
    calculate_delta(shorter, original)


def adjust_baselines(router: Router, location: str) -> None:
    data_file = Path(f"data/{location}-data.csv")

    baseline = router.get_single_duration(
        DESTINATION_MAP[location],
        DESTINATION_MAP["murphy"],
    )

    prior_distances = data.DistanceTable.from_file(data_file)
    adjusted_distances = prior_distances.adjust(baseline)

    adjusted_distances.save(Path(f"data/{location}-adjusted.csv"))


def calculate_delta(rerouted: data.DistanceTable, original: data.DistanceTable) -> None:
    delta = rerouted.subtract(original)
    delta.save("data/delta.csv")


def calculate_shorter(location1: str, location2: str, /) -> data.DistanceTable:
    adjusted_file1 = Path(f"data/{location1}-adjusted.csv")
    adjusted_file2 = Path(f"data/{location2}-adjusted.csv")

    distances1 = data.DistanceTable.from_file(adjusted_file1)
    distances2 = data.DistanceTable.from_file(adjusted_file2)

    distances_shorter = distances1.min(distances2)
    distances_shorter.save(Path("data/shorter.csv"))

    return distances_shorter


def collect_data(router: Router, destination: str) -> None:
    addresses = data.AddressTable.from_file(ADDRESS_DATA)

    data_file = Path(f"data/{destination}-data.csv")

    prior_distances = data.DistanceTable.from_file(data_file)

    distances = addresses.get_distance_via(
        prior_distances,
        lambda a: router.get_matrix_duration(a, DESTINATION_MAP[destination])
    )

    distances.save(data_file)


if __name__ == '__main__':
    main()
