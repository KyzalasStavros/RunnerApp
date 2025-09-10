#!/usr/bin/env python3
"""
5K Training Plan Optimizer - Main application entry point
A 7-week adaptive training plan for 5K preparation
"""

import os
import sys

# Import our training plan module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from training_plan import TrainingPlan

class FiveKTrainingApp:
    def __init__(self):
        self.app_name = "5K Training Plan Optimizer"
        self.version = "1.0.0"
        self.training_plan = TrainingPlan()

    def welcome(self):
        """Display welcome message"""
        print(f"🏃‍♂️ Welcome to {self.app_name} v{self.version} 🏃‍♀️")
        print("Your personalized 7-week training plan to conquer that 5K!")
        print("=" * 60)
        
        # Show current status
        current_week = self.training_plan.get_current_week()
        if current_week == 0:
            print("Ready to start your 7-week journey? Let's get moving! 💪")
        elif current_week >= 7:
            print("🎉 Congratulations! You've completed the training plan!")
            print("Time to crush that 5K! 🏃‍♂️💨")
        else:
            print(f"Currently on Week {current_week + 1} of your training plan")
            
        print()

    def interactive_mode(self):
        """Run the app in interactive mode"""
        self.welcome()
        
        while True:
            print("\n" + "=" * 60)
            print("What would you like to do?")
            print("1. 📅 View current/remaining training plan")
            print("2. 📝 Log weekly performance")
            print("3. 🔄 Get plan adjustments")
            print("4. ⏱️  Get 5K time prediction")
            print("5. 📊 View progress graphs")
            print("6. 📋 View training history")
            print("7. ⚙️  Reset training plan")
            print("8. ❓ Help & guidelines")
            print("9. 🚪 Quit")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == '1':
                self.show_training_plan()
            elif choice == '2':
                self.log_weekly_performance()
            elif choice == '3':
                self.show_adjustments()
            elif choice == '4':
                self.show_prediction()
            elif choice == '5':
                self.show_progress()
            elif choice == '6':
                self.show_history()
            elif choice == '7':
                self.reset_plan()
            elif choice == '8':
                self.show_help()
            elif choice == '9':
                print("\nThanks for using the 5K Training Optimizer!")
                print("Remember: consistency is key! Keep running! 🏃‍♂️💪")
                break
            else:
                print("❌ Invalid choice. Please enter 1-9.")

    def show_training_plan(self):
        """Display the current and remaining training plan"""
        print("\n" + "🏃‍♂️ TRAINING PLAN 🏃‍♀️".center(60, "="))
        current_week = self.training_plan.get_current_week()
        self.training_plan.print_plan(current_week)

    def log_weekly_performance(self):
        """Log performance for a completed week"""
        print("\n" + "📝 LOG WEEKLY PERFORMANCE".center(60, "="))
        
        try:
            current_week = self.training_plan.get_current_week()
            if current_week >= 7:
                print("🎉 You've completed all 7 weeks! Great job!")
                return
                
            print(f"Logging performance for Week {current_week + 1}")
            print("\nPlease provide the following information:")
            
            # Get pace
            pace_input = input("Average pace (min/km) - optional, press Enter to skip: ").strip()
            pace = float(pace_input) if pace_input else None
            
            # Get distance
            distance_input = input("Longest run distance (km) - optional, press Enter to skip: ").strip()
            distance = float(distance_input) if distance_input else None
            
            # Get recovery rating
            while True:
                recovery_input = input("Recovery feeling (1-10, where 1=very tired, 10=fully recovered): ").strip()
                try:
                    recovery = int(recovery_input)
                    if 1 <= recovery <= 10:
                        break
                    else:
                        print("Please enter a number between 1 and 10")
                except ValueError:
                    print("Please enter a valid number")
            
            # Check if workouts were skipped
            skipped_input = input("Did you skip any major workouts this week? (y/n): ").strip().lower()
            skipped = skipped_input in ['y', 'yes']
            
            # Get comments
            comments = input("Additional comments (optional): ").strip()
            
            # Log the week
            self.training_plan.log_week(
                current_week + 1, 
                pace=pace, 
                distance=distance, 
                recovery=recovery, 
                skipped=skipped, 
                comments=comments
            )
            
            print(f"✅ Week {current_week + 1} performance logged successfully!")
            
        except ValueError:
            print("❌ Please enter valid numbers for pace and distance")
        except Exception as e:
            print(f"❌ Error logging performance: {e}")

    def show_adjustments(self):
        """Show plan adjustments based on logged performance"""
        print("\n" + "🔄 PLAN ADJUSTMENTS".center(60, "="))
        adjustments = self.training_plan.adjust_plan()
        
        if not adjustments:
            print("No adjustments needed at this time.")
            print("Keep following your current plan! 💪")
        else:
            print("Based on your performance, here are the recommended adjustments:")
            for week, adjustment in adjustments.items():
                print(f"\n📋 Week {week}: {adjustment}")

    def show_prediction(self):
        """Show 5K time prediction"""
        print("\n" + "⏱️  5K TIME PREDICTION".center(60, "="))
        prediction = self.training_plan.predict_5k()
        print(prediction)

    def show_progress(self):
        """Show progress graphs"""
        print("\n" + "📊 PROGRESS VISUALIZATION".center(60, "="))
        try:
            self.training_plan.plot_progress()
        except Exception as e:
            print(f"❌ Error generating graphs: {e}")
            print("Make sure you have logged some performance data first.")

    def show_history(self):
        """Show training history"""
        print("\n" + "📋 TRAINING HISTORY".center(60, "="))
        logs = self.training_plan.load_logs()
        
        if not logs:
            print("No training history found.")
            print("Start logging your weekly performances to see your progress!")
            return
        
        print(f"{'Week':<6} {'Pace':<10} {'Distance':<10} {'Recovery':<10} {'Skipped':<8} {'Comments'}")
        print("-" * 70)
        
        for week in sorted(logs.keys(), key=int):
            data = logs[week]
            pace = f"{data['pace']:.1f}" if data['pace'] else "N/A"
            distance = f"{data['distance']:.1f}" if data['distance'] else "N/A"
            recovery = str(data['recovery']) if data['recovery'] else "N/A"
            skipped = "Yes" if data['skipped'] else "No"
            comments = data['comments'][:20] + "..." if len(data['comments']) > 20 else data['comments']
            
            print(f"{week:<6} {pace:<10} {distance:<10} {recovery:<10} {skipped:<8} {comments}")

    def reset_plan(self):
        """Reset the training plan"""
        print("\n" + "⚙️  RESET TRAINING PLAN".center(60, "="))
        confirm = input("Are you sure you want to reset your training plan? This will delete all logs (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            self.training_plan.reset_plan()
            print("✅ Training plan has been reset. You can start fresh!")
        else:
            print("Reset cancelled.")

    def show_help(self):
        """Show help and guidelines"""
        print("\n" + "❓ HELP & GUIDELINES".center(60, "="))
        print("""
🏃‍♂️ TERMINOLOGY & TRAINING GUIDELINES:

📍 Run/Walk Intervals:
   • Run: faster, purposeful running (HR: 140-160 bpm)
   • Walk: active recovery, comfortable pace (HR: 100-120 bpm)

📍 Jog vs Run:
   • Jog/Easy pace: conversational speed, RPE 3-4 (HR: 100-130 bpm)
   • Run/Brisk pace: faster, effortful pace, RPE 6-8 (HR: 140-160 bpm)

📍 Strides:
   • Short bursts (15-20s) near sprint pace, RPE 7-9 (HR: 150-170 bpm)

📍 Intervals:
   • Structured fast running with recovery periods, RPE 6-8 (HR: 140-160 bpm)

📍 Long Run:
   • Slower, endurance-focused run, RPE 3-5 (HR: 110-140 bpm)

📍 Strength Training Options:
   • Bodyweight: squats, lunges, planks, push-ups, burpees
   • Focus on legs, core, and functional movement patterns
   • 20-30 minutes, 2-3x per week on non-running days

📍 Cross-Training Alternatives:
   • Plyometrics: jump squats, box jumps, skipping rope
   • Yoga/Mobility: improves flexibility and recovery
   • Stair climbing: great cardio alternative
   • Brisk walking: active recovery option

💡 TRAINING STRUCTURE:
   • 4 main training days per week (Mon, Wed, Thu, Fri)
   • 3 rest days for recovery and optional strength work
   • Same total weekly volume as 5-day plans, better distributed
   • Tuesdays: strength/cross-training or complete rest
   • Weekends: rest and recovery

💡 TIPS:
   • Listen to your body to avoid injury
   • Consistency is more important than intensity
   • Use rest days for strength work or complete recovery
   • Stay hydrated and get adequate sleep
   • Adjust intensity based on how you feel

📱 USING THIS APP:
   1. Check your weekly plan regularly
   2. Log your performance after each week
   3. Follow the adjustment recommendations
   4. Track your progress with graphs
   5. Stay motivated with time predictions!
        """)

def main():
    """Main function"""
    app = FiveKTrainingApp()
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("5K Training Plan Optimizer")
            print("\nUsage:")
            print("  python main.py                    # Interactive mode")
            print("  python main.py --help             # Show this help")
            return
    
    # Run in interactive mode
    app.interactive_mode()

if __name__ == "__main__":
    main()
