"""
Test suite for the 5K Training Plan App
"""

import pytest
import sys
import os
import json
import tempfile
from unittest.mock import patch, mock_open

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from training_plan import TrainingPlan


class TestTrainingPlan:
    """Test cases for the TrainingPlan class"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Use a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.training_plan = TrainingPlan(log_file=self.temp_file.name)
    
    def teardown_method(self):
        """Cleanup after each test method"""
        # Remove the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_training_plan_creation(self):
        """Test creating a new training plan"""
        assert self.training_plan.log_file == self.temp_file.name
        assert len(self.training_plan.base_plan) == 7
        assert all(week in self.training_plan.base_plan for week in range(1, 8))
    
    def test_empty_logs(self):
        """Test behavior with empty logs"""
        logs = self.training_plan.load_logs()
        assert logs == {}
        
        current_week = self.training_plan.get_current_week()
        assert current_week == 0
    
    def test_log_week(self):
        """Test logging a week's performance"""
        self.training_plan.log_week(
            week=1, 
            pace=6.5, 
            distance=3.0, 
            recovery=7, 
            skipped=False, 
            comments="Good first week"
        )
        
        logs = self.training_plan.load_logs()
        assert "1" in logs
        assert logs["1"]["pace"] == 6.5
        assert logs["1"]["distance"] == 3.0
        assert logs["1"]["recovery"] == 7
        assert logs["1"]["skipped"] is False
        assert logs["1"]["comments"] == "Good first week"
        assert "logged_at" in logs["1"]
    
    def test_get_current_week(self):
        """Test getting the current week"""
        # Initially should be week 0
        assert self.training_plan.get_current_week() == 0
        
        # After logging week 1
        self.training_plan.log_week(1, pace=6.0)
        assert self.training_plan.get_current_week() == 1
        
        # After logging week 3
        self.training_plan.log_week(3, pace=5.5)
        assert self.training_plan.get_current_week() == 3
    
    def test_adjust_plan_skipped_workout(self):
        """Test plan adjustment when workouts are skipped"""
        self.training_plan.log_week(1, recovery=6, skipped=True)
        adjustments = self.training_plan.adjust_plan()
        
        assert 2 in adjustments
        assert "Reduce intensity" in adjustments[2]
    
    def test_adjust_plan_low_recovery(self):
        """Test plan adjustment for low recovery"""
        self.training_plan.log_week(1, recovery=3, skipped=False)
        adjustments = self.training_plan.adjust_plan()
        
        assert 2 in adjustments
        assert "extra rest" in adjustments[2] or "reduce intensity" in adjustments[2]
    
    def test_adjust_plan_high_recovery(self):
        """Test plan adjustment for high recovery"""
        self.training_plan.log_week(1, recovery=9, skipped=False)
        adjustments = self.training_plan.adjust_plan()
        
        assert 2 in adjustments
        assert ("increasing intensity" in adjustments[2] or 
                "extra workout" in adjustments[2] or
                "recovering well" in adjustments[2])
    
    def test_predict_5k_no_data(self):
        """Test 5K prediction with no data"""
        prediction = self.training_plan.predict_5k()
        assert "Not enough data" in prediction
    
    def test_predict_5k_with_data(self):
        """Test 5K prediction with pace data"""
        # Log a week with pace data
        self.training_plan.log_week(2, pace=6.0, recovery=7)
        
        prediction = self.training_plan.predict_5k()
        assert "5K Time Prediction" in prediction
        assert "Current estimated time: 30.0 minutes" in prediction
        assert "Projected race day time:" in prediction
    
    def test_predict_5k_no_pace_data(self):
        """Test 5K prediction with logs but no pace data"""
        self.training_plan.log_week(1, distance=3.0, recovery=6)
        
        prediction = self.training_plan.predict_5k()
        assert "No pace data available" in prediction
    
    def test_reset_plan(self):
        """Test resetting the training plan"""
        # First log some data
        self.training_plan.log_week(1, pace=6.0)
        assert self.training_plan.get_current_week() == 1
        
        # Reset the plan
        self.training_plan.reset_plan()
        
        # Should be back to empty
        assert self.training_plan.get_current_week() == 0
        logs = self.training_plan.load_logs()
        assert logs == {}
    
    def test_export_logs(self):
        """Test exporting training logs"""
        # Log some data
        self.training_plan.log_week(1, pace=6.0, distance=3.0, recovery=7)
        self.training_plan.log_week(2, pace=5.8, distance=4.0, recovery=8)
        
        # Export to a temporary file
        export_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        export_file.close()
        
        try:
            result = self.training_plan.export_logs(export_file.name)
            assert "exported" in result
            
            # Verify the exported file contains the data
            with open(export_file.name, 'r') as f:
                exported_data = json.load(f)
            
            assert "1" in exported_data
            assert "2" in exported_data
            assert exported_data["1"]["pace"] == 6.0
            assert exported_data["2"]["pace"] == 5.8
            
        finally:
            if os.path.exists(export_file.name):
                os.unlink(export_file.name)
    
    def test_base_plan_structure(self):
        """Test that the base plan has the correct structure"""
        base_plan = self.training_plan.base_plan
        
        # Should have 7 weeks
        assert len(base_plan) == 7
        
        # Each week should have workouts
        for week in range(1, 8):
            assert week in base_plan
            assert len(base_plan[week]) >= 4  # At least 4 workouts per week
            
        # Week 7 should include race day
        assert any("RACE DAY" in workout for workout in base_plan[7])
    
    def test_pace_improvement_detection(self):
        """Test detection of pace improvements"""
        # Log two weeks with improving pace
        self.training_plan.log_week(1, pace=7.0, recovery=6)
        self.training_plan.log_week(2, pace=6.5, recovery=7)  # Improved pace
        
        adjustments = self.training_plan.adjust_plan()
        
        # Should detect pace improvement
        assert 3 in adjustments
        assert "pace improvement" in adjustments[3].lower()
    
    def test_load_logs_error_handling(self):
        """Test error handling when loading corrupted logs"""
        # Write invalid JSON to the log file
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json content")
        
        # Should handle the error gracefully and return empty dict
        logs = self.training_plan.load_logs()
        assert logs == {}


class TestTrainingPlanIntegration:
    """Integration tests for the training plan"""
    
    def test_complete_week_cycle(self):
        """Test a complete week logging and adjustment cycle"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.close()
        
        try:
            training_plan = TrainingPlan(log_file=temp_file.name)
            
            # Week 1: Good performance
            training_plan.log_week(1, pace=7.0, distance=3.0, recovery=8, skipped=False)
            assert training_plan.get_current_week() == 1
            
            # Week 2: Improved pace
            training_plan.log_week(2, pace=6.5, distance=4.0, recovery=7, skipped=False)
            assert training_plan.get_current_week() == 2
            
            # Check adjustments
            adjustments = training_plan.adjust_plan()
            assert len(adjustments) >= 1
            
            # Check prediction
            prediction = training_plan.predict_5k()
            assert "32.5 minutes" in prediction  # 6.5 * 5 = 32.5
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
