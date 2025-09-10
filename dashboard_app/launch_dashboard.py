#!/usr/bin/env python3
"""
Training Dashboard Launcher
Simple script to launch the Streamlit dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the training dashboard"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(script_dir, "training_dashboard.py")
    
    print("🏃‍♂️ Starting Training Plan Dashboard...")
    print("Dashboard will open in your browser automatically")
    print("Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()
