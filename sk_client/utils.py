"""Utils for sk_client project."""
import os
import json
import math

from .types import Credentials, ExtentData, FeatureCollectionData
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


def pretty_format_json(json_dict: dict) -> str:
    """Pretty format json data into str."""
    return json.dumps(json_dict, indent=4, sort_keys=True)


def pretty_print_json(json_dict: dict) -> None:
    """Pretty print json data into stdout."""
    print(pretty_format_json(json_dict))


def load_detection_tile_data(
    z: int, x: int, y: int, scene_id: str
) -> FeatureCollectionData:
    """Save detection tile data (JSON) into file.

    Data are saved into "result" folder.
    """
    with open(
        f"result/{scene_id}/detections-{z}-{x}-{y}.geojson", "r", encoding="utf-8"
    ) as file:
        return json.load(file)


def save_detection_tile_data(
    scene_id: str, detection_tile_data: dict, z: int, x: int, y: int
):
    """Save detection tile data (JSON) into file.

    Data are saved into "result" folder.
    Each analysis data are in folder named by scene_id.
    """
    data_dir = f"result/{scene_id}"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with open(
        f"result/{scene_id}/detections-{z}-{x}-{y}.geojson", "w", encoding="utf-8"
    ) as file:
        json.dump(detection_tile_data, file)


def save_imagery_tile_data(scene_id: str, imagery_tile_data, z: int, x: int, y: int):
    """Save imagery tile data (PNG) into file.

    Data are saved into "result" folder.
    Each analysis data are in folder named by scene_id.
    """
    data_dir = f"result/{scene_id}"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with open(f"result/{scene_id}/imagery-{z}-{x}-{y}.png", "wb") as file:
        file.write(imagery_tile_data)


def convert_coordinates(longitude, latitude, zoom_level, mod_to_tile: bool = False):
    """Convert geographic coordinates.

    Convert longitude and latitude into x, y coordinates.
    For conversion, we use Web Mercator projection.
    See: https://en.wikipedia.org/wiki/Web_Mercator_projection

    :param longitude: Longitude in degrees
    :param latitude: Latitude in degrees
    :param zoom_level: Zoom level in map
    :param mod_to_tile: If final x/y coordinates modulo by 256,
        i.e. get position inside of tile 256x256.
    """
    long = math.radians(longitude)
    lat = math.radians(latitude)
    x = math.floor((256 / (2 * math.pi)) * (2**zoom_level) * (long + math.pi))
    y = math.floor(
        (256 / (2 * math.pi))
        * (2**zoom_level)
        * (math.pi - math.log(math.tan((math.pi / 4) + (lat / 2))))
    )
    if mod_to_tile:
        return x % 256, y % 256
    return x, y
