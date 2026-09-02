"""Compatibility wrapper for the single production inference engine.

Older imports may still reference ``backend.ml.inference.engine``. Keep that
import path stable without maintaining a second, conflicting model pipeline.
"""

from backend.ml.inference.production_engine import ProductionInferenceEngine, inference_engine

InferenceEngine = ProductionInferenceEngine

__all__ = ["InferenceEngine", "ProductionInferenceEngine", "inference_engine"]
