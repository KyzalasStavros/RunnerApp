#!/usr/bin/env python3
"""
Training Progression Analysis Script
Analyzes the progressive overload and distance progression of the 7-week training plan
"""

import matplotlib.pyplot as plt
import numpy as np
from src.training_plan import TrainingPlan
import re
import copy


def extract_session_data(training_plan):
    """Extract run/walk data from all training sessions using the new detailed sessions method"""
    detailed_sessions = training_plan.generate_detailed_sessions(21)
    sessions = []
    
    for detailed_session in detailed_sessions:
        session_counter = detailed_session['session']
        week = detailed_session['week']
        day_name = detailed_session['day_name']
        run_min = detailed_session['run_minutes']
        walk_min = detailed_session['walk_minutes']
        sets = detailed_session['sets']
        
        sessions.append({
            'session': session_counter,
            'week': week,
            'day': day_name,
            'run_min': run_min,
            'walk_min': walk_min,
            'sets': sets,
            'total_run_min': detailed_session['total_run_time'],
            'total_walk_min': walk_min * sets if walk_min > 0 else 0,
            'total_session_min': detailed_session['total_workout_time'],
            'workout_type': detailed_session['workout_type']
        })
    
    return sessions


def calculate_distances_with_fatigue(sessions, base_run_speed_kmh=12, walk_speed_m_per_min=100):
    """Calculate distances with progressive speed reduction based on interval duration"""
    
    def get_adjusted_speed(interval_run_minutes, base_speed_kmh):
        """Calculate adjusted running speed based on interval duration"""
        # Speed reductions based on interval duration:
        # 0-1 min: full speed (12 km/h)
        # 1-2.5 min: 10% reduction 
        # 2.5-4 min: 20% reduction (10% + 10%)
        # 4+ min: 30% reduction (10% + 10% + 10%)
        
        if interval_run_minutes <= 1.0:
            reduction_factor = 1.0  # No reduction
        elif interval_run_minutes <= 2.5:
            reduction_factor = 0.9  # 10% reduction
        elif interval_run_minutes <= 4.0:
            reduction_factor = 0.81  # 19% total reduction (0.9 * 0.9)
        else:
            reduction_factor = 0.729  # 27.1% total reduction (0.9 * 0.9 * 0.9)
        
        adjusted_speed_kmh = base_speed_kmh * reduction_factor
        adjusted_speed_m_per_min = (adjusted_speed_kmh * 1000) / 60  # Convert to m/min
        
        return adjusted_speed_kmh, adjusted_speed_m_per_min
    
    for session in sessions:
        # Get adjusted speed for this interval duration
        interval_run_min = session['run_min']
        adjusted_speed_kmh, adjusted_speed_m_per_min = get_adjusted_speed(interval_run_min, base_run_speed_kmh)
        
        # Store speed info in session
        session['adjusted_speed_kmh'] = adjusted_speed_kmh
        session['adjusted_speed_m_per_min'] = adjusted_speed_m_per_min
        
        # Calculate distances with adjusted speed
        session['run_distance_m'] = session['total_run_min'] * adjusted_speed_m_per_min
        session['walk_distance_m'] = session['total_walk_min'] * walk_speed_m_per_min
        session['total_distance_m'] = session['run_distance_m'] + session['walk_distance_m']
        session['total_distance_km'] = session['total_distance_m'] / 1000
        session['run_distance_km'] = session['run_distance_m'] / 1000
        session['walk_distance_km'] = session['walk_distance_m'] / 1000
    
    return sessions


def calculate_distances(sessions, run_speed_m_per_min=200, walk_speed_m_per_min=100):
    """Calculate distances based on time and speed assumptions (original method)"""
    for session in sessions:
        session['run_distance_m'] = session['total_run_min'] * run_speed_m_per_min
        session['walk_distance_m'] = session['total_walk_min'] * walk_speed_m_per_min
        session['total_distance_m'] = session['run_distance_m'] + session['walk_distance_m']
        session['total_distance_km'] = session['total_distance_m'] / 1000
        session['run_distance_km'] = session['run_distance_m'] / 1000
        session['walk_distance_km'] = session['walk_distance_m'] / 1000
    
    return sessions


def analyze_progressive_overload(sessions):
    """Analyze if the training shows progressive overload"""
    print("🔍 Progressive Overload Analysis")
    print("=" * 50)
    
    # Print simple table of sessions
    print("📋 Training Session Overview:")
    print("Week | Day | Run Time | Walk Time | Sets | Total Run Time")
    print("-" * 55)
    
    day_counter = 0
    for session in sessions:
        day_counter += 1
        # Reset day counter for each week (3 training days per week)
        day_in_week = ((day_counter - 1) % 3) + 1
        
        print(f"  {session['week']:2d} |  {day_in_week}  |   {session['run_min']:4.1f}   |   {session['walk_min']:4.1f}   |  {session['sets']:2d}  |    {session['total_run_min']:4.1f}")
    
    print()
    
    # Check total running time progression
    run_times = [s['total_run_min'] for s in sessions]
    total_times = [s['total_session_min'] for s in sessions]
    distances = [s['total_distance_km'] for s in sessions]
    
    print(f"📊 Session-by-session running time progression:")
    for i, session in enumerate(sessions):
        progress_indicator = ""
        if i > 0:
            prev_run_time = sessions[i-1]['total_run_min']
            if session['total_run_min'] > prev_run_time:
                progress_indicator = " ⬆️ (+{:.1f}min)".format(session['total_run_min'] - prev_run_time)
            elif session['total_run_min'] < prev_run_time:
                progress_indicator = " ⬇️ (-{:.1f}min)".format(prev_run_time - session['total_run_min'])
            else:
                progress_indicator = " ➡️ (same)"
        
        print(f"  Session {session['session']:2d} (Week {session['week']}, {session['day']}): "
              f"{session['total_run_min']:4.1f}min run, {session['total_distance_km']:4.1f}km total{progress_indicator}")
    
    # Calculate progression metrics
    total_increase = run_times[-1] - run_times[0]
    avg_weekly_increase = total_increase / 6  # 6 weeks of progression
    
    print(f"\n📈 Progression Summary:")
    print(f"   Starting running time: {run_times[0]:.1f} minutes")
    print(f"   Final running time: {run_times[-1]:.1f} minutes")
    print(f"   Total increase: {total_increase:.1f} minutes ({(total_increase/run_times[0]*100):.1f}% increase)")
    print(f"   Average weekly increase: {avg_weekly_increase:.1f} minutes/week")
    
    # Check for consistent progression (no major drops)
    decreases = 0
    for i in range(1, len(run_times)):
        if run_times[i] < run_times[i-1]:
            decreases += 1
    
    print(f"   Sessions with decreased running time: {decreases} out of {len(sessions)-1} progressions")
    
    if decreases <= 2:
        print("   ✅ Good progressive overload with minimal setbacks")
    elif decreases <= 4:
        print("   ⚠️  Some regression in progression - consider smoother increases")
    else:
        print("   ❌ Too many regressions - progression needs improvement")
    
    return sessions


def create_progression_graphs(sessions):
    """Create comprehensive progression visualization"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('7-Week Training Plan Progression Analysis', fontsize=16, fontweight='bold')
    
    session_numbers = [s['session'] for s in sessions]
    weeks = [s['week'] for s in sessions]
    run_times = [s['total_run_min'] for s in sessions]
    total_times = [s['total_session_min'] for s in sessions]
    distances = [s['total_distance_km'] for s in sessions]
    run_distances = [s['run_distance_km'] for s in sessions]
    
    # 1. Running time progression
    axes[0, 0].plot(session_numbers, run_times, 'o-', linewidth=2, markersize=6, color='red', label='Running time')
    axes[0, 0].plot(session_numbers, total_times, 's-', linewidth=2, markersize=6, color='blue', alpha=0.7, label='Total session time')
    axes[0, 0].set_xlabel('Training Session')
    axes[0, 0].set_ylabel('Time (minutes)')
    axes[0, 0].set_title('Running Time Progression')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    
    # Add week boundaries
    for week in range(2, 8):
        first_session_of_week = next((s['session'] for s in sessions if s['week'] == week), None)
        if first_session_of_week:
            axes[0, 0].axvline(x=first_session_of_week - 0.5, color='gray', linestyle='--', alpha=0.5)
    
    # 2. Distance progression
    axes[0, 1].plot(session_numbers, distances, 'o-', linewidth=2, markersize=6, color='green', label='Total distance')
    axes[0, 1].plot(session_numbers, run_distances, 's-', linewidth=2, markersize=6, color='darkgreen', alpha=0.7, label='Running distance')
    axes[0, 1].set_xlabel('Training Session')
    axes[0, 1].set_ylabel('Distance (km)')
    axes[0, 1].set_title('Distance Progression')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    
    # Add week boundaries
    for week in range(2, 8):
        first_session_of_week = next((s['session'] for s in sessions if s['week'] == week), None)
        if first_session_of_week:
            axes[0, 1].axvline(x=first_session_of_week - 0.5, color='gray', linestyle='--', alpha=0.5)
    
    # 3. Weekly totals
    weekly_data = {}
    for session in sessions:
        week = session['week']
        if week not in weekly_data:
            weekly_data[week] = {'run_time': 0, 'total_time': 0, 'distance': 0, 'run_distance': 0}
        weekly_data[week]['run_time'] += session['total_run_min']
        weekly_data[week]['total_time'] += session['total_session_min']
        weekly_data[week]['distance'] += session['total_distance_km']
        weekly_data[week]['run_distance'] += session['run_distance_km']
    
    week_numbers = sorted(weekly_data.keys())
    weekly_run_times = [weekly_data[w]['run_time'] for w in week_numbers]
    weekly_distances = [weekly_data[w]['distance'] for w in week_numbers]
    
    axes[1, 0].bar(week_numbers, weekly_run_times, alpha=0.7, color='orange', label='Weekly running time')
    axes[1, 0].set_xlabel('Week')
    axes[1, 0].set_ylabel('Total Running Time (minutes)')
    axes[1, 0].set_title('Weekly Running Volume')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_xticks(week_numbers)
    
    # 4. Training session table (instead of workout intensity)
    axes[1, 1].axis('off')  # Turn off axis for table
    
    # Prepare table data
    table_data = []
    day_counter = 0
    for session in sessions:
        day_counter += 1
        day_in_week = ((day_counter - 1) % 3) + 1
        table_data.append([
            f"{session['week']}",
            f"{day_in_week}",
            f"{session['run_min']:.1f}",
            f"{session['walk_min']:.1f}",
            f"{session['sets']}",
            f"{session['total_run_min']:.1f}"
        ])
    
    # Create table
    col_labels = ['Week', 'Day', 'Run (min)', 'Walk (min)', 'Sets', 'Total Run (min)']

    # Create the table
    table = axes[1, 1].table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]  # Fill the entire subplot
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)  # Make rows a bit taller
    
    # Color header row
    for i in range(len(col_labels)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(len(col_labels)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
            else:
                table[(i, j)].set_facecolor('white')
    
    axes[1, 1].set_title('Training Session Details')
    
    # Add week boundaries to other plots
    for week in range(2, 8):
        first_session_of_week = next((s['session'] for s in sessions if s['week'] == week), None)
        if first_session_of_week:
            axes[0, 0].axvline(x=first_session_of_week - 0.5, color='gray', linestyle='--', alpha=0.5)
            axes[0, 1].axvline(x=first_session_of_week - 0.5, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    # Save the plot as an image file
    plt.savefig('training_plan_progression_analysis.png', dpi=300, bbox_inches='tight')
    print(f"📊 Progression chart saved as 'training_plan_progression_analysis.png'")
    
    plt.show()
    
    return weekly_data


def print_detailed_stats(sessions, sessions_simple, weekly_data, weekly_data_simple):
    """Print detailed statistics about the training plan with comparison"""
    print(f"\n📊 Detailed Training Statistics")
    print("=" * 50)
    
    print(f"📈 Overall Progression (Fatigue-Adjusted vs Constant Speed):")
    total_sessions = len(sessions)
    total_running_time = sum(s['total_run_min'] for s in sessions)
    total_distance = sum(s['total_distance_km'] for s in sessions)
    total_run_distance = sum(s['run_distance_km'] for s in sessions)
    
    total_distance_simple = sum(s['total_distance_km'] for s in sessions_simple)
    total_run_distance_simple = sum(s['run_distance_km'] for s in sessions_simple)
    
    print(f"   Total training sessions: {total_sessions}")
    print(f"   Total running time: {total_running_time:.1f} minutes ({total_running_time/60:.1f} hours)")
    print(f"   Total distance (fatigue-adjusted): {total_distance:.1f} km")
    print(f"   Total distance (constant speed): {total_distance_simple:.1f} km")
    print(f"   Total running distance (fatigue-adjusted): {total_run_distance:.1f} km")
    print(f"   Total running distance (constant speed): {total_run_distance_simple:.1f} km")
    print(f"   Distance difference: {total_distance_simple - total_distance:.1f} km ({((total_distance_simple - total_distance)/total_distance_simple*100):.1f}% less with fatigue)")
    
    print(f"\n📅 Weekly Breakdown (Fatigue-Adjusted):")
    for week in sorted(weekly_data.keys()):
        data = weekly_data[week]
        data_simple = weekly_data_simple[week]
        print(f"   Week {week}: {data['run_time']:.1f}min running, {data['distance']:.1f}km total ({data_simple['distance']:.1f}km constant), {data['run_distance']:.1f}km running ({data_simple['run_distance']:.1f}km constant)")
    
    print(f"\n🏃‍♂️ Speed Analysis by Interval Duration:")
    interval_speeds = {}
    for session in sessions:
        interval_duration = session['run_min']
        speed_kmh = session['adjusted_speed_kmh']
        if interval_duration not in interval_speeds:
            interval_speeds[interval_duration] = speed_kmh
    
    for duration in sorted(interval_speeds.keys()):
        speed = interval_speeds[duration]
        reduction = (12 - speed) / 12 * 100
        print(f"   {duration:.1f} min intervals: {speed:.1f} km/h ({reduction:.1f}% reduction from max)")
    
    print(f"\n🎯 Training Targets:")
    # Estimate readiness for 5K
    final_week_run_distance = weekly_data[7]['run_distance']
    final_week_run_distance_simple = weekly_data_simple[7]['run_distance']
    if final_week_run_distance >= 5.0:
        print(f"   ✅ Week 7 running distance (fatigue-adjusted: {final_week_run_distance:.1f}km) meets 5K target")
    else:
        print(f"   ⚠️  Week 7 running distance (fatigue-adjusted: {final_week_run_distance:.1f}km) below 5K target")
        
    print(f"   📏 Week 7 running distance comparison: {final_week_run_distance:.1f}km (fatigue) vs {final_week_run_distance_simple:.1f}km (constant)")
    
    # Check progression consistency
    weekly_run_times = [weekly_data[w]['run_time'] for w in sorted(weekly_data.keys())]
    consistent_increases = 0
    for i in range(1, len(weekly_run_times)):
        if weekly_run_times[i] >= weekly_run_times[i-1]:
            consistent_increases += 1
    
    consistency_pct = (consistent_increases / (len(weekly_run_times) - 1)) * 100
    print(f"   Weekly progression consistency: {consistency_pct:.1f}% (weeks with increased/maintained volume)")


def main():
    """Main analysis function"""
    print("Training Plan Progression Analysis with Fatigue Modeling")
    print("=" * 60)
    print("Assumptions:")
    print("- Base running speed: 12 km/h (200m/min)")
    print("- Speed reduction by interval duration:")
    print("  • 0-1 min: 12.0 km/h (no reduction)")
    print("  • 1-2.5 min: 10.8 km/h (10% reduction)")
    print("  • 2.5-4 min: 9.7 km/h (19% reduction)")
    print("  • 4+ min: 8.7 km/h (27% reduction)")
    print("- Walking speed: 6 km/h (100m/min)")
    print("")
    
    # Create training plan instance
    training_plan = TrainingPlan()
    
    # Extract session data
    sessions = extract_session_data(training_plan)
    
    # Calculate distances with fatigue adjustment
    sessions_fatigue = calculate_distances_with_fatigue(copy.deepcopy(sessions))
    
    # Calculate distances with constant speed (for comparison)
    sessions_simple = calculate_distances(copy.deepcopy(sessions))
    
    # Analyze progressive overload (using fatigue-adjusted data)
    sessions_fatigue = analyze_progressive_overload(sessions_fatigue)
    
    # Create graphs (using fatigue-adjusted data)
    weekly_data_fatigue = create_progression_graphs(sessions_fatigue)
    
    # Calculate weekly data for simple method too
    weekly_data_simple = {}
    for session in sessions_simple:
        week = session['week']
        if week not in weekly_data_simple:
            weekly_data_simple[week] = {'run_time': 0, 'total_time': 0, 'distance': 0, 'run_distance': 0}
        weekly_data_simple[week]['run_time'] += session['total_run_min']
        weekly_data_simple[week]['total_time'] += session['total_session_min']
        weekly_data_simple[week]['distance'] += session['total_distance_km']
        weekly_data_simple[week]['run_distance'] += session['run_distance_km']
    
    # Print detailed statistics with comparison
    print_detailed_stats(sessions_fatigue, sessions_simple, weekly_data_fatigue, weekly_data_simple)
    
    print(f"\n✅ Analysis complete! Check the generated graphs for visual progression.")
    print(f"📝 Note: Graphs show fatigue-adjusted distances for more realistic estimates.")


if __name__ == "__main__":
    main()
