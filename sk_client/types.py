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
