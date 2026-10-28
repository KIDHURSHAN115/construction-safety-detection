"""
tracker.py - Multi-Object Tracking Service
===========================================
STATUS: Placeholder — implemented in Phase 3.

This module will wrap DeepSORT (or ByteTrack) to assign persistent
tracking IDs to each detected worker across video frames.

How tracking differs from detection
-------------------------------------
Detection answers "what is in THIS frame?" — each frame independently.
Tracking answers "is this the SAME person as in the PREVIOUS frame?" —
it connects detections across time using motion prediction (Kalman filter)
and appearance features (re-identification embeddings).

DeepSORT steps:
  1. Predict where each tracked person will be in the next frame.
  2. Match predictions to new detections using IoU + appearance distance.
  3. Update matched tracks; create new tracks for unmatched detections.
  4. Remove tracks that have not been matched for N consecutive frames.

This module will be fully implemented in Phase 3.
"""


class WorkerTracker:
    """Placeholder — full implementation in Phase 3."""

    def __init__(self):
        self._tracks: dict = {}

    def update(self, detections, frame):
        """
        Returns a list of TrackedWorker objects with persistent IDs.
        Currently a no-op stub — returns detections as-is.
        """
        return []

    def reset(self):
        self._tracks = {}
