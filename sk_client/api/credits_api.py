"""SpaceKnow Credits API."""
from typing import List

from ..types import ExtentData, AllocatedAreaData


class CreditsApi:
    """SpaceKnow Credits API."""

    BASE_URL = "https://api.spaceknow.com/credits"

    def __init__(self, api_client):
        self.api_client = api_client

    def get_remaining_credit(self) -> float:
        """Get user remaining credit."""
        url = f"{self.BASE_URL}/get-remaining-credit"
        data = self.api_client.send_post_query(url)
        return data["remainingCredit"]

    def allocate_area(
        self, scene_ids: List[str], geojson: ExtentData
    ) -> AllocatedAreaData:
        """Allocate an area and time range."""
        url = f"{self.BASE_URL}/area/allocate-geojson"
        json_data = {"geojson": geojson, "sceneIds": scene_ids}
        return self.api_client.send_post_query(url, json_data)

    def check_allocated_area(
        self, scene_ids: List[str], geojson: ExtentData
    ) -> AllocatedAreaData:
        """Allocate an area and time range."""
        url = f"{self.BASE_URL}/area/check-geojson"
        json_data = {"geojson": geojson, "sceneIds": scene_ids}
        return self.api_client.send_post_query(url, json_data)
