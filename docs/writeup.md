# Spoor Video Processing Prototype - Writeup

## How you thought about the problem
Coming into this assignment, Machine Learning and Computer Vision were new for me. Rather than spending all my time reading research papers and getting overwhelmed by theory, I took an agile, hands-on approach. 

I mentally divided the problem into vertical slices: first achieving basic object detection, then applying tracking, and finally wrapping it in a UI to verify the results. After finding some tutorials on the `ultralytics` package, I realized it provided a clean, well-documented abstraction layer for a beginner. I used an AI assistant as a pair-programmer and sounding board. 

My philosophy was to establish a working baseline quickly. In a real-world job scenario, if tasked with an unfamiliar domain, I would try to get assistance from somebody that has more knowledge on the topic, at least for suggestions on the architecture. Through this exercise, I learned that bird detection—especially flying flocks—has highly specific edge cases, which my initial naive approach uncovered.

## The main components of your solution
1. **Object Detection and Tracking**: I used **Ultralytics YOLOv8s** (small version for a good balance of speed and accuracy). It comes pre-trained on the COCO dataset, which includes "bird" as class `14`. Furthermore, Ultralytics provides a built-in BoT-SORT implementation, which simultaneously performs detection and assigns persistent track IDs. 
2. **Video Processing Loop**: `opencv-python-headless` is used to read the video frame-by-frame, pass each frame to the YOLO tracker, and format the output into a JSONL file. OpenCV is also used to draw the bounding boxes and track IDs onto the frames to generate the annotated output video.
3. **Containerization**: A Dockerfile using the official `uv` image was created to ensure a reproducible environment. I optimized the Docker build to cache the massive PyTorch/CUDA libraries using `uv sync` before copying the source code, reducing rebuild times to seconds.
4. **Web Interface (Streamlit)**: To satisfy the inspection requirement, a simple local web UI was built. It allows users to trigger the processing pipeline and parses the JSONL results into Pandas DataFrames to visualize bird counts and track durations.

## Important tradeoffs and assumptions
1. **Zero-Shot Generalization (The COCO Assumption):** I assumed the pre-trained COCO dataset would generalize well. This was a tradeoff: it worked perfectly for birds walking on the ground, but failed heavily when the birds took flight due to motion blur and morphological changes.
2. **Precision vs. Recall:** To detect distant birds in the background, I increased the inference resolution (`imgsz=1280`) and lowered the confidence threshold (`conf=0.15`). This successfully found more birds but risked introducing false positives (noise).
3. **Tracking Stability over Perfect Detection:** Initially, the system suffered from massive "Identity Switching." For roughly 100 actual birds, the system reported over 300 unique IDs because it lost track of birds when they blurred, assigning them new IDs a few frames later. I traded strict tracking constraints for memory by extending the `track_buffer` to 120 frames. This drastically stabilized the tracking IDs, bringing the final count much closer to reality (~160).

## What you intentionally left out
I intentionally left out implementing highly specialized tracking frameworks like **YOLOv8-SMOT** (which won the MVA 2025 Challenge for flying bird detection). 

While my research showed this model was perfectly suited to solve the motion-blur/flying bird issue, it required migrating the entire project to the OpenMMLab (`mmyolo`) framework. Given the 3-5 hour time limit, I made the engineering decision that adopting a heavy, complex new framework was too risky. I opted to stay within the clean `ultralytics` pipeline and optimize my tracker parameters (switching to BoT-SORT) rather than over-engineering the underlying framework.

 Slicing Aided Hyper Inference (SAHI): I actually implemented this on a separate branch since the implementation itself only took a bunch of minutes. It is significantly more efficient at detecting birds, it makes the duplicate detection problem even more evident. The reason I didnt push it in main is the awful amount of time it takes to process the video on my machine, for a demo for you it will be faster to run it in main. feel free to run the "sahi" branch if you want to see it in action or if you are confident it will run fast on your.

## What you would improve with more time
1. **Specialized Weights:** The biggest bottleneck is the generic COCO dataset. With more time, I would fine-tune the YOLOv8 model on a specialized dataset for small flying objects (like FBD-SV-2024). 
2. **Human-in-the-Loop Annotation:** I actually built a working prototype of a Human-in-the-Loop Annotation Studio directly into the Streamlit app. When the model misses a bird taking flight, the user can draw a box around it in the UI and save it. With more time, I would fully automate the MLOps pipeline so that saving an annotation automatically triggers a cloud GPU instance to fine-tune the model and push the new weights back to the edge device.


## How you would think about running something like this outside your local machine
To run this near cameras or on edge hardware, I'd keep the architecture simple. Instead of running on a laptop, you would install a small, rugged computer directly attached to the camera. It would run this exact Docker container and process the live video feed locally. Then, instead of trying to upload heavy video files over a potentially weak internet connection, the edge device would only send the lightweight JSONL text data back to the cloud. 

## How you used AI
I used an LLM extensively as a pair-programmer and domain tutor. Since ML was new to me, the AI was crucial for bootstrapping the initial architecture and helping me debug obscure PyTorch and Docker environment errors. 

More importantly, I used it to understand *why* my results were failing. When my bird count was artificially inflating, the AI helped me understand the concepts of "Identity Switching" and Kalman filters, leading to the decision to swap ByteTrack for BoT-SORT and adjust the `track_buffer`. While the AI provided the code snippets, the architectural decisions, trade-off evaluations, and debugging direction were driven by my prompt engineering and problem-solving process.
