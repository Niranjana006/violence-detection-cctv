🛡️ AI-Powered Violence Detection System

A multi-user web application that detects violent activity in videos using deep learning. Built with Streamlit, TensorFlow, and SQLite, and deployed on the cloud with real-time email alerts.

🌐 Live Application

👉 https://violence-detection-cctv-ebjp.onrender.com/

✨ Features

🔐 Multi-user authentication system

🎬 Upload and analyze MP4, AVI, MOV, MKV videos

🤖 Deep learning-based violence detection (CNN + BiLSTM)

📧 Real-time email alerts using Resend API

📊 User-specific analytics dashboard

📸 Automatic incident screenshot capture

🎯 Adjustable detection sensitivity

💾 Persistent video & incident history

🧠 System Workflow

User uploads video

Frames are extracted and preprocessed

16-frame sequences are fed into CNN + BiLSTM model

Model predicts violence probability

If threshold exceeded:

Incident stored in database

Screenshot captured

Email alert sent

Dashboard updated

🏗️ Tech Stack

Frontend: Streamlit

Backend: Python

AI Model: TensorFlow / Keras

Database: SQLite

Email Service: Resend API

Deployment: Render

🚀 Run Locally
1. Install Python

Python 3.8 or higher required.

2. Install dependencies
pip install -r requirements.txt
3. Add trained model

Place your model file here:

models/best_mobilenet_bilstm.h5
4. Configure environment variables

Create a .env file:

RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=onboarding@resend.dev
5. Start the application
streamlit run app.py

Open in browser:

http://localhost:8501
📧 Email Notification System

The system uses Resend HTTP API for sending alerts.

When violence is detected:

Incident timestamps are generated

Screenshots captured

User receives structured email alert

For production:

Use verified domain

Configure DKIM/SPF

Rotate API keys regularly

🎯 Model Requirements

Input shape: (None, 16, 64, 64, 3)

Output shape: (None, 2) → [NonViolence, Violence]

Format: TensorFlow/Keras .h5

Frames normalized between 0–1

📊 Performance

Processes video frames continuously

Supports multiple users

Stores incident history per user

Captures screenshots automatically

Cloud demo mode simulates detection if model unavailable

🔒 Security

SHA-256 password hashing

Per-user data isolation

Secure session handling

Environment variable-based secrets

No hardcoded credentials

🛠 Troubleshooting
Email not sending

Check RESEND_API_KEY

Ensure sender email is valid

Verify Render environment variables

Model not loading

Confirm model path in models/

Verify input/output shape

Port already in use
streamlit run app.py --server.port 8502
