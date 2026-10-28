"""
ppe_association.py - PPE-to-Worker Association Service
=======================================================
STATUS: Placeholder — implemented in Phase 3.

This module associates PPE detections (helmets, vests) with the correct
worker by analyzing bounding box overlap (IoU) and vertical proximity
(PPE is typically located above the worker's torso bounding box).

The association logic will:
  1. For each detected worker, define a "head region" (top ~30% of the bbox).
  2. Check if any helmet detection overlaps significantly with the head region.
  3. Similarly check for vest detections in the torso region.
  4. Assign PPE status: 'present', 'missing', or 'uncertain'.

'Uncertain' is used when:
  - The model detected neither present nor absent PPE.
  - Confidence is below the certain threshold.
  - The worker is heavily occluded.

Full implementation in Phase 3.
"""


def associate_ppe_to_workers(worker_detections, ppe_detections, certain_threshold=0.65):
    """
    Placeholder: returns empty PPE status for each worker.
    Full implementation in Phase 3.
    """
    results = []
    for worker in worker_detections:
        results.append({
            "detection": worker,
            "track_id": None,
            "ppe_status": {"helmet": "uncertain", "vest": "uncertain"},
        })
    return results
