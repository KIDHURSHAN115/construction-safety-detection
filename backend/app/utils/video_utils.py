"""
video_utils.py - Video Input / Frame Utilities
================================================
Helpers for opening video sources (files, webcam, RTSP),
extracting frames, and resizing them for processing.
"""

import logging
import time
from pathlib import Path
from typing import Generator, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoSource:
    """
    Wraps an OpenCV VideoCapture to provide:
    - Automatic source type detection (file / webcam / RTSP)
    - Clean resource management (use as context manager)
    - Optional frame resizing
    - FPS tracking

    Usage:
        with VideoSource("path/to/video.mp4") as vs:
            for frame, frame_number in vs.frames():
                process(frame)
    """

    def __init__(
        self,
        source: str | int,
        max_width: int = 1280,
        frame_skip: int = 1,
    ):
        """
        Parameters
        ----------
        source     : Path to video file, integer webcam index, or RTSP URL
        max_width  : Resize frame if wider than this (0 = no resize)
        frame_skip : Process every Nth frame (1 = every frame)
        """
        self.source = source
        self.max_width = max_width
        self.frame_skip = max(1, frame_skip)
        self._cap: Optional[cv2.VideoCapture] = None

        # Timing
        self._fps_target: float = 30.0
        self._fps_actual: float = 0.0
        self._frame_times: list[float] = []

    # ── Context manager ──────────────────────────────────────────────────────

    def __enter__(self) -> "VideoSource":
        self.open()
        return self

    def __exit__(self, *args) -> None:
        self.release()

    # ── Open / Release ───────────────────────────────────────────────────────

    def open(self) -> None:
        """Open the video source. Raises RuntimeError on failure."""
        source_repr = self.source
        if isinstance(self.source, str):
            if self.source.isdigit():
                source = int(self.source)
                source_repr = f"webcam:{source}"
            else:
                source = self.source
        else:
            source = self.source
            source_repr = f"webcam:{source}"

        logger.info(f"Opening video source: {source_repr}")
        self._cap = cv2.VideoCapture(source)

        if not self._cap.isOpened():
            self._cap = None
            raise RuntimeError(
                f"Cannot open video source: '{source_repr}'. "
                "Check that the file exists, the webcam is connected, "
                "or the RTSP stream is accessible."
            )

        self._fps_target = self._cap.get(cv2.CAP_PROP_FPS) or 30.0
        logger.info(
            f"Video source opened: {source_repr} | "
            f"FPS={self._fps_target:.1f} | "
            f"Resolution={self.width}×{self.height}"
        )

    def release(self) -> None:
        """Release the video capture object."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("Video source released.")

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def is_open(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    @property
    def width(self) -> int:
        if self._cap:
            return int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        return 0

    @property
    def height(self) -> int:
        if self._cap:
            return int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return 0

    @property
    def total_frames(self) -> int:
        """Total frame count (only meaningful for file sources)."""
        if self._cap:
            return int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return -1

    @property
    def fps_actual(self) -> float:
        """Recently measured actual processing FPS."""
        return self._fps_actual

    @property
    def source_label(self) -> str:
        if isinstance(self.source, int) or (
            isinstance(self.source, str) and self.source.isdigit()
        ):
            return f"Webcam {self.source}"
        if isinstance(self.source, str) and self.source.startswith("rtsp://"):
            return f"RTSP: {self.source[:40]}…"
        return Path(str(self.source)).name

    # ── Frame generator ──────────────────────────────────────────────────────

    def frames(self) -> Generator[Tuple[np.ndarray, int], None, None]:
        """
        Generator that yields (frame, frame_number) tuples.

        Handles:
        - frame_skip: skips frames to reduce compute
        - max_width:  resizes oversized frames
        - FPS measurement
        - Graceful end-of-stream
        """
        if not self.is_open:
            raise RuntimeError("Video source is not open. Call open() first.")

        frame_number = 0
        skip_counter = 0
        t_last = time.perf_counter()

        while True:
            ret, frame = self._cap.read()

            if not ret:
                logger.info("End of video stream.")
                break

            frame_number += 1
            skip_counter += 1

            # Skip frames
            if skip_counter < self.frame_skip:
                continue
            skip_counter = 0

            # Resize if too wide
            if self.max_width > 0 and frame.shape[1] > self.max_width:
                scale = self.max_width / frame.shape[1]
                new_w = int(frame.shape[1] * scale)
                new_h = int(frame.shape[0] * scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # Update FPS measurement (rolling average over last 30 frames)
            t_now = time.perf_counter()
            elapsed = t_now - t_last
            t_last = t_now

            self._frame_times.append(elapsed)
            if len(self._frame_times) > 30:
                self._frame_times.pop(0)
            if self._frame_times:
                avg_elapsed = sum(self._frame_times) / len(self._frame_times)
                self._fps_actual = 1.0 / avg_elapsed if avg_elapsed > 0 else 0.0

            yield frame, frame_number


def read_single_frame(source: str | int) -> Optional[np.ndarray]:
    """
    Read a single frame from the source and return it.
    Useful for generating thumbnail previews.
    """
    try:
        cap = cv2.VideoCapture(source if isinstance(source, int) else source)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None
    except Exception as e:
        logger.error(f"Failed to read frame from {source}: {e}")
        return None


def save_frame(frame: np.ndarray, output_path: str | Path, quality: int = 90) -> bool:
    """
    Save a frame as a JPEG image.

    Returns True on success, False on failure.
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        success = cv2.imwrite(str(output_path), frame, params)
        if success:
            logger.debug(f"Frame saved: {output_path}")
        else:
            logger.warning(f"Failed to save frame: {output_path}")
        return success
    except Exception as e:
        logger.error(f"Exception saving frame to {output_path}: {e}")
        return False
