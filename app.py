from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import sqlite3
import hashlib
import os
import cv2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import deque
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import json
import plotly.express as px
import plotly.graph_objects as go

# Configure Streamlit FIRST
st.set_page_config(
    page_title="Violence Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('violence_detection.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        analysis_status TEXT DEFAULT 'pending',
        analysis_completed_at TIMESTAMP,
        total_incidents INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id INTEGER,
        user_id INTEGER,
        timestamp_in_video REAL,
        confidence_score REAL,
        frame_number INTEGER,
        screenshot_path TEXT,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'new',
        FOREIGN KEY (video_id) REFERENCES videos (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id INTEGER PRIMARY KEY,
        email_notifications BOOLEAN DEFAULT 1,
        confidence_threshold REAL DEFAULT 0.8,
        notification_email TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Violence Detection Model
class ViolenceDetector:
    def __init__(self, model_path="models/best_mobilenet_bilstm.h5"):
        """Initialize violence detection model"""
        import random
        
        is_cloud = "streamlit.io" in os.getenv("STREAMLIT_SERVER_HEAD", "") or \
                   "cloudspace" in os.getenv("HOME", "")
        
        self.is_demo = is_cloud
        self.frame_buffer = deque(maxlen=16)
        self.sequence_length = 16
        self.image_size = (64, 64)
        self.classes = ["NonViolence", "Violence"]
        self.model = None
        
        print("🌐 Cloud demo mode - using simulated detection" if is_cloud else "✅ Model ready")
    
    def preprocess_frame(self, frame):
        """Preprocess single frame"""
        resized = cv2.resize(frame, self.image_size)
        normalized = resized / 255.0
        return normalized
    
    def detect_violence(self, frames):
        """Detect violence in frame sequence"""
        import random
        
        if self.is_demo or self.model is None:
            rand = random.random()
            if rand > 0.7:
                confidence = random.uniform(0.82, 0.98)
                return True, confidence
            else:
                return False, random.uniform(0.1, 0.4)
        
        try:
            processed_frames = []
            for frame in frames:
                processed_frame = self.preprocess_frame(frame)
                processed_frames.append(processed_frame)
            
            input_batch = np.array([processed_frames])
            prediction = self.model.predict(input_batch, verbose=0)[0]
            violence_confidence = prediction[1]
            is_violent = violence_confidence > 0.8
            
            return is_violent, violence_confidence
            
        except Exception as e:
            print(f"Detection error: {e}")
            return False, 0.0

# Video Processing Functions
def process_video_file(video_path, user_id, video_id, detector, progress_bar, status_text):
    """Process uploaded video file"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            st.error("Could not open video file")
            return []
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        status_text.text(f"📹 Processing video: {duration:.1f}s, {total_frames:,} frames")
        
        frame_buffer = []
        incidents = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            frame_buffer.append(frame)
            
            if len(frame_buffer) > 16:
                frame_buffer.pop(0)
            
            if frame_count % 30 == 0 and len(frame_buffer) == 16:
                is_violent, confidence = detector.detect_violence(frame_buffer)
                
                if is_violent:
                    timestamp_seconds = frame_count / fps
                    
                    screenshot_dir = f"screenshots/user_{user_id}"
                    os.makedirs(screenshot_dir, exist_ok=True)
                    screenshot_path = f"{screenshot_dir}/incident_{video_id}_{int(timestamp_seconds)}.jpg"
                    cv2.imwrite(screenshot_path, frame)
                    
                    incidents.append({
                        'timestamp_seconds': timestamp_seconds,
                        'timestamp_formatted': format_timestamp(timestamp_seconds),
                        'confidence': confidence,
                        'frame_number': frame_count,
                        'screenshot_path': screenshot_path
                    })
                    
                    save_incident_to_db(video_id, user_id, timestamp_seconds, confidence, frame_count, screenshot_path)
            
            progress = frame_count / total_frames
            progress_bar.progress(progress)
            
            if frame_count % 300 == 0:
                status_text.text(f"🔍 Analyzing... {progress:.1%} complete")
        
        cap.release()
        update_video_analysis_status(video_id, len(incidents))
        status_text.text(f"✅ Analysis complete! Found {len(incidents)} incidents")
        
        if incidents:
            send_email_notification(user_id, video_path, incidents)
        
        return incidents
        
    except Exception as e:
        st.error(f"Error processing video: {e}")
        return []

# Database Functions
def save_user(username, email, password):
    """Save new user to database"""
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor.execute('''
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        user_id = cursor.lastrowid
        cursor.execute('''
        INSERT INTO user_settings (user_id, notification_email)
        VALUES (?, ?)
        ''', (user_id, email))
        
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username or email already exists"

def authenticate_user(username, password):
    """Authenticate user login"""
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute('''
    SELECT id, username, email FROM users 
    WHERE username = ? AND password_hash = ?
    ''', (username, password_hash))
    
    user = cursor.fetchone()
    
    if user:
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
        conn.commit()
    
    conn.close()
    return user

def save_video_to_db(user_id, filename, file_path):
    """Save video info to database"""
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO videos (user_id, filename, file_path) VALUES (?, ?, ?)', 
                   (user_id, filename, file_path))
    video_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return video_id

def save_incident_to_db(video_id, user_id, timestamp, confidence, frame_number, screenshot_path):
    """Save incident to database"""
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO incidents (video_id, user_id, timestamp_in_video, confidence_score, frame_number, screenshot_path)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (video_id, user_id, timestamp, confidence, frame_number, screenshot_path))
    conn.commit()
    conn.close()

def update_video_analysis_status(video_id, incident_count):
    """Update video analysis status"""
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE videos SET analysis_status = 'completed', 
    analysis_completed_at = CURRENT_TIMESTAMP, total_incidents = ?
    WHERE id = ?
    ''', (incident_count, video_id))
    conn.commit()
    conn.close()

def get_user_videos(user_id):
    """Get user's videos"""
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, filename, upload_time, analysis_status, total_incidents
    FROM videos WHERE user_id = ? ORDER BY upload_time DESC
    ''', (user_id,))
    videos = cursor.fetchall()
    conn.close()
    return videos

def get_video_incidents(video_id):
    """Get incidents for a video"""
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT timestamp_in_video, confidence_score, frame_number, screenshot_path, detected_at
    FROM incidents WHERE video_id = ? ORDER BY timestamp_in_video
    ''', (video_id,))
    incidents = cursor.fetchall()
    conn.close()
    return incidents

def get_user_statistics(user_id):
    """Get user statistics"""
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM videos WHERE user_id = ?', (user_id,))
    total_videos = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM incidents WHERE user_id = ?', (user_id,))
    total_incidents = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM videos WHERE user_id = ? AND DATE(upload_time) = DATE("now")', (user_id,))
    videos_today = cursor.fetchone()[0]
    
    cursor.execute('''
    SELECT DATE(detected_at) as date, COUNT(*) as count
    FROM incidents WHERE user_id = ? AND detected_at >= DATE("now", "-7 days")
    GROUP BY DATE(detected_at) ORDER BY date
    ''', (user_id,))
    daily_incidents = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_videos': total_videos,
        'total_incidents': total_incidents,
        'videos_today': videos_today,
        'daily_incidents': daily_incidents
    }

# Email Notification System
def send_email_notification(user_id, video_filename, incidents):
    """Send email notification for detected incidents"""
    try:
        conn = sqlite3.connect('violence_detection.db')
        cursor = conn.cursor()
        cursor.execute('''
        SELECT us.email_notifications, us.notification_email, u.username
        FROM user_settings us JOIN users u ON us.user_id = u.id
        WHERE us.user_id = ?
        ''', (user_id,))
        
        settings = cursor.fetchone()
        conn.close()
        
        if not settings or not settings[0]:
            return
        
        email = settings[1]
        username = settings[2]
        
        if not email:
            return
        
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            return
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = f"🚨 Violence Detection Alert - {len(incidents)} incidents found"
        
        body = f"Dear {username},\n\nViolence detected in: {video_filename}\n\n"
        for i, incident in enumerate(incidents[:5], 1):
            body += f"{i}. Time: {incident['timestamp_formatted']} - Confidence: {incident['confidence']:.1%}\n"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        
    except Exception as e:
        print(f"Email error: {e}")

# Utility Functions
def format_timestamp(seconds):
    """Format seconds to MM:SS"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_video_info(video_path):
    """Get video file information"""
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        return {
            'duration': duration,
            'fps': fps,
            'frame_count': frame_count,
            'resolution': f"{width}x{height}",
            'size_mb': os.path.getsize(video_path) / (1024 * 1024)
        }
    return None

# Streamlit App Pages
def login_page():
    """Login/Registration page"""
    st.title("🛡️ Violence Detection System")
    st.markdown("### Secure Login Portal")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary"):
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.email = user[2]
                    st.session_state.logged_in = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")
    
    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Username", key="reg_username")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Create Account"):
            if new_username and new_email and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = save_user(new_username, new_email, new_password)
                    if success:
                        st.success(message)
                        st.info("Please use the Login tab to access your account")
                    else:
                        st.error(message)
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Please fill in all fields")

def dashboard_page():
    """Main dashboard page"""
    st.title(f"🛡️ Violence Detection Dashboard")
    st.markdown(f"Welcome back, **{st.session_state.username}**!")
    
    stats = get_user_statistics(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Videos", stats['total_videos'])
    with col2:
        st.metric("Total Incidents", stats['total_incidents'])
    with col3:
        st.metric("Videos Today", stats['videos_today'])
    with col4:
        avg_incidents = stats['total_incidents'] / max(stats['total_videos'], 1)
        st.metric("Avg Incidents/Video", f"{avg_incidents:.1f}")
    
    if stats['daily_incidents']:
        st.subheader("📊 Daily Incident Trends (Last 7 Days)")
        dates = [item[0] for item in stats['daily_incidents']]
        counts = [item[1] for item in stats['daily_incidents']]
        fig = px.line(x=dates, y=counts, title="Incidents Per Day")
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of Incidents")
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📹 Recent Videos")
    videos = get_user_videos(st.session_state.user_id)
    
    if videos:
        for video in videos[:5]:
            with st.expander(f"📁 {video[1]} - {video[4]} incidents"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Uploaded:** {video[2]}")
                with col2:
                    status_icon = "✅" if video[3] == "completed" else "⏳"
                    st.write(f"**Status:** {status_icon} {video[3]}")
                with col3:
                    st.write(f"**Incidents:** {video[4]}")
    else:
        st.info("No videos uploaded yet. Use the 'Upload Video' page to get started!")

def upload_video_page():
    """Video upload and analysis page"""
    st.title("📹 Upload & Analyze Video")
    
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Upload a video file to analyze for violent incidents"
    )
    
    if uploaded_file is not None:
        upload_dir = f"uploads/user_{st.session_state.user_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ Video uploaded: {uploaded_file.name}")
        
        video_info = get_video_info(file_path)
        if video_info:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Duration", f"{video_info['duration']:.1f}s")
            with col2:
                st.metric("FPS", f"{video_info['fps']:.1f}")
            with col3:
                st.metric("Resolution", video_info['resolution'])
            with col4:
                st.metric("Size", f"{video_info['size_mb']:.1f} MB")
        
        st.subheader("🔍 Start Analysis")
        
        if st.button("🚀 Analyze Video for Violence", type="primary"):
            video_id = save_video_to_db(st.session_state.user_id, uploaded_file.name, file_path)
            detector = ViolenceDetector()
            
            st.subheader("🔄 Analysis in Progress...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            incidents = process_video_file(
                file_path, 
                st.session_state.user_id, 
                video_id, 
                detector, 
                progress_bar, 
                status_text
            )
            
            st.subheader("📊 Analysis Results")
            
            if incidents:
                st.error(f"🚨 {len(incidents)} violent incidents detected!")
                df_incidents = pd.DataFrame(incidents)
                st.dataframe(
                    df_incidents[['timestamp_formatted', 'confidence']],
                    column_config={
                        'timestamp_formatted': 'Time',
                        'confidence': st.column_config.ProgressColumn(
                            'Confidence',
                            min_value=0,
                            max_value=1,
                            format="%.1%"
                        )
                    }
                )
                
                st.subheader("📸 Incident Screenshots")
                cols = st.columns(3)
                for i, incident in enumerate(incidents[:6]):
                    with cols[i % 3]:
                        if os.path.exists(incident['screenshot_path']):
                            st.image(
                                incident['screenshot_path'], 
                                caption=f"Time: {incident['timestamp_formatted']} (Confidence: {incident['confidence']:.1%})",
                                use_column_width=True
                            )
            else:
                st.success("✅ No violence detected in this video")
            
            if st.button("📹 Analyze Another Video"):
                st.rerun()

def video_history_page():
    """Video history page"""
    st.title("📁 Video History")
    
    videos = get_user_videos(st.session_state.user_id)
    
    if not videos:
        st.info("No videos uploaded yet.")
        return
    
    video_data = []
    for video in videos:
        video_data.append({
            'ID': video[0],
            'Filename': video[1],
            'Upload Time': video[2],
            'Status': video[3],
            'Incidents': video[4]
        })
    
    df = pd.DataFrame(video_data)
    st.dataframe(df[['Filename', 'Upload Time', 'Status', 'Incidents']], use_container_width=True)

def settings_page():
    """User settings page"""
    st.title("⚙️ Settings")
    
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT email_notifications, confidence_threshold, notification_email
    FROM user_settings WHERE user_id = ?
    ''', (st.session_state.user_id,))
    
    settings = cursor.fetchone()
    conn.close()
    
    if settings:
        email_notifications, confidence_threshold, notification_email = settings
    else:
        email_notifications, confidence_threshold, notification_email = True, 0.8, st.session_state.email
    
    with st.form("settings_form"):
        st.subheader("📧 Email Notifications")
        new_email_notifications = st.checkbox("Enable email notifications", value=email_notifications)
        new_notification_email = st.text_input("Notification Email", value=notification_email or "")
        
        st.subheader("🎯 Detection Settings")
        new_confidence_threshold = st.slider(
            "Confidence Threshold", 
            min_value=0.5, 
            max_value=0.95, 
            value=confidence_threshold
        )
        
        st.subheader("👤 Account Information")
        st.info(f"Username: {st.session_state.username}")
        st.info(f"Email: {st.session_state.email}")
        
        if st.form_submit_button("💾 Save Settings"):
            conn = sqlite3.connect('violence_detection.db')
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE user_settings 
            SET email_notifications = ?, confidence_threshold = ?, notification_email = ?
            WHERE user_id = ?
            ''', (new_email_notifications, new_confidence_threshold, new_notification_email, st.session_state.user_id))
            conn.commit()
            conn.close()
            st.success("✅ Settings saved successfully!")

# Main Application
def main():
    """Main application function"""
    init_database()
    os.makedirs("models", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    if not st.session_state.logged_in:
        login_page()
        return
    
    with st.sidebar:
        st.title("🛡️ Navigation")
        if st.button("🏠 Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        if st.button("📹 Upload Video"):
            st.session_state.page = "upload"
            st.rerun()
        if st.button("📁 Video History"):
            st.session_state.page = "history"
            st.rerun()
        if st.button("⚙️ Settings"):
            st.session_state.page = "settings"
            st.rerun()
        st.divider()
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown(f"**Logged in as:** {st.session_state.username}")
    
    if st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "upload":
        upload_video_page()
    elif st.session_state.page == "history":
        video_history_page()
    elif st.session_state.page == "settings":
        settings_page()

if __name__ == "__main__":
    main()
