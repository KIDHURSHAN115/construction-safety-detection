"""
drawing.py - Visualization Utilities
======================================
Functions that draw bounding boxes, labels, and status overlays
on video frames using OpenCV.

Color scheme:
  GREEN  = safe / PPE present
  RED    = violation / PPE missing
  ORANGE = uncertain / low confidence
  BLUE   = person (tracking box)
  PURPLE = restricted zone
  WHITE  = general text
"""

import cv2
import numpy as np
from typing import Optional

# ── Color palette (BGR format for OpenCV) ────────────────────────────────────
COLORS = {
    "person":      (219, 152,  52),   # steel blue
    "helmet":      ( 50, 205,  50),   # lime green
    "no-helmet":   ( 34,  34, 220),   # vivid red
    "vest":        ( 50, 205, 120),   # sea green
    "no-vest":     ( 70,  70, 235),   # orange-red
    "uncertain":   ( 50, 180, 235),   # amber
    "zone":        ( 64,   0, 128),   # purple
    "alert":       (  0,   0, 255),   # pure red
    "safe":        ( 50, 200,  50),   # green
    "text_bg":     ( 30,  30,  30),   # near-black
    "white":       (255, 255, 255),
}

# Font settings
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE_LABEL = 0.55
FONT_SCALE_SMALL = 0.42
FONT_SCALE_HUD   = 0.65
FONT_THICKNESS   = 1
BOLD_THICKNESS   = 2


def draw_detection_box(
    frame: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    label: str,
    confidence: float,
    color: tuple,
    track_id: Optional[int] = None,
) -> None:
    """
    Draw a bounding box with a label on the frame (in-place).

    Parameters
    ----------
    frame      : BGR numpy array from OpenCV
    x1,y1,x2,y2 : Bounding box corners in pixels
    label      : Text to display (e.g. 'Person', 'No Helmet')
    confidence : Detection confidence 0.0–1.0
    color      : BGR tuple for the box color
    track_id   : Optional worker tracking ID
    """
    # Draw the bounding rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # Build label text
    if track_id is not None:
        text = f"ID:{track_id} {label} {confidence:.0%}"
    else:
        text = f"{label} {confidence:.0%}"

    # Measure text size to draw a background pill
    (tw, th), baseline = cv2.getTextSize(text, FONT, FONT_SCALE_LABEL, FONT_THICKNESS)

    # Label background
    label_y = max(y1 - 6, th + 6)
    cv2.rectangle(
        frame,
        (x1, label_y - th - 6),
        (x1 + tw + 8, label_y + baseline - 2),
        color,
        cv2.FILLED,
    )

    # Label text (white)
    cv2.putText(
        frame,
        text,
        (x1 + 4, label_y - 2),
        FONT,
        FONT_SCALE_LABEL,
        COLORS["white"],
        FONT_THICKNESS,
        cv2.LINE_AA,
    )


def draw_person_box(
    frame: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    track_id: Optional[int],
    confidence: float,
    ppe_status: Optional[dict] = None,
) -> None:
    """
    Draw a person detection box with PPE status indicators.

    ppe_status example:
        {
          "helmet": "present" | "missing" | "uncertain",
          "vest":   "present" | "missing" | "uncertain",
        }
    """
    # Choose box color based on violations
    has_violation = False
    if ppe_status:
        has_violation = any(v == "missing" for v in ppe_status.values())

    color = COLORS["alert"] if has_violation else COLORS["person"]

    label = "Worker" if track_id is None else f"Worker #{track_id}"
    draw_detection_box(frame, x1, y1, x2, y2, label, confidence, color, track_id)

    # Draw PPE status badges below the label
    if ppe_status:
        badge_y = y1 + 2
        badge_x = x1 + 2
        for ppe_type, status in ppe_status.items():
            badge_color = {
                "present":   COLORS["helmet"],
                "missing":   COLORS["alert"],
                "uncertain": COLORS["uncertain"],
            }.get(status, COLORS["uncertain"])

            icon = {
                "present":   "✓",
                "missing":   "✗",
                "uncertain": "?",
            }.get(status, "?")

            badge_text = f"{icon} {ppe_type.capitalize()}"
            (tw, th), _ = cv2.getTextSize(badge_text, FONT, FONT_SCALE_SMALL, FONT_THICKNESS)

            # Badge background
            cv2.rectangle(
                frame,
                (badge_x, badge_y),
                (badge_x + tw + 6, badge_y + th + 4),
                badge_color,
                cv2.FILLED,
            )
            cv2.putText(
                frame,
                badge_text,
                (badge_x + 3, badge_y + th + 1),
                FONT,
                FONT_SCALE_SMALL,
                COLORS["white"],
                FONT_THICKNESS,
                cv2.LINE_AA,
            )
            badge_y += th + 8


def draw_ppe_box(
    frame: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    class_name: str,
    confidence: float,
) -> None:
    """Draw a PPE item bounding box (helmet, vest, etc.)."""
    color = COLORS.get(class_name, COLORS["uncertain"])
    label_map = {
        "helmet":    "Helmet ✓",
        "no-helmet": "NO Helmet ✗",
        "vest":      "Vest ✓",
        "no-vest":   "NO Vest ✗",
    }
    label = label_map.get(class_name, class_name.capitalize())
    draw_detection_box(frame, x1, y1, x2, y2, label, confidence, color)


def draw_restricted_zone(
    frame: np.ndarray,
    polygon_points: list[tuple[int, int]],
    active: bool = False,
    label: str = "Restricted Zone",
) -> None:
    """
    Draw a semi-transparent restricted zone polygon on the frame.

    polygon_points: list of (x, y) tuples defining the zone boundary.
    active: if True, zone is highlighted (someone is inside).
    """
    if len(polygon_points) < 3:
        return

    pts = np.array(polygon_points, dtype=np.int32)
    overlay = frame.copy()

    color = (0, 0, 220) if active else COLORS["zone"]
    cv2.fillPoly(overlay, [pts], color)
    cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)

    # Draw border
    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)

    # Draw label at centroid
    cx = int(pts[:, 0].mean())
    cy = int(pts[:, 1].mean())
    (tw, th), _ = cv2.getTextSize(label, FONT, FONT_SCALE_SMALL, FONT_THICKNESS)
    cv2.rectangle(
        frame,
        (cx - tw // 2 - 4, cy - th - 4),
        (cx + tw // 2 + 4, cy + 4),
        color,
        cv2.FILLED,
    )
    cv2.putText(
        frame,
        label,
        (cx - tw // 2, cy),
        FONT,
        FONT_SCALE_SMALL,
        COLORS["white"],
        FONT_THICKNESS,
        cv2.LINE_AA,
    )


def draw_hud(
    frame: np.ndarray,
    fps: float,
    frame_number: int,
    person_count: int,
    violation_count: int,
    source_label: str = "",
) -> None:
    """
    Draw a Heads-Up Display (HUD) overlay on the frame with
    system statistics (FPS, worker count, violation count).
    """
    h, w = frame.shape[:2]

    # Semi-transparent top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 45), (20, 20, 20), cv2.FILLED)
    cv2.addWeighted(overlay, 0.70, frame, 0.30, 0, frame)

    stats = [
        f"FPS: {fps:.1f}",
        f"Frame: {frame_number}",
        f"Workers: {person_count}",
        f"Violations: {violation_count}",
    ]
    if source_label:
        stats.insert(0, f"Source: {source_label}")

    x_pos = 10
    for stat in stats:
        color = COLORS["alert"] if "Violations" in stat and violation_count > 0 else COLORS["white"]
        cv2.putText(frame, stat, (x_pos, 28), FONT, FONT_SCALE_HUD, color, BOLD_THICKNESS, cv2.LINE_AA)
        (tw, _), _ = cv2.getTextSize(stat, FONT, FONT_SCALE_HUD, BOLD_THICKNESS)
        x_pos += tw + 25

    # Phase label in corner
    phase_text = "PHASE 1 — DETECTION PROTOTYPE"
    (tw, th), _ = cv2.getTextSize(phase_text, FONT, FONT_SCALE_SMALL, FONT_THICKNESS)
    cv2.putText(
        frame,
        phase_text,
        (w - tw - 8, h - 8),
        FONT,
        FONT_SCALE_SMALL,
        (100, 100, 100),
        FONT_THICKNESS,
        cv2.LINE_AA,
    )


def draw_alert_banner(frame: np.ndarray, message: str) -> None:
    """Draw a flashing alert banner at the bottom of the frame."""
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - 50), (w, h), (0, 0, 180), cv2.FILLED)
    cv2.addWeighted(overlay, 0.80, frame, 0.20, 0, frame)

    (tw, th), _ = cv2.getTextSize(message, FONT, FONT_SCALE_HUD, BOLD_THICKNESS)
    cx = (w - tw) // 2
    cv2.putText(
        frame,
        f"⚠  {message}",
        (cx, h - 15),
        FONT,
        FONT_SCALE_HUD,
        COLORS["white"],
        BOLD_THICKNESS,
        cv2.LINE_AA,
    )
