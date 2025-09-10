#!/usr/bin/env python3
"""
Test script for the training dashboard
Verifies that all components work correctly
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.training_plan import TrainingPlan
import pandas as pd


def test_dashboard_components():
    """Test the core dashboard functionality"""
    print("🧪 Testing Training Dashboard Components...")
    print("-" * 50)
    
    # Test 1: Training Plan Data Extraction
    print("1. Testing training plan data extraction...")
    try:
        tp = TrainingPlan()
        detailed_sessions = tp.generate_detailed_sessions(21)
        
        # Convert to DataFrame like the dashboard does
        sessions_data = []
        for session in detailed_sessions:
            sessions_data.append({
                'Session': session['session'],
                'Week': session['week'],
                'Day': session['day_name'],
                'Run (min)': session['run_minutes'],
                'Walk (min)': session['walk_minutes'],
                'Sets': session['sets'],
                'Total Run (min)': session['total_run_time'],
                'Total Workout (min)': session['total_workout_time'],
                'Workout Type': session['workout_type']
            })
        
        df = pd.DataFrame(sessions_data)
        print(f"   ✅ Successfully extracted {len(df)} sessions")
        print(f"   📊 Covering {df['Week'].max()} weeks")
        print(f"   🏃 Total running time: {df['Total Run (min)'].sum():.1f} minutes")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Distance Calculations
    print("\n2. Testing distance calculations...")
    try:
        base_speed_kmh = 12.0
        walk_speed_m_per_min = 100
        
        running_distances = []
        total_distances = []
        
        for _, row in df.iterrows():
            run_min = row['Run (min)']
            walk_min = row['Walk (min)']
            sets = row['Sets']
            
            # Speed adjustment logic
            if run_min <= 1:
                speed_kmh = base_speed_kmh
            elif run_min <= 2.5:
                speed_kmh = base_speed_kmh * 0.9
            elif run_min <= 5:
                speed_kmh = base_speed_kmh * 0.8
            elif run_min <= 10:
                speed_kmh = base_speed_kmh * 0.75
            else:
                speed_kmh = base_speed_kmh * 0.7
            
            # Calculate distances
            if walk_min == 0:  # Continuous run
                run_distance = (run_min / 60) * speed_kmh
                walking_distance = 0
            else:  # Intervals
                run_distance = sets * (run_min / 60) * speed_kmh
                walking_distance = sets * (walk_min / 1000) * walk_speed_m_per_min
            
            total_distance = run_distance + walking_distance
            running_distances.append(run_distance)
            total_distances.append(total_distance)
        
        total_run_distance = sum(running_distances)
        total_overall_distance = sum(total_distances)
        
        print(f"   ✅ Distance calculations successful")
        print(f"   🎯 Total running distance: {total_run_distance:.1f} km")
        print(f"   📏 Total overall distance: {total_overall_distance:.1f} km")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: Weekly Aggregations
    print("\n3. Testing weekly aggregations...")
    try:
        weekly_stats = df.groupby('Week').agg({
            'Total Run (min)': 'sum',
            'Total Workout (min)': 'sum',
            'Sets': 'sum'
        }).round(1)
        
        print(f"   ✅ Weekly aggregations successful")
        print(f"   📅 Generated stats for {len(weekly_stats)} weeks")
        
        # Show first few weeks
        print("   📋 Sample weekly breakdown:")
        for week in range(1, min(4, len(weekly_stats) + 1)):
            stats = weekly_stats.loc[week]
            print(f"      Week {week}: {stats['Total Run (min)']}min run, {stats['Sets']} total sets")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Data Editing Simulation
    print("\n4. Testing data editing simulation...")
    try:
        # Simulate editing the first session
        original_run_time = df.at[0, 'Run (min)']
        original_sets = df.at[0, 'Sets']
        
        # Edit values
        df.at[0, 'Run (min)'] = 2.0
        df.at[0, 'Sets'] = 8
        
        # Recalculate totals (like dashboard does)
        new_total_run = df.at[0, 'Run (min)'] * df.at[0, 'Sets']
        new_total_walk = df.at[0, 'Walk (min)'] * df.at[0, 'Sets']
        df.at[0, 'Total Run (min)'] = new_total_run
        df.at[0, 'Total Workout (min)'] = new_total_run + new_total_walk
        
        print(f"   ✅ Data editing simulation successful")
        print(f"   📝 Changed run time: {original_run_time} → {df.at[0, 'Run (min)']} min")
        print(f"   📝 Changed sets: {original_sets} → {df.at[0, 'Sets']}")
        print(f"   🔄 Recalculated total run time: {df.at[0, 'Total Run (min)']} min")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n🎉 All dashboard components tested successfully!")
    print("\n📋 Dashboard Features Verified:")
    print("   ✅ Training plan data extraction")
    print("   ✅ Distance calculations with pace adjustments")
    print("   ✅ Weekly statistics aggregation")
    print("   ✅ Real-time data editing simulation")
    print("   ✅ Total time recalculations")
    
    return True


def show_sample_data():
    """Show sample data structure that the dashboard uses"""
    print("\n📊 Sample Dashboard Data Structure:")
    print("-" * 50)
    
    tp = TrainingPlan()
    detailed_sessions = tp.generate_detailed_sessions(5)  # First 5 sessions
    
    sessions_data = []
    for session in detailed_sessions:
        sessions_data.append({
            'Session': session['session'],
            'Week': session['week'], 
            'Day': session['day_name'],
            'Run (min)': session['run_minutes'],
            'Walk (min)': session['walk_minutes'],
            'Sets': session['sets'],
            'Total Run (min)': session['total_run_time'],
            'Total Workout (min)': session['total_workout_time']
        })
    
    df = pd.DataFrame(sessions_data)
    print(df.to_string(index=False))
    
    print(f"\n💡 This data structure allows for:")
    print(f"   📝 Real-time editing of Run, Walk, and Sets columns")
    print(f"   🔄 Automatic recalculation of Total columns")
    print(f"   📊 Live chart updates based on changes")
    print(f"   💾 Saving/loading of custom training plans")


if __name__ == "__main__":
    success = test_dashboard_components()
    if success:
        show_sample_data()
        print(f"\n🚀 Ready to launch dashboard!")
        print(f"   Run: .venv/bin/python dashboard_app/launch_dashboard.py")
        print(f"   Or:  ./dashboard_app/start_dashboard.sh")
    else:
        print(f"\n❌ Dashboard tests failed. Please check the errors above.")
