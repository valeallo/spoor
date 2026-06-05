import streamlit as st
import os
import pandas as pd
import json
from src.video_processor import process_video

st.set_page_config(page_title="Spoor Tracker", page_icon="🐦", layout="wide")

st.title("🐦 Spoor Bird Tracking Analysis")

INPUT_DIR = "input_videos"
OUTPUT_DIR = "output"

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------
# Sidebar Controls
# -----------------
st.sidebar.header("1. Process a Video")

input_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".mp4")]

if not input_files:
    st.sidebar.warning(f"No .mp4 files found in `{INPUT_DIR}/` directory.")
else:
    selected_video = st.sidebar.selectbox("Select video to process:", input_files)
    
    if st.sidebar.button("Run Tracker"):
        input_path = os.path.join(INPUT_DIR, selected_video)
        with st.spinner("Processing video... This may take a few minutes."):
            try:
                process_video(input_path, OUTPUT_DIR)
                st.sidebar.success("Processing complete!")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

import re

tab1, tab2 = st.tabs(["Dashboard", "Annotation Studio"])

with tab1:
    # -----------------
    # Main Area Analysis
    # -----------------
    st.header("2. Analyze Results")

    output_files = os.listdir(OUTPUT_DIR)
    runs = []

    # Pattern to extract base name and timestamp from jsonl files: base_name_results_YYYYMMDD_HHMMSS.jsonl
    pattern = re.compile(r"^(.*)_results_(\d{8}_\d{6})\.jsonl$")

    for f in output_files:
        match = pattern.match(f)
        if match:
            base_name = match.group(1)
            timestamp = match.group(2)
            # Format timestamp for display: YYYY-MM-DD HH:MM:SS
            display_time = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
            runs.append({
                "display": f"Video: {base_name} | Run at: {display_time}",
                "base_name": base_name,
                "timestamp": timestamp,
                "jsonl_file": f
            })

    if not runs:
        st.info("No tracking results found. Run the tracker on a video to generate results.")
    else:
        # Create a dictionary for the selectbox
        run_options = {run["display"]: run for run in runs}
        selected_display = st.selectbox("Select a processing run to view:", list(run_options.keys()))
        selected_run = run_options[selected_display]
        
        jsonl_path = os.path.join(OUTPUT_DIR, selected_run["jsonl_file"])
        video_filename = f"{selected_run['base_name']}_annotated_{selected_run['timestamp']}.mp4"
        video_path = os.path.join(OUTPUT_DIR, video_filename)
        
        # Load data
        data = []
        with open(jsonl_path, 'r') as f:
            for line in f:
                data.append(json.loads(line))
                
        if not data:
            st.warning("Selected JSONL file is empty.")
        else:
            # Display the video
            if os.path.exists(video_path):
                try:
                    with open(video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                    st.download_button(
                        label="🎬 Download / Play Annotated Video",
                        data=video_bytes,
                        file_name=video_filename,
                        mime="video/mp4"
                    )
                except Exception as e:
                    st.error(f"Error loading video file: {e}")
            else:
                st.error(f"Could not find the annotated video file at: {video_path}")
                
            df = pd.DataFrame(data)
            
            # Filter for only birds for analytics
            df_birds = df[df['class'] == 'bird']
            
            if df_birds.empty:
                st.warning("No birds were detected in this video.")
            else:
                # Basic Metrics
                total_unique_birds = df_birds['track_id'].nunique()
                total_frames = df_birds['frame_id'].max() - df_birds['frame_id'].min() + 1
                avg_birds_per_frame = df_birds.groupby('frame_id')['track_id'].count().mean()
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Unique Birds Detected", total_unique_birds)
                col2.metric("Total Frames Processed", total_frames)
                col3.metric("Avg Birds per Frame", f"{avg_birds_per_frame:.1f}")
                
                st.divider()
                
                # Chart 1: Birds over time
                st.subheader("Bird Count Over Time")
                birds_per_frame = df_birds.groupby('frame_id')['track_id'].count().reset_index()
                birds_per_frame.rename(columns={'track_id': 'Bird Count', 'frame_id': 'Frame'}, inplace=True)
                st.line_chart(birds_per_frame.set_index('Frame'))
                
                # Chart 2: Track durations
                st.subheader("Track Durations")
                track_durations = df_birds.groupby('track_id')['frame_id'].count().reset_index()
                track_durations.rename(columns={'frame_id': 'Frames Tracked', 'track_id': 'Track ID'}, inplace=True)
                st.bar_chart(track_durations.set_index('Track ID'))
            
            # Raw Data View
            with st.expander("View Raw JSONL Data (Includes All Detected Objects)"):
                st.dataframe(df)

with tab2:
    st.header("Annotation Studio")
    st.write("Extract frames where the model missed birds and draw bounding boxes to train a custom model.")
    
    import cv2
    from PIL import Image
    try:
        from streamlit_drawable_canvas import st_canvas
        HAS_CANVAS = True
    except ImportError:
        HAS_CANVAS = False
        st.error("streamlit-drawable-canvas is not installed. Please wait for the docker build to finish.")

    if HAS_CANVAS and input_files:
        anno_video = st.selectbox("Select video to annotate:", input_files, key="anno_video")
        frame_num = st.number_input("Frame number to extract:", min_value=0, value=0)
        
        if st.button("Extract Frame"):
            vid_path = os.path.join(INPUT_DIR, anno_video)
            cap = cv2.VideoCapture(vid_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.session_state["current_frame"] = Image.fromarray(frame_rgb)
                st.session_state["current_frame_name"] = f"{anno_video}_frame_{frame_num}"
            else:
                st.error("Could not extract frame. Is the frame number beyond the video length?")
            cap.release()
            
        if "current_frame" in st.session_state:
            st.write(f"Annotating: {st.session_state['current_frame_name']}")
            
            # Create a canvas component
            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                stroke_width=2,
                stroke_color="#00FF00",
                background_image=st.session_state["current_frame"],
                update_streamlit=True,
                height=st.session_state["current_frame"].height // 2, # Scale down for UI
                width=st.session_state["current_frame"].width // 2,
                drawing_mode="rect",
                key="canvas",
            )
            
            if st.button("Save Annotation"):
                if canvas_result.json_data is not None:
                    objects = canvas_result.json_data.get("objects", [])
                    if not objects:
                        st.warning("No bounding boxes drawn!")
                    else:
                        import uuid
                        os.makedirs("custom_dataset/images/train", exist_ok=True)
                        os.makedirs("custom_dataset/labels/train", exist_ok=True)
                        
                        file_id = f"{st.session_state['current_frame_name']}_{uuid.uuid4().hex[:8]}"
                        canvas_w = st.session_state["current_frame"].width // 2
                        canvas_h = st.session_state["current_frame"].height // 2
                        
                        img_path = f"custom_dataset/images/train/{file_id}.jpg"
                        st.session_state["current_frame"].save(img_path)
                        
                        label_path = f"custom_dataset/labels/train/{file_id}.txt"
                        with open(label_path, "w") as f:
                            for obj in objects:
                                if obj["type"] == "rect":
                                    left = obj["left"]
                                    top = obj["top"]
                                    w = obj["width"] * obj["scaleX"]
                                    h = obj["height"] * obj["scaleY"]
                                    
                                    x_center = (left + w / 2) / canvas_w
                                    y_center = (top + h / 2) / canvas_h
                                    norm_w = w / canvas_w
                                    norm_h = h / canvas_h
                                    
                                    f.write(f"0 {x_center} {y_center} {norm_w} {norm_h}\n")
                        
                        st.success(f"Saved {len(objects)} bird annotations to custom_dataset!")
                        
    elif not input_files:
        st.info("No videos found to annotate.")

    # ----------------
    # Training Engine
    # ----------------
    st.divider()
    st.subheader("Fine-Tune Model")
    st.write("Once you have annotated several frames, you can fine-tune the model to learn your specific birds.")
    
    num_annotated = 0
    if os.path.exists("custom_dataset/images/train"):
        num_annotated = len(os.listdir("custom_dataset/images/train"))
        
    st.metric("Total Annotated Frames", num_annotated)
    
    if st.button("Start Fine-Tuning"):
        if num_annotated < 3:
            st.warning("Please annotate at least 3 frames before training.")
        else:
            yaml_content = f"""path: {os.path.abspath('custom_dataset')}
train: images/train
val: images/train
names:
  0: bird
"""
            os.makedirs("custom_dataset", exist_ok=True)
            with open("custom_dataset/data.yaml", "w") as f:
                f.write(yaml_content)
                
            st.info("Training started! Check the terminal output for progress.")
            import subprocess
            import sys
            # Run training in background so it doesn't freeze the UI forever
            subprocess.Popen([sys.executable, "src/train.py"])
