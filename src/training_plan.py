"""
5K Training Plan - Core training logic and data management
Based on a 7-week adaptive training plan for 5K preparation
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class TrainingPlan:
    """Manages the 7-week training plan for 5K preparation"""
    
    def __init__(self, log_file: str = "training_log.json"):
        self.log_file = log_file
        # Build dynamic base plan with progressive session-by-session overload.
        # More realistic progression with gradual walk time reduction while maintaining
        # aggressive run time increases to meet 7-week goal.
        # Run time increases by 0.5 minutes per session, walk time reduces gradually
        
        def get_walk_time(session_num):
            """Calculate walk time based on session number for gradual reduction"""
            if session_num <= 6:    # Weeks 1-2: 2.0 min walk
                return 2.0
            elif session_num <= 12:  # Weeks 3-4: 1.5 min walk  
                return 1.5
            elif session_num <= 18:  # Weeks 5-6: 1.0 min walk
                return 1.0
            else:                    # Week 7: 0.5 min walk
                return 0.5
        
        interval_progress = []
        for session in range(1, 22):  # 21 sessions total
            run_time = 1.0 + (session - 1) * 0.5  # Start at 1.0, increase by 0.5 each session
            walk_time = get_walk_time(session)
            interval_progress.append((run_time, walk_time))
        
        # Progressive volume-focused plan for muscle endurance building
        # Weeks 1-3: Focus on increasing volume with intervals
        # Week 4+: Hybrid approach with intervals + continuous runs
        
        interval_progress = [
            # Week 1: Base building with moderate volume
            (1.0, 2.0),  # Start conservative
            (2.0, 2.0),  # Double run time
            (3.0, 2.0),  # Continue building
            
            # Week 2: Increase both run time and recovery to handle more volume
            (4.0, 3.0),  # Longer recovery for muscle endurance
            (5.0, 3.0),  # Peak interval duration
            (8.0, 5.0),  # Long interval with extended recovery
            
            # Week 3: Volume peak with varied intervals
            (6.0, 3.0),  # Sustained effort focus
            (8.0, 3.0),  # Push endurance boundaries
            (10.0, 3.0), # Peak interval - major milestone
            
            # Week 4: Hybrid transition - mix intervals with continuous (increased volume)
            (6.0, 2.0),  # Longer intervals for higher volume
            (28.0, 0),   # Continuous run day (28 minutes)
            (7.0, 2.0),  # Back to intervals, longer
            
            # Week 5: Interval + tempo mix - peak hybrid volume
            (5.0, 1.5),  # Faster intervals, more sets
            (32.0, 0),   # Tempo run day (32 minutes)
            (8.0, 2.0),  # Long intervals
            
            # Week 6: Speed + endurance - maintain peak volume
            (4.0, 1.0),  # Speed work with more sets
            (35.0, 0),   # Easy continuous run (35 minutes)
            (9.0, 2.0),  # Endurance intervals
            
            # Week 7: Race prep taper
            (4.0, 1.5),  # Maintain fitness
            (20.0, 0),   # Easy run (20 minutes)
            (2.0, 1.0),  # Race pace practice
        ]
        
        # Store as class attribute for access in other methods
        self.interval_progress = interval_progress

        def fmt_min(x: float) -> str:
            return f"{x:.1f}".rstrip('0').rstrip('.')

        def compute_sets(session_idx: int, run_min: float, week: int) -> int:
            """Calculate sets based on muscle endurance focus and progressive volume"""
            if run_min == 0:  # Continuous run day
                return 1
            
            # CUSTOM SET NUMBERS for weeks 1-3 only
            custom_sets = {
                # Week 1: High volume muscle endurance building
                1: 16,  # Session 1: 1min run
                2: 13,  # Session 2: 2min run  
                3: 10,  # Session 3: 3min run
                
                # Week 2: Moderate volume with longer intervals
                4: 7,   # Session 4: 4min run
                5: 6,   # Session 5: 5min run
                6: 5,   # Session 6: 8min run
                
                # Week 3: Focus on longer intervals
                7: 6,   # Session 7: 6min run
                8: 5,   # Session 8: 8min run
                9: 4,   # Session 9: 10min run
            }
            
            # Use custom sets for sessions 1-9 (weeks 1-3), then calculate for later weeks
            if session_idx in custom_sets:
                return custom_sets[session_idx]
            
            # For weeks 4+ use calculated approach
            if week == 4:
                # Week 4 calculated sets
                if session_idx == 10:  # 6min run
                    return 6
                elif session_idx == 11:  # 28min continuous
                    return 1
                elif session_idx == 12:  # 7min run
                    return 5
            elif week == 5:
                base_sets = 8 - (session_idx - 13) * 0.5  # 8, 7.5, 7
                return max(6, int(base_sets))
            elif week == 6:
                base_sets = 7 - (session_idx - 16) * 0.5  # 7, 6.5, 6
                return max(5, int(base_sets))
            else:
                # Week 7: Taper
                base_sets = 5 - (session_idx - 19) * 0.5
                return max(3, int(base_sets))

        self.base_plan = {}
        session_counter = 1
        max_sessions = len(interval_progress)
        
        # Generate all 7 weeks of the base plan display
        for week in range(1, 8):  # All 7 weeks
            if session_counter > max_sessions:
                break
                
            week_list = []
            # Monday interval
            if session_counter <= max_sessions:
                run_min, walk_min = interval_progress[session_counter - 1]
                sets = compute_sets(session_counter, run_min, week)
                
                if run_min == 0 and walk_min == 0:  # Continuous run day
                    week_list.append(f"Mon: Continuous run (20-30 min) [HR: 130-150 bpm]")
                elif walk_min == 0:  # Continuous run with specified time
                    week_list.append(f"Mon: Continuous run ({int(run_min)} min) [HR: 130-150 bpm]")
                else:
                    week_list.append(f"Mon: Run/walk intervals ({fmt_min(run_min)} min run / {fmt_min(walk_min)} min walk × {sets}) [HR: 130-150/100-120 bpm]")
                session_counter += 1
            
            # Tuesday interval  
            if session_counter <= max_sessions:
                run_min, walk_min = interval_progress[session_counter - 1]
                sets = compute_sets(session_counter, run_min, week)
                
                if run_min == 0 and walk_min == 0:  # Continuous run day
                    week_list.append(f"Tue: Continuous run (25-35 min) [HR: 140-160 bpm]")
                elif walk_min == 0:  # Continuous run with specified time
                    week_list.append(f"Tue: Continuous run ({int(run_min)} min) [HR: 140-160 bpm]")
                else:
                    week_list.append(f"Tue: Run/walk intervals ({fmt_min(run_min)} min run / {fmt_min(walk_min)} min walk × {sets}) [HR: 140-160/100-120 bpm]")
                session_counter += 1
            
            week_list.append("Wed: Rest or strength training (squats, lunges, planks, push-ups)")

            # Thursday interval
            if session_counter <= max_sessions:
                run_min, walk_min = interval_progress[session_counter - 1]
                sets = compute_sets(session_counter, run_min, week)
                
                if run_min == 0 and walk_min == 0:  # Continuous run day
                    week_list.append(f"Thu: Continuous run (20-30 min) [HR: 130-150 bpm]")
                elif walk_min == 0:  # Continuous run with specified time
                    week_list.append(f"Thu: Continuous run ({int(run_min)} min) [HR: 130-150 bpm]")
                else:
                    week_list.append(f"Thu: Run/walk intervals ({fmt_min(run_min)} min run / {fmt_min(walk_min)} min walk × {sets}) [HR: 130-150/100-120 bpm]")
                session_counter += 1
                
            week_list.append("Fri: Rest or yoga/mobility work")
            week_list.append("Weekend: Rest")
            
            self.base_plan[week] = week_list

            # Add race day to the final week
            if week == 7:
                week_list.append("Sun: RACE DAY — 5K race! Good luck and race smart 🎉")
                self.base_plan[week] = week_list

    def load_logs(self) -> Dict[str, Any]:
        """Load training logs from JSON file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load logs from {self.log_file}: {e}")
                return {}
        return {}

    def save_logs(self, logs: Dict[str, Any]) -> None:
        """Save training logs to JSON file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=4)
        except IOError as e:
            print(f"Error: Could not save logs to {self.log_file}: {e}")

    def get_current_week(self) -> int:
        """Get the current training week (0-based)"""
        logs = self.load_logs()
        if not logs:
            return 0
        
        completed_weeks = [int(week) for week in logs.keys()]
        return max(completed_weeks) if completed_weeks else 0

    def print_plan(self, current_week: int) -> None:
        """Print the remaining training plan"""
        if current_week >= 7:
            print("🎉 Congratulations! You've completed all 7 weeks!")
            print("You're ready for your 5K race! 🏃‍♂️💨")
            return
            
        if current_week < 0:
            current_week = 0
            
        print(f"📅 Remaining Training Plan (Week {current_week + 1} to 7):")
        print("=" * 60)
        
        for week in range(current_week + 1, 8):
            print(f"\n🗓️  Week {week}")
            print("-" * 20)
            for day, workout in enumerate(self.base_plan[week], 1):
                print(f"  {workout}")
            
            # Add weekly focus
            focuses = {
                1: "🎯 Focus: Building base fitness with walk/run intervals + strength foundation",
                2: "🎯 Focus: Increasing running duration, reducing walk breaks + bodyweight training",
                3: "🎯 Focus: Continuous running for longer periods + plyometric power",
                4: "🎯 Focus: Building endurance and consistency + functional strength",
                5: "🎯 Focus: Speed work introduction with structured intervals + circuit training",
                6: "🎯 Focus: Peak training with longer intervals + explosive power",
                7: "🎯 Focus: Tapering and race preparation + mobility/recovery"
            }
            if week in focuses:
                print(f"  {focuses[week]}")

    def log_week(self, week: int, pace: Optional[float] = None, 
                 distance: Optional[float] = None, recovery: Optional[int] = None, 
                 skipped: bool = False, comments: str = "") -> None:
        """Log weekly training results"""
        logs = self.load_logs()
        
        # Add timestamp for this log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logs[str(week)] = {
            "pace": pace,
            "distance": distance,
            "recovery": recovery,
            "skipped": skipped,
            "comments": comments,
            "logged_at": timestamp
        }
        
        self.save_logs(logs)

    def adjust_plan(self) -> Dict[int, str]:
        """Suggest plan adjustments based on logged performance"""
        logs = self.load_logs()
        adjustments = {}
        
        for week_str, data in logs.items():
            week = int(week_str)
            next_week = week + 1
            
            if next_week > 7:  # No adjustments needed after week 7
                continue
                
            suggestions = []
            
            # Check if workouts were skipped
            if data.get("skipped", False):
                suggestions.append("Reduce intensity (shorter intervals, more easy running)")
                
            # Check recovery rating
            recovery = data.get("recovery")
            if recovery is not None:
                if recovery < 4:
                    suggestions.append("Add extra rest day or reduce intensity")
                elif recovery < 6:
                    suggestions.append("Consider easier pace or shorter workouts")
                elif recovery > 8:
                    suggestions.append("You're recovering well! Maintain current intensity")
                elif recovery >= 9:
                    suggestions.append("Consider slightly increasing intensity or adding extra workout")
            
            # Check pace improvement
            if week > 1 and data.get("pace"):
                prev_week_data = logs.get(str(week - 1), {})
                prev_pace = prev_week_data.get("pace")
                if prev_pace and data["pace"] < prev_pace:
                    suggestions.append("Great pace improvement! Keep it up!")
                elif prev_pace and data["pace"] > prev_pace * 1.1:
                    suggestions.append("Pace seems slower - focus on easy runs this week")
            
            if suggestions:
                adjustments[next_week] = " | ".join(suggestions)
                
        return adjustments

    def predict_5k(self) -> str:
        """Predict 5K race time based on recent performance"""
        logs = self.load_logs()
        
        if not logs:
            return "📊 Not enough data to predict race time. Start logging your weekly performance!"

        # Get the most recent week with pace data
        weeks_with_pace = [(int(w), data) for w, data in logs.items() 
                          if data.get("pace") is not None]
        
        if not weeks_with_pace:
            return "📊 No pace data available. Log your running pace to get predictions!"

        # Use the most recent pace data
        latest_week, latest_data = max(weeks_with_pace, key=lambda x: x[0])
        pace = latest_data["pace"]  # in min/km
        
        # Current estimated 5K time
        current_5k_estimate = pace * 5
        
        # Calculate improvement factor based on training progression
        weeks_completed = latest_week
        weeks_remaining = max(0, 7 - weeks_completed)
        
        # Estimate 2-4% improvement per week (being conservative)
        weekly_improvement = 0.025  # 2.5% average
        
        # Factor in recovery - better recovery = better potential improvement
        recovery = latest_data.get("recovery", 5)
        if recovery >= 8:
            weekly_improvement = 0.03  # 3% if recovering well
        elif recovery <= 4:
            weekly_improvement = 0.015  # 1.5% if struggling
            
        # Calculate projected improvement
        total_improvement_factor = (1 - weekly_improvement) ** weeks_remaining
        projected_5k_time = current_5k_estimate * total_improvement_factor
        
        # Format the output
        result = f"📊 5K Time Prediction (based on Week {latest_week} data):\n"
        result += f"   Current estimated time: {current_5k_estimate:.1f} minutes ({current_5k_estimate//60:.0f}:{current_5k_estimate%60:04.1f})\n"
        
        if weeks_remaining > 0:
            result += f"   Projected race day time: {projected_5k_time:.1f} minutes ({projected_5k_time//60:.0f}:{projected_5k_time%60:04.1f})\n"
            result += f"   Potential improvement: {current_5k_estimate - projected_5k_time:.1f} minutes\n"
            result += f"   Weeks remaining: {weeks_remaining}"
        else:
            result += "   🏁 You've completed the training plan! Time to race!"
            
        return result

    def plot_progress(self) -> None:
        """Create progress visualization graphs"""
        logs = self.load_logs()
        
        if not logs:
            print("📊 No data to plot yet. Start logging your weekly performance!")
            return

        # Prepare data for plotting
        weeks = []
        paces = []
        distances = []
        recovery_scores = []

        for week_str, data in sorted(logs.items(), key=lambda x: int(x[0])):
            week = int(week_str)
            weeks.append(week)
            
            paces.append(data.get("pace") if data.get("pace") else None)
            distances.append(data.get("distance") if data.get("distance") else None)
            recovery_scores.append(data.get("recovery") if data.get("recovery") else None)

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('🏃‍♂️ 5K Training Progress Dashboard', fontsize=16, fontweight='bold')

        # Pace progression
        pace_weeks = [w for w, p in zip(weeks, paces) if p is not None]
        pace_values = [p for p in paces if p is not None]
        
        if pace_values:
            axes[0, 0].plot(pace_weeks, pace_values, marker='o', linewidth=2, markersize=8, color='blue')
            axes[0, 0].set_xlabel('Week')
            axes[0, 0].set_ylabel('Pace (min/km)')
            axes[0, 0].set_title('🏃‍♂️ Pace Progression')
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].invert_yaxis()  # Faster pace = lower value
            
            # Add trend line
            if len(pace_values) > 1:
                z = np.polyfit(pace_weeks, pace_values, 1)
                p = np.poly1d(z)
                axes[0, 0].plot(pace_weeks, p(pace_weeks), "--", alpha=0.7, color='red')
        else:
            axes[0, 0].text(0.5, 0.5, 'No pace data yet', ha='center', va='center', transform=axes[0, 0].transAxes)
            axes[0, 0].set_title('🏃‍♂️ Pace Progression')

        # Distance progression
        dist_weeks = [w for w, d in zip(weeks, distances) if d is not None]
        dist_values = [d for d in distances if d is not None]
        
        if dist_values:
            axes[0, 1].plot(dist_weeks, dist_values, marker='s', linewidth=2, markersize=8, color='green')
            axes[0, 1].set_xlabel('Week')
            axes[0, 1].set_ylabel('Distance (km)')
            axes[0, 1].set_title('📏 Longest Run Distance')
            axes[0, 1].grid(True, alpha=0.3)
        else:
            axes[0, 1].text(0.5, 0.5, 'No distance data yet', ha='center', va='center', transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('📏 Longest Run Distance')

        # Recovery scores
        recovery_weeks = [w for w, r in zip(weeks, recovery_scores) if r is not None]
        recovery_values = [r for r in recovery_scores if r is not None]
        
        if recovery_values:
            colors = ['red' if r <= 4 else 'orange' if r <= 6 else 'green' for r in recovery_values]
            axes[1, 0].bar(recovery_weeks, recovery_values, color=colors, alpha=0.7)
            axes[1, 0].set_xlabel('Week')
            axes[1, 0].set_ylabel('Recovery Score (1-10)')
            axes[1, 0].set_title('💪 Recovery Scores')
            axes[1, 0].set_ylim(0, 10)
            axes[1, 0].grid(True, alpha=0.3)
        else:
            axes[1, 0].text(0.5, 0.5, 'No recovery data yet', ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('💪 Recovery Scores')

        # 5K time projection
        if pace_values:
            projected_times = [p * 5 for p in pace_values]  # Convert pace to 5K time
            axes[1, 1].plot(pace_weeks, projected_times, marker='o', linewidth=2, markersize=8, color='purple')
            axes[1, 1].set_xlabel('Week')
            axes[1, 1].set_ylabel('Projected 5K Time (min)')
            axes[1, 1].set_title('🎯 5K Time Projection')
            axes[1, 1].grid(True, alpha=0.3)
            
            # Add goal line (example: 25 minutes)
            goal_time = 25
            axes[1, 1].axhline(y=goal_time, color='red', linestyle='--', alpha=0.7, label=f'Goal: {goal_time} min')
            axes[1, 1].legend()
        else:
            axes[1, 1].text(0.5, 0.5, 'No projection data yet', ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('🎯 5K Time Projection')

        plt.tight_layout()
        plt.show()

    def reset_plan(self) -> None:
        """Reset the training plan by clearing all logs"""
        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
                print(f"✅ Training log file '{self.log_file}' has been deleted.")
            except OSError as e:
                print(f"❌ Error deleting log file: {e}")
        else:
            print("ℹ️  No log file found to delete.")

    def generate_detailed_sessions(self, session_count: int = 21) -> List[Dict[str, Any]]:
        """Generate detailed workout sessions using the new volume-focused approach"""
        
        def compute_sets(session_idx: int, run_min: float, week: int) -> int:
            """Calculate sets based on muscle endurance focus and progressive volume"""
            if run_min == 0:  # Old style continuous run day
                return 1
            
            # Check if it's a continuous run (walk_min = 0 in the interval_progress)
            if session_idx <= len(self.interval_progress):
                _, walk_min = self.interval_progress[session_idx - 1]
                if walk_min == 0:  # New style continuous run
                    return 1
            
            # CUSTOM SET NUMBERS for weeks 1-3 only
            custom_sets = {
                # Week 1: High volume muscle endurance building
                1: 16,  # Session 1: 1min run
                2: 12,  # Session 2: 2min run  
                3: 10,  # Session 3: 3min run
                
                # Week 2: Moderate volume with longer intervals
                4: 6,   # Session 4: 4min run
                5: 4,   # Session 5: 5min run
                6: 3,   # Session 6: 8min run
                
                # Week 3: Focus on longer intervals
                7: 5,   # Session 7: 6min run
                8: 3,   # Session 8: 8min run
                9: 2,   # Session 9: 10min run
            }
            
            # Use custom sets for sessions 1-9 (weeks 1-3), then calculate for later weeks
            if session_idx in custom_sets:
                return custom_sets[session_idx]
            
            # For weeks 4+ use calculated approach
            if week == 4:
                # Week 4 calculated sets
                if session_idx == 10:  # 6min run
                    return 6
                elif session_idx == 11:  # 28min continuous
                    return 1
                elif session_idx == 12:  # 7min run
                    return 5
            
            # For weeks 5+ use calculated approach
            if week == 5:
                base_sets = 8 - (session_idx - 13) * 0.5  # 8, 7.5, 7
                return max(6, int(base_sets))
            elif week == 6:
                base_sets = 7 - (session_idx - 16) * 0.5  # 7, 6.5, 6
                return max(5, int(base_sets))
            else:
                # Week 7: Taper
                base_sets = 5 - (session_idx - 19) * 0.5
                return max(3, int(base_sets))
        
        # Generate workout sessions
        workout_sessions = []
        for session_idx in range(1, session_count + 1):
            if session_idx > len(self.interval_progress):
                # Hybrid approach for Week 4+
                week = (session_idx - 1) // 3 + 1
                
                # Alternate between long intervals and continuous runs
                if session_idx % 2 == 1:  # Odd sessions: long intervals
                    run_min = 10.0
                    walk_min = 3.0
                    sets = compute_sets(session_idx, run_min, week)
                    workout_type = "long_intervals"
                else:  # Even sessions: moderate continuous run with walk breaks
                    # Continuous run with structured walk breaks
                    total_run_time = 20 + (session_idx - len(self.interval_progress)) * 2
                    run_min = total_run_time
                    walk_min = 0  # Continuous with brief breaks built in
                    sets = 1
                    workout_type = "continuous_with_breaks"
            else:
                run_min, walk_min = self.interval_progress[session_idx - 1]
                week = (session_idx - 1) // 3 + 1
                sets = compute_sets(session_idx, run_min, week)
                
                # Determine workout type
                if walk_min == 0:  # Continuous run
                    workout_type = "continuous_run"
                else:
                    workout_type = "interval_training"
            
            # Calculate day of week and day number
            week_num = (session_idx - 1) // 3 + 1
            day_in_week = (session_idx - 1) % 3 + 1
            
            # Map to actual days (Mon=1, Tue=2, Thu=4)
            day_mapping = {1: 1, 2: 2, 3: 4}  # Mon, Tue, Thu
            day_of_week = day_mapping[day_in_week]
            
            # Calculate total workout time and running volume
            total_run_time = run_min * sets
            total_workout_time = (run_min + walk_min) * sets if walk_min > 0 else run_min
            
            workout_sessions.append({
                "session": session_idx,
                "week": week_num,
                "day": day_of_week,
                "day_name": ["Mon", "Tue", "Thu"][day_in_week - 1],
                "run_minutes": run_min,
                "walk_minutes": walk_min,
                "sets": sets,
                "total_run_time": total_run_time,
                "total_workout_time": total_workout_time,
                "workout_type": workout_type,
                "focus": "muscle_endurance",
                "target_hr_zones": {
                    "run": "140-160 bpm" if day_in_week == 2 else "130-150 bpm",
                    "walk": "100-120 bpm"
                }
            })
            
        return workout_sessions

    def export_logs(self, filename: str = None) -> str:
        """Export training logs to a file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"training_export_{timestamp}.json"
            
        logs = self.load_logs()
        
        try:
            with open(filename, 'w') as f:
                json.dump(logs, f, indent=4)
            return f"✅ Training logs exported to '{filename}'"
        except IOError as e:
            return f"❌ Error exporting logs: {e}"
