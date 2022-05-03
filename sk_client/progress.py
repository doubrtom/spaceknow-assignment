"""Module to hold steps in analysis progress.

Each step prints info into typer.echo output.
"""
from typing import List, Optional
from pathlib import Path
import logging
import time

import typer

from . import utils, image_processing
from .types import (
    InitiatedPipelineData,
    ImageMetadata,
    PipelineStatusData,
    ExtentData,
    KrakenAnalysisResultData,
)
from .api_client import SpaceKnowClient
from .exceptions import PipelineFailedError
from .data import RunningAnalysesData

logger = logging.getLogger(__name__)


def wait_pipeline(
    api_client: SpaceKnowClient, pipeline_data: InitiatedPipelineData
) -> None:
    """Wait till pipeline is resolved."""
    pipeline_id = pipeline_data["pipelineId"]
    pipeline_status: PipelineStatusData = pipeline_data
    typer.echo(f"... Waiting pipeline with ID: {pipeline_id}. Waiting .", nl=False)
    while True:
        # add new dot for each checking, like "progress bar"
        typer.echo(".", nl=False)

        if pipeline_status["status"] == "RESOLVED":
            typer.echo(".")
            return
        if pipeline_status["status"] == "FAILED":
            typer.echo(f"Pipeline with id={pipeline_id} failed.", err=True)
            raise PipelineFailedError(pipeline_id=pipeline_id)

        time.sleep(pipeline_status["nextTry"])
        pipeline_status = api_client.tasking_api.get_status(pipeline_id)


def load_geojson(geojson_name) -> ExtentData:
    """Load geojson with selected area, raise error on missing file."""
    geojson_path = Path(f"data/{geojson_name}.geojson")
    if not geojson_path.is_file():
        typer.echo(
            f"GeoJSON file does not exist: data/{geojson_name}.geojson", err=True
        )
        raise typer.Exit(1)
    return utils.load_geojson_data(geojson_name)


def search_imagery(
    api_client: SpaceKnowClient, selected_area: ExtentData
) -> InitiatedPipelineData:
    """Search for existing imagery for selected area."""
    typer.echo("\n# Searching for imagery in selected area.")
    search_imagery_data = utils.load_analysis_settings("search_imagery")
    search_imagery_data["extent"] = selected_area
    pipeline_data = api_client.imagery_api.search_initiate(search_imagery_data)
    typer.echo(f"--> Pipeline ID: {pipeline_data['pipelineId']}")
    return pipeline_data


def retrieve_imagery(
    api_client: SpaceKnowClient, pipeline_data: InitiatedPipelineData
) -> List[ImageMetadata]:
    """Retrieve found imagery for selected area."""
    typer.echo("\n# Retrieving imagery found in selected area.")
    return api_client.imagery_api.search_retrieve(pipeline_data["pipelineId"])


def select_imagery(ra_data: RunningAnalysesData) -> Optional[int]:
    """Ask user to select imagery.

    :return: Index of selected imagery or None for all.
    """
    imagery_count = len(ra_data.scenes_list)
    if imagery_count == 0:
        typer.echo("No imagery found for selected area.")
        raise typer.Exit(1)

    typer.echo("\n# Founded imagery:")
    for index, scene_data in enumerate(ra_data.scenes_list):
        scene_title = ra_data.get_scene_title(scene_data["sceneId"])
        typer.echo(f"   {index}) {scene_title}")

    while True:
        selected_index: str = typer.prompt(
            "> Select imagery for analysis, enter index above or 'all' for all imagery"
        )
        if selected_index == "all":
            return None
        if not selected_index.isdigit():
            typer.echo("Invalid index, you have to insert number.")
            continue
        index = int(selected_index)
        if not (0 <= index < imagery_count):  # pylint: disable=C0325
            typer.echo(f"Invalid index, insert number >= 0 and < {imagery_count}.")
            continue
        return index


def allocate_area(
    api_client: SpaceKnowClient, scene_id: str, selected_area: ExtentData
):
    """Allocate selected area."""
    typer.echo("\n# Allocating selected area")
    analysis_data = {"scene_ids": [scene_id], "geojson": selected_area}
    allocated_data = api_client.credits_api.allocate_area(**analysis_data)
    typer.echo(f"--> km2: {allocated_data['km2']}")
    typer.echo(f"--> cost: {allocated_data['cost']}")


def run_kraken_analysis_cars(
    api_client: SpaceKnowClient, scene_id: str, selected_area: ExtentData
) -> InitiatedPipelineData:
    """Release kraken for 'cars'."""
    typer.echo("\n# Run kraken analysis for 'cars'.")
    return api_client.kraken_api.release_initiate(
        "cars",
        [scene_id],
        selected_area,
    )


def retrieve_kraken_analysis_cars(
    api_client: SpaceKnowClient, pipeline_data: InitiatedPipelineData
) -> KrakenAnalysisResultData:
    """Retrieve kraken result for 'cars'."""
    typer.echo("\n# Retrieve kraken analysis for 'cars'.")
    return api_client.kraken_api.release_retrieve(pipeline_data["pipelineId"])


def download_cars_analysis_tiles(
    api_client: SpaceKnowClient, tiles: List[List[int]], map_id: str, scene_id: str
) -> None:
    """Download all 'cars' detection tiles."""
    typer.echo("\n# Downloading kraken detection tiles for 'cars'.")
    typer.echo(f"--> map ID: {map_id}")
    tile_count = len(tiles)
    for tile_index, tile in enumerate(tiles):
        typer.echo(
            f"--> downloading tile ({tile_index + 1}/{tile_count}): "
            f"{tile[0]}, {tile[1]}, {tile[2]}"
        )
        detection_tile_data = api_client.kraken_api.get_tile_data(
            map_id, tile[0], tile[1], tile[2], "detections.geojson"
        )
        if detection_tile_data is None:
            continue
        utils.save_detection_tile_data(
            scene_id, detection_tile_data, tile[0], tile[1], tile[2]
        )


def run_kraken_analysis_imagery(
    api_client: SpaceKnowClient, scene_id: str, selected_area: ExtentData
) -> InitiatedPipelineData:
    """Release kraken for 'imagery'."""
    typer.echo("\n# Run kraken analysis for 'imagery'.")
    return api_client.kraken_api.release_initiate(
        "imagery",
        [scene_id],
        selected_area,
    )


def retrieve_kraken_analysis_imagery(
    api_client: SpaceKnowClient, pipeline_data: InitiatedPipelineData
) -> KrakenAnalysisResultData:
    """Retrieve kraken result for 'cars'."""
    typer.echo("\n# Retrieve kraken analysis for 'imagery'.")
    return api_client.kraken_api.release_retrieve(pipeline_data["pipelineId"])


def download_imagery_analysis_tiles(
    api_client: SpaceKnowClient, tiles: List[List[int]], map_id: str, scene_id: str
) -> None:
    """Download all 'imagery' tiles."""
    typer.echo("\n# Downloading kraken tiles for 'imagery'.")
    typer.echo(f"--> map ID: {map_id}")
    tile_count = len(tiles)
    for tile_index, tile in enumerate(tiles):
        typer.echo(
            f"--> downloading tile ({tile_index + 1}/{tile_count}): "
            f"{tile[0]}, {tile[1]}, {tile[2]}"
        )
        imagery_tile_data = api_client.kraken_api.get_tile_data(
            map_id, tile[0], tile[1], tile[2], "truecolor.png"
        )
        if imagery_tile_data is None:
            continue
        utils.save_imagery_tile_data(
            scene_id, imagery_tile_data, tile[0], tile[1], tile[2]
        )


def render_detected_items_into_imageries(ra_data: RunningAnalysesData) -> None:
    """Render detected items into imagery."""
    for scene_id in ra_data.selected_scenes:
        scene_title = ra_data.get_scene_title(scene_id)
        typer.echo(
            f"# Rendering detected objects into imagery tiles, scene: {scene_title}."
        )
        selected_zoom = ra_data.selected_zoom[scene_id]
        image_processing.render_detected_objects(
            ra_data.cars_analysis_results[scene_id]["tiles"], selected_zoom, scene_id
        )


def stitch_imageries(tiles: List[List[int]], scene_id: str) -> None:
    """Stitch all imageries into final image."""
    typer.echo("\n# Stitching all enhanced imageries into final result.")
    image_processing.stitch_tiles(tiles, scene_id)


def run_analysis_pipelines(api_client: SpaceKnowClient, ra_data: RunningAnalysesData):
    """Run all async pipelines at the same time for all selected scenes."""
    for scene_id in ra_data.selected_scenes:
        allocate_area(api_client, scene_id, ra_data.selected_area)

        pipeline = run_kraken_analysis_cars(api_client, scene_id, ra_data.selected_area)
        ra_data.mapping_pipeline_to_scene_id[pipeline["pipelineId"]] = scene_id
        ra_data.cars_analysis_pipelines.append(pipeline)

        pipeline = run_kraken_analysis_imagery(
            api_client, scene_id, ra_data.selected_area
        )
        ra_data.mapping_pipeline_to_scene_id[pipeline["pipelineId"]] = scene_id
        ra_data.imagery_analysis_pipelines.append(pipeline)


def process_cars_analysis_pipelines(
    api_client: SpaceKnowClient, ra_data: RunningAnalysesData
):
    """Process all pipelines for 'cars' analyses."""
    for pipeline in ra_data.cars_analysis_pipelines:
        scene_id = ra_data.get_scene_id(pipeline)
        try:
            wait_pipeline(api_client, pipeline)
        except PipelineFailedError:
            ra_data.failed_scene_ids.add(scene_id)
            continue
        kraken_result_data = retrieve_kraken_analysis_cars(api_client, pipeline)
        ra_data.cars_analysis_results[scene_id] = kraken_result_data
        download_cars_analysis_tiles(
            api_client,
            kraken_result_data["tiles"],
            kraken_result_data["mapId"],
            scene_id,
        )


def process_imagery_analysis_pipelines(
    api_client: SpaceKnowClient, ra_data: RunningAnalysesData
):
    """Process all pipelines for 'imagery' analyses."""
    for pipeline in ra_data.imagery_analysis_pipelines:
        scene_id = ra_data.get_scene_id(pipeline)
        if ra_data.is_scene_failed(scene_id):
            # Do not process imagery pipeline when 'cars' detection failed
            continue
        try:
            wait_pipeline(api_client, pipeline)
        except PipelineFailedError:
            ra_data.failed_scene_ids.add(scene_id)
            continue
        kraken_result_data = retrieve_kraken_analysis_imagery(api_client, pipeline)
        selected_zoom = select_zoom_level(
            scene_id,
            ra_data,
            kraken_result_data["tiles"][0][0],
            kraken_result_data["maxZoom"],
        )
        zoomed_tiles = utils.zoom_tiles(kraken_result_data["tiles"], selected_zoom)
        ra_data.imagery_analysis_results[scene_id] = kraken_result_data
        ra_data.selected_zoom[scene_id] = selected_zoom
        download_imagery_analysis_tiles(
            api_client,
            zoomed_tiles,
            kraken_result_data["mapId"],
            scene_id,
        )
        stitch_imageries(zoomed_tiles, scene_id)


def select_zoom_level(
    scene_id: str, ra_data: RunningAnalysesData, current_zoom_level, max_zoom_level
) -> int:
    """Allow user to select zoom level for result imagery."""
    scene_title = ra_data.get_scene_title(scene_id)
    while True:
        selected_zoom_str: str = typer.prompt(
            f"> Select zoom level for scene ({scene_title}), "
            f"number from {current_zoom_level} to {max_zoom_level}"
        )
        if not selected_zoom_str.isdigit():
            typer.echo("Invalid zoom level, you have to insert number.")
            continue
        selected_zoom = int(selected_zoom_str)
        if not (
            current_zoom_level <= selected_zoom <= max_zoom_level
        ):  # pylint: disable=C0325
            typer.echo(
                f"Invalid zoom level, "
                f"insert number >= {current_zoom_level} and <= {max_zoom_level}."
            )
            continue
        return selected_zoom


def count_detected_items(ra_data: RunningAnalysesData):
    """Count detected items in imageries for all scenes."""
    for scene_id, cars_analysis_results in ra_data.cars_analysis_results.items():
        for tile in cars_analysis_results["tiles"]:
            detection_geojson = utils.load_detection_tile_data(*tile, scene_id)
            for feature in detection_geojson["features"]:
                feature_class = feature["properties"]["class"]
                if feature_class == "cars":
                    ra_data.add_detected_car()
                if feature_class == "trucks":
                    ra_data.add_detected_truck()
