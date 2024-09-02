from os import PathLike
from typing import Any, Sequence
from onnxruntime import SessionIOBinding
from onnxruntime import InferenceSession
from onnxruntime import SessionOptions


class Session(InferenceSession):
    def __init__(self, path_or_bytes: str | bytes | PathLike,
                 sess_options: Any | None = None,
                 providers: Sequence[str | tuple[str, dict[Any, Any]]] | None = None,
                 provider_options: Sequence[dict[Any, Any]] | None = None,
                 **kwargs) -> None:
        super().__init__(path_or_bytes, sess_options, providers,
                         provider_options, **kwargs)
        