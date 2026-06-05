# Research Report: Why Bird Detection Fails and How to Improve It

## 1. Problem Statement

Our current prototype uses YOLOv8s (small) with `conf=0.15` and `imgsz=1280` to detect and track pigeons in a video. While it successfully detects and tracks birds in the foreground, it consistently **fails to detect birds in the background** — particularly those that are small, overlapping, or partially occluded by other birds.

This report investigates the root causes of these detection failures, surveys the academic literature for solutions, and evaluates open-source tools and models that could improve performance without requiring a significantly larger model.

---

## 2. Root Cause Analysis

### 2.1 Resolution Loss During Downsampling

YOLO models resize all input images to a fixed square resolution before inference (e.g., `640×640` or `1280×1280`). Our source video is `1920×1080`. When this is resized to `1280×1280`, distant birds that occupy only ~15–20 pixels in the original frame shrink to **~8–10 pixels**. At this scale, the model's convolutional layers cannot extract enough discriminative features to distinguish a bird from background texture.

**Key insight from literature**: Standard YOLO architectures struggle with objects below ~10–15 pixels after resizing (Joel Huang, 2025). The deep downsampling paths in the backbone cause the signal from tiny objects to vanish before reaching the detection head.

### 2.2 Non-Maximum Suppression (NMS) in Dense Flocks

When birds are packed closely together (as in our pigeon flock), their bounding boxes overlap significantly. YOLO's NMS step is designed to remove duplicate detections of the *same* object. However, it cannot distinguish between "two boxes for one bird" and "two boxes for two adjacent birds." With the default IoU threshold (~0.45), NMS aggressively removes valid detections in dense clusters, treating them as duplicates.

### 2.3 Confidence Threshold Filtering

The default confidence threshold in YOLO is `0.25`. We lowered it to `0.15`, which helped. However, distant and blurry birds often score below even this threshold because:
- They lack clear edges and texture
- They are partially occluded by neighboring birds
- Motion blur further degrades their appearance

### 2.4 ByteTrack's Internal Filtering

Even if YOLO *does* produce a low-confidence detection for a distant bird, ByteTrack has its own internal confidence gate. By default, it requires a confidence of `>0.6` to initialize a new track. This means that birds detected at, say, 20% confidence are silently discarded by the tracker and never appear in the output, even though YOLO saw them.

### 2.5 COCO "Bird" Class Generalization

YOLOv8 is trained on the COCO dataset, which defines a generic "bird" class. COCO images tend to feature birds in clear, well-lit, isolated poses. The model has limited exposure to:
- Dense flocks of ground-feeding pigeons
- Birds viewed from above or at steep angles
- Cluttered urban environments with similar-colored pavement

---

## 3. Solutions from the Literature

### 3.1 SAHI — Slicing Aided Hyper Inference ⭐ (Recommended)

**What it is**: SAHI is an open-source Python library (`pip install sahi`) that implements a tiling strategy. Instead of passing the entire frame to YOLO at once, it:
1. Slices the image into smaller overlapping tiles (e.g., `640×640`)
2. Runs YOLO inference on each tile independently
3. Merges all detections back into the original coordinate space using NMS

**Why it helps**: Each tile is processed at full resolution, so a bird that was 10px in the full frame becomes 40–60px in a tile — well within YOLO's detection range.

**Tradeoff**: Inference time increases linearly with the number of tiles. A `1920×1080` image sliced into `640×640` tiles with 20% overlap produces ~12 tiles, making inference ~12× slower per frame.

**Integration effort**: Very low. SAHI has native support for Ultralytics YOLOv8 via `AutoDetectionModel.from_pretrained(model_type='yolov8')`. It can be added to our existing pipeline with minimal code changes.

- **GitHub**: [github.com/obss/sahi](https://github.com/obss/sahi) (~4k stars)
- **License**: MIT

### 3.2 FB-YOLO — Flying Bird YOLO

**What it is**: A specialized YOLO variant designed for detecting flying birds near wind turbines. Published in *PeerJ Computer Science* (May 2026), it uses:
- PP-LCNet as a lightweight backbone
- DCSSE (Dilated Channel Shuffle Squeeze-and-Excitation) attention module
- AS-EIoU loss function optimized for small targets

**Why it helps**: Purpose-built for the exact problem we face — small, distant birds in surveillance video.

**Status**: The paper is published but **no official GitHub repository with pretrained weights** has been released yet. The authors may provide weights upon request. The associated dataset contains 6,038 annotated images.

### 3.3 Temporal Stacking / Multi-Frame Input

**What it is**: Instead of feeding a single frame to the detector, stack 3–5 consecutive frames into a multi-channel input. Moving objects (birds) create temporal signatures that distinguish them from static background.

**Why it helps**: A stationary rock and a stationary bird look identical in a single frame. But across 5 frames, the bird moves slightly while the rock doesn't. This temporal signal is a powerful discriminator.

**Research**: Extensively studied by the Visual Computing Lab (vclab.ca) in their work on bird detection at the Klim and Skagen wind farms in Denmark.

**Integration effort**: Moderate. Requires modifying the data pipeline to buffer frames and the model input channels (retraining needed).

### 3.4 Background Subtraction (MOG2) as a Pre-Filter

**What it is**: Use OpenCV's `BackgroundSubtractorMOG2` to create a motion mask before running YOLO. Only regions with detected motion are passed to the neural network.

**Why it helps**: 
- Dramatically reduces the search space for YOLO
- Can detect *any* moving object regardless of appearance (no confidence threshold needed)
- Extremely lightweight — runs in real-time on a CPU

**Limitation**: Only works with a fixed camera. Will not detect stationary birds (e.g., birds sitting still on the ground). Our pigeon video has a mostly fixed camera, so this could work as a complementary approach.

### 3.5 Super-Resolution Pre-Processing

**What it is**: Run a lightweight super-resolution model (e.g., Real-ESRGAN) on the image before passing it to YOLO. This "hallucmates" high-frequency detail into low-resolution regions.

**Why it helps**: Can make distant 10px birds look like 40px birds, pushing them above YOLO's detection threshold.

**Tradeoff**: Adds significant computational overhead. May introduce artifacts that confuse the detector.

---

## 4. Open-Source Models and Datasets Worth Exploring

| Project | Description | GitHub | License |
|---------|-------------|--------|---------|
| **SAHI** | Tiling framework for small object detection. Works with any YOLO model. | [obss/sahi](https://github.com/obss/sahi) | MIT |
| **FBD-SV-2024** | Flying Bird Detection dataset (28,694 frames, 28,366 annotations). Ideal for fine-tuning. | [Ziwei89/FBD-SV-2024](https://github.com/Ziwei89/FBD-SV-2024_github) | Public |
| **LEAF-YOLO** | Lightweight model for small object detection in aerial imagery. Optimized for edge devices. | [highquanglity/LEAF-YOLO](https://github.com/highquanglity/LEAF-YOLO) | Open |
| **Birder** | Wildlife imagery analysis framework with detection + classification. Supports knowledge distillation. | [birder-project/birder](https://github.com/birder-project/birder) | Open |
| **PytorchWildlife (Microsoft)** | Conservation-focused AI hub including MegaDetector for wildlife. | [microsoft/Biodiversity](https://github.com/microsoft/Biodiversity) | MIT |
| **Roboflow Datasets** | Community-contributed "Wind turbine bird detection" datasets for fine-tuning. | [roboflow.com/universe](https://universe.roboflow.com/) | Various |

---

## 5. Recommended Improvement Path (Without Changing Model Size)

Given the constraints of keeping the model lightweight and the project as a prototype, here is a prioritized roadmap:

### Phase 1: Quick Win — Integrate SAHI (Estimated effort: 1–2 hours)
- Add `sahi` to `pyproject.toml`
- Modify `detector.py` to use `get_sliced_prediction()` instead of direct `model.track()`
- Expected improvement: **2–3× more birds detected** in background regions
- Cost: ~10–12× slower inference per frame (acceptable for offline processing)

### Phase 2: Hybrid Approach — Add MOG2 Pre-Filter (Estimated effort: 2–3 hours)
- Run background subtraction on each frame to generate motion regions
- Use motion regions as "regions of interest" for YOLO
- This catches moving birds that YOLO misses, without lowering confidence thresholds globally

### Phase 3: Fine-Tune on Domain Data (Estimated effort: 4–8 hours)
- Download the FBD-SV-2024 dataset
- Fine-tune `yolov8s.pt` on it using `yolo train data=fbd.yaml model=yolov8s.pt epochs=50`
- This teaches the model what "small distant birds" look like, dramatically improving recall without changing the model architecture

### Phase 4: Production — Custom Training Pipeline
- Collect and annotate real footage from the deployment environment (cameras near wind turbines)
- Train on a combination of COCO, FBD-SV-2024, and custom data
- Deploy with ONNX/TensorRT for edge inference

---

## 6. Conclusion

The detection failures we observe are **not a bug** — they are well-documented limitations of general-purpose object detection models when applied to small, dense, and distant targets. The academic literature offers several proven solutions, with **SAHI (tiling)** being the most practical immediate improvement for our prototype, and **fine-tuning on domain-specific data** being the long-term solution for production deployment.
