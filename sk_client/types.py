"""
Types defined for sk_client project.

See python typing module for more info.
"""
from typing import TypedDict


class Credentials(TypedDict):
    """Credentials for SpaceKnow API."""

    username: str
    password: str


class AuthTokenData(TypedDict):
    """Response from Auth API, when getting JWT token."""

    id_token: str
    access_token: str
    token_type: str
