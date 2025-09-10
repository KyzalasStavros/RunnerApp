#!/usr/bin/env python3
"""
Test script for the new volume-focused training plan
"""

from src.training_plan import TrainingPlan
import pandas as pd

def test_new_plan():
    """Test the new volume-focused interval progression"""
    print("🏃‍♂️ Testing New Volume-Focused Training Plan")
    print("=" * 60)
    
    # Create training plan instance
    plan = TrainingPlan()
    
    # Generate detailed sessions (first 12 sessions = 4 weeks)
    sessions = plan.generate_detailed_sessions(session_count=12)
    
    # Convert to DataFrame for easy viewing
    df = pd.DataFrame(sessions)
    
    # Display the first few weeks
    print("\n📋 First 4 Weeks of Training Sessions:")
    print("-" * 60)
    
    for week in range(1, 5):
        week_sessions = df[df['week'] == week]
        if week_sessions.empty:
            continue
            
        print(f"\n🗓️  WEEK {week}:")
        for _, session in week_sessions.iterrows():
            day_name = session['day_name']
            run_min = session['run_minutes']
            walk_min = session['walk_minutes']
            sets = session['sets']
            total_run = session['total_run_time']
            workout_type = session['workout_type']
            
            if workout_type == "interval_training":
                print(f"  {day_name}: {run_min:.1f}min run / {walk_min:.1f}min walk × {sets} sets")
                print(f"        → Total running: {total_run:.1f} minutes")
            elif workout_type == "continuous_with_breaks":
                print(f"  {day_name}: {run_min:.1f}min continuous run (with breaks)")
                print(f"        → Total running: {total_run:.1f} minutes")
            else:
                print(f"  {day_name}: {run_min:.1f}min run / {walk_min:.1f}min walk × {sets} sets ({workout_type})")
                print(f"        → Total running: {total_run:.1f} minutes")
    
    # Show volume progression summary
    print("\n📊 Volume Progression Summary:")
    print("-" * 60)
    
    weekly_volumes = df.groupby('week')['total_run_time'].sum()
    
    for week, volume in weekly_volumes.items():
        week_sessions = df[df['week'] == week]
        avg_sets = week_sessions['sets'].mean()
        print(f"Week {week}: {volume:.1f} min total running, avg {avg_sets:.1f} sets/session")
    
    # Verify the interval progression matches specification
    print("\n🎯 Interval Progression Verification:")
    print("-" * 60)
    
    expected_intervals = [(1.0, 2.0), (2.0, 2.0), (3.0, 2.0), (4.0, 3.0), (5.0, 3.0), (8.0, 5.0), (6.0, 3.0), (8.0, 3.0), (10.0, 3.0)]
    
    for i, (expected_run, expected_walk) in enumerate(expected_intervals):
        if i < len(df):
            actual_run = df.iloc[i]['run_minutes']
            actual_walk = df.iloc[i]['walk_minutes']
            match = "✅" if (actual_run == expected_run and actual_walk == expected_walk) else "❌"
            print(f"Session {i+1}: Expected ({expected_run}, {expected_walk}) → Actual ({actual_run}, {actual_walk}) {match}")
    
    print("\n🔍 Key Features of New Plan:")
    print("-" * 60)
    print("• Volume-focused approach for muscle endurance building")
    print("• High initial set counts (10-16 sets) to build muscular endurance")
    print("• Progressive interval lengthening with controlled volume")
    print("• Hybrid approach after Week 3 (long intervals + continuous runs)")
    print("• Mon-Tue-Thu schedule with appropriate recovery")
    print("• Heart rate zone guidance for each session")

if __name__ == "__main__":
    test_new_plan()
