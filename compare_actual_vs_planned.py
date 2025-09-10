#!/usr/bin/env python3
"""
Training Data Analysis Comparison
Compares extracted smart watch data with training plan expectations
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the path to import training_plan
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from training_plan import TrainingPlan


def load_extracted_data(filename):
    """Load the extracted training data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        print("Please run the extract_watch_data.py script first.")
        return None


def analyze_actual_vs_planned():
    """Compare actual training data with the planned training"""
    
    # Load the most recent extracted data
    import glob
    json_files = glob.glob("mi_data_extracted/training_data_extracted_*.json")
    if not json_files:
        print("No extracted training data found. Please run extract_watch_data.py first.")
        return
    
    latest_file = max(json_files)
    print(f"Loading data from: {latest_file}")
    
    actual_data = load_extracted_data(latest_file)
    if not actual_data:
        return
    
    # Generate the current training plan
    trainer = TrainingPlan()
    
    # Get the training schedule structure
    # Since the training plan is session-based, let's create expected data structure
    expected_sessions = {
        (1, 1): {"run_min": 1.0, "walk_min": 2.0, "sets": 16},
        (1, 2): {"run_min": 1.0, "walk_min": 2.5, "sets": 14}, 
        (1, 3): {"run_min": 1.5, "walk_min": 2.0, "sets": 14}
    }
    
    print("\n" + "="*80)
    print("ACTUAL vs PLANNED TRAINING ANALYSIS")
    print("="*80)
    
    # Analyze each session
    for session in actual_data:
        week = session['week']
        day = session['day']
        
        print(f"\n📊 Week {week}, Day {day} Analysis:")
        print("-" * 40)
        
        # Find corresponding planned session
        session_key = (week, day)
        planned_session = expected_sessions.get(session_key)
        
        if planned_session:
            print(f"📋 Planned Session:")
            print(f"   Run/Walk: {planned_session['run_min']:.1f}min / {planned_session['walk_min']:.1f}min")
            print(f"   Sets: {planned_session['sets']}")
            
            total_time = (planned_session['run_min'] + planned_session['walk_min']) * planned_session['sets']
            print(f"   Total planned time: ~{total_time:.0f} min")
            
            # Calculate expected distance based on plan (assuming 12 km/h run, 6 km/h walk)
            run_distance = planned_session['run_min'] * planned_session['sets'] * 0.2  # 12 km/h = 0.2 km/min
            walk_distance = planned_session['walk_min'] * planned_session['sets'] * 0.1  # 6 km/h = 0.1 km/min
            expected_distance = run_distance + walk_distance
            print(f"   Expected distance: ~{expected_distance:.1f} km")
        
        print(f"\n⌚ Actual Session:")
        if session['duration']:
            actual_minutes = sum(int(x) * (60, 1, 1/60)[i] for i, x in enumerate(session['duration'].split(':')))
            print(f"   Duration: {session['duration']} ({actual_minutes:.0f} min)")
        else:
            print(f"   Duration: Not captured")
        
        if session['distance']:
            print(f"   Distance: {session['distance']} km")
        else:
            print(f"   Distance: Not captured")
            
        if session['avg_pace']:
            print(f"   Avg Pace: {session['avg_pace']} /km")
        
        if session['avg_hr']:
            print(f"   Avg HR: {session['avg_hr']} bpm")
            
            # Analyze HR zones
            avg_hr = int(session['avg_hr'])
            if avg_hr < 120:
                hr_zone = "🟢 Easy/Recovery (Good for walk intervals)"
            elif avg_hr < 140:
                hr_zone = "🟡 Moderate (Good overall intensity)"
            elif avg_hr < 160:
                hr_zone = "🟠 Hard (High intensity - may be too much)"
            else:
                hr_zone = "🔴 Very Hard (Too intense for base training)"
            
            print(f"   HR Zone: {hr_zone}")
        
        if session['steps']:
            print(f"   Steps: {session['steps']}")
        
        if session['calories']:
            print(f"   Calories: {session['calories']} kcal")
        
        # Comparison and recommendations
        print(f"\n💡 Analysis:")
        if session['avg_hr']:
            avg_hr = int(session['avg_hr'])
            if week == 1:
                if avg_hr > 150:
                    print(f"   ⚠️  HR {avg_hr} is quite high for Week 1 - plan may be too aggressive")
                elif avg_hr > 140:
                    print(f"   ⚠️  HR {avg_hr} is moderately high - monitor fatigue")
                else:
                    print(f"   ✅ HR {avg_hr} is good for base building")
            
            if day == 3 and avg_hr > 140:
                print(f"   ⚠️  Session 3 HR high - indicates cumulative fatigue")
    
    # Summary and recommendations
    print(f"\n" + "="*80)
    print("OVERALL ASSESSMENT & RECOMMENDATIONS")
    print("="*80)
    
    hr_values = [int(s['avg_hr']) for s in actual_data if s['avg_hr']]
    if hr_values:
        avg_hr_all = sum(hr_values) / len(hr_values)
        max_hr_session = max(hr_values)
        
        print(f"📈 Heart Rate Summary:")
        print(f"   Average HR across sessions: {avg_hr_all:.0f} bpm")
        print(f"   Highest session HR: {max_hr_session} bpm")
        
        if avg_hr_all > 145:
            print(f"\n🚨 RECOMMENDATION: Plan appears too aggressive")
            print(f"   • Average HR {avg_hr_all:.0f} is high for base training")
            print(f"   • Consider reducing interval duration or intensity")
            print(f"   • The conservative plan update should help")
        elif avg_hr_all > 130:
            print(f"\n⚠️  RECOMMENDATION: Monitor fatigue carefully")
            print(f"   • HR trending upward - watch for overtraining")
            print(f"   • Ensure adequate recovery between sessions")
        else:
            print(f"\n✅ RECOMMENDATION: Training intensity looks good")
            print(f"   • HR levels appropriate for progressive training")
    
    # Show the conservative plan updates
    print(f"\n📋 Conservative Plan Updates (implemented):")
    print(f"   • Week 1: 1.0/2.0, 1.0/2.5, 1.5/2.0 min intervals")
    print(f"   • Schedule: Mon-Tue-Thu (better recovery)")
    print(f"   • Tuesday sessions easier for back-to-back recovery")
    print(f"   • Target HR: 140-160 run, 100-120 walk")


def create_hr_trend_visualization():
    """Create a comprehensive 2x2 visualization of training trends"""
    # Load data
    import glob
    json_files = glob.glob("mi_data_extracted/training_data_extracted_*.json")
    if not json_files:
        return
    
    latest_file = max(json_files)
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    # Prepare data for visualization
    sessions = [f"W{s['week']}D{s['day']}" for s in data]
    
    # Extract data for each metric
    hr_data = [(session, int(s['avg_hr'])) for session, s in zip(sessions, data) if s['avg_hr']]
    pace_data = []
    distance_data = [(session, float(s['distance'])) for session, s in zip(sessions, data) if s['distance']]
    duration_data = []
    
    # Process pace data (convert MM:SS to decimal minutes)
    for session, s in zip(sessions, data):
        if s['avg_pace']:
            try:
                pace_parts = s['avg_pace'].split(':')
                pace_decimal = int(pace_parts[0]) + int(pace_parts[1]) / 60
                pace_data.append((session, pace_decimal))
            except:
                pass
    
    # Process duration data (convert HH:MM:SS to decimal minutes)
    for session, s in zip(sessions, data):
        if s['duration']:
            try:
                duration_parts = s['duration'].split(':')
                if len(duration_parts) == 3:  # HH:MM:SS
                    duration_minutes = int(duration_parts[0]) * 60 + int(duration_parts[1]) + int(duration_parts[2]) / 60
                else:  # MM:SS
                    duration_minutes = int(duration_parts[0]) + int(duration_parts[1]) / 60
                duration_data.append((session, duration_minutes))
            except:
                pass
    
    # Create 2x2 subplot
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. Heart Rate Trend (top-left)
    if hr_data:
        sessions_hr, hr_values = zip(*hr_data)
        ax1.plot(sessions_hr, hr_values, 'ro-', linewidth=2, markersize=8)
        ax1.axhspan(100, 120, alpha=0.2, color='green', label='Target Walk HR')
        ax1.axhspan(140, 160, alpha=0.2, color='orange', label='Target Run HR')
        ax1.axhspan(160, 180, alpha=0.2, color='red', label='Too High')
        ax1.set_ylabel('Heart Rate (bpm)')
        ax1.set_title('Heart Rate Progression')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        # Add value labels
        for i, (session, hr) in enumerate(hr_data):
            ax1.annotate(f'{hr}', (i, hr), textcoords="offset points", xytext=(0,10), ha='center')
    
    # 2. Pace Trend (top-right)
    if pace_data:
        sessions_pace, pace_values = zip(*pace_data)
        ax2.plot(sessions_pace, pace_values, 'bo-', linewidth=2, markersize=8)
        ax2.set_ylabel('Pace (min/km)')
        ax2.set_title('Pace Progression')
        ax2.grid(True, alpha=0.3)
        ax2.invert_yaxis()  # Faster pace = lower values = better
        # Add value labels
        for i, (session, pace) in enumerate(pace_data):
            pace_str = f"{int(pace)}:{int((pace % 1) * 60):02d}"
            ax2.annotate(pace_str, (i, pace), textcoords="offset points", xytext=(0,10), ha='center')
    
    # 3. Distance Trend (bottom-left)
    if distance_data:
        sessions_dist, distance_values = zip(*distance_data)
        ax3.plot(sessions_dist, distance_values, 'go-', linewidth=2, markersize=8)
        ax3.set_ylabel('Distance (km)')
        ax3.set_title('Distance Progression')
        ax3.grid(True, alpha=0.3)
        # Add value labels
        for i, (session, dist) in enumerate(distance_data):
            ax3.annotate(f'{dist}', (i, dist), textcoords="offset points", xytext=(0,10), ha='center')
    
    # 4. Duration Trend (bottom-right)
    if duration_data:
        sessions_dur, duration_values = zip(*duration_data)
        ax4.plot(sessions_dur, duration_values, 'mo-', linewidth=2, markersize=8)
        ax4.set_ylabel('Duration (minutes)')
        ax4.set_title('Duration Progression')
        ax4.grid(True, alpha=0.3)
        # Add value labels
        for i, (session, dur) in enumerate(duration_data):
            ax4.annotate(f'{int(dur)}m', (i, dur), textcoords="offset points", xytext=(0,10), ha='center')
    
    # Set x-axis labels for all subplots
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_xlabel('Training Session')
        ax.tick_params(axis='x', rotation=45)
    
    plt.suptitle('Training Progress Analysis - Week 1', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('training_progress_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Training progress visualization saved as 'training_progress_analysis.png'")


if __name__ == "__main__":
    analyze_actual_vs_planned()
    create_hr_trend_visualization()
    print(f"\n🏃‍♂️ Analysis complete! The conservative plan adjustments should help manage intensity.")
