"""Module with classes to hold data in the sk_client app."""
from typing import List, Optional

import typer

from .types import ExtentData, InitiatedPipelineData, ImageMetadata


class RunningAnalysesData:  # pylint: disable=R0902
    """Hold data for running analysis.

    todo(doubravskytomas): add comments for fields in __init__
    """

    def __init__(self):
        self.scenes_list: List[ImageMetadata] = []
        self.scenes_index = {}  # scene_id -> index in scenes_list
        self.selected_area: Optional[ExtentData] = None
        self.selected_zoom = {}  # scene_id -> zoom level
        self.selected_scenes = []
        self.cars_analysis_pipelines = []
        self.imagery_analysis_pipelines = []
        self.mapping_pipeline_to_scene_id = {}
        self.failed_scene_ids = set()
        self.imagery_analysis_results = {}  # scene_id -> results
        self.cars_analysis_results = {}  # scene_id -> results
        self.detected_cars_count = 0
        self.detected_trucks_count = 0

    def add_detected_car(self):
        """Add one new detected car into stats."""
        self.detected_cars_count += 1

    def add_detected_truck(self):
        """Add one new detected truck into stats."""
        self.detected_trucks_count += 1

    def get_scene_id(self, pipeline: InitiatedPipelineData) -> str:
        """Return scene ID by pipeline ID."""
        return self.mapping_pipeline_to_scene_id.get(pipeline["pipelineId"])

    def is_scene_failed(self, scene_id: str) -> bool:
        """Return if scene failed during any processing."""
        return scene_id in self.failed_scene_ids

    def print_stats(self):
        """Print statistics about finished analysis."""
        typer.echo(f"-> Scene processed: {len(self.selected_scenes)}")
        successfully = len(self.selected_scenes) - len(self.failed_scene_ids)
        typer.echo(f"--> successfully: {successfully}")
        typer.echo(f"--> unsuccessfully: {len(self.failed_scene_ids)}")
        detected_items_total = self.detected_cars_count + self.detected_trucks_count
        typer.echo(f"-> Detected items: {detected_items_total} total")
        typer.echo(f"--> cars: {self.detected_cars_count}")
        typer.echo(f"--> trucks: {self.detected_trucks_count}")

    def register_scenes(self, list_imagery_data: List[ImageMetadata]):
        """Register founded scenes/imagery."""
        self.scenes_list = list_imagery_data
        for index, imagery_data in enumerate(list_imagery_data):
            self.scenes_index[imagery_data["sceneId"]] = index

    def get_scene_data_by_id(self, scene_id: str) -> ImageMetadata:
        """Return scene/imagery data by sceneId."""
        return self.scenes_list[self.scenes_index[scene_id]]

    def get_scene_title(self, scene_id: str):
        """Generate title for scene."""
        scene_data = self.scenes_list[self.scenes_index[scene_id]]
        if "cloudCover" in scene_data:
            cloudy = scene_data["cloudCover"]
        else:
            cloudy = "N/A"
        return (
            f"{scene_data['datetime']}, "
            f"{scene_data['provider']}.{scene_data['dataset']}, cloudy: {cloudy}"
        )

    def select_scene(self, selected_index: Optional[int]):
        """Save selected scenes by user.

        :param selected_index: Index of registered scenes in self.scenes,
            or None for selecting all scenes.
        """
        if selected_index is None:
            self.selected_scenes = [
                scene_data["sceneId"] for scene_data in self.scenes_list
            ]
        else:
            scene_data = self.scenes_list[selected_index]
            self.selected_scenes = [scene_data["sceneId"]]
