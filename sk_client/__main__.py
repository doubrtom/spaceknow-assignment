"""Run main task for sk_client project."""
from pathlib import Path

from .api_client import SpaceKnowClient
from . import utils


def set_auth_token_to_api_client(space_know_client: SpaceKnowClient):
    """Set auth token to SpaceKnowClient.

    It tries to load auth token from file, so we do not spam AUTH server.
    If not found, get auth token from auth server and save it to file.
    """
    auth_token_file = Path("auth_token.txt")

    if auth_token_file.is_file():
        with auth_token_file.open("r", encoding="utf-8") as file:
            id_token = file.read().strip()
        space_know_client.set_auth_token(id_token)
    else:
        auth_data = space_know_client.auth_api.get_auth_data(utils.load_credentials())
        with auth_token_file.open("w", encoding="utf-8") as file:
            file.write(auth_data["id_token"])
        space_know_client.set_auth_token(auth_data["id_token"])


api_client = SpaceKnowClient()
set_auth_token_to_api_client(api_client)

# User info
# user_info = api_client.user_api.get_user_info()
# utils.pretty_print_json(user_info)

# Remaining credit
credit = api_client.credits_api.get_remaining_credit()
print(credit)
