# Quick Database Fix Script
# Run this to fix the database schema error

import sqlite3
import os

def fix_database():
    """Fix the database schema by adding missing columns"""
    print("🔧 Fixing database schema...")
    
    # Connect to database
    conn = sqlite3.connect('violence_detection.db')
    cursor = conn.cursor()
    
    try:
        # Check if last_login column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'last_login' not in columns:
            print("📝 Adding missing last_login column...")
            cursor.execute('ALTER TABLE users ADD COLUMN last_login TIMESTAMP')
            print("✅ Added last_login column")
        else:
            print("✅ last_login column already exists")
        
        # Commit changes
        conn.commit()
        print("✅ Database schema fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing database: {e}")
        print("💡 Deleting database to recreate fresh...")
        conn.close()
        
        # Delete and recreate database
        if os.path.exists('violence_detection.db'):
            os.remove('violence_detection.db')
            print("✅ Old database deleted - will recreate automatically")
    
    finally:
        if conn:
            conn.close()

def create_env_file():
    """Create .env file from template"""
    print("📧 Setting up email configuration...")
    
    if os.path.exists('config_template.env') and not os.path.exists('.env'):
        # Copy template to .env
        with open('config_template.env', 'r') as template:
            content = template.read()
        
        with open('.env', 'w') as env_file:
            env_file.write(content)
        
        print("✅ Created .env file from template")
        print("⚠️  Edit .env file to add your email settings (optional)")
    elif os.path.exists('.env'):
        print("✅ .env file already exists")
    else:
        print("⚠️  config_template.env not found - creating basic .env")
        with open('.env', 'w') as env_file:
            env_file.write("""# Email Configuration (Optional)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
""")
        print("✅ Created basic .env file")

if __name__ == "__main__":
    print("🛡️ Violence Detection System - Quick Fix")
    print("=" * 50)
    
    # Fix database schema
    fix_database()
    print()
    
    # Create .env file
    create_env_file()
    print()
    
    print("🎉 Fixes complete! Now run:")
    print("   streamlit run app.py")