"""SpaceKnow Kraken API.

The API interfaces imagery and analyses through tiled web map interface.
"""
from typing import List

from ..types import ExtentData, KrakenAnalysisResultData


class KrakenApi:
    """SpaceKnow Kraken API."""

    BASE_URL = "https://api.spaceknow.com/kraken"

    def __init__(self, api_client):
        self.api_client = api_client

    def release_initiate(
        self,
        map_type: str,
        scene_ids: List[str],
        geojson: ExtentData,
    ):
        """Start analysis over selected area."""
        url = f"{self.BASE_URL}/release/initiate"
        json_data = {
            "mapType": map_type,
            "sceneIds": scene_ids,
            "extent": geojson,
        }
        return self.api_client.send_post_query(url, json_data)

    def release_retrieve(self, pipeline_id: str) -> KrakenAnalysisResultData:
        """Retrieve analysis data over selected area."""
        url = f"{self.BASE_URL}/release/retrieve"
        json_data = {"pipelineId": pipeline_id}
        return self.api_client.send_post_query(url, json_data)

    def get_tile_data(self, map_id: str, z: int, x: int, y: int, file_name: str):
        """Download one tile data for kraken run."""
        url = f"{self.BASE_URL}/grid/{map_id}/-/{z}/{x}/{y}/{file_name}"
        response = self.api_client.send_get_query(url)
        if file_name in ["truecolor.png"]:
            return response.content
        else:
            return response.json()
