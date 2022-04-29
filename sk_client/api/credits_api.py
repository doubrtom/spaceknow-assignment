"""SpaceKnow Credits API."""


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
