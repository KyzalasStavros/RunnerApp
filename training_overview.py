#!/usr/bin/env python
"""
Training Overview - Complete Analysis

Combines all analysis tools and provides comprehensive overview
"""

import os
import json
import glob
from datetime import datetime
import subprocess
import sys


def run_complete_analysis():
    """Run all analysis tools and provide a comprehensive overview"""
    
    print("🏃‍♂️ COMPLETE TRAINING PLAN ANALYSIS")
    print("=" * 60)
    print(f"Analysis run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if smart watch data exists
    json_files = glob.glob("mi_data_extracted/training_data_extracted_*.json")
    has_actual_data = len(json_files) > 0
    
    print(f"\n📱 Smart Watch Data: {'✅ Available' if has_actual_data else '❌ Not found'}")
    if has_actual_data:
        latest_file = max(json_files)
        with open(latest_file, 'r') as f:
            data = json.load(f)
        print(f"   • {len(data)} training sessions extracted")
        print(f"   • Latest data: {latest_file}")
    else:
        print(f"   • Run 'python extract_watch_data.py --folder mi_data' to extract data")
    
    print(f"\n📊 Available Analysis Tools:")
    print(f"   1. 🔍 extract_watch_data.py - Extract data from smart watch images")
    print(f"   2. 📈 analyze_training_plan.py - Progressive overload analysis with fatigue modeling")
    print(f"   3. 🎯 compare_actual_vs_planned.py - Compare actual vs planned training")
    print(f"   4. 🏃‍♂️ main.py - Interactive training plan management")
    print(f"   5. 📋 training_overview.py - This summary script")
    
    # Check which tools exist
    print(f"\n🔧 Tool Status:")
    tools = [
        ('extract_watch_data.py', 'Smart watch data extraction'),
        ('analyze_training_plan.py', 'Training plan analysis'),
        ('compare_actual_vs_planned.py', 'Actual vs planned comparison'),
        ('main.py', 'Training plan manager'),
        ('src/training_plan.py', 'Core training plan module')
    ]
    
    for tool, description in tools:
        status = "✅" if os.path.exists(tool) else "❌"
        print(f"   {status} {tool} - {description}")
    
    # Run theoretical analysis
    print(f"\n📈 1. Running Training Plan Analysis...")
    try:
        result = subprocess.run([sys.executable, 'analyze_training_plan.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Training plan analysis completed")
            # Show key metrics from output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Total distance' in line or 'Average fatigue' in line or 'Progressive overload' in line:
                    print(f"   📊 {line.strip()}")
        else:
            print(f"   ❌ Error: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Failed to run analysis: {e}")
    
    # Run actual vs planned comparison if data exists
    if has_actual_data:
        print(f"\n🎯 2. Running Actual vs Planned Comparison...")
        try:
            result = subprocess.run([sys.executable, 'compare_actual_vs_planned.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Actual vs planned comparison completed")
                print("   📊 Check training_progress_analysis.png for visualizations")
            else:
                print(f"   ❌ Error: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Failed to run comparison: {e}")
    else:
        print(f"\n🎯 2. Actual vs Planned Comparison:")
        print("   ⏳ Waiting for smart watch data...")
        print("   💡 Take screenshots of your completed workouts and run:")
        print("      python extract_watch_data.py --folder mi_data")
    
    # Summary and recommendations
    print(f"\n📋 Summary & Recommendations:")
    print(f"   • Training plan uses conservative progressive overload")
    print(f"   • Heart rate zones optimized for base building")
    print(f"   • 3 days/week schedule allows proper recovery")
    
    if has_actual_data:
        print(f"   • Continue monitoring actual vs planned metrics")
        print(f"   • Use visualization to track progress trends")
    else:
        print(f"   • Start collecting actual workout data for comparison")
        print(f"   • Use Mi Fitness app screenshots for data extraction")
    
    print(f"\n🎯 Next Steps:")
    if not has_actual_data:
        print(f"   1. Complete your first training session")
        print(f"   2. Take a screenshot of the workout summary in Mi Fitness")
        print(f"   3. Save it as mi_data/Session_W1_D1.JPG")
        print(f"   4. Run: python extract_watch_data.py --folder mi_data")
    else:
        print(f"   1. Continue following your training plan")
        print(f"   2. Extract data after each session")
        print(f"   3. Monitor trends in the progress visualization")
        print(f"   4. Adjust intensity if heart rate consistently too high")
    
    print(f"\n" + "=" * 60)
    print(f"Analysis complete! 🏃‍♂️💪")


if __name__ == "__main__":
    run_complete_analysis()
