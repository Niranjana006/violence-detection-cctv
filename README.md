# 🛡️ Violence Detection System

A multi-user web application for detecting violence in video files using deep learning. Built with Streamlit, TensorFlow, and designed for Windows deployment.

## ✨ Features

- 🔐 **Multi-user Authentication** - Secure login system with user isolation
- 🎬 **Video File Analysis** - Upload and analyze MP4, AVI, MOV, MKV files
- 🤖 **AI-powered Detection** - Uses CNN+BiLSTM model for accurate violence detection
- 📧 **Email Alerts** - Automatic notifications when violence is detected
- 📊 **Analytics Dashboard** - User-specific statistics and trends
- 📱 **Web Interface** - Easy-to-use browser-based dashboard
- 💾 **Progress Tracking** - Monitor analysis history and results
- 🎯 **Customizable Settings** - Adjust detection sensitivity and notifications

## 🚀 Quick Start (Windows)

### Method 1: One-Click Start (Recommended)
1. **Download** this folder to your computer
2. **Copy your model** to `models/best_mobilenet_bilstm.h5`
3. **Double-click** `start.bat`
4. **Wait** for automatic setup (first time only)
5. **Open browser** to http://localhost:8501

### Method 2: Manual Setup
1. Install Python 3.8+ from https://python.org
2. Open Command Prompt in this folder
3. Run: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`

## 📁 Folder Structure

```
violence_detection_system/
├── 📄 app.py                    # Main application
├── 🚀 start.bat                 # Windows startup script
├── 📋 requirements.txt          # Python dependencies
├── ⚙️ config_template.env       # Configuration template
├── 📚 README.md                 # This file
├── 🤖 models/                   # AI models folder
│   └── best_mobilenet_bilstm.h5 # Your trained model (ADD THIS)
├── 📁 uploads/                  # User uploaded videos
├── 📸 screenshots/              # Alert screenshots
├── 🗄️ violence_detection.db     # SQLite database (auto-created)
└── 🐍 venv/                     # Virtual environment (auto-created)
```

## 🔧 Setup Instructions

### Step 1: Add Your Model
```bash
# Copy your trained model file to:
models/best_mobilenet_bilstm.h5
```

### Step 2: Configure Email (Optional)
1. Copy `config_template.env` to `.env`
2. Edit `.env` with your email settings:
```env
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

### Step 3: Start the System
- **Windows**: Double-click `start.bat`
- **Manual**: Run `streamlit run app.py`

## 👥 User Guide

### Creating an Account
1. Open http://localhost:8501
2. Click "Register" tab
3. Enter username, email, password
4. Click "Create Account"
5. Use "Login" tab to access your account

### Analyzing Videos
1. **Login** to your account
2. Go to **"Upload Video"** page
3. **Drag & drop** or click to select video file
4. **Review** video information (duration, size, etc.)
5. **Click** "Analyze Video for Violence"
6. **Wait** for analysis to complete
7. **Review** results with timestamps and screenshots

### Viewing Results
- **Dashboard**: Overview of your analysis statistics
- **Video History**: List of all analyzed videos
- **Click** on any video to see detailed incident reports
- **Screenshots** are automatically saved for each incident

### Managing Settings
- **Email Notifications**: Enable/disable alert emails
- **Detection Sensitivity**: Adjust confidence threshold
- **Account Info**: View your account details

## 📧 Email Configuration

### Gmail Setup (Recommended - Free)
1. Enable 2-factor authentication on your Google account
2. Go to Google Account > Security > App passwords
3. Generate an app password for "Violence Detection"
4. Use this 16-character password in your `.env` file

### Other Email Providers
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Outlook**: `smtp-mail.outlook.com:587`
- **Custom SMTP**: Contact your email provider for settings

## 🎯 Model Requirements

Your model should meet these specifications:
- **Input Shape**: (None, 16, 64, 64, 3) - 16 frames of 64x64 RGB images
- **Output Shape**: (None, 2) - Binary classification [NonViolence, Violence]
- **Format**: TensorFlow/Keras .h5 file
- **Preprocessing**: Frames normalized to 0-1 range

## 🔒 Security Features

- **Password Hashing**: SHA-256 encrypted passwords
- **User Isolation**: Each user only sees their own data
- **Session Management**: Secure login sessions
- **File Isolation**: User files stored in separate directories
- **Database Security**: SQLite with proper constraints

## 📊 Performance

- **Processing Speed**: ~30-50 FPS depending on hardware
- **Memory Usage**: ~500MB-2GB depending on video size
- **File Size Limits**: Up to 500MB per video (configurable)
- **Concurrent Users**: Supports multiple simultaneous users

## 🛠️ Troubleshooting

### Common Issues

**1. Model Not Found Error**
```
❌ Error: Model file not found
✅ Solution: Copy your model to models/best_mobilenet_bilstm.h5
```

**2. Port Already in Use**
```
❌ Error: Port 8501 is already in use
✅ Solution: 
   - Close other Streamlit applications
   - Or change port: streamlit run app.py --server.port 8502
```

**3. Email Not Sending**
```
❌ Error: Failed to send email
✅ Solutions:
   - Check .env file configuration
   - Verify Gmail app password
   - Test with: python -c "import smtplib; print('SMTP available')"
```

**4. Video Upload Fails**
```
❌ Error: Could not process video
✅ Solutions:
   - Check file format (MP4, AVI, MOV, MKV)
   - Ensure file size < 500MB
   - Try converting video to MP4
```

**5. Python/Dependencies Issues**
```
❌ Error: Module not found
✅ Solutions:
   - Run: pip install -r requirements.txt
   - Use: python -m pip install streamlit
   - Check Python version: python --version (need 3.8+)
```

### Performance Issues

**Slow Video Processing**
- Use smaller video files (<100MB)
- Convert to lower resolution (720p instead of 4K)
- Ensure adequate RAM (4GB+ recommended)

**High Memory Usage**
- Process shorter videos (<5 minutes)
- Close other applications
- Restart the application periodically

## 🔄 Updates and Maintenance

### Updating the System
1. Download new version
2. Copy your `models/` and `.env` files to new version
3. Run the new `start.bat`

### Backing Up Data
Important files to backup:
- `violence_detection.db` (all user data)
- `models/best_mobilenet_bilstm.h5` (your trained model)
- `.env` (your configuration)
- `uploads/` folder (user videos)
- `screenshots/` folder (incident screenshots)

### Database Management
- Database file: `violence_detection.db`
- View data: Use SQLite browser or DB Browser for SQLite
- Reset database: Delete the .db file (will lose all data)

## 🆘 Support

### Getting Help
1. Check this README troubleshooting section
2. Verify all files are in correct locations
3. Check the console/terminal for error messages
4. Test with a small video file first

### System Requirements
- **OS**: Windows 10/11 (primary), Mac/Linux (compatible)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space minimum
- **Internet**: Required for initial setup and email alerts

### File Locations
- **Application**: http://localhost:8501
- **Database**: `violence_detection.db`
- **Logs**: Check console window
- **Uploads**: `uploads/user_[ID]/`
- **Screenshots**: `screenshots/user_[ID]/`

## 📄 License

This software is for educational and research purposes. Please ensure compliance with local laws regarding video analysis and privacy.

## 🎉 Getting Started

1. **Download** and extract this folder
2. **Copy** your model file to `models/`
3. **Double-click** `start.bat`
4. **Create** your account
5. **Upload** a test video
6. **Analyze** and view results!

**Welcome to the Violence Detection System! 🛡️**