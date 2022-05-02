"""Module with classes to hold data in the sk_client app."""
from typing import Optional

import typer

from .types import ExtentData, InitiatedPipelineData


class RunningAnalysesData:
    """Hold data for running analysis.

    todo(doubravskytomas): add comments for fields in __init__
    """

    def __init__(self):
        self.selected_area: Optional[ExtentData] = None
        self.selected_scenes = []
        self.cars_analysis_pipelines = []
        self.imagery_analysis_pipelines = []
        self.mapping_pipeline_to_scene_id = {}
        self.failed_scene_ids = set()
        self.imagery_analysis_results = dict()  # scene_id -> results
        self.cars_analysis_results = dict()  # scene_id -> results
        self.detected_cars_count = 0
        self.detected_trucks_count = 0

    def add_detected_car(self):
        self.detected_cars_count += 1

    def add_detected_truck(self):
        self.detected_trucks_count += 1

    def get_scene_id(self, pipeline: InitiatedPipelineData) -> str:
        """Return scene ID by pipeline ID."""
        return self.mapping_pipeline_to_scene_id.get(pipeline['pipelineId'])

    def is_scene_failed(self, scene_id: str) -> bool:
        """Return if scene failed during any processing."""
        return scene_id in self.failed_scene_ids

    def print_stats(self):
        """Print statistics about finished analysis."""
        typer.echo(f"-> Scene processed: {len(self.selected_scenes)}")
        typer.echo(f"--> successfully: {len(self.selected_scenes) - len(self.failed_scene_ids)}")
        typer.echo(f"--> unsuccessfully: {len(self.failed_scene_ids)}")
        typer.echo(f"-> Detected items: {self.detected_cars_count + self.detected_trucks_count} total")
        typer.echo(f"--> cars: {self.detected_cars_count}")
        typer.echo(f"--> trucks: {self.detected_trucks_count}")
