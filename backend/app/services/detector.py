"""
detector.py - YOLOv8 Object Detection Service
===============================================
Wraps the Ultralytics YOLOv8 model and provides a clean interface
for the rest of the pipeline.

Phase 1:  Uses YOLOv8n (COCO) → detects 'person' only.
Phase 2+: Upgraded to a PPE fine-tuned model that also detects
           helmet / no-helmet / vest / no-vest.

How YOLO detection works (simple explanation):
- The input image is divided into a grid of cells.
- Each cell predicts bounding boxes and class probabilities.
- Non-Maximum Suppression (NMS) removes overlapping boxes.
- We keep only boxes whose confidence >= DETECTION_CONFIDENCE.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# ── Class definitions ────────────────────────────────────────────────────────
# COCO model (Phase 1) class IDs we care about
COCO_PERSON_CLASS_ID = 0

# PPE model class names (Phase 2 – fine-tuned model)
# These must match the dataset labels used during training.
PPE_CLASS_NAMES = {
    "person",
    "hardhat",
    "no-hardhat",
    "safety vest",
    "no-safety vest",
    "helmet",      # alternative naming
    "no-helmet",
    "vest",
    "no-vest",
}

# Map raw class names to our canonical internal names
PPE_CLASS_ALIAS = {
    "hardhat": "helmet",
    "hard hat": "helmet",
    "helmet": "helmet",
    "no-hardhat": "no-helmet",
    "no hardhat": "no-helmet",
    "no-helmet": "no-helmet",
    "safety vest": "vest",
    "safetyvest": "vest",
    "vest": "vest",
    "no-safety vest": "no-vest",
    "no safety vest": "no-vest",
    "no-vest": "no-vest",
    "person": "person",
    "worker": "person",
}


class Detection:
    """Represents a single detected object in a frame."""

    __slots__ = (
        "class_name",   # canonical name: 'person', 'helmet', 'vest', etc.
        "class_id",     # integer class ID from the model
        "confidence",   # float 0.0–1.0
        "bbox",         # (x1, y1, x2, y2) in pixel coordinates
        "bbox_xywh",    # (cx, cy, w, h) center-format – used by tracker
    )

    def __init__(
        self,
        class_name: str,
        class_id: int,
        confidence: float,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ):
        self.class_name = class_name
        self.class_id = class_id
        self.confidence = round(confidence, 4)
        self.bbox = (x1, y1, x2, y2)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        w = x2 - x1
        h = y2 - y1
        self.bbox_xywh = (cx, cy, w, h)

    def area(self) -> int:
        x1, y1, x2, y2 = self.bbox
        return max(0, x2 - x1) * max(0, y2 - y1)

    def __repr__(self) -> str:
        x1, y1, x2, y2 = self.bbox
        return (
            f"Detection(class='{self.class_name}', "
            f"conf={self.confidence:.2f}, "
            f"box=[{x1},{y1},{x2},{y2}])"
        )


class ObjectDetector:
    """
    Loads a YOLOv8 model and runs inference on video frames.

    Parameters
    ----------
    model_path : str or Path
        Path to the .pt model file. If the file does not exist,
        Ultralytics will attempt to download the named model.
    confidence : float
        Minimum detection confidence (0.0 – 1.0).
    device : str
        'cpu', 'cuda', or 'cuda:0' etc.
    """

    def __init__(
        self,
        model_path: str | Path = "yolov8n.pt",
        confidence: float = 0.50,
        device: str = "cpu",
    ):
        self.model_path = str(model_path)
        self.confidence = confidence
        self.device = device
        self._model = None
        self._class_names: dict[int, str] = {}
        self._is_ppe_model: bool = False

    def load(self) -> None:
        """Load the model. Call this once before starting inference."""
        try:
            from ultralytics import YOLO  # import here to keep startup fast

            logger.info(f"Loading model from: {self.model_path}")
            self._model = YOLO(self.model_path)

            # Build class name map
            self._class_names = self._model.names  # {0: 'person', 1: 'bicycle', ...}

            # Detect whether this is a PPE-specific model
            raw_names = set(v.lower() for v in self._class_names.values())
            self._is_ppe_model = bool(raw_names & {"hardhat", "no-hardhat", "helmet", "no-helmet"})

            model_type = "PPE fine-tuned" if self._is_ppe_model else "COCO pretrained"
            logger.info(
                f"Model loaded successfully: {model_type} | "
                f"Classes: {list(self._class_names.values())} | "
                f"Device: {self.device}"
            )

            if not self._is_ppe_model:
                logger.warning(
                    "⚠️  Using COCO model — only 'person' class will be used. "
                    "Helmet/vest detection requires a PPE fine-tuned model. "
                    "See model_weights/README.md for instructions."
                )

        except ImportError:
            raise RuntimeError(
                "Ultralytics is not installed. Run: pip install ultralytics"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model '{self.model_path}': {e}")

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def is_ppe_model(self) -> bool:
        return self._is_ppe_model

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """
        Run inference on a single BGR frame (OpenCV format).

        Returns a list of Detection objects filtered by confidence.
        Returns an empty list if the model is not loaded.
        """
        if not self.is_loaded:
            logger.error("Model not loaded. Call load() first.")
            return []

        try:
            results = self._model(
                frame,
                conf=self.confidence,
                device=self.device,
                verbose=False,
            )
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return []

        detections: list[Detection] = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                raw_name = self._class_names.get(cls_id, "unknown").lower()

                # In COCO mode, only keep 'person'
                if not self._is_ppe_model and cls_id != COCO_PERSON_CLASS_ID:
                    continue

                # Map to canonical class name
                canonical = PPE_CLASS_ALIAS.get(raw_name, raw_name)

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append(
                    Detection(
                        class_name=canonical,
                        class_id=cls_id,
                        confidence=conf,
                        x1=int(x1),
                        y1=int(y1),
                        x2=int(x2),
                        y2=int(y2),
                    )
                )

        return detections

    def detect_persons(self, frame: np.ndarray) -> list[Detection]:
        """Convenience: return only 'person' detections."""
        return [d for d in self.detect(frame) if d.class_name == "person"]

    def detect_ppe(self, frame: np.ndarray) -> list[Detection]:
        """Return only PPE-related detections (non-person)."""
        return [d for d in self.detect(frame) if d.class_name != "person"]

    def unload(self) -> None:
        """Release the model from memory."""
        self._model = None
        logger.info("Model unloaded.")
