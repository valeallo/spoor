import json
import os
import numpy as np
from src.detector import BirdDetector

def test_detector_initialization():
    """Test that the detector initializes without error."""
    detector = BirdDetector(model_name="yolov8s.pt")
    assert detector is not None
    assert detector.bird_class_id == 14

def test_empty_frame_handling():
    """Test that the detector handles empty/black frames gracefully."""
    detector = BirdDetector(model_name="yolov8s.pt")
    
    # Create a dummy black frame (H, W, C)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    detections = detector.track_frame(dummy_frame)
    
    # Should be empty since there are no birds in a black frame
    assert isinstance(detections, list)
    assert len(detections) == 0

def test_jsonl_output_format(tmp_path):
    """Test the structure of a single JSONL record."""
    record = {
        "frame_id": 1,
        "bbox": [10.0, 20.0, 30.0, 40.0],
        "track_id": 5,
        "class": "bird",
        "timestamp": 0.033
    }
    
    file_path = tmp_path / "test_results.jsonl"
    with open(file_path, "w") as f:
        f.write(json.dumps(record) + "\n")
        
    assert os.path.exists(file_path)
    
    with open(file_path, "r") as f:
        loaded_record = json.loads(f.readline())
        
    assert loaded_record["frame_id"] == 1
    assert loaded_record["track_id"] == 5
    assert len(loaded_record["bbox"]) == 4
    assert loaded_record["class"] == "bird"
