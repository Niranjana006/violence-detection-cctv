# Violence Detection System - Setup and Test Script
# Run this to verify your installation and configuration

import os
import sys
import sqlite3
import cv2
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'tensorflow', 
        'cv2',
        'numpy',
        'pandas',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
                print(f"✅ OpenCV {cv2.__version__}")
            elif package == 'tensorflow':
                import tensorflow as tf
                print(f"✅ TensorFlow {tf.__version__}")
            elif package == 'streamlit':
                import streamlit
                print(f"✅ Streamlit {streamlit.__version__}")
            elif package == 'numpy':
                import numpy as np
                print(f"✅ NumPy {np.__version__}")
            elif package == 'pandas':
                import pandas as pd
                print(f"✅ Pandas {pd.__version__}")
            elif package == 'plotly':
                import plotly
                print(f"✅ Plotly {plotly.__version__}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    return missing_packages

def check_model_file():
    """Check if model file exists"""
    model_path = "models/best_mobilenet_bilstm.h5"
    
    if os.path.exists(model_path):
        print(f"✅ Model file found: {model_path}")
        
        # Try to load the model
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(model_path)
            print(f"✅ Model loads successfully")
            print(f"   Input shape: {model.input_shape}")
            print(f"   Output shape: {model.output_shape}")
            return True
        except Exception as e:
            print(f"❌ Model file corrupt or incompatible: {e}")
            return False
    else:
        print(f"❌ Model file not found: {model_path}")
        print(f"   Please copy your trained model to this location")
        return False

def check_directories():
    """Check and create necessary directories"""
    directories = [
        "models",
        "uploads", 
        "screenshots"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}/")
        else:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Created directory: {directory}/")

def test_database():
    """Test database creation and operations"""
    try:
        conn = sqlite3.connect('test_violence_detection.db')
        cursor = conn.cursor()
        
        # Test table creation
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_users (
            id INTEGER PRIMARY KEY,
            username TEXT
        )
        ''')
        
        # Test insert
        cursor.execute("INSERT INTO test_users (username) VALUES (?)", ("test_user",))
        
        # Test select
        cursor.execute("SELECT * FROM test_users")
        result = cursor.fetchone()
        
        conn.close()
        os.remove('test_violence_detection.db')  # Clean up
        
        print("✅ Database operations work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_video_processing():
    """Test basic video processing capabilities"""
    try:
        # Test OpenCV video creation (synthetic test)
        import numpy as np
        
        # Create a test video file
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        test_video = cv2.VideoWriter('test_video.mp4', fourcc, 30.0, (64, 64))
        
        # Write some test frames
        for i in range(60):  # 2 seconds at 30 FPS
            frame = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
            test_video.write(frame)
        
        test_video.release()
        
        # Test reading the video
        cap = cv2.VideoCapture('test_video.mp4')
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Read a frame
            ret, frame = cap.read()
            if ret:
                print("✅ Video processing capabilities work")
                print(f"   Test video: {frame_count} frames at {fps} FPS")
                success = True
            else:
                print("❌ Could not read video frame")
                success = False
            
            cap.release()
        else:
            print("❌ Could not open test video file")
            success = False
        
        # Clean up
        if os.path.exists('test_video.mp4'):
            os.remove('test_video.mp4')
        
        return success
        
    except Exception as e:
        print(f"❌ Video processing test failed: {e}")
        return False

def check_email_config():
    """Check email configuration"""
    if os.path.exists('.env'):
        print("✅ Configuration file (.env) exists")
        
        with open('.env', 'r') as f:
            content = f.read()
            
        if 'SENDER_EMAIL=' in content and 'SENDER_PASSWORD=' in content:
            # Check if they're filled in
            lines = content.split('\n')
            email_set = False
            password_set = False
            
            for line in lines:
                if line.startswith('SENDER_EMAIL=') and '@' in line:
                    email_set = True
                if line.startswith('SENDER_PASSWORD=') and len(line.split('=')[1].strip()) > 5:
                    password_set = True
            
            if email_set and password_set:
                print("✅ Email configuration appears to be set up")
            else:
                print("⚠️  Email configuration exists but may need completion")
                print("   Please edit .env file with your email settings")
        else:
            print("⚠️  Email configuration incomplete in .env file")
    else:
        print("⚠️  No .env configuration file found")
        print("   Copy config_template.env to .env and configure email settings")

def create_test_user():
    """Create a test user account"""
    try:
        # Import the database functions from main app
        sys.path.append('.')
        
        # Simple test database setup
        conn = sqlite3.connect('violence_detection.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create test user
        import hashlib
        password_hash = hashlib.sha256("test123".encode()).hexdigest()
        
        cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
        ''', ("testuser", "test@example.com", password_hash))
        
        conn.commit()
        conn.close()
        
        print("✅ Test user created successfully")
        print("   Username: testuser")
        print("   Password: test123")
        print("   Email: test@example.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        return False

def main():
    """Main setup and test function"""
    print("=" * 60)
    print("🛡️  Violence Detection System - Setup & Test")
    print("=" * 60)
    print()
    
    # Check Python version
    print("🐍 Checking Python Version...")
    python_ok = check_python_version()
    print()
    
    # Check dependencies
    print("📦 Checking Dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"💡 Install with: pip install {' '.join(missing)}")
        print()
    else:
        print("✅ All dependencies installed")
    print()
    
    # Check directories
    print("📁 Checking Directories...")
    check_directories()
    print()
    
    # Check model file
    print("🤖 Checking Model File...")
    model_ok = check_model_file()
    print()
    
    # Test database
    print("🗄️  Testing Database...")
    db_ok = test_database()
    print()
    
    # Test video processing
    print("🎬 Testing Video Processing...")
    video_ok = test_video_processing()
    print()
    
    # Check email config
    print("📧 Checking Email Configuration...")
    check_email_config()
    print()
    
    # Create test user
    print("👤 Creating Test User...")
    user_ok = create_test_user()
    print()
    
    # Summary
    print("=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    
    all_checks = [
        ("Python Version", python_ok),
        ("Dependencies", len(missing) == 0),
        ("Model File", model_ok),
        ("Database", db_ok),
        ("Video Processing", video_ok),
        ("Test User", user_ok)
    ]
    
    passed = sum(1 for _, ok in all_checks if ok)
    total = len(all_checks)
    
    for check_name, ok in all_checks:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{check_name:20} {status}")
    
    print()
    print(f"Overall Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Setup complete! You're ready to start the application.")
        print("🚀 Run 'start.bat' or 'streamlit run app.py' to begin")
    else:
        print("⚠️  Some issues need to be resolved before starting")
        print("📚 Check the README.md file for troubleshooting")
    
    print()
    print("Next Steps:")
    print("1. Copy your model file to models/best_mobilenet_bilstm.h5")
    print("2. Configure email settings in .env file (optional)")
    print("3. Run start.bat to launch the application")
    print("4. Open http://localhost:8501 in your browser")

if __name__ == "__main__":
    main()