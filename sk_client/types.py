"""
Types defined for sk_client project.

See python typing module for more info.
"""
from typing import List, Literal, TypedDict

from typing_extensions import NotRequired


class Credentials(TypedDict):
    """Credentials for SpaceKnow API."""

    username: str
    password: str


class AuthTokenData(TypedDict):
    """Response from Auth API, when getting JWT token."""

    id_token: str
    access_token: str
    token_type: str


class GeometryData(TypedDict):
    """Geometry data."""

    type: str
    coordinates: List[List[List[float]]]


class ExtentData(TypedDict):
    """Extent, GeoJSON with non-empty MBR."""

    type: str
    id: NotRequired[str]
    geometry: NotRequired[GeometryData]
    geometries: NotRequired[List[GeometryData]]
    properties: NotRequired[dict]


class FeatureCollectionData(TypedDict):
    """Collection of features - "array" of GeoJSON."""

    type: Literal["FeatureCollection"]
    features: List[ExtentData]


class SearchImageryInitiateData(TypedDict):
    """Request data to start imagery searching async task."""

    provider: Literal["gbdx", "maxar", "pl", "iceye", "ee", "esa", "noaa"]
    dataset: str
    extent: ExtentData
    startDatetime: str
    endDatetime: str
    minIntersection: float
    onlyDownloadable: bool
    onlyIngested: bool


class InitiatedPipelineData(TypedDict):
    """Response from API when created new async task."""

    nextTry: int
    pipelineId: str
    status: Literal["NEW", "PROCESSING", "FAILED", "RESOLVED"]


class PipelineStatusData(TypedDict):
    """Status of async pipeline."""

    nextTry: NotRequired[int]
    status: Literal["NEW", "PROCESSING", "FAILED", "RESOLVED"]


class ImageMetadata(TypedDict):
    """Image metadata for found imagery by Ragnar API.

    Not all fields are documented.
    """

    sceneId: str
    datetime: str
    satellite: str
    provider: str
    dataset: str
    cloudCover: NotRequired[float]


class AllocatedAreaData(TypedDict):
    """Data about allocated area."""

    km2: float
    cost: float


class KrakenAnalysisResultData(TypedDict):
    """Data result for kraken analysis."""

    mapId: str
    maxZoom: int
    tiles: List[List[int]]  # List of map tiles, tile in format [z, x, y] coordinates
