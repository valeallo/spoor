# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Install system dependencies required by OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cache dependencies by only copying pyproject.toml first
COPY pyproject.toml .
# Create dummy files so hatchling doesn't fail during the initial sync
RUN mkdir -p src && touch src/__init__.py && touch README.md
RUN uv sync

# Pre-download the YOLO weights so they are baked into the Docker image
RUN uv run python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"

# Now copy the rest of the project files
ADD . /app

# Sync the project itself
RUN uv sync

# Define the volume for input and output
VOLUME ["/app/input_videos", "/app/output"]

# Set the default entrypoint
ENTRYPOINT ["uv", "run", "python", "-m", "src.main"]
# Default command args if none provided
CMD ["--input", "/app/input_videos/pigeon-6093.mp4", "--output", "/app/output"]
