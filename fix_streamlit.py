# Streamlit Version Fix Script
# Fixes the experimental_rerun deprecation error

import os
import re

def fix_streamlit_rerun():
    """Fix deprecated experimental_rerun calls"""
    print("🔧 Fixing Streamlit version compatibility...")
    
    app_file = "app.py"
    
    if not os.path.exists(app_file):
        print("❌ app.py not found!")
        return False
    
    try:
        # Read the file
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count occurrences
        old_count = content.count('st.experimental_rerun()')
        
        if old_count == 0:
            print("✅ No experimental_rerun calls found - already fixed!")
            return True
        
        # Replace all occurrences
        new_content = content.replace('st.experimental_rerun()', 'st.rerun()')
        
        # Write back to file
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Fixed {old_count} experimental_rerun calls")
        print("✅ Updated to st.rerun() for compatibility")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing file: {e}")
        return False

def check_streamlit_version():
    """Check Streamlit version"""
    try:
        import streamlit as st
        version = st.__version__
        print(f"📦 Streamlit version: {version}")
        
        # Parse version
        major, minor = map(int, version.split('.')[:2])
        
        if major >= 1 and minor >= 18:
            print("✅ Modern Streamlit version - using st.rerun()")
            return True
        else:
            print("⚠️  Older Streamlit version - might need st.experimental_rerun()")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check Streamlit version: {e}")
        return True  # Assume modern version

if __name__ == "__main__":
    print("🛡️ Violence Detection System - Streamlit Fix")
    print("=" * 50)
    
    # Check version
    modern_version = check_streamlit_version()
    print()
    
    # Fix the code
    if fix_streamlit_rerun():
        print("\n🎉 Fix complete! Now run:")
        print("   streamlit run app.py")
    else:
        print("\n❌ Fix failed - manual intervention needed")
        
    print("\n💡 If you still get errors, try:")
    print("   pip install streamlit --upgrade")