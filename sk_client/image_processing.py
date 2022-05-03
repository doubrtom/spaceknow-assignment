"""Module for processing of loaded imagery tiles."""
import logging
import math
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
    - imagery (imagery from API)
    - empty img (white color) in resolution 256x256 px
    """
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

    # group tiles by rows
    for tile in tiles:
        rows[tile[2]].append(tile[1])

    concatenated_row_images = []
    for y in sorted(rows.keys()):
        x_values = sorted(rows[y])
        row_images = [__get_image_for_stitching(zoom, x, y, scene_id) for x in x_values]
        concatenated_row_images.append(cv2.hconcat(row_images))

    stitched_image = cv2.vconcat(concatenated_row_images)

    cv2.imwrite(f"result/{scene_id}/stitched-imagery.png", stitched_image)


def render_detected_objects(tiles: List[List[int]], selected_zoom: int, scene_id: str):
    """Render items from detections tiles into imagery tiles.

    :param tiles: Tiles from 'cars' analysis to process in format [[z, x, y], ...]
    :param selected_zoom: Zoom of stitched imagery
    :param scene_id: ID of scene, where objects were detected
    """
    stitched_imagery_path = f"result/{scene_id}/stitched-imagery.png"

    if not file_exists(stitched_imagery_path):
        logger.warning(
            "Skipping detected objects rendering. "
            f"Stitched imagery file not found: result/{scene_id}/stitched-imagery.png"
        )
        return
    stitched_imagery = cv2.imread(stitched_imagery_path, cv2.IMREAD_UNCHANGED)

    for tile in tiles:
        stitched_imagery = render_detected_objects_into_imagery(
            stitched_imagery, *tile, selected_zoom, scene_id
        )

    cv2.imwrite(f"result/{scene_id}/result.png", stitched_imagery)


def render_detected_objects_into_imagery(
    stitched_imagery, z, x, y, selected_zoom, scene_id
):  # pylint: disable=R0913
    """Render detected objects into imagery.

    :param stitched_imagery: OpenCV imager with stitched imagery
    :param z: Zoom of 'cars' analysis tiles
    :param x: X coordinate of 'cars' analysis tile
    :param y: Y coordinate of 'cars' analysis tile
    :param selected_zoom: Selected zoom of stitched imagery
    :param scene_id: ID of scene, where objects were detected
    :return: OpenCV stitched imagery with rendered detected objects
        from selected 'cars' analysis tile
    """
    try:
        detection_geojson = utils.load_detection_tile_data(z, x, y, scene_id)
    except FileNotFoundError:
        logger.warning(
            "Detection geojson file not found: "
            f"result/{scene_id}/detections-{z}-{x}-{y}.geojson"
        )
        return stitched_imagery

    fill_color = (0, 255, 0, 255)  # color in BGRA

    for feature in detection_geojson["features"]:
        coordinates = feature["geometry"]["coordinates"][0]
        points = get_coordinates_for_rendering(z, x, y, selected_zoom, coordinates)
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        stitched_imagery = cv2.fillPoly(stitched_imagery, [pts], fill_color)

    return stitched_imagery


def get_coordinates_for_rendering(tile_z, tile_x, tile_y, selected_zoom, points):
    """Convert coordinates for rendering in one tile.

    Convert coordinates and ensure all points are inside tile,
    where we are going to render detected item.

    We are rendering into stitched imagery,
    so we have to re-calculate pixels per tile
    and tile position in grid.

    We got selected_zoom - it is zoom level for stitched imagery tiles,
    and we got tile_z - it is zoom level per 'cars' analysis tile.

    We stitched also 4 tiles on tile_z zoom level,
    so we have to subtract 1 zoom level and recalculate tile x, y coordinates one level zoom out.
    """
    zoom_step = 2 ** (selected_zoom - tile_z + 1)
    pixels_per_tile = 256 * zoom_step
    tile_x = math.floor(tile_x / 2)
    tile_y = math.floor(tile_y / 2)

    x_start = tile_x * pixels_per_tile
    x_end = (tile_x + 1) * pixels_per_tile
    y_start = tile_y * pixels_per_tile
    y_end = (tile_y + 1) * pixels_per_tile
    converted_points = []
    for point in points:
        x, y = utils.convert_coordinates(point[0], point[1], selected_zoom)
        if x < x_start:
            x = x_start
        elif x >= x_end:
            x = x_end - 1
        if y < y_start:
            y = y_start
        elif y >= y_end:
            y = y_end - 1
        x = x - (pixels_per_tile / 2)
        y = y - (pixels_per_tile / 2)
        converted_points.append([x % pixels_per_tile, y % pixels_per_tile])
    return converted_points

