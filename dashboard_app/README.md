# Training Plan Dashboard 🏃‍♂️

An interactive web dashboard for editing and visualizing your 7-week training plan progression.

## Features

### 📋 Interactive Training Plan Editor
- Edit run times, walk times, and set counts for any session
- Real-time validation and constraints
- Visual feedback for changes

### 📊 Live Progression Charts
- **Running Time Progression**: See how your run times increase over sessions
- **Distance Progression**: Track total and running distance improvements  
- **Weekly Volume**: Monitor total training volume per week
- **Session Details Table**: Color-coded overview of all sessions

### 💾 Save/Load Custom Plans
- Save your custom training plans with descriptive names
- Load previously saved plans
- Reset to default plan anytime

### 📈 Training Statistics
- Total running time and workout time
- Average session duration
- Total running distance
- Weekly breakdown by volume and sets

## Quick Start

### Option 1: Direct Launch
```bash
cd dashboard_app
python launch_dashboard.py
```

### Option 2: Manual Streamlit
```bash
cd dashboard_app
streamlit run training_dashboard.py
```

## Usage

1. **Launch the Dashboard**: Run one of the commands above
2. **Edit Sessions**: Use the table on the left to modify run/walk times and sets
3. **View Live Updates**: Charts on the right update automatically as you edit
4. **Save Your Plan**: Use the sidebar to save custom plans or load existing ones
5. **Analyze Progress**: Check the statistics and weekly breakdown at the bottom

## Dashboard Layout

```
┌─────────────────┬─────────────────────────────────┐
│  📋 Edit Table  │     📊 Live Charts              │
│                 │                                 │
│  Session data   │  • Running Time Progression     │
│  with real-time │  • Distance Progression         │
│  editing        │  • Weekly Volume Bar Chart      │
│                 │  • Session Details Table        │
└─────────────────┴─────────────────────────────────┘
│              📈 Training Statistics                │
│         📅 Weekly Breakdown Table                 │
└───────────────────────────────────────────────────┘
```

## Plan Management

### Saving Plans
1. Make your edits to the training sessions
2. Select "Save Current Plan" in the sidebar
3. Enter a descriptive name
4. Click "Save Plan"

### Loading Plans
1. Select "Load Saved Plan" in the sidebar
2. Choose from your saved plans
3. Click "Load Plan"

### Resetting
1. Select "Create New" in the sidebar
2. Click "Reset to Default" to restore original plan

## Data Files

- **Saved Plans**: Stored in `dashboard_app/saved_plans/` as JSON files
- **Format**: Each plan includes session data, creation date, and metadata

## Technical Details

- **Framework**: Streamlit for web interface
- **Charts**: Plotly for interactive visualizations
- **Data**: Pandas DataFrames for session management
- **Storage**: JSON files for plan persistence

## Customization Tips

### Editing Sessions
- **Run Time**: 0.0 to 60.0 minutes (0.5 min increments)
- **Walk Time**: 0.0 to 10.0 minutes (0.5 min increments) 
- **Sets**: 1 to 20 sets (integer values)
- **Continuous Runs**: Set walk time to 0 for continuous running sessions

### Understanding Charts
- **Week Boundaries**: Vertical dashed lines separate weeks
- **Color Coding**: Different colors for each week in session table
- **Distance Calculation**: Accounts for pace adjustments based on interval duration
- **Volume Tracking**: Shows progression and helps identify peak training weeks

## Troubleshooting

### Dashboard Won't Start
```bash
# Install required packages
pip install streamlit plotly pandas

# Check Python path
python -c "import streamlit; print('Streamlit installed successfully')"
```

### Charts Not Updating
- Refresh the browser page
- Check that all edits are within valid ranges
- Ensure no negative values in the session data

### Save/Load Issues
- Check that `dashboard_app/saved_plans/` directory exists
- Verify file permissions for writing JSON files
- Plan names should not contain special characters

## Advanced Features

### Custom Distance Calculations
The dashboard includes sophisticated distance calculations that account for:
- **Pace Adjustment**: Longer intervals use slower paces
- **Fatigue Modeling**: Speed decreases with interval duration
- **Walking Segments**: Separate calculation for recovery walks

### Real-time Validation
- **Automatic Recalculation**: Total times update when you edit individual values
- **Constraint Checking**: Prevents invalid combinations
- **Type Detection**: Automatically identifies interval vs. continuous sessions

Enjoy your interactive training plan dashboard! 🎉
