"""SpaceKnow Ragnar API (Search Imagery)."""
from ..types import InitiatedPipelineData, SearchImageryInitiateData


class ImageryApi:
    """SpaceKnow Ragnar API (Search Imagery)."""

    BASE_URL = "https://api.spaceknow.com/imagery"

    def __init__(self, api_client):
        self.api_client = api_client

    def search_initiate(
        self, search_data: SearchImageryInitiateData
    ) -> InitiatedPipelineData:
        """Start async search for imagery."""
        url = f"{self.BASE_URL}/search/initiate"
        return self.api_client.send_post_query(url, search_data)
