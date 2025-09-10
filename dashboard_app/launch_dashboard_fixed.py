#!/usr/bin/env python3
"""
Reliable Training Dashboard Launcher
Fixed version that handles Streamlit setup properly
"""

import subprocess
import sys
import os
import time

def main():
    """Launch the training dashboard with proper setup"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(script_dir, "training_dashboard.py")
    
    print("🏃‍♂️ Starting Training Plan Dashboard...")
    print("Dashboard will be available at: http://localhost:8502")
    print("Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Use subprocess with proper input handling
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--server.port", "8502",
            "--server.headless", "true", 
            "--browser.gatherUsageStats", "false"
        ]
        
        # Start the process with stdin as empty input
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Send empty line to handle any prompts
        process.stdin.write("\n")
        process.stdin.flush()
        
        print("🎉 Dashboard is starting...")
        print("✅ Open your browser and go to: http://localhost:8502")
        print("⏳ If the page doesn't load immediately, wait 10-15 seconds and refresh")
        
        # Monitor the process
        try:
            while True:
                line = process.stdout.readline()
                if line:
                    if "Local URL:" in line:
                        print(f"🌐 {line.strip()}")
                    elif "error" in line.lower() or "exception" in line.lower():
                        print(f"⚠️  {line.strip()}")
                    elif "can now view" in line.lower():
                        print("✅ Dashboard is ready!")
                        
                if process.poll() is not None:
                    break
                    
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down dashboard...")
            process.terminate()
            process.wait()
            print("✅ Dashboard stopped successfully!")
            
    except FileNotFoundError:
        print("❌ Error: Streamlit not found!")
        print("Please install streamlit: pip install streamlit")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()
