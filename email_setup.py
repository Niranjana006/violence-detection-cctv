from datetime import datetime
# Email Setup Guide for Violence Detection System
# Complete Gmail configuration for automatic alerts

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_config():
    """Test email configuration"""
    print("📧 Testing Email Configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("💡 Run: python email_setup.py to create configuration")
        return False
    
    # Read .env file
    email_config = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    email_config[key] = value
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
    
    # Check required fields
    required_fields = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
    missing_fields = []
    
    for field in required_fields:
        if field not in email_config or not email_config[field] or email_config[field] == f'your_{field.lower()}':
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing email configuration: {missing_fields}")
        print("💡 Please update your .env file with actual email settings")
        return False
    
    # Test email connection
    try:
        print("🔄 Testing SMTP connection...")
        server = smtplib.SMTP(email_config['SMTP_SERVER'], int(email_config['SMTP_PORT']))
        server.starttls()
        server.login(email_config['SENDER_EMAIL'], email_config['SENDER_PASSWORD'])
        server.quit()
        print("✅ Email configuration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        print("💡 Check your email credentials and app password")
        return False

def create_email_config():
    """Interactive email configuration setup"""
    print("🔧 Setting Up Email Configuration")
    print("=" * 40)
    
    print("\n📋 You'll need:")
    print("1. Gmail account")
    print("2. Gmail App Password (not your regular password)")
    print("3. Recipient email address")
    
    # Get user input
    sender_email = input("\n📧 Enter your Gmail address: ").strip()
    
    print("\n🔒 Gmail App Password Setup:")
    print("1. Go to https://myaccount.google.com/")
    print("2. Security → 2-Step Verification (enable if not done)")
    print("3. App passwords → Generate password for 'Violence Detection'")
    print("4. Copy the 16-character password")
    
    sender_password = input("\n🔑 Enter Gmail App Password: ").strip()
    notification_email = input("\n📨 Enter notification email (can be same): ").strip()
    
    # Create .env content
    env_content = f"""# Violence Detection System - Email Configuration

# Gmail SMTP Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL={sender_email}
SENDER_PASSWORD={sender_password}

# Notification Settings
NOTIFICATION_EMAIL={notification_email}

# Model Configuration
MODEL_PATH=models/best_mobilenet_bilstm.h5
CONFIDENCE_THRESHOLD=0.8
SEQUENCE_LENGTH=16
IMAGE_SIZE=64

# Application Settings
DEBUG_MODE=False
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ Email configuration saved to .env file")
        
        # Test the configuration
        if test_email_config():
            print("🎉 Email setup complete!")
            return True
        else:
            print("⚠️  Configuration saved but test failed")
            print("💡 Double-check your Gmail app password")
            return False
            
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def send_test_email():
    """Send a test email to verify setup"""
    print("📤 Sending Test Email...")
    
    # Read config
    if not os.path.exists('.env'):
        print("❌ No .env file found. Run email setup first.")
        return
    
    config = {}
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key] = value
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = config['SENDER_EMAIL']
        msg['To'] = config.get('NOTIFICATION_EMAIL', config['SENDER_EMAIL'])
        msg['Subject'] = "🛡️ Violence Detection System - Test Alert"
        
        body = """
        Violence Detection System Test Email
        
        ✅ Email configuration is working correctly!
        
        This is a test message to verify that your email alert system 
        is properly configured and functional.
        
        📊 System Status:
        • Email notifications: Enabled
        • SMTP connection: Successful
        • Test timestamp: """ + str(datetime.now()) + """
        
        You will receive similar alerts when violence is detected in uploaded videos.
        
        Best regards,
        Violence Detection System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(config['SMTP_SERVER'], int(config['SMTP_PORT']))
        server.starttls()
        server.login(config['SENDER_EMAIL'], config['SENDER_PASSWORD'])
        server.sendmail(config['SENDER_EMAIL'], config.get('NOTIFICATION_EMAIL', config['SENDER_EMAIL']), msg.as_string())
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📧 Check your inbox: {config.get('NOTIFICATION_EMAIL', config['SENDER_EMAIL'])}")
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")

def main():
    """Main email setup function"""
    print("🛡️ Violence Detection System - Email Setup")
    print("=" * 50)
    
    while True:
        print("\n🎯 Choose an option:")
        print("1. 🔧 Setup email configuration")
        print("2. 🧪 Test current configuration")
        print("3. 📤 Send test email")
        print("4. 📋 View current configuration")
        print("5. 🚪 Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            create_email_config()
        elif choice == '2':
            test_email_config()
        elif choice == '3':
            send_test_email()
        elif choice == '4':
            if os.path.exists('.env'):
                print("\n📋 Current .env configuration:")
                with open('.env', 'r') as f:
                    for line in f:
                        if 'PASSWORD' in line:
                            # Hide password
                            key, value = line.strip().split('=', 1)
                            print(f"{key}=***hidden***")
                        else:
                            print(line.strip())
            else:
                print("❌ No .env file found")
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()