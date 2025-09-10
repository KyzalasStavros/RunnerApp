# 🏃‍♂️ Interactive Training Plan Dashboard

A comprehensive, interactive training plan dashboard built with Streamlit. Create, edit, and visualize your training progressions with real-time updates.

## Features

- ✅ **Interactive Table Editing**: Modify training sessions directly in the browser
- ✅ **Real-time Charts**: See progression updates as you edit
- ✅ **Plan Management**: Save, load, and update your training plans
- ✅ **Progress Analytics**: Weekly breakdowns and statistics
- ✅ **Distance Calculations**: Automatic running distance estimates

## Plan Management

### Save/Update Options:
- **Update Current Plan**: Save changes back to the loaded plan
- **Save as New Plan**: Create a copy with a different name
- **Load Existing Plans**: Browse and load previously saved plans

## 🚀 Deployment

### Option 1: Streamlit Cloud (Recommended)
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy from your forked repository
5. Set the main file as `streamlit_app.py`

### Option 2: Local Development
```bash
git clone <your-repo-url>
cd RunnerApp
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Usage

1. **Create/Edit Plans**: Use the interactive table to modify training sessions
2. **Save Plans**: Choose between updating existing plans or creating new ones
3. **Load Plans**: Browse and load previously saved training plans
4. **Analyze Progress**: View real-time charts and weekly statistics

## Technical Details

- **Frontend**: Streamlit with Plotly charts
- **Data Storage**: JSON files (simple, GitHub-friendly)
- **State Management**: Streamlit session state
- **Charts**: Interactive Plotly visualizations

## File Structure
```
RunnerApp/
├── streamlit_app.py          # Main entry point for deployment
├── dashboard_app/
│   └── training_dashboard.py # Main dashboard application
├── src/
│   └── training_plan.py      # Core training plan logic
└── saved_plans/              # JSON files for saved plans
```

---

**Ready to deploy**: This app is configured for easy deployment on Streamlit Cloud with zero additional setup required!
