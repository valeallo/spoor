# Spoor Bird Tracker

A prototype for detecting and tracking birds in a video, producing structured JSONL output and an annotated video.

## Prerequisites
- Docker (optional, for containerized execution)
- `uv` (optional, for local execution)

## Running with Docker (Recommended)

1. Build the Docker image:
   ```bash
   docker build -t spoor-tracker .
   ```

2. Run the container, mounting the input video and output directories:
   ```bash
   # In PowerShell
   docker run --rm -v ${PWD}/input_videos:/app/input_videos -v ${PWD}/output:/app/output spoor-tracker --input /app/input_videos/pigeon-6093.mp4 --output /app/output
   ```

The script will process the video and place `results.jsonl` and `annotated_video.mp4` into the `output/` directory on your host machine.

## Running Locally with `uv`

If you have `uv` installed, you can run the project directly:

1. Install dependencies and run:
   ```bash
   uv run python -m src.main --input input_videos/pigeon-6093.mp4 --output output
   ```

## Running Tests

To run the validation tests locally:
```bash
uv run pytest tests/
```
