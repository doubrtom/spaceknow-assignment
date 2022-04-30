"""Utils for sk_client project."""
import os
import json

from .types import Credentials, ExtentData
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


def load_geojson_data(file_name: str) -> ExtentData:
    """Load GeoJSON data from data sub-folder.

    :param file_name: File name of GeoJSON file without extension
    :return: Loaded GeoJSON file
    """
    with open(f"data/{file_name}.geojson", "r", encoding="utf-8") as file:
        return json.load(file)


def load_analysis_settings(file_name: str) -> dict:
    """Load analysis settings saved in JSON files.

    :param file_name: File name of analysis setting file without extension
    :return: Loaded settings
    """
    with open(f"analysis_settings/{file_name}.json", "r", encoding="utf-8") as file:
        return json.load(file)


def pretty_print_json(json_dict: dict) -> None:
    """Pretty print json data into stdout."""
    print(json.dumps(json_dict, indent=4, sort_keys=True))


def save_detection_tile_data(detection_tile_data: dict, z: int, x: int, y: int):
    """Save detection tile data (JSON) into file.

    Data are saved into "result" folder.
    """
    with open(f"result/detections-{z}-{x}-{y}.geojson", "w", encoding="utf-8") as file:
        json.dump(detection_tile_data, file)


def save_imagery_tile_data(imagery_tile_data, z: int, x: int, y: int):
    """Save imagery tile data (PNG) into file.

    Data are saved into "result" folder.
    """
    with open(f"result/imagery-{z}-{x}-{y}.png", "wb") as file:
        file.write(imagery_tile_data)
