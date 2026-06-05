from typing import Any, Dict, List
import os
from ultralytics import YOLO

class BirdDetector:
    def __init__(self):
        """
        Initializes the YOLOv8 model for bird detection.
        Dynamically loads custom weights if available, otherwise falls back to base YOLOv8s.
        """
        # COCO dataset class ID for 'bird' is 14. Custom trained model has 'bird' as class 0.
        custom_weights = "runs/detect/custom_bird_model/weights/best.pt"
        if os.path.exists(custom_weights):
            print(f"Loading custom fine-tuned weights from {custom_weights}...")
            self.model = YOLO(custom_weights)
            self.bird_class_id = 0
        else:
            print("Loading base YOLOv8s weights...")
            self.model = YOLO("yolov8s.pt")
            self.bird_class_id = 14

    def track_frame(self, frame) -> List[Dict[str, Any]]:
        """
        Runs object tracking on a single frame.
        
        Args:
            frame: A numpy array representing the image (from cv2).
            
        Returns:
            A list of detection dictionaries containing bbox, track_id, and class.
        """
        # Run tracking using custom Bot-SORT config.
        # We use src/custom_tracker.yaml which increases track_buffer to 120.
        # This prevents the tracker from "forgetting" a bird if it's blurry for a few frames,
        # which stops it from re-detecting the same bird as a brand new ID.
        # We also slightly raised conf to 0.15 to prevent noise from generating new IDs.
        results = self.model.track(frame, persist=True, classes=[self.bird_class_id], tracker="src/custom_tracker.yaml", verbose=False, conf=0.15, iou=0.8, imgsz=1920)
        
        detections = []
        if not results or len(results) == 0:
            return detections
            
        result = results[0]
        
        if result.boxes is None:
            return detections
            
        boxes = result.boxes
        
        for i in range(len(boxes)):
            # Bounding box in [x_min, y_min, x_max, y_max] format
            xyxy = boxes.xyxy[i].tolist()
            
            # If tracking ID is not assigned yet (e.g., very first frame or low confidence)
            track_id = None
            if boxes.id is not None:
                track_id = int(boxes.id[i].item())
                
            cls_id = int(boxes.cls[i].item())
            
            # Get specific class name from YOLO, and format our class label
            yolo_class_name = self.model.names[cls_id]
            class_name = "bird" if cls_id == self.bird_class_id else f"non-bird ({yolo_class_name})"
            
            detections.append({
                "bbox": [round(x, 2) for x in xyxy],
                "track_id": track_id,
                "class": class_name
            })
            
        return detections
    
    def annotate_frame(self, frame, results):
        """
        Helper to annotate the frame using Ultralytics built-in plotter if needed.
        Currently not used directly, as we manually draw in video_processor for more control,
        but available if we want YOLO's default styling.
        """
        return results[0].plot() if results else frame
