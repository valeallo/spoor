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
4. Once complete, use the main area to select the generated JSONL file and view the analytics charts!

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
