# Network Troubleshooting for Email Setup
# Diagnose and fix SMTP connection issues

import socket
import smtplib
import ssl
import os

def test_internet_connection():
    """Test basic internet connectivity"""
    print("🌐 Testing Internet Connection...")
    
    try:
        # Test DNS resolution
        socket.gethostbyname("www.google.com")
        print("✅ Internet connection: OK")
        return True
    except socket.gaierror:
        print("❌ Internet connection: FAILED")
        print("💡 Check your internet connection and try again")
        return False

def test_smtp_port_access():
    """Test if SMTP ports are accessible"""
    print("🔌 Testing SMTP Port Access...")
    
    smtp_servers = [
        ("smtp.gmail.com", 587, "Gmail TLS"),
        ("smtp.gmail.com", 465, "Gmail SSL"),
        ("smtp.gmail.com", 25, "Gmail Basic")
    ]
    
    working_configs = []
    
    for server, port, name in smtp_servers:
        try:
            print(f"   Testing {name} ({server}:{port})...")
            sock = socket.create_connection((server, port), timeout=10)
            sock.close()
            print(f"   ✅ {name}: Port {port} is accessible")
            working_configs.append((server, port, name))
        except Exception as e:
            print(f"   ❌ {name}: Port {port} blocked - {type(e).__name__}")
    
    if working_configs:
        print(f"\n✅ Found {len(working_configs)} working SMTP configurations")
        return working_configs
    else:
        print("\n❌ All SMTP ports are blocked")
        return []

def test_dns_resolution():
    """Test DNS resolution for Gmail SMTP"""
    print("🔍 Testing DNS Resolution...")
    
    try:
        ip = socket.gethostbyname("smtp.gmail.com")
        print(f"✅ smtp.gmail.com resolves to: {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        print("💡 Try using Google DNS (8.8.8.8, 8.8.4.4)")
        return False

def test_alternative_smtp():
    """Test with alternative SMTP settings"""
    print("🔄 Testing Alternative SMTP Connection...")
    
    # Read credentials from .env
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    config = {}
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key] = value
    
    email = config.get('SENDER_EMAIL')
    password = config.get('SENDER_PASSWORD')
    
    if not email or not password:
        print("❌ Email credentials not found in .env")
        return False
    
    # Try different configurations
    configurations = [
        {"server": "smtp.gmail.com", "port": 587, "tls": True, "name": "Gmail TLS"},
        {"server": "smtp.gmail.com", "port": 465, "tls": False, "name": "Gmail SSL"},
    ]
    
    for config_item in configurations:
        try:
            print(f"   Trying {config_item['name']}...")
            
            if config_item['tls']:
                # TLS connection
                server = smtplib.SMTP(config_item['server'], config_item['port'])
                server.starttls()
            else:
                # SSL connection
                server = smtplib.SMTP_SSL(config_item['server'], config_item['port'])
            
            server.login(email, password)
            server.quit()
            
            print(f"   ✅ {config_item['name']}: Authentication successful!")
            
            # Update .env with working configuration
            update_env_config(config_item)
            return True
            
        except Exception as e:
            print(f"   ❌ {config_item['name']}: {type(e).__name__} - {e}")
    
    return False

def update_env_config(working_config):
    """Update .env file with working SMTP configuration"""
    print(f"📝 Updating .env with working configuration...")
    
    # Read current .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Update SMTP settings
    updated_lines = []
    for line in lines:
        if line.startswith('SMTP_SERVER='):
            updated_lines.append(f'SMTP_SERVER={working_config["server"]}\n')
        elif line.startswith('SMTP_PORT='):
            updated_lines.append(f'SMTP_PORT={working_config["port"]}\n')
        else:
            updated_lines.append(line)
    
    # Write back
    with open('.env', 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ .env file updated with working configuration")

def suggest_network_fixes():
    """Suggest network troubleshooting steps"""
    print("\n🔧 NETWORK TROUBLESHOOTING STEPS:")
    print("=" * 50)
    
    print("\n1. 🔥 FIREWALL ISSUES:")
    print("   • Temporarily disable Windows Firewall")
    print("   • Add exception for Python/Streamlit")
    print("   • Check corporate firewall settings")
    
    print("\n2. 🌐 DNS ISSUES:")
    print("   • Change DNS to Google: 8.8.8.8, 8.8.4.4")
    print("   • Flush DNS: ipconfig /flushdns")
    print("   • Try different network (mobile hotspot)")
    
    print("\n3. 🏢 CORPORATE/ISP BLOCKING:")
    print("   • Contact IT department about SMTP access")
    print("   • Try from personal network/mobile hotspot")
    print("   • Check if ISP blocks outgoing SMTP")
    
    print("\n4. 📧 ALTERNATIVE EMAIL PROVIDERS:")
    print("   • Try Outlook: smtp-mail.outlook.com:587")
    print("   • Try Yahoo: smtp.mail.yahoo.com:587")
    print("   • Use email service with API (SendGrid, Mailgun)")
    
    print("\n5. 🔒 WINDOWS SECURITY:")
    print("   • Run as Administrator")
    print("   • Check Windows Defender settings")
    print("   • Temporarily disable antivirus")

def create_offline_mode():
    """Create offline mode configuration"""
    print("📴 Setting up OFFLINE MODE...")
    
    # Update .env to disable email
    offline_config = """# Violence Detection System - OFFLINE MODE
# Email alerts disabled due to network issues

# Email Configuration (DISABLED)
SMTP_SERVER=disabled
SMTP_PORT=0
SENDER_EMAIL=offline@localhost
SENDER_PASSWORD=disabled
NOTIFICATION_EMAIL=disabled

# Model Configuration
MODEL_PATH=models/best_mobilenet_bilstm.h5
CONFIDENCE_THRESHOLD=0.8
SEQUENCE_LENGTH=16
IMAGE_SIZE=64

# Application Settings - OFFLINE MODE
DEBUG_MODE=True
EMAIL_ENABLED=False
"""
    
    with open('.env', 'w') as f:
        f.write(offline_config)
    
    print("✅ Offline mode configured")
    print("🔄 Restart your app: streamlit run app.py")
    print("📱 Your app will work without email alerts")

def main():
    """Main network troubleshooting function"""
    print("🛡️ Violence Detection System - Network Troubleshooting")
    print("=" * 60)
    
    # Step 1: Basic connectivity
    if not test_internet_connection():
        print("\n❌ Fix internet connection first!")
        return
    
    # Step 2: DNS resolution
    if not test_dns_resolution():
        suggest_network_fixes()
        return
    
    # Step 3: Port access
    working_configs = test_smtp_port_access()
    
    if not working_configs:
        print("\n❌ SMTP ports are blocked by firewall/network")
        suggest_network_fixes()
        
        # Offer offline mode
        print("\n🤔 Would you like to continue WITHOUT email alerts?")
        choice = input("Enter 'y' for offline mode, 'n' to troubleshoot: ").lower()
        
        if choice == 'y':
            create_offline_mode()
        else:
            suggest_network_fixes()
        return
    
    # Step 4: Test SMTP authentication
    print(f"\n📧 Testing SMTP Authentication...")
    if test_alternative_smtp():
        print("\n🎉 EMAIL SETUP SUCCESSFUL!")
        print("📧 Try sending a test email now")
        print("🔄 Restart your app: streamlit run app.py")
    else:
        print("\n❌ SMTP authentication failed")
        print("💡 Double-check your Gmail app password")
        
        # Show current config
        print("\n📋 Current email settings:")
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if 'EMAIL' in line or 'SMTP' in line:
                        if 'PASSWORD' in line:
                            key, value = line.strip().split('=', 1)
                            print(f"   {key}=***hidden***")
                        else:
                            print(f"   {line.strip()}")

if __name__ == "__main__":
    main()