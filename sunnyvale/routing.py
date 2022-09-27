import googlemaps

from sunnyvale.datatypes import TravelTime, Location
from sunnyvale.api.google_maps import distance_matrix


class Router:
    def __init__(self, client: googlemaps.Client):
        self.client = client

    def get_single_duration(
            self, origin: Location, dest: Location
    ) -> TravelTime:
        travel_times = self.get_matrix_duration([origin], dest)
        return travel_times[origin]

    def get_matrix_duration(
            self, origins: list[Location], dest: Location,
    ) -> dict[Location, TravelTime]:
        # Rate limiting
        assert len(origins) <= 25

        api_result: distance_matrix.Result = self.client.distance_matrix(
            origins, [dest]
        )

        rows = api_result["rows"]

        travel_times: dict[Location, TravelTime] = {}
        for origin, row in zip(origins, rows):
            [element] = row["elements"]

            travel_times[origin] = TravelTime.from_api_element(element)

        return travel_times
