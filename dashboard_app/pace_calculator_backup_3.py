#!/usr/bin/env python3
"""
Clean Pace Calculator Implementation
Simple, reliable pace/time/distance calculations for training dashboard
"""

import streamlit as st


class PaceCalculator:
    """Clean pace calculator with simple logic: Time + Distance → Pace"""
    
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'pace_time_min' not in st.session_state:
            st.session_state.pace_time_min = 0
        if 'pace_time_sec' not in st.session_state:
            st.session_state.pace_time_sec = 0
        if 'pace_distance' not in st.session_state:
            st.session_state.pace_distance = 0.0
        if 'pace_min_per_km' not in st.session_state:
            st.session_state.pace_min_per_km = 7.5  # Default 7'30'' pace
        if 'fixed_pace_mode' not in st.session_state:
            st.session_state.fixed_pace_mode = True  # Default to ON
    
    def render(self):
        """Render the pace calculator widget"""
        st.markdown("### 🏃‍♂️ Pace Calculator")
        
        # Info about calculation logic
        st.info("💡 **Logic**: Time + Distance → Calculate Pace | Pace + Distance → Calculate Time")
        
        # Fixed pace mode toggle with direct widget key usage
        fixed_mode = st.toggle(
            "Fixed Pace Mode", 
            value=True,  # Default to ON
            help="Fixed: Same pace for all intervals | Variable: Slower pace for longer intervals",
            key="fixed_pace_toggle"
        )
        
        # DEBUG: Track toggle changes
        print(f"🔧 TOGGLE DEBUG: Widget value = {fixed_mode}")
        print(f"🔧 TOGGLE DEBUG: Session state = {st.session_state.get('fixed_pace_mode', True)}")
        
        # Update session state from widget
        st.session_state.fixed_pace_mode = fixed_mode
        
        # Layout: Two columns for inputs
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_time_inputs()
            self._render_distance_input()
        
        # Calculate pace BEFORE rendering pace display and inputs
        self._pre_calculate_pace()
        
        with col2:
            self._render_pace_display()
            self._render_pace_inputs()
            self._render_clear_button()
        
        # Final calculation and update values
        self._perform_calculations()
    
    def _render_time_inputs(self):
        """Render time input fields"""
        st.markdown("**⏱️ Time**")
        time_col1, time_col2 = st.columns(2)
        
        with time_col1:
            time_min = st.number_input(
                "Minutes", 
                value=st.session_state.pace_time_min,
                min_value=0,
                max_value=300,
                step=1,
                key="input_time_min"
            )
            st.session_state.pace_time_min = time_min
        
        with time_col2:
            time_sec = st.number_input(
                "Seconds", 
                value=st.session_state.pace_time_sec,
                min_value=0,
                max_value=59,
                step=1,
                key="input_time_sec"
            )
            st.session_state.pace_time_sec = time_sec
    
    def _render_distance_input(self):
        """Render distance input field"""
        distance = st.number_input(
            "Distance (km)", 
            value=st.session_state.pace_distance,
            min_value=0.0,
            max_value=50.0,
            step=0.1,
            format="%.2f",
            key="input_distance"
        )
        st.session_state.pace_distance = distance
    
    def _render_pace_display(self):
        """Render pace display header using the best available pace value"""
        # Check if we have time and distance for automatic calculation
        time_total = st.session_state.pace_time_min + (st.session_state.pace_time_sec / 60.0)
        distance = st.session_state.pace_distance
        
        if time_total > 0 and distance > 0:
            # Use calculated pace when we have time + distance
            pace_display = self._format_pace_display(st.session_state.pace_min_per_km)
            st.markdown(f"**🏃 Pace ({pace_display} min/km)** 🔄 *Auto-calculated*")
            print(f"📊 DISPLAY DEBUG: Using calculated pace {pace_display} (time={time_total:.1f}, distance={distance:.1f})")
        else:
            # Use widget values when no calculation is possible
            current_pace_min = st.session_state.get('input_pace_min', 7)
            current_pace_sec = st.session_state.get('input_pace_sec', 30)
            current_pace_total = current_pace_min + (current_pace_sec / 60.0)
            pace_display = self._format_pace_display(current_pace_total)
            st.markdown(f"**🏃 Pace ({pace_display} min/km)** ✏️ *Manual input*")
            print(f"📊 DISPLAY DEBUG: Using widget pace {pace_display} (from widgets: {current_pace_min}'{current_pace_sec:02d}'')")
    
    def _render_pace_inputs(self):
        """Render pace input fields"""
        pace_col1, pace_col2 = st.columns(2)
        
        # Always determine what values to show based on current session state
        time_total = st.session_state.pace_time_min + (st.session_state.pace_time_sec / 60.0)
        distance = st.session_state.pace_distance
        
        # Show calculated pace when we have time + distance, otherwise show manual values
        if time_total > 0 and distance > 0:
            # Show calculated pace when we have time + distance
            display_pace_min = int(st.session_state.pace_min_per_km)
            display_pace_sec = int((st.session_state.pace_min_per_km - display_pace_min) * 60)
            input_disabled = True
            help_text = "Calculated from time + distance (read-only)"
            print(f"🎯 WIDGET DEBUG: Auto-calc mode - showing {display_pace_min}'{display_pace_sec:02d}''")
        else:
            # Show default/manual values when no calculation
            display_pace_min = 7
            display_pace_sec = 30
            input_disabled = False
            help_text = "Enter pace manually"
            print(f"🎯 WIDGET DEBUG: Manual mode - showing {display_pace_min}'{display_pace_sec:02d}''")
        
        with pace_col1:
            input_pace_min = st.number_input(
                "Minutes",
                value=display_pace_min,
                min_value=0,
                max_value=20,
                step=1,
                key="input_pace_min",
                disabled=input_disabled,
                help=help_text
            )
        
        with pace_col2:
            input_pace_sec = st.number_input(
                "Seconds",
                value=display_pace_sec,
                min_value=0,
                max_value=59,
                step=1,
                key="input_pace_sec",
                disabled=input_disabled,
                help=help_text
            )
        
        # Always use the current widget values for manual input
        self.manual_pace = input_pace_min + (input_pace_sec / 60.0)
        
        # DEBUG: Track pace input changes
        print(f"🎯 INPUT DEBUG: Widget values - min={input_pace_min}, sec={input_pace_sec}, total={self.manual_pace:.2f}, disabled={input_disabled}")
        if hasattr(self, '_last_manual_pace') and abs(self.manual_pace - self._last_manual_pace) > 0.01:
            print(f"🎯 INPUT DEBUG: Manual pace changed from {self._last_manual_pace:.2f} to {self.manual_pace:.2f}")
        self._last_manual_pace = self.manual_pace
    
    def _render_clear_button(self):
        """Render clear button"""
        st.markdown("")  # Space
        if st.button("🗑️ Clear", key="clear_button", use_container_width=True):
            self.clear_all_fields()
    
    def _pre_calculate_pace(self):
        """Pre-calculate pace for display purposes only"""
        time_total = st.session_state.pace_time_min + (st.session_state.pace_time_sec / 60.0)
        distance = st.session_state.pace_distance
        
        # If we have time and distance, calculate pace for display
        if time_total > 0 and distance > 0:
            calculated_pace = time_total / distance
            st.session_state.pace_min_per_km = calculated_pace
            print(f"🔄 PRE-CALC DEBUG: Display pace = {calculated_pace:.2f} min/km")
    
    def _perform_calculations(self):
        """Perform pace calculations based on current inputs"""
        time_total = st.session_state.pace_time_min + (st.session_state.pace_time_sec / 60.0)
        distance = st.session_state.pace_distance
        
        # DEBUG: Log current state
        print(f"🔍 CALC DEBUG: time_total={time_total:.2f}, distance={distance:.2f}, manual_pace={self.manual_pace:.2f}")
        print(f"🔍 CALC DEBUG: current pace_min_per_km={st.session_state.pace_min_per_km:.2f}")
        
        # PRIMARY RULE: If we have both time and distance, calculate pace
        if time_total > 0 and distance > 0:
            calculated_pace = time_total / distance
            st.session_state.pace_min_per_km = calculated_pace
            print(f"✅ CALC: Time+Distance → Pace = {calculated_pace:.2f} min/km")
            
        # SECONDARY RULE: If we have pace and distance but no time, calculate time
        elif self.manual_pace > 0 and distance > 0 and time_total == 0:
            calculated_time = self.manual_pace * distance
            st.session_state.pace_time_min = int(calculated_time)
            st.session_state.pace_time_sec = int((calculated_time - int(calculated_time)) * 60)
            st.session_state.pace_min_per_km = self.manual_pace
            print(f"✅ CALC: Pace+Distance → Time = {calculated_time:.2f} min")
        
        # FALLBACK: Use manual pace if entered
        elif self.manual_pace > 0:
            st.session_state.pace_min_per_km = self.manual_pace
            print(f"✅ CALC: Manual pace → {self.manual_pace:.2f} min/km")
        
        print(f"🎯 CALC DEBUG: Final pace_min_per_km={st.session_state.pace_min_per_km:.2f}")
        print("=" * 50)
    
    def _format_pace_display(self, pace_decimal):
        """Format pace as min'sec'' display"""
        if pace_decimal > 0:
            pace_min = int(pace_decimal)
            pace_sec = int((pace_decimal - pace_min) * 60)
            return f"{pace_min}'{pace_sec:02d}''"
        return "0'00''"
    
    def clear_all_fields(self):
        """Clear all calculator fields"""
        st.session_state.pace_time_min = 0
        st.session_state.pace_time_sec = 0
        st.session_state.pace_distance = 0.0
        st.session_state.pace_min_per_km = 7.5  # Reset to default
        st.rerun()
    
    # Public methods for integration with training dashboard
    def get_base_speed_kmh(self):
        """Get base speed in km/h for distance calculations"""
        # Ensure session state is initialized
        self.init_session_state()
        if st.session_state.pace_min_per_km > 0:
            return 60 / st.session_state.pace_min_per_km
        return 8.0  # Default speed (7'30'' pace)
    
    def is_fixed_pace_mode(self):
        """Check if fixed pace mode is enabled"""
        # Ensure session state is initialized
        self.init_session_state()
        return st.session_state.fixed_pace_mode
    
    def get_pace_display(self):
        """Get formatted pace for display"""
        # Ensure session state is initialized
        self.init_session_state()
        return self._format_pace_display(st.session_state.pace_min_per_km)


# Static helper functions for external use
def get_current_base_speed_kmh():
    """Get current base speed without creating instance"""
    # Initialize session state if needed
    if 'pace_min_per_km' not in st.session_state:
        st.session_state.pace_min_per_km = 7.5
    
    pace = st.session_state.pace_min_per_km
    speed = 60 / pace if pace > 0 else 8.0
    
    print(f"🚀 SPEED DEBUG: pace={pace:.2f} min/km → speed={speed:.2f} km/h")
    return speed

def get_current_fixed_pace_mode():
    """Get current fixed pace mode without creating instance"""
    # Initialize session state if needed
    if 'fixed_pace_mode' not in st.session_state:
        st.session_state.fixed_pace_mode = False
    
    mode = st.session_state.fixed_pace_mode
    print(f"🔧 MODE DEBUG: fixed_pace_mode={mode}")
    return mode

# Legacy function for backward compatibility
def render_pace_calculator():
    """Render pace calculator (legacy function)"""
    calc = PaceCalculator()
    calc.render()
    return {
        'base_speed_kmh': get_current_base_speed_kmh(),
        'is_fixed_pace': get_current_fixed_pace_mode(),
        'pace_display': calc.get_pace_display()
    }
