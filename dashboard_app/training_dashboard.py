#!/usr/bin/env python3
"""
Interactive Training Plan Dashboard
Real-time editing of training sessions with automatic graph updates
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
import sys
from datetime import datetime
import numpy as np

# Add parent directory to path to import our training plan
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.training_plan import TrainingPlan
from dashboard_app.pace_calculator import render_pace_calculator, PaceCalculator, get_current_base_speed_kmh, get_current_fixed_pace_mode


class TrainingDashboard:
    """Interactive dashboard for training plan editing and visualization"""
    
    def __init__(self):
        self.setup_page_config()
        self.training_plan = TrainingPlan()
        self.custom_plans_dir = "dashboard_app/saved_plans"
        self.deleted_plans_dir = "dashboard_app/deleted_plans"
        self.ensure_save_directory()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Training Plan Dashboard",
            page_icon="🏃‍♂️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS to style legend elements
        st.markdown("""
        <style>
        /* Make legend lines thinner */
        .legendlines .js-line {
            stroke-width: 1px !important;
        }
        
        /* Make legend markers smaller */
        .legendsymbols .legendpoints .scatterpts {
            transform: translate(20px,0) scale(0.5) !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def ensure_save_directory(self):
        """Ensure the saved plans and deleted plans directories exist"""
        if not os.path.exists(self.custom_plans_dir):
            os.makedirs(self.custom_plans_dir)
        if not os.path.exists(self.deleted_plans_dir):
            os.makedirs(self.deleted_plans_dir)
    
    def get_session_data(self):
        """Extract session data from training plan"""
        detailed_sessions = self.training_plan.generate_detailed_sessions(21)
        sessions_data = []
        
        # Convert day names to numbers
        day_name_to_number = {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7}
        
        for session in detailed_sessions:
            day_name = session['day_name']
            day_number = day_name_to_number.get(day_name, 1)  # Default to 1 if not found
            
            sessions_data.append({
                'Session': session['session'],
                'Week': session['week'],
                'Day': day_number,
                'Run (min)': session['run_minutes'],
                'Walk (min)': session['walk_minutes'],
                'Sets': session['sets'],
                'Total Run (min)': session['total_run_time'],
                'Total Workout (min)': session['total_workout_time'],
                'Workout Type': session['workout_type']
            })
        
        return pd.DataFrame(sessions_data)
    
    def calculate_distances(self, df):
        """Calculate running and total distances with fatigue modeling"""
        print(f"\n📊 DASHBOARD: Starting distance calculation for {len(df)} rows")
        
        # Get base speed from pace calculator using static functions
        base_speed_kmh = get_current_base_speed_kmh()
        is_fixed_pace = get_current_fixed_pace_mode()
        
        print(f"📊 DASHBOARD: Using base_speed={base_speed_kmh:.2f} km/h, fixed_pace={is_fixed_pace}")
        
        walk_speed_m_per_min = 100
        
        running_distances = []
        total_distances = []
        
        for _, row in df.iterrows():
            run_min = row['Run (min)']
            walk_min = row['Walk (min)']
            sets = row['Sets']
            
            # Adjust speed based on interval duration (only if not in fixed pace mode)
            if is_fixed_pace:
                speed_kmh = base_speed_kmh
            else:
                # Adjust speed based on interval duration
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
        
        df['Running Distance (km)'] = running_distances
        df['Total Distance (km)'] = total_distances
        
        return df
    
    def create_progression_charts(self, df):
        """Create the 3 vertically stacked progression charts"""
        # Calculate weekly totals
        weekly_data = df.groupby('Week').agg({
            'Total Run (min)': 'sum',
            'Total Workout (min)': 'sum',
            'Running Distance (km)': 'sum',
            'Total Distance (km)': 'sum'
        }).reset_index()
        
        # Create subplots - 3 charts in vertical layout
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=(
                'Running Time Progression',
                'Distance Progression', 
                'Weekly Running Volume'
            ),
            vertical_spacing=0.15,  # Increased spacing between plots for better separation
            specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Top Chart: Running Time Progression
        fig.add_trace(
            go.Scatter(
                x=df['Session'],
                y=df['Total Run (min)'],  # Total running time per session
                mode='lines+markers',
                name='Total Run Time',  # Shortened legend text
                line=dict(color='red', width=2),
                marker=dict(size=6)  # Smaller markers for cleaner legend
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['Session'],
                y=df['Total Workout (min)'],
                mode='lines+markers',
                name='Total Session Time',  # Shortened legend text
                line=dict(color='blue', width=2),
                marker=dict(size=6)  # Smaller markers for cleaner legend
            ),
            row=1, col=1
        )
        
        # Middle Chart: Distance Progression
        fig.add_trace(
            go.Scatter(
                x=df['Session'],
                y=df['Total Distance (km)'],
                mode='lines+markers',
                name='Total Distance',  # Shortened
                line=dict(color='green', width=2, dash='dash'),  # Fixed color
                marker=dict(size=6)  # Smaller markers for cleaner legend
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['Session'],
                y=df['Running Distance (km)'],
                mode='lines+markers',
                name='Running Distance',  # Shortened
                line=dict(color='darkgreen', width=2),  # Fixed color
                marker=dict(size=6)  # Smaller markers for cleaner legend
            ),
            row=2, col=1
        )
        
        # Bottom Chart: Weekly Volume
        fig.add_trace(
            go.Bar(
                x=weekly_data['Week'],
                y=weekly_data['Total Run (min)'],
                name='Weekly Running Volume',
                marker_color='orange',
                showlegend=False
            ),
            row=3, col=1
        )
        
        # Don't add vertical lines to avoid compatibility issues with table subplots
        # Week boundaries are clearly visible in the color-coded table instead
        
        # Update layout for vertical chart arrangement
        fig.update_layout(
            title_text="Training Plan Progression Analysis",
            title_x=0.0,  # Left-aligned title instead of centered
            title_font_size=14,  # Slightly smaller font to fit better
            title_pad=dict(t=10, b=5),  # Reduced padding above (t) and below (b) title
            height=950,  # Increased height to match table height
            showlegend=True,
            legend=dict(
                x=0.5,  # Center horizontally
                y=1,  # Moved higher up for better positioning
                xanchor='center',  # Center anchor point
                yanchor='top',  # Top anchor point
                font=dict(size=10, color='white'),  # White font for dark background
                bgcolor='rgba(0,0,0,0.8)',  # Dark semi-transparent background
                bordercolor='rgba(255,255,255,0.3)',  # Light border for dark theme
                borderwidth=1,
                orientation='h',  # Horizontal orientation for top placement
                itemsizing='constant',  # Consistent sizing
                tracegroupgap=5,  # Space between legend items
            ),
            margin=dict(l=60, r=30, t=80, b=30)  # Reduced top and bottom margins for less spacing
        )
        
        # Update axes labels for vertical layout
        fig.update_xaxes(title_text="Training Session", row=1, col=1)
        fig.update_yaxes(title_text="Time (minutes)", row=1, col=1)
        fig.update_xaxes(title_text="Training Session", row=2, col=1)
        fig.update_yaxes(title_text="Distance (km)", row=2, col=1)
        fig.update_xaxes(title_text="Week", row=3, col=1)
        fig.update_yaxes(title_text="Total Running Time (minutes)", row=3, col=1)
        
        # Add extra space above the first chart for the legend by extending y-axis range
        first_chart_max = max(df['Total Run (min)'].max(), df['Total Workout (min)'].max())
        fig.update_yaxes(range=[0, first_chart_max + 40], row=1, col=1)
        
        return fig
    
    def save_custom_plan(self, df, plan_name):
        """Save custom training plan to JSON file"""
        plan_data = {
            'name': plan_name,
            'created': datetime.now().isoformat(),
            'sessions': df.to_dict('records')
        }
        
        filename = f"{self.custom_plans_dir}/{plan_name.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(plan_data, f, indent=2)
        
        return filename
    
    def load_custom_plan(self, filename):
        """Load custom training plan from JSON file"""
        filepath = f"{self.custom_plans_dir}/{filename}"
        with open(filepath, 'r') as f:
            plan_data = json.load(f)
        
        return pd.DataFrame(plan_data['sessions'])
    
    def get_saved_plans(self):
        """Get list of saved plan files"""
        if not os.path.exists(self.custom_plans_dir):
            return []
        
        plans = []
        for filename in os.listdir(self.custom_plans_dir):
            if filename.endswith('.json'):
                plans.append(filename)
        
        return plans
    
    def delete_plan(self, plan_name):
        """Move a plan to the deleted_plans folder instead of permanent deletion"""
        import shutil
        from datetime import datetime
        
        # Add .json extension if not present
        if not plan_name.endswith('.json'):
            plan_name += '.json'
        
        source_path = f"{self.custom_plans_dir}/{plan_name}"
        
        # Create timestamp for the deleted file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = plan_name.replace('.json', '')
        deleted_filename = f"{base_name}_deleted_{timestamp}.json"
        destination_path = f"{self.deleted_plans_dir}/{deleted_filename}"
        
        try:
            # Move the file to deleted folder
            shutil.move(source_path, destination_path)
            return True, f"Plan moved to deleted_plans/{deleted_filename}"
        except Exception as e:
            return False, f"Error deleting plan: {str(e)}"
    
    def add_new_session(self, df):
        """Add a new session to the training plan with proper week/day calculation"""
        if len(df) == 0:
            # First session
            new_session = {
                'Session': 1,
                'Week': 1,
                'Day': 1,  # Monday = 1
                'Run (min)': 1.0,
                'Walk (min)': 2.0,
                'Sets': 10,
                'Total Run (min)': 10.0,
                'Total Workout (min)': 30.0,
                'Workout Type': 'Intervals'
            }
        else:
            last_session = df.iloc[-1]
            new_session_num = last_session['Session'] + 1
            
            # Calculate week and day based on session pattern (Mon-Tue-Thu = 3 sessions per week)
            sessions_per_week = 3
            new_week = ((new_session_num - 1) // sessions_per_week) + 1
            session_in_week = ((new_session_num - 1) % sessions_per_week) + 1
            
            # Map session in week to day (1=Monday, 2=Tuesday, 4=Thursday, etc.)
            day_mapping = {1: 1, 2: 2, 3: 4}  # Mon=1, Tue=2, Thu=4
            new_day = day_mapping[session_in_week]
            
            # Default values for new session (can be customized)
            new_session = {
                'Session': new_session_num,
                'Week': new_week,
                'Day': new_day,
                'Run (min)': 5.0,  # Default run time
                'Walk (min)': 1.5,  # Default walk time
                'Sets': 6,  # Default sets
                'Total Run (min)': 30.0,  # Will be recalculated
                'Total Workout (min)': 39.0,  # Will be recalculated
                'Workout Type': 'Intervals'
            }
            
            # Recalculate totals
            if new_session['Walk (min)'] == 0:  # Continuous run
                new_session['Total Run (min)'] = new_session['Run (min)']
                new_session['Total Workout (min)'] = new_session['Run (min)']
                new_session['Workout Type'] = 'Continuous'
            else:  # Intervals
                total_run = new_session['Run (min)'] * new_session['Sets']
                total_walk = new_session['Walk (min)'] * new_session['Sets']
                new_session['Total Run (min)'] = total_run
                new_session['Total Workout (min)'] = total_run + total_walk
                new_session['Workout Type'] = 'Intervals'
        
        # Add new session to dataframe
        new_df = pd.concat([df, pd.DataFrame([new_session])], ignore_index=True)
        return new_df
    
    def run(self):
        """Main dashboard application"""
        st.title("🏃‍♂️ Interactive Training Plan Dashboard")
        st.markdown("Edit your training sessions in the comprehensive table and see real-time updates to progression charts!")
        
        # Sidebar for plan management
        st.sidebar.header("Plan Management")
        
        # Load/Save options
        action = st.sidebar.selectbox(
            "Choose Action",
            ["Create New", "Load Saved Plan", "Save Current Plan", "Delete Plan"]
        )
        
        # Initialize session state for the dataframe and track loaded plan
        if 'training_df' not in st.session_state:
            st.session_state.training_df = self.get_session_data()
        if 'current_plan_name' not in st.session_state:
            st.session_state.current_plan_name = None  # Track currently loaded plan
        if 'plan_modified' not in st.session_state:
            st.session_state.plan_modified = False  # Track if plan has been modified
        
        # Handle different actions
        if action == "Load Saved Plan":
            saved_plans = self.get_saved_plans()
            if saved_plans:
                selected_plan = st.sidebar.selectbox("Select Plan", saved_plans)
                if st.sidebar.button("Load Plan"):
                    st.session_state.training_df = self.load_custom_plan(selected_plan)
                    st.session_state.current_plan_name = selected_plan.replace('.json', '')
                    st.session_state.plan_modified = False
                    st.success(f"Loaded plan: {selected_plan}")
            else:
                st.sidebar.info("No saved plans found")
        
        elif action == "Save Current Plan":
            # Show current plan status
            if st.session_state.current_plan_name:
                st.sidebar.info(f"📄 Current plan: **{st.session_state.current_plan_name}**")
                if st.session_state.plan_modified:
                    st.sidebar.warning("⚠️ Plan has unsaved changes")
                
                # Option 1: Update existing plan
                if st.sidebar.button("💾 Update Current Plan", help="Save changes to the current plan"):
                    filename = self.save_custom_plan(st.session_state.training_df, st.session_state.current_plan_name)
                    st.session_state.plan_modified = False
                    st.success(f"Updated plan: {st.session_state.current_plan_name}")
                
                st.sidebar.markdown("---")  # Separator
            
            # Option 2: Save as new plan
            st.sidebar.markdown("**Save as New Plan:**")
            plan_name = st.sidebar.text_input("New Plan Name", placeholder="Enter new plan name...")
            if st.sidebar.button("💾 Save as New Plan") and plan_name:
                if plan_name != st.session_state.current_plan_name:  # Prevent overwriting current plan accidentally
                    filename = self.save_custom_plan(st.session_state.training_df, plan_name)
                    st.success(f"Saved new plan: {plan_name}")
                else:
                    st.error("Please choose a different name or use 'Update Current Plan'")
        
        elif action == "Create New":
            if st.sidebar.button("Reset to Default"):
                st.session_state.training_df = self.get_session_data()
                st.session_state.current_plan_name = None
                st.session_state.plan_modified = False
                st.success("Reset to default training plan")
        
        elif action == "Delete Plan":
            saved_plans = self.get_saved_plans()
            if saved_plans:
                # Determine the default selection (currently loaded plan)
                current_plan_file = None
                default_index = 0
                
                if st.session_state.current_plan_name:
                    current_plan_file = f"{st.session_state.current_plan_name}.json"
                    if current_plan_file in saved_plans:
                        default_index = saved_plans.index(current_plan_file)
                
                selected_plan = st.sidebar.selectbox(
                    "Select Plan to Delete", 
                    saved_plans,
                    index=default_index,
                    help="Currently loaded plan is preselected"
                )
                
                # Show current plan indicator
                if st.session_state.current_plan_name and selected_plan == f"{st.session_state.current_plan_name}.json":
                    st.sidebar.info("📋 This is your currently loaded plan")
                
                # Show warning
                st.sidebar.warning("⚠️ This will move the plan to deleted_plans folder")
                
                # Initialize confirmation state
                if 'delete_confirmation' not in st.session_state:
                    st.session_state.delete_confirmation = False
                
                # Two-step deletion process
                if not st.session_state.delete_confirmation:
                    if st.sidebar.button("🗑️ Delete Plan", help="Click to confirm deletion"):
                        st.session_state.delete_confirmation = True
                        st.rerun()
                else:
                    col1, col2 = st.sidebar.columns(2)
                    with col1:
                        if st.button("✅ Confirm Delete", help="Final confirmation"):
                            success, message = self.delete_plan(selected_plan)
                            if success:
                                # If we deleted the currently loaded plan, reset
                                if st.session_state.current_plan_name == selected_plan.replace('.json', ''):
                                    st.session_state.current_plan_name = None
                                    st.session_state.plan_modified = False
                                st.success(message)
                            else:
                                st.error(message)
                            st.session_state.delete_confirmation = False
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel"):
                            st.session_state.delete_confirmation = False
                            st.rerun()
            else:
                st.sidebar.info("No saved plans to delete")
        
        # Main content area - table gets more space, charts get fixed width
        col1, col2 = st.columns([2, 1])  # 2:1 ratio gives table 66% of space
        
        with col1:
            st.header("📋 Training Plan Editor")
            st.markdown("**Edit sessions & see totals update automatically**")
            
            # Add session management buttons
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("➕ Add Session", help="Add a new training session"):
                    st.session_state.training_df = self.add_new_session(st.session_state.training_df)
                    st.session_state.plan_modified = True
                    st.rerun()
            
            with col_btn2:
                if st.button("🗑️ Remove Last", help="Remove the last session"):
                    if len(st.session_state.training_df) > 1:  # Keep at least 1 session
                        st.session_state.training_df = st.session_state.training_df.iloc[:-1].reset_index(drop=True)
                        st.session_state.plan_modified = True
                        st.rerun()
                    else:
                        st.warning("Cannot remove the last remaining session!")
            
            st.markdown("---")  # Separator line
            
            # Show current plan info
            current_sessions = len(st.session_state.training_df)
            current_weeks = st.session_state.training_df['Week'].max() if current_sessions > 0 else 0
            st.info(f"📊 Current Plan: **{current_sessions} sessions** across **{current_weeks} weeks**")
            
            # Create an editable dataframe with all essential information
            edited_df = st.data_editor(
                st.session_state.training_df[['Session', 'Week', 'Day', 'Run (min)', 'Walk (min)', 'Sets', 'Total Run (min)', 'Total Workout (min)']],
                column_config={
                    "Session": st.column_config.NumberColumn(
                        "Session #",
                        disabled=True,
                        width="small"
                    ),
                    "Week": st.column_config.NumberColumn(
                        "Week",
                        disabled=True,
                        width="small"
                    ),
                    "Day": st.column_config.NumberColumn(
                        "Day",
                        min_value=1,
                        max_value=7,
                        step=1,
                        width="small",
                        help="Day of week (1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat, 7=Sun)"
                    ),
                    "Run (min)": st.column_config.NumberColumn(
                        "Run (min)",
                        min_value=0.0,
                        max_value=60.0,
                        step=0.5,
                        format="%.1f",
                        help="Duration of running intervals"
                    ),
                    "Walk (min)": st.column_config.NumberColumn(
                        "Walk (min)",
                        min_value=0.0,
                        max_value=10.0,
                        step=0.5,
                        format="%.1f",
                        help="Duration of walking recovery (0 = continuous run)"
                    ),
                    "Sets": st.column_config.NumberColumn(
                        "Sets",
                        min_value=1,
                        max_value=20,
                        step=1,
                        help="Number of run/walk repetitions"
                    ),
                    "Total Run (min)": st.column_config.NumberColumn(
                        "Total Run (min)",
                        disabled=True,
                        format="%.1f",
                        help="Calculated total running time"
                    ),
                    "Total Workout (min)": st.column_config.NumberColumn(
                        "Total Workout (min)",
                        disabled=True,
                        format="%.1f",
                        help="Total session duration"
                    )
                },
                width='stretch',
                height=850,  # Increased to show all 21+ rows (approximately 40px per row)
                hide_index=True
            )
            
            # Update the session state when data is edited
            editable_columns = ['Session', 'Week', 'Day', 'Run (min)', 'Walk (min)', 'Sets']
            if not edited_df[editable_columns].equals(st.session_state.training_df[editable_columns]):
                # Update only the editable fields
                st.session_state.training_df['Run (min)'] = edited_df['Run (min)']
                st.session_state.training_df['Walk (min)'] = edited_df['Walk (min)']
                st.session_state.training_df['Sets'] = edited_df['Sets']
                
                # Mark plan as modified
                st.session_state.plan_modified = True
                
                # Recalculate totals
                for i, row in st.session_state.training_df.iterrows():
                    if row['Walk (min)'] == 0:  # Continuous run
                        st.session_state.training_df.at[i, 'Total Run (min)'] = row['Run (min)']
                        st.session_state.training_df.at[i, 'Total Workout (min)'] = row['Run (min)']
                        st.session_state.training_df.at[i, 'Workout Type'] = 'Continuous'
                    else:  # Intervals
                        total_run = row['Run (min)'] * row['Sets']
                        total_walk = row['Walk (min)'] * row['Sets']
                        st.session_state.training_df.at[i, 'Total Run (min)'] = total_run
                        st.session_state.training_df.at[i, 'Total Workout (min)'] = total_run + total_walk
                        st.session_state.training_df.at[i, 'Workout Type'] = 'Intervals'
                
                st.rerun()
        
        with col2:
            # Add pace calculator first
            render_pace_calculator()
            
            st.markdown("---")  # Separator line
            
            st.header("📊 Live Progression Charts")
            
            # Calculate distances and create charts
            df_with_distances = self.calculate_distances(st.session_state.training_df.copy())
            chart = self.create_progression_charts(df_with_distances)
            
            # Display the chart with controlled sizing
            st.plotly_chart(chart, use_container_width=True)
        
        # Training Plan Logic Explanation
        st.header("🧠 Training Plan Logic & Best Practices")
        
        with st.expander("📚 What Makes a Good Training Plan?", expanded=False):
            st.markdown("""
            **Progressive Overload Principles:**
            - **Gradual Intensity Increase**: Run times should progressively increase week by week
            - **Volume Management**: Total weekly running time should build by 10-15% per week
            - **Recovery Balance**: Include adequate rest between high-intensity sessions
            
            **Periodization Strategy:**
            - **Weeks 1-3**: Build aerobic base with shorter intervals and higher volume
            - **Weeks 4-6**: Introduce longer intervals and continuous runs for endurance
            - **Week 7+**: Taper and race-specific preparation
            
            **Key Metrics to Monitor:**
            - **Weekly Volume**: Aim for steady progression without sudden jumps
            - **Intensity Distribution**: 80% easy/moderate, 20% hard efforts
            - **Recovery Ratio**: Start with longer walks, gradually reduce rest periods
            
            **Session Structure Guidelines:**
            - **Day 1 (Monday)**: Interval training for speed/anaerobic capacity
            - **Day 2 (Tuesday)**: Tempo or sustained efforts for lactate threshold
            - **Day 4 (Thursday)**: Long intervals or continuous runs for aerobic power
            - **Rest Days**: Essential for adaptation and injury prevention
            
            **Distance Progression:**
            - **Running Distance**: Should increase as fitness improves (shown in charts above)
            - **Pace Variations**: Shorter intervals = faster pace, longer intervals = sustainable pace
            - **Total Distance**: Includes both running and walking for complete training load
            """)
        
        # Additional statistics
        st.header("📈 Training Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_run_time_hours = st.session_state.training_df['Total Run (min)'].sum() / 60
            st.metric("Total Running Time", f"{total_run_time_hours:.1f} hours")
        
        with col2:
            total_workout_time_hours = st.session_state.training_df['Total Workout (min)'].sum() / 60
            st.metric("Total Workout Time", f"{total_workout_time_hours:.1f} hours")
        
        with col3:
            avg_session_time_minutes = st.session_state.training_df['Total Workout (min)'].mean()
            st.metric("Avg Session Time", f"{avg_session_time_minutes:.1f} minutes")
        
        with col4:
            df_with_distances = self.calculate_distances(st.session_state.training_df.copy())
            total_run_distance = df_with_distances['Running Distance (km)'].sum()
            st.metric("Total Run Distance", f"{total_run_distance:.1f} km")
        
        # Weekly breakdown with distance calculations
        st.header("📅 Weekly Breakdown")
        
        # Calculate distances for weekly breakdown
        df_with_distances = self.calculate_distances(st.session_state.training_df.copy())
        
        weekly_stats = df_with_distances.groupby('Week').agg({
            'Total Run (min)': ['sum', 'mean'],
            'Total Workout (min)': 'sum',
            'Running Distance (km)': ['sum', 'mean']
        }).round(2)
        
        # Flatten column names
        weekly_stats.columns = [
            'Total Run (min)', 
            'Avg Run Time/Session (min)',
            'Total Workout (min)', 
            'Total Distance Run (km)',
            'Avg Distance/Session (km)'
        ]
        
        # Add session count per week
        session_counts = df_with_distances.groupby('Week').size()
        weekly_stats['Sessions'] = session_counts
        
        # Reorder columns for better readability
        weekly_stats = weekly_stats[['Sessions', 'Total Run (min)', 'Total Workout (min)', 
                                   'Total Distance Run (km)', 'Avg Run Time/Session (min)', 'Avg Distance/Session (km)']]
        
        st.dataframe(weekly_stats, width='stretch')


def main():
    """Run the dashboard application"""
    dashboard = TrainingDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
