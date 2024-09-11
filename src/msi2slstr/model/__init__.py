"""
Package defining model runtime environments.

It exposes a single :class:`Runtime` class used for inference.
"""
from . import *
from .onnx import Runtime
