"""SpaceKnow Auth API."""
from ..types import Credentials, AuthTokenData
from .. import settings


class AuthApi:
    """SpaceKnow Auth API."""

    BASE_URL = "https://spaceknow.auth0.com"

    def __init__(self, api_client):
        self.api_client = api_client

    def get_auth_data(self, credentials: Credentials) -> AuthTokenData:
        """Send credentials to auth server and return auth data."""
        url = f"{self.BASE_URL}/oauth/ro"
        json_data = {
            "client_id": settings.SPACEKNOW_CLIENT_ID,
            "connection": "Username-Password-Authentication",
            "grant_type": "password",
            "scope": "openid",
            **credentials,
        }
        return self.api_client.send_post_query(url, json_data)
