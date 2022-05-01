"""Management for sk_client project.

Project is controlled by CLI generated by typer library.
"""
from pathlib import Path

import typer

from .exceptions import PipelineFailedError
from .api_client import SpaceKnowClient
from . import utils, progress


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


app = typer.Typer(add_completion=False)


@app.command("credits", help="Print remaining user credits.")
def user_credits():
    """Print remaining user credits."""
    credit = api_client.credits_api.get_remaining_credit()
    typer.echo(f"Remaining user credits: {credit}")


@app.command(help="Print user info.")
def user_info():
    """Print user info."""
    info = api_client.user_api.get_user_info()
    typer.echo("User info:")
    typer.echo(utils.pretty_format_json(info))


@app.command(help="Run 'cars' detection over selected area.")
def main(
    geojson_name: str = typer.Argument(
        ..., help="File name of geojson file in data folder, without file extension."
    )
):
    """Run 'cars' analysis for selected area."""
    geojson_path = Path(f"data/{geojson_name}.geojson")
    if not geojson_path.is_file():
        typer.echo(
            f"GeoJSON file does not exist: data/{geojson_name}.geojson", err=True
        )
        raise typer.Exit(1)
    selected_area = utils.load_geojson_data(geojson_name)

    search_pipeline = progress.search_imagery(api_client, selected_area)
    progress.wait_pipeline(api_client, search_pipeline)
    list_imagery_data = progress.retrieve_imagery(api_client, search_pipeline)
    selected_imagery_index = progress.select_imagery(list_imagery_data)

    if selected_imagery_index is None:
        selected_scenes = [
            imagery_data["sceneId"] for imagery_data in list_imagery_data
        ]
    else:
        selected_imagery_data = list_imagery_data[selected_imagery_index]
        selected_scenes = [selected_imagery_data["sceneId"]]

    # Run all async pipeline at the same time.
    cars_analysis_pipelines = []
    imagery_analysis_pipelines = []
    mapping_pipeline_to_scene_id = {}
    failed_scene_ids = []
    for scene_id in selected_scenes:
        progress.allocate_area(api_client, scene_id, selected_area)

        pipeline = progress.run_kraken_analysis_cars(
            api_client, scene_id, selected_area
        )
        mapping_pipeline_to_scene_id[pipeline["pipelineId"]] = scene_id
        cars_analysis_pipelines.append(pipeline)

        pipeline = progress.run_kraken_analysis_imagery(
            api_client, scene_id, selected_area
        )
        mapping_pipeline_to_scene_id[pipeline["pipelineId"]] = scene_id
        imagery_analysis_pipelines.append(pipeline)

    for pipeline in cars_analysis_pipelines:
        scene_id = mapping_pipeline_to_scene_id[pipeline["pipelineId"]]
        try:
            progress.wait_pipeline(api_client, pipeline)
        except PipelineFailedError:
            failed_scene_ids.append(scene_id)
            continue
        kraken_result_data = progress.retrieve_kraken_analysis_cars(
            api_client, pipeline
        )
        progress.download_cars_analysis_tiles(
            api_client,
            kraken_result_data["tiles"],
            kraken_result_data["mapId"],
            scene_id,
        )

    for pipeline in imagery_analysis_pipelines:
        scene_id = mapping_pipeline_to_scene_id[pipeline["pipelineId"]]
        if scene_id in failed_scene_ids:
            # Do not process imagery pipeline when 'cars' detection failed
            continue
        try:
            progress.wait_pipeline(api_client, pipeline)
        except PipelineFailedError:
            failed_scene_ids.append(scene_id)
            continue
        kraken_result_data = progress.retrieve_kraken_analysis_cars(
            api_client, pipeline
        )
        progress.download_imagery_analysis_tiles(
            api_client,
            kraken_result_data["tiles"],
            kraken_result_data["mapId"],
            mapping_pipeline_to_scene_id[pipeline["pipelineId"]],
        )
        progress.render_detected_items_into_imagery(
            kraken_result_data["tiles"],
            mapping_pipeline_to_scene_id[pipeline["pipelineId"]],
        )
        progress.stitch_enhanced_imageries(
            kraken_result_data["tiles"],
            mapping_pipeline_to_scene_id[pipeline["pipelineId"]],
        )

    typer.echo("\n-------------------------------------------------------------")
    typer.echo("Analysis done, see 'result' folder for generated data. Stats:")
    typer.echo(f"-> Scene processed: {len(selected_scenes)}")
    typer.echo(f"--> Successfully: {len(selected_scenes) - len(failed_scene_ids)}")
    typer.echo(f"--> Unsuccessfully: {len(failed_scene_ids)}")


app()
