"""
violation_engine.py - Violation Detection Engine
=================================================
STATUS: Placeholder — implemented in Phase 4.

This module implements persistence-based violation rules.
A violation alert is only raised if the unsafe condition persists
for a configurable number of consecutive frames or seconds.

This prevents false alerts from:
  - Momentary occlusion (a helmet briefly hidden behind another person)
  - Single missed detection (YOLO confidence dips below threshold for 1 frame)
  - Low-confidence uncertain states

Violation types (Phase 4+):
  - MISSING_HELMET     : Worker PPE helmet status = 'missing' for N seconds
  - MISSING_VEST       : Worker PPE vest status = 'missing' for N seconds
  - RESTRICTED_ZONE    : Worker centroid inside a defined polygon zone
  - UNSAFE_POSTURE     : Pose-based rule (Phase 5, clearly labeled prototype)

Each violation record will include:
  - worker_track_id
  - violation_type
  - start_timestamp
  - duration_seconds
  - confidence_score (average over persistence window)
  - severity (LOW / MEDIUM / HIGH)
  - evidence_frame_path (optional)
  - alert_status (POTENTIAL / CONFIRMED / DISMISSED)

Full implementation in Phase 4.
"""


class ViolationEngine:
    """Placeholder — full implementation in Phase 4."""

    def __init__(self, persistence_seconds=3.0, cooldown_seconds=30.0):
        self.persistence_seconds = persistence_seconds
        self.cooldown_seconds = cooldown_seconds
        self._state: dict = {}

    def process(self, worker_ppe_results, frame_timestamp, frame):
        """Returns a list of new violations. Currently a no-op."""
        return []

    def reset(self):
        self._state = {}
