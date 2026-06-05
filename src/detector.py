from typing import Any, Dict, List
import os
import torch
import supervision as sv
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

class BirdDetector:
    def __init__(self, model_name=None):
        """
        Initializes the YOLOv8 model for bird detection using SAHI.
        """
        custom_weights = "runs/detect/custom_bird_model/weights/best.pt"
        if os.path.exists(custom_weights):
            print(f"Loading custom fine-tuned weights from {custom_weights} via SAHI...")
            model_path = custom_weights
            self.bird_class_id = 0
        else:
            print("Loading base YOLOv8s weights via SAHI...")
            model_path = "yolov8s.pt"
            self.bird_class_id = 14

        device = "cuda:0" if torch.cuda.is_available() else "cpu"

        # Load the model via SAHI
        self.detection_model = AutoDetectionModel.from_pretrained(
            model_type="yolov8",
            model_path=model_path,
            confidence_threshold=0.15,
            device=device
        )
        
        # Initialize Supervision Tracker with a long memory to prevent duplication
        self.tracker = sv.ByteTrack(lost_track_buffer=120)

    def track_frame(self, frame) -> List[Dict[str, Any]]:
        """
        Runs sliced object tracking on a single frame.
        """
        # 1. Run SAHI sliced prediction
        result = get_sliced_prediction(
            frame,
            self.detection_model,
            slice_height=640,
            slice_width=640,
            overlap_height_ratio=0.2,
            overlap_width_ratio=0.2,
            verbose=False
        )
        
        # 2. Convert to Supervision format manually
        import numpy as np
        if len(result.object_prediction_list) == 0:
            detections = sv.Detections.empty()
        else:
            xyxy = []
            confidence = []
            class_id = []
            for pred in result.object_prediction_list:
                xyxy.append([pred.bbox.minx, pred.bbox.miny, pred.bbox.maxx, pred.bbox.maxy])
                confidence.append(pred.score.value)
                class_id.append(pred.category.id)
            
            detections = sv.Detections(
                xyxy=np.array(xyxy),
                confidence=np.array(confidence),
                class_id=np.array(class_id)
            )
        
        # 3. Filter for birds before passing to tracker
        if len(detections) > 0:
            detections = detections[detections.class_id == self.bird_class_id]
            
        # 4. Update the tracker with detections
        tracked_detections = self.tracker.update_with_detections(detections)
        
        # 5. Format the output to match our JSONL schema
        output = []
        for i in range(len(tracked_detections)):
            xyxy = tracked_detections.xyxy[i].tolist()
            tracker_id = int(tracked_detections.tracker_id[i]) if tracked_detections.tracker_id is not None else None
            cls_id = int(tracked_detections.class_id[i])
            
            class_name = "bird" if cls_id == self.bird_class_id else "non-bird"
            
            output.append({
                "bbox": [round(x, 2) for x in xyxy],
                "track_id": tracker_id,
                "class": class_name
            })
            
        return output
    
    def annotate_frame(self, frame, results):
        """
        Helper to annotate the frame using Ultralytics built-in plotter if needed.
        Currently not used directly, as we manually draw in video_processor for more control.
        """
        return frame
