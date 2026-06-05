# Custom Training Pipeline Setup Plan

*Note: This plan was created for future consideration to improve the detection of small, flying birds by fine-tuning the YOLOv8 model on a domain-specific dataset (like FBD-SV-2024).*

## Proposed Changes

### 1. Version Control & Branching
- Ensure all current working changes (Bot-SORT tracker, Streamlit UI, research reports) are committed to the `main` branch.
- Create and check out a new branch called `feature/custom-training` to isolate the machine learning pipeline from the production app.

### 2. Training Pipeline Implementation
- Create a new script `src/train.py` that contains the Ultralytics training loop. It will be pre-configured to train `yolov8s.pt` on a custom dataset, saving the weights and metrics to a structured output directory.
- Create a `dataset/` directory.
- Create a `dataset/README.md` explaining exactly how to download and format the FBD-SV-2024 dataset (or any other dataset in YOLO format).

### 3. Documentation
- Update the main `README.md` (in the new branch) to include instructions on how to start the background training job (e.g., using `nohup` or `screen` so it can run overnight without interruption).
- Document how to evaluate the new weights and integrate them back into `src/detector.py` once training is complete.
