"""Utils for sk_client project."""
import os
import json

from .types import Credentials
from .exceptions import ImproperlyConfiguredError


def get_env_variable(var_name) -> str:
    """Load system environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"You have to set {var_name} environment variable."
        raise ImproperlyConfiguredError(error_msg) from KeyError


def load_credentials() -> Credentials:
    """Load credentials from system environment variables.

    Environment variables:
    - SPACEKNOW_USERNAME
    - SPACEKNOW_PASSWORD
    """
    return {
        "username": get_env_variable("SPACEKNOW_USERNAME"),
        "password": get_env_variable("SPACEKNOW_PASSWORD"),
    }


def pretty_print_json(json_dict: dict) -> None:
    """Pretty print json data into stdout."""
    print(json.dumps(json_dict, indent=4, sort_keys=True))
