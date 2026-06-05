import argparse
import sys
from .video_processor import process_video

def main():
    parser = argparse.ArgumentParser(description="Spoor bird tracking prototype.")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input video file.")
    parser.add_argument("--output", "-o", type=str, required=True, help="Directory to save outputs.")
    
    args = parser.parse_args()
    
    try:
        process_video(args.input, args.output)
    except Exception as e:
        print(f"Error processing video: {e}", file=sys.stderr)
        sys.exit(1)
        
if __name__ == "__main__":
    main()
