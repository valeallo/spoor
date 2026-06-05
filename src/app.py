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
            st.subheader("Annotated Video")
            st.video(video_path)
            
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
