"""Module for processing of loaded imagery tiles."""
import logging
from os.path import exists as file_exists
from typing import List
from collections import defaultdict

import cv2
import numpy as np

from . import utils


logger = logging.getLogger(__name__)


def __get_image_for_stitching(z, x, y, scene_id):
    """Load image tile for stitching.

    Image is found in this order:
    - enhanced imagery (image with rendered detected items)
    - imagery (imagery from API)
    - empty img (white color) in resolution 256x256 px
    """
    path = f"result/{scene_id}/enhanced-imagery-{z}-{x}-{y}.png"
    if file_exists(path):
        return cv2.imread(path, cv2.IMREAD_UNCHANGED)
    path = f"result/{scene_id}/imagery-{z}-{x}-{y}.png"
    if file_exists(path):
        return cv2.imread(path, cv2.IMREAD_UNCHANGED)
    logger.warning(
        f"Tile for stitching not found, use empty image. "
        f"Tile values: z={z}, x={x}, y={y}."
    )
    return np.zeros((256, 256, 4), dtype=np.uint8)


def stitch_tiles(tiles: List[List[int]], scene_id: str):
    """Stitch all tiles into result image.

    :param tiles: Tiles to process in format [[x, y, z], ...]
    :param scene_id: Scene ID, where tiles data come from
    """
    if len(tiles) == 0:
        return
    rows = defaultdict(list)
    zoom = tiles[0][0]

    for tile in tiles:
        rows[tile[2]].append(tile[1])

    concatenated_row_images = []
    for y in sorted(rows.keys()):
        x_values = sorted(rows[y])
        row_images = [__get_image_for_stitching(zoom, x, y, scene_id) for x in x_values]
        concatenated_row_images.append(cv2.hconcat(row_images))

    result_image = cv2.vconcat(concatenated_row_images)

    cv2.imwrite(f"result/{scene_id}/result.png", result_image)


def render_detected_objects(tiles: List[List[int]], scene_id: str):
    """Render items from detections tiles into imagery tiles.

    :param tiles: Tiles to process in format [[x, y, z], ...]
    :param scene_id: ID of scene, where objects were detected
    """
    for tile in tiles:
        render_detected_objects_into_tile(*tile, scene_id)


def render_detected_objects_into_tile(z, x, y, scene_id):
    """Render detected objects into imagery.

    :param z: Zoom of map
    :param x: X coordinate of tile
    :param y: Y coordinate of tile
    :param scene_id: ID of scene, where objects were detected
    """
    try:
        detection_geojson = utils.load_detection_tile_data(z, x, y, scene_id)
    except FileNotFoundError:
        logger.warning(
            "Detection geojson file not found: "
            f"result/{scene_id}/detections-{z}-{x}-{y}.geojson"
        )
        return
    imagery_path = f"result/{scene_id}/imagery-{z}-{x}-{y}.png"

    if not file_exists(imagery_path):
        logger.warning(
            f"Imagery tile file not found: result/{scene_id}/imagery-{z}-{x}-{y}.png"
        )
        return
    image = cv2.imread(imagery_path, cv2.IMREAD_UNCHANGED)

    is_closed = True
    color = (255, 0, 0, 255)  # color in BGR
    thickness = 2  # in px

    for feature in detection_geojson["features"]:
        points = feature["geometry"]["coordinates"][0]
        points = [utils.convert_coordinates(p[0], p[1], z, True) for p in points]
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        image = cv2.polylines(image, [pts], is_closed, color, thickness)

    cv2.imwrite(f"result/{scene_id}/enhanced-imagery-{z}-{x}-{y}.png", image)
