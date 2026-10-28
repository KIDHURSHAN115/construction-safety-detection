"""
pose_estimator.py - MediaPipe Pose Estimation Service
======================================================
STATUS: Placeholder — implemented in Phase 5.

This module wraps MediaPipe Pose to extract 33 body keypoints
from each worker's bounding box crop.

Keypoints include:
  - Shoulders, elbows, wrists (upper body)
  - Hips, knees, ankles (lower body)
  - Nose, eyes, ears (head)

Planned usage:
  - Detect raised arms (potential climbing behavior)
  - Detect crouching / falling posture
  - Feed into configurable rule-based unsafe action detection

⚠️  IMPORTANT LIMITATION:
Pose estimation alone CANNOT reliably determine:
  - Whether a worker is wearing a safety harness
  - Whether a worker is safely secured at height
These require a dedicated object detection model trained on harness imagery.

The pose module in Phase 5 will be clearly labeled as a
"PROTOTYPE / EXPERIMENTAL" feature with explicit confidence caveats.

Full implementation in Phase 5.
"""


class PoseEstimator:
    """Placeholder — full implementation in Phase 5."""

    def __init__(self):
        self._model = None

    def load(self):
        pass

    def estimate(self, frame_crop):
        """Returns None until fully implemented in Phase 5."""
        return None

    def unload(self):
        self._model = None
