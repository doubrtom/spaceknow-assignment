"""SpaceKnow User API."""


class UserApi:
    """SpaceKnow User API."""

    BASE_URL = "https://api.spaceknow.com/user"

    def __init__(self, api_client):
        self.api_client = api_client

    def get_user_info(self) -> dict:
        """Get user info."""
        url = f"{self.BASE_URL}/info"
        return self.api_client.send_post_query(url)
