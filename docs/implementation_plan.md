# Spoor Video Processing Prototype

This document outlines the implementation plan for the object detection and tracking prototype, as requested in the assignment. The system will process a video, detect and track objects (specifically birds), produce a structured JSONL output, and provide an annotated video for inspection. The entire solution will be containerized using Docker and use `uv` as the package manager.

## User Review Required

> [!IMPORTANT]
> Please review the chosen tools and frameworks. I plan to use **Ultralytics YOLOv8** for detection and its built-in tracker (ByteTrack/BoT-SORT). This provides a robust, pre-trained model capable of detecting "birds" (COCO class 14) out-of-the-box, saving significant time while yielding good results. 
> 
> Also, confirm if the expected bounding box format `[x_min, y_min, x_max, y_max]` in pixel coordinates is acceptable for the `bbox` field.

## Proposed Changes

### 1. Environment and Packaging
- **`pyproject.toml` & `uv.lock`**: Set up a Python project managed by `uv`.
- Dependencies: `ultralytics` (for YOLOv8), `opencv-python-headless` (for video reading/writing), `pytest` (for validation).

### 2. Core Processing Logic
- **`src/main.py`**: The main CLI entrypoint that accepts input video path and output directory.
- **`src/video_processor.py`**: Handles reading the video using OpenCV, frame by frame.
- **`src/detector.py`**: Wraps the YOLOv8 model. Uses `model.track()` to simultaneously detect and assign track IDs. Filters detections for the "bird" class (and possibly other relevant objects if needed, but primarily birds).
- **Output Generation**: For each frame, appends a JSON object to `results.jsonl` with fields: `frame_id`, `bbox` (pixel coordinates), `track_id`, `class`, and `timestamp` (calculated from frame ID and FPS).
- **Inspection Generation**: Uses OpenCV or Ultralytics' built-in annotator to draw bounding boxes and track IDs onto the frame, saving it to an output video file (e.g., `annotated_video.mp4`).

### 3. Containerization
- **`Dockerfile`**: A multi-stage Dockerfile that:
  - Installs `uv`.
  - Copies the project files.
  - Installs dependencies using `uv sync` or `uv pip install`.
  - Sets the entrypoint to run the `src/main.py` script.
- The user will be able to run the container by mounting a volume for the input video and output directory.

### 4. Validation
- **`tests/test_processor.py`**: Simple tests to validate:
  - The JSONL output format conforms to the schema.
  - Bounding boxes are within image dimensions.
  - Track IDs persist when given simulated sequential detections.

### 5. Writeup
- **`docs/writeup.md`**: A short markdown document addressing the points requested in the assignment (tradeoffs, assumptions, improvements, etc.).

## Verification Plan

### Automated Tests
- Run `uv run pytest tests/` to ensure unit tests pass.

### Manual Verification
- Build the Docker image: `docker build -t spoor-tracker .`
- Run the container against `input_videos/pigeon-6093.mp4`.
- Verify that `results.jsonl` is created and contains the correct fields.
- Watch `annotated_video.mp4` to visually inspect the tracking quality and verify that track IDs remain stable.
