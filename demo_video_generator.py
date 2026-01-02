# Demo Video Generator
# Creates test videos for the Violence Detection System

import cv2
import numpy as np
import os

def create_demo_video(filename, duration=10, fps=30, violence_scenes=True):
    """
    Create a demo video for testing the violence detection system
    
    Args:
        filename: Output video filename
        duration: Video duration in seconds
        fps: Frames per second
        violence_scenes: Whether to include simulated violence patterns
    """
    
    # Video settings
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    # Create output directory
    os.makedirs("demo_videos", exist_ok=True)
    output_path = os.path.join("demo_videos", filename)
    
    # Initialize video writer
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    print(f"Creating demo video: {filename}")
    print(f"Duration: {duration}s, FPS: {fps}, Total frames: {total_frames}")
    
    for frame_num in range(total_frames):
        # Create base frame
        frame = np.ones((height, width, 3), dtype=np.uint8) * 50  # Dark background
        
        # Add timestamp
        timestamp = frame_num / fps
        cv2.putText(frame, f"Time: {timestamp:.1f}s", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add frame number
        cv2.putText(frame, f"Frame: {frame_num}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        if violence_scenes:
            # Simulate different scenes throughout the video
            scene_type = get_scene_type(timestamp, duration)
            frame = add_scene_content(frame, scene_type, timestamp)
        else:
            # Normal scenes only
            frame = add_normal_scene(frame, timestamp)
        
        # Write frame to video
        video_writer.write(frame)
        
        # Progress indicator
        if frame_num % (total_frames // 10) == 0:
            progress = (frame_num / total_frames) * 100
            print(f"Progress: {progress:.0f}%")
    
    video_writer.release()
    print(f"✅ Demo video created: {output_path}")
    return output_path

def get_scene_type(timestamp, total_duration):
    """Determine scene type based on timestamp"""
    progress = timestamp / total_duration
    
    if 0.2 <= progress <= 0.3:  # Violence scene 1 (20-30%)
        return "violence"
    elif 0.6 <= progress <= 0.65:  # Violence scene 2 (60-65%)
        return "violence"
    elif 0.85 <= progress <= 0.9:  # Violence scene 3 (85-90%)
        return "violence"
    else:
        return "normal"

def add_scene_content(frame, scene_type, timestamp):
    """Add content based on scene type"""
    height, width = frame.shape[:2]
    
    if scene_type == "violence":
        # Simulate violence with rapid movement, color changes
        frame = add_violence_simulation(frame, timestamp)
        
        # Add warning text
        cv2.putText(frame, "SIMULATED VIOLENCE", (width//2 - 150, height//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
    else:
        frame = add_normal_scene(frame, timestamp)
    
    return frame

def add_violence_simulation(frame, timestamp):
    """Add visual patterns that might be detected as violence"""
    height, width = frame.shape[:2]
    
    # Rapid color flashing
    intensity = int(abs(np.sin(timestamp * 20)) * 100) + 50
    frame[:, :, 2] = intensity  # Red channel variation
    
    # Random rapid movements (simulated)
    for _ in range(10):
        x = np.random.randint(0, width - 50)
        y = np.random.randint(0, height - 50)
        color = (np.random.randint(100, 255), 0, 0)  # Random red tones
        cv2.rectangle(frame, (x, y), (x + 30, y + 30), color, -1)
    
    # Chaotic line patterns
    for _ in range(20):
        pt1 = (np.random.randint(0, width), np.random.randint(0, height))
        pt2 = (np.random.randint(0, width), np.random.randint(0, height))
        cv2.line(frame, pt1, pt2, (0, 0, 255), 2)
    
    return frame

def add_normal_scene(frame, timestamp):
    """Add normal scene content"""
    height, width = frame.shape[:2]
    
    # Gentle color variation
    base_color = int(abs(np.sin(timestamp * 0.5)) * 50) + 100
    frame[:, :, 1] = base_color  # Green channel
    
    # Some geometric shapes (peaceful)
    cv2.circle(frame, (width//4, height//4), 30, (100, 255, 100), 2)
    cv2.rectangle(frame, (width//2, height//2), (width//2 + 100, height//2 + 80), (100, 100, 255), 2)
    
    # Text indicating normal scene
    cv2.putText(frame, "Normal Scene", (width//2 - 80, height - 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 100), 2)
    
    return frame

def create_test_video_set():
    """Create a set of test videos for different scenarios"""
    
    print("🎬 Creating Demo Video Set for Violence Detection Testing")
    print("=" * 60)
    
    # Video configurations
    videos_to_create = [
        {
            "filename": "test_with_violence.mp4",
            "duration": 20,
            "violence_scenes": True,
            "description": "20-second video with 3 simulated violence scenes"
        },
        {
            "filename": "test_no_violence.mp4", 
            "duration": 15,
            "violence_scenes": False,
            "description": "15-second video with only normal scenes"
        },
        {
            "filename": "test_short_violence.mp4",
            "duration": 8,
            "violence_scenes": True,
            "description": "8-second video with brief violence simulation"
        }
    ]
    
    created_videos = []
    
    for video_config in videos_to_create:
        print(f"\n📹 Creating: {video_config['filename']}")
        print(f"   {video_config['description']}")
        
        video_path = create_demo_video(
            video_config["filename"],
            video_config["duration"],
            fps=30,
            violence_scenes=video_config["violence_scenes"]
        )
        
        created_videos.append(video_path)
    
    print("\n" + "=" * 60)
    print("✅ Demo Video Set Created Successfully!")
    print("\nCreated Videos:")
    for video in created_videos:
        file_size = os.path.getsize(video) / (1024 * 1024)  # MB
        print(f"   📁 {video} ({file_size:.1f} MB)")
    
    print(f"\n📂 All videos saved in: demo_videos/")
    print("\n🧪 Testing Instructions:")
    print("1. Start the Violence Detection System")
    print("2. Login/Register an account")
    print("3. Go to 'Upload Video' page")
    print("4. Test with these demo videos:")
    print("   • test_with_violence.mp4 (should detect incidents)")
    print("   • test_no_violence.mp4 (should detect no incidents)")
    print("   • test_short_violence.mp4 (should detect brief incident)")
    
    return created_videos

def create_readme_for_demos():
    """Create README for demo videos"""
    readme_content = """# Demo Videos for Violence Detection Testing

## 📹 Included Videos

### test_with_violence.mp4
- **Duration**: 20 seconds
- **Expected Result**: Should detect 3 violence incidents
- **Incident Times**: ~4s, ~12s, ~17s
- **Purpose**: Test positive detection capability

### test_no_violence.mp4  
- **Duration**: 15 seconds
- **Expected Result**: Should detect 0 incidents
- **Purpose**: Test false positive rate

### test_short_violence.mp4
- **Duration**: 8 seconds  
- **Expected Result**: Should detect 1-2 incidents
- **Purpose**: Test detection on shorter videos

## 🧪 How to Test

1. **Start the Violence Detection System**
   ```bash
   python app.py
   # or
   streamlit run app.py
   ```

2. **Create Account / Login**
   - Open http://localhost:8501
   - Register new account or login

3. **Upload Test Videos**
   - Go to "Upload Video" page
   - Upload each demo video
   - Start analysis

4. **Verify Results**
   - Check if detection results match expectations
   - Review incident timestamps and screenshots
   - Verify email notifications (if configured)

## 📊 Expected Performance

- **test_with_violence.mp4**: 3 incidents detected
- **test_no_violence.mp4**: 0 incidents detected  
- **test_short_violence.mp4**: 1-2 incidents detected

## ⚠️ Important Notes

- These are **synthetic test videos** with simulated patterns
- Real-world performance may vary significantly
- Use these only for system testing and validation
- Replace with real training data for production use

## 🔧 Customization

To create your own test videos:
```python
python demo_video_generator.py
```

Modify the `create_demo_video()` function to customize:
- Video duration
- Violence simulation patterns
- Scene complexity
- Frame rate and resolution
"""
    
    with open("demo_videos/README.md", "w") as f:
        f.write(readme_content)
    
    print("📚 Created README.md in demo_videos folder")

if __name__ == "__main__":
    try:
        # Create demo video set
        created_videos = create_test_video_set()
        
        # Create documentation
        create_readme_for_demos()
        
        print("\n🎉 Demo video generation complete!")
        print("📂 Check the 'demo_videos' folder")
        
    except Exception as e:
        print(f"❌ Error creating demo videos: {e}")
        print("💡 Make sure OpenCV is installed: pip install opencv-python")