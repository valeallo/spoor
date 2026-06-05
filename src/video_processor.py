import cv2
import json
import os
from typing import Dict, Any
from datetime import datetime

from .detector import BirdDetector

def process_video(input_path: str, output_dir: str):
    """
    Processes the video, generates JSONL results and an annotated video.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    if base_name.endswith("_processed"):
        base_name = base_name[:-10]
        
    existing_jsonls = [f for f in os.listdir(output_dir) if f.endswith(".jsonl")]
    run_number = len(existing_jsonls) + 1
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_path = os.path.join(output_dir, f"{run_number:02d}_{base_name}_results_{timestamp_str}.jsonl")
    video_out_path = os.path.join(output_dir, f"{run_number:02d}_{base_name}_annotated_{timestamp_str}.mp4")
    
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {input_path}")
        
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Initialize VideoWriter for mp4 output (native OS friendly)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_video = cv2.VideoWriter(video_out_path, fourcc, fps, (width, height))
    
    detector = BirdDetector()
    
    frame_id = 0
    
    with open(jsonl_path, 'w') as jsonl_file:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frame
            detections = detector.track_frame(frame)
            timestamp = frame_id / fps
            
            # Write to JSONL
            for det in detections:
                record = {
                    "frame_id": frame_id,
                    "bbox": det["bbox"],
                    "track_id": det["track_id"],
                    "class": det["class"],
                    "timestamp": round(timestamp, 3)
                }
                jsonl_file.write(json.dumps(record) + "\n")
                
                # Annotate frame
                bbox = det["bbox"]
                track_id = det["track_id"] if det["track_id"] is not None else "Unknown"
                
                # Draw bounding box
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"{det['class']} {track_id}"
                cv2.putText(frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            
            out_video.write(frame)
            frame_id += 1
            
            if frame_id % 30 == 0:
                print(f"Processed {frame_id}/{total_frames} frames...")
                
    cap.release()
    out_video.release()
        
    print(f"Processing complete. Results saved to {output_dir}")
