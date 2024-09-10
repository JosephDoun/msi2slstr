from onnxruntime import SessionIOBinding
from onnxruntime import InferenceSession
from onnxruntime import SessionOptions, RunOptions
from numpy import ndarray

from ..config import _OpenRelativePath
from ..config import onnx_providers, onnx_provider_options


class Runtime:
    def __init__(self) -> None:
        self.session_options = SessionOptions()
        
        with _OpenRelativePath("../resources/model.onnx", "rb") as model_file:
            self.session = InferenceSession(bytes(model_file.read()),
                                            providers=onnx_providers,
                                            provider_options=None,)

        self.run_options = RunOptions()
        self.run_options
        
    def __call__(self, sen2: ndarray, sen3: ndarray) -> list[ndarray]:
        return self.session.run([], input_feed={"x": sen2, "y": sen3},
                                run_options=self.run_options)
        