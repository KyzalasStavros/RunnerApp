import streamlit as st

class PaceCalculator:
    """Simplified pace calculator with just running and walking pace inputs"""
    
    def __init__(self):
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables with defaults"""
        # Running pace: 7'30'' (7.5 min/km)
        if 'running_pace_min' not in st.session_state:
            st.session_state.running_pace_min = 7
        if 'running_pace_sec' not in st.session_state:
            st.session_state.running_pace_sec = 30
            
        # Walking pace: 11'00'' (11.0 min/km)
        if 'walking_pace_min' not in st.session_state:
            st.session_state.walking_pace_min = 11
        if 'walking_pace_sec' not in st.session_state:
            st.session_state.walking_pace_sec = 0
            
        # Fixed pace mode: True by default
        if 'fixed_pace_mode' not in st.session_state:
            st.session_state.fixed_pace_mode = True
    
    def render(self):
        """Render the simplified pace calculator"""
        st.markdown("### ⏱️ Pace Settings")
        
        # Fixed pace mode toggle
        fixed_mode = st.toggle(
            "Fixed Pace Mode", 
            value=True,  # Default to ON
            help="Fixed: Same pace for all intervals | Variable: Slower pace for longer intervals",
            key="fixed_pace_toggle"
        )
        st.session_state.fixed_pace_mode = fixed_mode
        
        # Layout: Two columns for running and walking pace
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏃 Running Pace**")
            
            # Running pace inputs
            pace_col1, pace_col2 = st.columns(2)
            with pace_col1:
                running_min = st.number_input(
                    "Minutes", 
                    value=7,
                    min_value=3,
                    max_value=15,
                    step=1,
                    key="running_pace_min_input"
                )
            with pace_col2:
                running_sec = st.number_input(
                    "Seconds", 
                    value=30,
                    min_value=0,
                    max_value=59,
                    step=5,
                    key="running_pace_sec_input"
                )
            
            # Update session state
            st.session_state.running_pace_min = running_min
            st.session_state.running_pace_sec = running_sec
            
            # Calculate lap time for 400m
            pace_total_min = running_min + (running_sec / 60.0)
            lap_distance_km = 0.4  # 400m lap
            lap_time_min = pace_total_min * lap_distance_km
            lap_time_sec = int(round(lap_time_min * 60))
            lap_min = lap_time_sec // 60
            lap_sec = lap_time_sec % 60
            
            # Display current running pace
            # st.info(f"🏃 **{running_min}'{running_sec:02d}''** per km")
            st.info(
                f"🏃 **{running_min}'{running_sec:02d}''** per km "
                f"| {lap_min}'{lap_sec:02d}'' per lap"
            )
                    
        with col2:
            st.markdown("**🚶 Walking Pace**")
            
            # Walking pace inputs
            walk_col1, walk_col2 = st.columns(2)
            with walk_col1:
                walking_min = st.number_input(
                    "Minutes", 
                    value=11,
                    min_value=8,
                    max_value=20,
                    step=1,
                    key="walking_pace_min_input"
                )
            with walk_col2:
                walking_sec = st.number_input(
                    "Seconds", 
                    value=0,
                    min_value=0,
                    max_value=59,
                    step=5,
                    key="walking_pace_sec_input"
                )
            
            # Update session state
            st.session_state.walking_pace_min = walking_min
            st.session_state.walking_pace_sec = walking_sec
            
            # Calculate lap time for 400m
            pace_total_min = walking_min + (walking_sec / 60.0)
            lap_distance_km = 0.4  # 400m lap
            lap_time_min = pace_total_min * lap_distance_km
            lap_time_sec = int(round(lap_time_min * 60))
            lap_min = lap_time_sec // 60
            lap_sec = lap_time_sec % 60

            # Display current walking pace
            # st.info(f"🚶 **{walking_min}'{walking_sec:02d}''** per km")
            st.info(
                f"🚶 **{walking_min}'{walking_sec:02d}''** per km "
                f"| {lap_min}'{lap_sec:02d}''per lap"
            )
        # Clear button
        col_spacer, col_button = st.columns([3, 1])
        # with col_button:
        #     if st.button("🗑️ Reset", help="Reset to default paces", key="reset_paces"):
        #         self._reset_to_defaults()
        #         st.rerun()
    
    # def _reset_to_defaults(self):
    #     """Reset pace values to defaults"""
    #     st.session_state.running_pace_min = 7
    #     st.session_state.running_pace_sec = 30
    #     st.session_state.walking_pace_min = 11
    #     st.session_state.walking_pace_sec = 0
    
    def get_running_speed_kmh(self):
        """Convert running pace to km/h"""
        pace_min = st.session_state.get('running_pace_min', 7)
        pace_sec = st.session_state.get('running_pace_sec', 30)
        pace_total_min = pace_min + (pace_sec / 60.0)
        
        if pace_total_min > 0:
            return 60 / pace_total_min  # Convert min/km to km/h
        else:
            return 8.0  # Fallback: 7'30'' pace = 8 km/h
    
    def get_walking_speed_m_per_min(self):
        """Convert walking pace to meters per minute"""
        pace_min = st.session_state.get('walking_pace_min', 11)
        pace_sec = st.session_state.get('walking_pace_sec', 0)
        pace_total_min = pace_min + (pace_sec / 60.0)
        
        if pace_total_min > 0:
            walking_speed_kmh = 60 / pace_total_min  # Convert to km/h first
            return (walking_speed_kmh * 1000) / 60  # Convert km/h to m/min
        else:
            return 90  # Fallback: ~5.4 km/h walking speed
    
    def is_fixed_pace_mode(self):
        """Get current fixed pace mode setting"""
        return st.session_state.get('fixed_pace_mode', True)


# Backward compatibility functions for existing imports
def render_pace_calculator():
    """Render pace calculator - for compatibility with existing code"""
    calculator = PaceCalculator()
    calculator.render()

def get_current_base_speed_kmh():
    """Get current running speed without creating instance"""
    calculator = PaceCalculator()
    return calculator.get_running_speed_kmh()

def get_current_walking_speed_m_per_min():
    """Get current walking speed without creating instance"""
    calculator = PaceCalculator()
    return calculator.get_walking_speed_m_per_min()

def get_current_fixed_pace_mode():
    """Get current fixed pace mode without creating instance"""
    return st.session_state.get('fixed_pace_mode', True)