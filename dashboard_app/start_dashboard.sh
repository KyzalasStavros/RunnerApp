#!/bin/bash
# Direct Streamlit Launch Script
# Alternative to the Python launcher

echo "🏃‍♂️ Starting Training Plan Dashboard..."
echo "Dashboard will open in your browser at: http://localhost:8501"
echo "Press Ctrl+C to stop the dashboard"
echo "-" * 50

cd "$(dirname "$0")"
../.venv/bin/streamlit run training_dashboard.py \
    --server.port 8501 \
    --server.headless false \
    --browser.gatherUsageStats false
