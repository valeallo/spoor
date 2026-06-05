from ultralytics import YOLO
import os

def main():
    # We fine-tune the base model
    model = YOLO("yolov8s.pt")
    
    # The dataset yaml should be created by app.py
    data_yaml = os.path.abspath("custom_dataset/data.yaml")
    
    print("Starting YOLOv8 fine-tuning on custom dataset...")
    
    # Train the model. 
    # Use small epochs for quick iteration.
    results = model.train(
        data=data_yaml,
        epochs=50,
        imgsz=1280,
        project="runs/detect",
        name="custom_bird_model",
        exist_ok=True, # Overwrite previous custom model to keep it simple
        device="cpu" # Default to CPU to ensure it runs anywhere, but YOLO auto-detects GPU if available
    )
    print("Training complete! New weights saved to runs/detect/custom_bird_model/weights/best.pt")

if __name__ == "__main__":
    main()
