"""Management for sk_client project.

Project is controlled by CLI generated by typer library.
"""
from pathlib import Path
import logging

import typer

from .data import RunningAnalysesData
from .api_client import SpaceKnowClient
from . import utils, progress


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.CRITICAL)


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
    ra_data = RunningAnalysesData()
    ra_data.selected_area = progress.load_geojson(geojson_name)

    search_pipeline = progress.search_imagery(api_client, ra_data.selected_area)
    progress.wait_pipeline(api_client, search_pipeline)
    list_imagery_data = progress.retrieve_imagery(api_client, search_pipeline)
    ra_data.register_scenes(list_imagery_data)
    selected_imagery_index = progress.select_imagery(ra_data)
    ra_data.select_scene(selected_imagery_index)

    progress.run_analysis_pipelines(api_client, ra_data)
    progress.process_cars_analysis_pipelines(api_client, ra_data)
    progress.process_imagery_analysis_pipelines(api_client, ra_data)
    progress.render_detected_items_into_imageries(ra_data)
    progress.count_detected_items(ra_data)

    typer.echo("\n-------------------------------------------------------------")
    typer.echo("Analysis done, see 'result' folder for generated data. Stats:")
    ra_data.print_stats()


app()
