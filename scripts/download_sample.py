"""
download_sample.py - Sample Video Downloader
=============================================
Downloads a free, public-domain video clip for testing.
Run this if test_detection.py cannot find a sample video.

Usage:
    python scripts/download_sample.py

What it downloads:
  - OpenCV's official test video (vtest.avi) — people walking.
    This is used to verify that person detection is working.
    For construction-specific testing, obtain a licensed clip
    from the sources listed in datasets/README.md.
"""

import sys
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
SAMPLE_PATH = DATASETS_DIR / "sample_video.mp4"
SAMPLE_AVI_PATH = DATASETS_DIR / "sample_video.avi"

# Free/open source test videos (no login required)
DOWNLOAD_SOURCES = [
    {
        "url": "https://github.com/opencv/opencv/raw/master/samples/data/vtest.avi",
        "description": "OpenCV vtest.avi – pedestrians (good for person detection test)",
        "output": SAMPLE_AVI_PATH,
    },
    {
        "url": "https://media.pexels.com/videos/2278095/free-video-2278095.mp4",
        "description": "Pexels construction site footage (people on site)",
        "output": SAMPLE_PATH,
    },
]


def download_file(url: str, output: Path, description: str) -> bool:
    """Download a file with a progress indicator."""
    print(f"\n📥  Downloading: {description}")
    print(f"    URL    : {url}")
    print(f"    Output : {output}")

    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        def progress(block_count, block_size, total_size):
            if total_size > 0:
                pct = min(100, block_count * block_size * 100 // total_size)
                bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                print(f"\r    [{bar}] {pct}%", end="", flush=True)

        urllib.request.urlretrieve(url, str(output), reporthook=progress)
        print()  # newline after progress bar

        size_mb = output.stat().st_size / 1_048_576
        if size_mb < 0.01:
            print(f"    ⚠️  Downloaded file is very small ({size_mb:.2f} MB) — may be invalid.")
            output.unlink(missing_ok=True)
            return False

        print(f"    ✅  Downloaded successfully ({size_mb:.2f} MB)")
        return True

    except urllib.error.URLError as e:
        print(f"\n    ❌  Network error: {e.reason}")
        output.unlink(missing_ok=True)
        return False
    except Exception as e:
        print(f"\n    ❌  Error: {e}")
        output.unlink(missing_ok=True)
        return False


def main() -> None:
    print("\n" + "═" * 60)
    print("  📹  Sample Video Downloader")
    print("═" * 60)

    # Check if a sample already exists
    for path in [SAMPLE_PATH, SAMPLE_AVI_PATH]:
        if path.exists() and path.stat().st_size > 10_000:
            print(f"\n✅  Sample video already exists: {path}")
            print("    Delete it to re-download.")
            return

    success = False
    for source in DOWNLOAD_SOURCES:
        if download_file(source["url"], source["output"], source["description"]):
            success = True
            final_path = source["output"]
            break

    if not success:
        print("\n❌  All download attempts failed.")
        print("\nManual options:")
        print("  1. Download any .mp4 from https://www.pexels.com/search/videos/construction/")
        print(f"     and save it as: {SAMPLE_PATH}")
        print("  2. Use your webcam: python scripts/test_detection.py --source 0")
        print("  3. Specify your own video: python scripts/test_detection.py --source path/to/video.mp4")
        sys.exit(1)

    print(f"\n✅  Ready to test! Run:")
    print(f"    python scripts/test_detection.py --source \"{final_path}\"")
    print()


if __name__ == "__main__":
    main()
