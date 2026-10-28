"""
test_detection.py - Phase 1 Detection Prototype
================================================
PURPOSE
-------
This standalone script is your first working proof-of-concept.
It loads a video source (sample file, uploaded file, or webcam),
runs YOLOv8 detection on each frame, draws bounding boxes with
confidence labels, and shows the result in a window.

WHAT THIS PHASE DEMONSTRATES
------------------------------
  ✅ Video source loading (file or webcam)
  ✅ YOLOv8 person detection
  ✅ Bounding box drawing
  ✅ FPS measurement and HUD overlay
  ✅ Clean exit with resource cleanup

WHAT THIS PHASE DOES NOT YET DO
---------------------------------
  ❌ Helmet / vest detection (needs PPE model – Phase 2)
  ❌ Worker tracking (Phase 3)
  ❌ Violation rules (Phase 4)
  ❌ Dashboard / API (Phase 6+)

HOW TO RUN
----------
1. Activate your virtual environment:
      .\\venv\\Scripts\\Activate.ps1

2. From the PROJECT ROOT directory:
      python scripts/test_detection.py

   Or specify a video file:
      python scripts/test_detection.py --source path/to/video.mp4

   Or use webcam:
      python scripts/test_detection.py --source 0

CONTROLS (when window is open)
-------------------------------
  Q or ESC  = Quit
  S         = Save current frame to evidence/
  P         = Pause / resume

COMMON ERRORS
-------------
  ModuleNotFoundError: ultralytics
    → Run: pip install ultralytics

  cv2.error / window does not open
    → If running over SSH / headless, add --no-display flag

  Model download fails
    → Check internet connection; ultralytics downloads yolov8n.pt (~6MB)
"""

import sys
import os
import time
import logging
import argparse
from pathlib import Path

# ── Make sure we can import from backend/app ─────────────────────────────────
# This script lives in scripts/ which is one level above backend/
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# ── Now we can import our own modules ────────────────────────────────────────
try:
    import cv2
    import numpy as np
except ImportError:
    print("❌  OpenCV not found. Run: pip install opencv-python")
    sys.exit(1)

try:
    from app.services.detector import ObjectDetector
    from app.utils.drawing import (
        draw_person_box,
        draw_ppe_box,
        draw_hud,
        draw_alert_banner,
        COLORS,
    )
    from app.utils.video_utils import VideoSource, save_frame
except ImportError as e:
    print(f"❌  Import error: {e}")
    print("    Make sure you run this from the PROJECT ROOT directory.")
    sys.exit(1)

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("test_detection")


# ── Default video source ──────────────────────────────────────────────────────
SAMPLE_VIDEO_PATH = PROJECT_ROOT / "datasets" / "sample_video.mp4"
MODEL_PATH = PROJECT_ROOT / "model_weights" / "yolov8n.pt"
EVIDENCE_DIR = PROJECT_ROOT / "evidence"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 1 – Construction Site Detection Prototype"
    )
    parser.add_argument(
        "--source",
        default=str(SAMPLE_VIDEO_PATH),
        help=(
            "Video source: path to a video file, "
            "integer webcam index (0, 1, …), "
            "or RTSP URL. "
            f"Default: {SAMPLE_VIDEO_PATH}"
        ),
    )
    parser.add_argument(
        "--model",
        default=str(MODEL_PATH),
        help="Path to YOLOv8 .pt model file. Default: model_weights/yolov8n.pt",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.45,
        help="Minimum detection confidence (0.0–1.0). Default: 0.45",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=1280,
        help="Resize frames wider than this (0 = no resize). Default: 1280",
    )
    parser.add_argument(
        "--frame-skip",
        type=int,
        default=1,
        help="Process every Nth frame (1 = every frame). Default: 1",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Run headless (no OpenCV window); saves output video instead.",
    )
    parser.add_argument(
        "--save-output",
        action="store_true",
        help="Save the processed video to evidence/output.mp4",
    )
    return parser.parse_args()


def try_download_sample_video() -> bool:
    """
    Attempt to download a small public domain construction site sample video.
    Returns True if successful, False otherwise.
    """
    import urllib.request

    # Small free-to-use construction site clip from Pexels / public domain
    # Using a crowd test video as fallback since construction videos require specific licensing
    urls = [
        # Pexels free video (construction workers)
        "https://www.pexels.com/download/video/2278095/",
        # Fallback: a simple walking pedestrian video for person detection testing
        "https://github.com/opencv/opencv/raw/master/samples/data/vtest.avi",
    ]

    SAMPLE_VIDEO_PATH.parent.mkdir(parents=True, exist_ok=True)

    for url in urls:
        try:
            logger.info(f"Downloading sample video from: {url}")
            logger.info("This may take a moment …")
            urllib.request.urlretrieve(url, str(SAMPLE_VIDEO_PATH))
            if SAMPLE_VIDEO_PATH.stat().st_size > 10_000:  # > 10KB
                logger.info(f"✅  Sample video saved to: {SAMPLE_VIDEO_PATH}")
                return True
        except Exception as e:
            logger.warning(f"Download failed ({url}): {e}")
            if SAMPLE_VIDEO_PATH.exists():
                SAMPLE_VIDEO_PATH.unlink()

    return False


def main() -> None:
    args = parse_args()

    print("\n" + "═" * 65)
    print("  🏗️  Construction Site Safety Detection — Phase 1 Prototype")
    print("═" * 65)
    print(f"  Source    : {args.source}")
    print(f"  Model     : {args.model}")
    print(f"  Confidence: {args.confidence}")
    print(f"  Display   : {'No (headless)' if args.no_display else 'Yes (OpenCV window)'}")
    print("═" * 65 + "\n")

    # ── Resolve source ────────────────────────────────────────────────────────
    source: str | int = args.source
    if args.source.isdigit():
        source = int(args.source)  # webcam index
    elif not Path(args.source).exists() and not args.source.startswith("rtsp"):
        # Video file doesn't exist — try to download sample
        if args.source == str(SAMPLE_VIDEO_PATH):
            logger.warning(f"Sample video not found at: {args.source}")
            print("\n📥  Attempting to download a sample video …")
            if not try_download_sample_video():
                print("\n❌  Could not download a sample video automatically.")
                print("    Options:")
                print(f"    1. Place any .mp4 video at:  {SAMPLE_VIDEO_PATH}")
                print("    2. Run with your webcam:   python scripts/test_detection.py --source 0")
                print("    3. Specify a video file:   python scripts/test_detection.py --source path/to/video.mp4")
                sys.exit(1)
        else:
            logger.error(f"Video file not found: {args.source}")
            sys.exit(1)

    # ── Load model ────────────────────────────────────────────────────────────
    detector = ObjectDetector(
        model_path=args.model,
        confidence=args.confidence,
        device="cpu",  # Change to "cuda" if you have an NVIDIA GPU
    )

    print("⏳  Loading YOLOv8 model …")
    print("    (On first run, ~6 MB model file will be downloaded automatically)\n")
    detector.load()

    if not detector.is_ppe_model:
        print("ℹ️   Phase 1 note: Using COCO model → detects PERSONS only.")
        print("    Helmet/vest detection will be added in Phase 2 (PPE model).\n")

    # ── Set up output video writer ────────────────────────────────────────────
    video_writer = None
    output_path = EVIDENCE_DIR / "phase1_output.mp4"

    # ── Create evidence directory ─────────────────────────────────────────────
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    # ── Main processing loop ─────────────────────────────────────────────────
    paused = False
    frame_count = 0
    person_count_history: list[int] = []

    print("▶️   Starting video processing …")
    if not args.no_display:
        print("    Controls: Q/ESC = Quit | S = Save frame | P = Pause\n")

    try:
        with VideoSource(source, max_width=args.max_width, frame_skip=args.frame_skip) as vs:

            # Set up video writer after source is opened
            if args.save_output or args.no_display:
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                fps_out = max(1.0, vs._fps_target / args.frame_skip)
                video_writer = cv2.VideoWriter(
                    str(output_path), fourcc, fps_out, (vs.width, vs.height)
                )
                if video_writer.isOpened():
                    logger.info(f"Saving output to: {output_path}")

            for frame, frame_number in vs.frames():

                # Handle pause (only in display mode)
                if not args.no_display and paused:
                    key = cv2.waitKey(50) & 0xFF
                    if key in (ord("p"), ord("P")):
                        paused = False
                    elif key in (ord("q"), 27):  # Q or ESC
                        break
                    continue

                frame_count += 1

                # ── Run detection ─────────────────────────────────────────────
                detections = detector.detect(frame)

                persons = [d for d in detections if d.class_name == "person"]
                ppe_items = [d for d in detections if d.class_name != "person"]

                person_count_history.append(len(persons))
                if len(person_count_history) > 30:
                    person_count_history.pop(0)

                # ── Draw results ──────────────────────────────────────────────
                # Draw person boxes
                for det in persons:
                    x1, y1, x2, y2 = det.bbox
                    # Phase 1: No PPE status yet — will be added in Phase 2
                    draw_person_box(
                        frame, x1, y1, x2, y2,
                        track_id=None,
                        confidence=det.confidence,
                        ppe_status=None,
                    )

                # Draw PPE item boxes (only visible if using PPE model)
                for det in ppe_items:
                    x1, y1, x2, y2 = det.bbox
                    draw_ppe_box(frame, x1, y1, x2, y2, det.class_name, det.confidence)

                # Draw HUD overlay
                draw_hud(
                    frame,
                    fps=vs.fps_actual,
                    frame_number=frame_number,
                    person_count=len(persons),
                    violation_count=0,  # No violation engine yet (Phase 4)
                    source_label=vs.source_label,
                )

                # ── Display or save ───────────────────────────────────────────
                if video_writer is not None:
                    video_writer.write(frame)

                if not args.no_display:
                    cv2.imshow("Construction Safety Detection — Phase 1", frame)
                    key = cv2.waitKey(1) & 0xFF

                    if key in (ord("q"), 27):  # Q or ESC
                        logger.info("User requested quit.")
                        break
                    elif key in (ord("s"), ord("S")):
                        ts = int(time.time())
                        out_img = EVIDENCE_DIR / f"frame_{ts}.jpg"
                        save_frame(frame, out_img)
                        print(f"  📸  Frame saved: {out_img}")
                    elif key in (ord("p"), ord("P")):
                        paused = not paused
                        print(f"  {'⏸️  Paused' if paused else '▶️  Resumed'}")

                # ── Console progress every 30 processed frames ─────────────────
                if frame_count % 30 == 0:
                    avg_persons = (
                        sum(person_count_history) / len(person_count_history)
                        if person_count_history
                        else 0
                    )
                    print(
                        f"  Frame {frame_number:5d} | "
                        f"FPS: {vs.fps_actual:5.1f} | "
                        f"Persons detected: {len(persons)} | "
                        f"Avg (30f): {avg_persons:.1f}"
                    )

    except RuntimeError as e:
        print(f"\n❌  Video source error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user (Ctrl+C)")
    finally:
        if video_writer is not None:
            video_writer.release()
        if not args.no_display:
            cv2.destroyAllWindows()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "═" * 65)
    print("  ✅  Phase 1 Detection Complete")
    print("═" * 65)
    print(f"  Total frames processed : {frame_count}")
    if person_count_history:
        peak = max(person_count_history)
        avg = sum(person_count_history) / len(person_count_history)
        print(f"  Peak persons in frame  : {peak}")
        print(f"  Average persons/frame  : {avg:.2f}")
    if args.save_output or args.no_display:
        print(f"  Output video saved to  : {output_path}")
    print("\n  ▶️  Next Step: Phase 2 — PPE Fine-tuned Model Integration")
    print("═" * 65 + "\n")


if __name__ == "__main__":
    main()
