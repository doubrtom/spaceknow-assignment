"""SpaceKnow Tasking API."""


class TaskingApi:
    """SpaceKnow Tasking API."""

    BASE_URL = "https://api.spaceknow.com/tasking"

    def __init__(self, api_client):
        self.api_client = api_client

    def get_status(self, pipeline_id: str) -> float:
        """Get pipeline status."""
        url = f"{self.BASE_URL}/get-status"
        json_data = {"pipelineId": pipeline_id}
        return self.api_client.send_post_query(url, json_data)
