# Spoor Bird Tracker

A prototype for detecting and tracking birds in a video, producing structured JSONL output and an annotated video.

## Prerequisites
- Docker (optional, for containerized execution)
- `uv` (optional, for local execution)

## Running with Docker (Recommended)

1. Build the Docker image:
   ```bash
   docker compose up --build
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:8501
   ```

3. Use the sidebar to select a video from your local `input_videos/` folder and click "Run Tracker".
4. Once complete, use the **Dashboard** tab to view the generated video and analytics charts.
5. All generated artifacts (`.mp4` and `.jsonl`) are automatically saved to the `output/` directory for your inspection.
6. Use the **Annotation Studio** tab to extract frames where the model missed birds, draw bounding boxes, and automatically trigger YOLOv8 fine-tuning!

## Features
- **Accurate Tracking**: Uses YOLOv8s and BoT-SORT with an extended 120-frame memory buffer to mitigate track ID switches.
- **Interactive UI**: Streamlit web interface to run pipelines, play videos, and plot analytical charts.
- **Human-in-the-Loop Studio**: Integrated canvas tool to actively draw missed bounding boxes and fine-tune the model natively within the app.

## Running Locally with `uv`

If you have `uv` installed, you can run the UI directly:

1. Install dependencies and run:
   ```bash
   uv run streamlit run src/app.py
   ```

## Running Tests

To run the validation tests locally:
```bash
uv run pytest tests/
```
