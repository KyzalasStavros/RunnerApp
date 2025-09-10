#!/usr/bin/env python3
"""
Streamlit Entry Point for Training Plan Dashboard
This file serves as the main entry point for Streamlit Cloud deployment
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the dashboard
from dashboard_app.training_dashboard import main

if __name__ == "__main__":
    main()
