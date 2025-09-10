#!/usr/bin/env python3
"""
Complete Training Plan Overview - All 21 Sessions
"""

from src.training_plan import TrainingPlan

def show_complete_progression():
    """Show the complete 21-session progression"""
    print("🏃‍♂️ COMPLETE 7-WEEK TRAINING PLAN OVERVIEW")
    print("=" * 70)
    
    plan = TrainingPlan()
    sessions = plan.generate_detailed_sessions(session_count=21)
    
    print("\n📋 All 21 Training Sessions:")
    print("-" * 70)
    
    current_week = 0
    for session in sessions:
        if session['week'] != current_week:
            current_week = session['week']
            print(f"\n🗓️  WEEK {current_week}")
            print("-" * 30)
        
        day_name = session['day_name']
        run_min = session['run_minutes']
        walk_min = session['walk_minutes'] 
        sets = session['sets']
        total_run = session['total_run_time']
        workout_type = session['workout_type']
        
        if workout_type == "interval_training":
            print(f"  Session {session['session']:2d} ({day_name}): {run_min:.1f}min run / {walk_min:.1f}min walk × {sets:2d} sets → {total_run:.1f}min total")
        elif workout_type == "continuous_with_breaks":
            print(f"  Session {session['session']:2d} ({day_name}): {run_min:.1f}min continuous run → {total_run:.1f}min total")
        else:
            print(f"  Session {session['session']:2d} ({day_name}): {run_min:.1f}min run / {walk_min:.1f}min walk × {sets:2d} sets ({workout_type}) → {total_run:.1f}min total")
    
    print("\n📊 Weekly Volume Summary:")
    print("-" * 70)
    
    weekly_volumes = {}
    for session in sessions:
        week = session['week']
        if week not in weekly_volumes:
            weekly_volumes[week] = {'total_run': 0, 'sessions': 0, 'avg_sets': 0}
        
        weekly_volumes[week]['total_run'] += session['total_run_time']
        weekly_volumes[week]['sessions'] += 1
        weekly_volumes[week]['avg_sets'] += session['sets']
    
    for week in sorted(weekly_volumes.keys()):
        data = weekly_volumes[week]
        avg_sets = data['avg_sets'] / data['sessions']
        print(f"Week {week}: {data['total_run']:5.1f} minutes total running | {data['sessions']} sessions | {avg_sets:.1f} avg sets/session")
    
    print("\n🎯 Training Plan Highlights:")
    print("-" * 70)
    print("• Volume-focused muscle endurance building (Weeks 1-3)")
    print("• High set counts early: 16→13→10 sets in Week 1")
    print("• Peak volume in Week 3: 10min intervals with 8 sets")
    print("• Hybrid approach from Week 4: intervals + continuous runs")
    print("• Progressive taper in Week 7 for race preparation")
    print("• Mon-Tue-Thu schedule with optimal recovery")
    print("• Heart rate zone guidance for each session type")

if __name__ == "__main__":
    show_complete_progression()
