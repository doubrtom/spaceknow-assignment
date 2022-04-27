"""Module with SpaceKnowClient to communicate with SpaceKnow API."""
import logging
from typing import Optional

import requests

from .api import auth_api, user_api


logger = logging.getLogger(__name__)


class SpaceKnowClient:
    """API client to communicate with SpaceKnow API.

    It is wrapping all communication details like credentials, headers,
    managing request errors, ...
    """

    def __init__(self):
        self.auth_id_token: Optional[str] = None
        self.number_of_queries: int = 0
        self.headers = {
            "Content-Type": "application/json",
        }
        # Init API classes
        self.auth_api = auth_api.AuthApi(self)
        self.user_api = user_api.UserApi(self)

    def set_auth_token(self, id_token: str):
        """Save auth id_token and add auth header."""
        self.auth_id_token = id_token
        self.headers["Authorization"] = f"Bearer {id_token}"

    def send_post_query(self, url: str, json_data: Optional[dict] = None):
        """Send POST query."""
        response = requests.post(url, json=json_data, headers=self.headers)
        self.number_of_queries += 1
        if not response.ok:
            logger.error(
                "Unable to get response for URL=%s, reason: %s",
                url,
                response.json(),
            )
            response.raise_for_status()
        return response.json()
