from typing import Any, Dict, List
from ultralytics import YOLO

class BirdDetector:
    def __init__(self, model_name: str = "yolov8s.pt"):
        """
        Initializes the YOLOv8 model for detection and tracking.
        We use the small model (yolov8s) to improve accuracy over nano while remaining fast.
        """
        # This will automatically download the model if not present.
        self.model = YOLO(model_name)
        # In COCO dataset, class 14 is 'bird'
        self.bird_class_id = 14

    def track_frame(self, frame) -> List[Dict[str, Any]]:
        """
        Runs object tracking on a single frame.
        
        Args:
            frame: A numpy array representing the image (from cv2).
            
        Returns:
            A list of detection dictionaries containing bbox, track_id, and class.
        """
        # Run tracking using ByteTrack. persist=True tells it to keep track IDs across frames.
        # classes=[self.bird_class_id] filters for only birds.
        # We lowered conf to 0.05, increased NMS IoU to 0.8 for overlapping flocks, and imgsz to 1920 to detect very small background birds.
        results = self.model.track(frame, persist=True, classes=[self.bird_class_id], tracker="bytetrack.yaml", verbose=False, conf=0.05, iou=0.8, imgsz=1920)
        
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
            class_name = "bird" if cls_id == self.bird_class_id else "non-bird"
            
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
