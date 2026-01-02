# Quick Fix for Email Setup Bug
# Fixes the 'pd is not defined' error

import os
import re
from datetime import datetime

def fix_email_script():
    """Fix the pd.Timestamp bug in email_setup.py"""
    print("🔧 Fixing email script bug...")
    
    if not os.path.exists('email_setup.py'):
        print("❌ email_setup.py not found!")
        return False
    
    try:
        # Read the file
        with open('email_setup.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix the pandas timestamp issue
        if 'pd.Timestamp.now()' in content:
            print("📝 Fixing pandas timestamp...")
            content = content.replace('pd.Timestamp.now()', 'datetime.now()')
            
            # Add datetime import if not present
            if 'from datetime import datetime' not in content:
                content = 'from datetime import datetime\n' + content
            
            # Write back
            with open('email_setup.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed pandas timestamp issue")
            return True
        else:
            print("✅ No pandas issues found")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing file: {e}")
        return False

def send_test_email_fixed():
    """Send test email with fixed imports"""
    print("📤 Sending Test Email (Fixed)...")
    
    # Read .env config
    if not os.path.exists('.env'):
        print("❌ No .env file found")
        return False
    
    config = {}
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key] = value
    
    # Check required fields
    required = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
    for field in required:
        if field not in config or not config[field]:
            print(f"❌ Missing {field} in .env file")
            return False
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = config['SENDER_EMAIL']
        msg['To'] = config.get('NOTIFICATION_EMAIL', config['SENDER_EMAIL'])
        msg['Subject'] = "🛡️ Violence Detection System - Test Alert"
        
        # Email body with current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        body = f"""
Violence Detection System Test Email

✅ Email configuration is working correctly!

This is a test message to verify that your email alert system 
is properly configured and functional.

📊 System Status:
• Email notifications: Enabled
• SMTP connection: Successful  
• Test timestamp: {current_time}

You will receive similar alerts when violence is detected in uploaded videos.

Best regards,
Violence Detection System
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email with error handling
        print(f"🔄 Connecting to {config['SMTP_SERVER']}:{config['SMTP_PORT']}...")
        
        server = smtplib.SMTP(config['SMTP_SERVER'], int(config['SMTP_PORT']))
        server.set_debuglevel(1)  # Enable debug output
        server.starttls()
        
        print("🔐 Authenticating...")
        server.login(config['SENDER_EMAIL'], config['SENDER_PASSWORD'])
        
        print("📧 Sending email...")
        server.sendmail(
            config['SENDER_EMAIL'], 
            config.get('NOTIFICATION_EMAIL', config['SENDER_EMAIL']), 
            msg.as_string()
        )
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📧 Check your inbox: {config.get('NOTIFICATION_EMAIL', config['SENDER_EMAIL'])}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        print(f"💡 Error type: {type(e).__name__}")
        
        # Provide specific troubleshooting
        if "getaddrinfo failed" in str(e):
            print("🌐 Network connectivity issue - try mobile hotspot")
        elif "Authentication failed" in str(e):
            print("🔑 Check your Gmail app password")
        elif "Connection refused" in str(e):
            print("🔌 SMTP port blocked - try port 465")
        
        return False

if __name__ == "__main__":
    print("🛡️ Violence Detection System - Email Bug Fix")
    print("=" * 50)
    
    # Fix the script
    if fix_email_script():
        print("\n🧪 Testing email with fixed script...")
        send_test_email_fixed()
    
    print("\n💡 You can also run the fixed version:")
    print("   python email_setup.py")