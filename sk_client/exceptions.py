"""Exceptions for sk_client project."""


class ImproperlyConfiguredError(RuntimeError):
    """Raise when improperly configured project."""


class PipelineFailedError(RuntimeError):
    """Raise when pipeline failed."""

    def __init__(self, *args, pipeline_id: str, **kwargs):
        self.pipeline_id = pipeline_id
