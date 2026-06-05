# Spoor Video Processing Prototype - Writeup

## Problem Approach
The goal was to build a system that processes a video, detects and tracks birds across frames, and produces structured output. Given the 3-5 hour time constraint and the requirement for a prototype, using a state-of-the-art pre-trained model was the most efficient approach. 

## Main Components
1. **Object Detection and Tracking**: I used **Ultralytics YOLOv8n** (nano version for speed). It comes pre-trained on the COCO dataset, which includes "bird" as class `14`. Furthermore, Ultralytics provides a built-in ByteTrack/BoT-SORT implementation via `model.track()`, which simultaneously performs detection and assigns persistent track IDs.
2. **Video Processing Loop**: `opencv-python-headless` is used to read the video frame-by-frame, pass each frame to the YOLO tracker, and format the output into a JSONL file. OpenCV is also used to draw the bounding boxes and track IDs onto the frames to generate the annotated output video.
3. **Containerization**: A Dockerfile using the official `uv` image was created to ensure a reproducible environment, simplifying dependency management and execution.

## Tradeoffs and Assumptions
- **Speed vs. Accuracy**: I opted for `yolov8n` to ensure the prototype runs quickly, even on machines without a GPU. If accuracy is paramount, `yolov8x` or a fine-tuned model would perform better.
- **Pre-trained Limitations**: The COCO "bird" class is generic. It will detect many birds but might struggle with specific species, small birds at a distance, or challenging lighting/weather, which are common in real wind farm deployments.
- **Tracking Algorithm**: ByteTrack is used. It works well for general tracking but can struggle with occlusions or if birds fly out of frame and return (it might assign a new ID).

## What Was Left Out
- **Database Integration**: Results are dumped to JSONL rather than a persistent database like SQLite or PostgreSQL for simplicity, though the JSONL is structured enough to be ingested easily.
- **Real-time Streaming**: The system processes an existing video file instead of reading from an RTSP stream, which would be closer to a real-world camera deployment.
- **Extensive Error Recovery**: The current script assumes a relatively clean video file and doesn't implement extensive retry logic for corrupted frames.

## Future Improvements
- **Fine-Tuning**: Train the YOLO model specifically on Spoor's dataset (birds near wind farms, varying weather conditions, different camera angles).
- **Edge Deployment Optimization**: Convert the PyTorch model to TensorRT or ONNX to maximize inference speed on edge hardware (e.g., NVIDIA Jetson).
- **Advanced Tracking**: Implement a re-identification (ReID) model to re-associate track IDs if a bird leaves the frame and re-enters, or gets occluded by a turbine blade.
- **Monitoring**: Add Prometheus metrics to track inference latency, detection counts, and system health.

## Running Outside Local Machine (Edge/Cloud)
For edge deployment (e.g., near cameras):
- The solution would need to be optimized for the specific edge hardware (e.g., using TensorRT on an NVIDIA Jetson).
- Input would shift from file reading to consuming an RTSP or WebRTC stream directly from the camera.
- Outputs wouldn't be written locally; instead, detections would be sent via MQTT or an HTTP API to a central cloud server, minimizing bandwidth usage (only sending metadata or short video clips of events rather than a 24/7 video stream).

## AI / Automation Tools Usage
An AI assistant (Antigravity) was used to bootstrap the project structure, write the `pyproject.toml` utilizing `uv`, generate the OpenCV video processing loop, create the Dockerfile, and draft the initial unit tests. The assistant also drafted this writeup based on the decisions made during implementation. The AI was instructed to focus on the Ultralytics YOLOv8 library due to its out-of-the-box tracking capabilities which drastically reduced development time.
