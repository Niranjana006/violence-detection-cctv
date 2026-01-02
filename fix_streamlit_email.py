# Streamlit App Email Integration Fix
# Fixes the missing email alerts during video analysis

import os
import re

def fix_streamlit_email_integration():
    """Fix the email integration in app.py"""
    print("🔧 Fixing Streamlit app email integration...")
    
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        return False
    
    try:
        # Read app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if email function exists and is properly integrated
        fixes_needed = []
        
        # Fix 1: Ensure .env loading
        if 'from dotenv import load_dotenv' not in content:
            print("📝 Adding dotenv import...")
            content = "from dotenv import load_dotenv\n" + content
            fixes_needed.append("Added dotenv import")
        
        if 'load_dotenv()' not in content:
            print("📝 Adding load_dotenv() call...")
            # Add after imports
            import_section = content.find('import')
            if import_section != -1:
                # Find end of imports
                lines = content.split('\n')
                insert_line = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_line = i + 1
                    elif line.strip() == '' or line.strip().startswith('#'):
                        continue
                    else:
                        break
                
                lines.insert(insert_line, '\n# Load environment variables')
                lines.insert(insert_line + 1, 'load_dotenv()\n')
                content = '\n'.join(lines)
                fixes_needed.append("Added load_dotenv() call")
        
        # Fix 2: Update send_email_notification function to use os.getenv
        email_function_pattern = r'def send_email_notification\([^)]+\):[^}]*?smtp_server = "smtp\.gmail\.com"[^}]*?sender_email = "your_email@gmail\.com"[^}]*?sender_password = "your_app_password"'
        
        if re.search(email_function_pattern, content, re.DOTALL):
            print("📝 Updating email function to use environment variables...")
            
            # Replace the hardcoded email function
            new_email_function = '''def send_email_notification(user_id, video_filename, incidents):
    """Send email notification for detected incidents"""
    try:
        # Get user settings
        conn = sqlite3.connect('violence_detection.db')
        cursor = conn.cursor()
        
        cursor.execute("""
    SELECT us.email_notifications, us.notification_email, u.username
    FROM user_settings us
    JOIN users u ON us.user_id = u.id
    WHERE us.user_id = ?
""", (user_id,))

        
        settings = cursor.fetchone()
        conn.close()
        
        if not settings or not settings[0]:  # Email notifications disabled
            print("📧 Email notifications disabled for user")
            return
        
        email = settings[1]
        username = settings[2]
        
        if not email:
            print("📧 No notification email set for user")
            return
        
        # Email configuration from environment variables
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            print("❌ Email configuration missing in .env file")
            return
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = f"🚨 Violence Detection Alert - {len(incidents)} incidents found"
        
        # Email body
        body = f"""
Dear {username},

Violence has been detected in your uploaded video: {video_filename}

📊 Detection Summary:
• Total incidents: {len(incidents)}
• Video file: {video_filename}
• Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🚨 Detected Incidents:
"""
        
        for i, incident in enumerate(incidents[:5], 1):  # Show first 5 incidents
            timestamp = incident.get('timestamp_formatted', 'Unknown')
            confidence = incident.get('confidence', 0)
            body += f"   {i}. Time: {timestamp} - Confidence: {confidence:.1%}\\n"
        
        if len(incidents) > 5:
            body += f"   ... and {len(incidents) - 5} more incidents\\n"
        
        body += f"""

Please login to the Violence Detection System to review the full analysis.

This is an automated alert from the Violence Detection System.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print(f"📧 Sending email alert to {email}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        
        print(f"✅ Email notification sent to {email}")
        
    except Exception as e:
        print(f"❌ Failed to send email notification: {e}")'''
            
            # Replace the function
            content = re.sub(
                r'def send_email_notification\([^}]*?\n        print\(f"❌ Failed to send email notification: \{e\}"\)',
                new_email_function,
                content,
                flags=re.DOTALL
            )
            fixes_needed.append("Updated email function to use .env variables")
        
        # Fix 3: Ensure email is called after incidents are found
        if 'if incidents:' in content and 'send_email_notification(' not in content.split('if incidents:')[1].split('else:')[0]:
            print("📝 Adding email notification call after incident detection...")
            
            # Find the incidents section and add email call
            incidents_pattern = r'(if incidents:.*?)(st\.error\(f"🚨 \{len\(incidents\)\} violent incidents detected!"\))'
            
            replacement = r'\1\2\n                    \n                    # Send email notification\n                    if os.path.exists(file_path):\n                        send_email_notification(st.session_state.user_id, uploaded_file.name, incidents)'
            
            content = re.sub(incidents_pattern, replacement, content, flags=re.DOTALL)
            fixes_needed.append("Added email notification call after incident detection")
        
        # Write back to file
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        if fixes_needed:
            print("✅ Applied fixes:")
            for fix in fixes_needed:
                print(f"   • {fix}")
            return True
        else:
            print("✅ No fixes needed - integration looks correct")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing app.py: {e}")
        return False

def create_env_loader():
    """Create a simple .env loader if python-dotenv is not available"""
    print("📝 Creating simple .env loader...")
    
    env_loader_code = '''
# Simple .env file loader (if python-dotenv not available)
def load_env_file():
    """Load environment variables from .env file"""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_env_file()
'''
    
    # Read app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add env loader if not present
    if 'load_env_file()' not in content:
        # Insert after imports
        lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_end = i + 1
        
        lines.insert(import_end, env_loader_code)
        content = '\n'.join(lines)
        
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added .env loader to app.py")

def test_streamlit_email_workflow():
    """Test if the email workflow is properly integrated"""
    print("🧪 Testing Streamlit email workflow integration...")
    
    # Check if .env file exists and has required variables
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return False
    
    # Read .env
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value
    
    required_vars = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
    missing_vars = [var for var in required_vars if var not in env_vars or not env_vars[var]]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables configured correctly")
    
    # Check database settings
    try:
        import sqlite3
        conn = sqlite3.connect('violence_detection.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, email_notifications, notification_email FROM user_settings WHERE user_id = 1")
        settings = cursor.fetchone()
        
        if settings and settings[1] and settings[2]:
            print(f"✅ User email settings configured: {settings[2]}")
        else:
            print("❌ User email settings not configured")
            # Fix user settings
            cursor.execute("SELECT email FROM users WHERE id = 1")
            user_email = cursor.fetchone()
            if user_email:
                cursor.execute('''
                INSERT OR REPLACE INTO user_settings 
                (user_id, email_notifications, notification_email)
                VALUES (1, 1, ?)
                ''', (user_email[0],))
                conn.commit()
                print(f"✅ Fixed user email settings: {user_email[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database settings error: {e}")
        return False
    
    print("✅ Streamlit email workflow should now work!")
    return True

def main():
    """Main fix function"""
    print("🛡️ Violence Detection System - Streamlit Email Fix")
    print("=" * 60)
    
    print("\n1️⃣ Fixing app.py email integration...")
    if fix_streamlit_email_integration():
        print("✅ App integration fixed")
    else:
        print("❌ Failed to fix app integration")
        return
    
    print("\n2️⃣ Adding environment loader...")
    create_env_loader()
    
    print("\n3️⃣ Testing email workflow...")
    if test_streamlit_email_workflow():
        print("✅ Email workflow ready")
    else:
        print("❌ Email workflow has issues")
    
    print("\n" + "=" * 60)
    print("🎉 STREAMLIT EMAIL FIX COMPLETE!")
    print("\n📋 Next steps:")
    print("1. 🔄 Restart your Streamlit app:")
    print("   streamlit run app.py")
    print("2. 📱 Login to your account")
    print("3. 📹 Upload and analyze a video")
    print("4. 📧 You should now receive email alerts!")
    
    print("\n💡 If you still don't get emails:")
    print("• Check spam/junk folder")
    print("• Verify Settings page has email notifications enabled")
    print("• Check terminal for email sending messages")

if __name__ == "__main__":
    main()