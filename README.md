# RunnerApp - Training Plan Analysis System

A comprehensive training plan management and analysis system with smart watch data integration.

## 📋 Project Overview

This system helps manage a progressive running training plan with real-world feedback through smart watch data analysis. It includes OCR-based data extraction from fitness apps, training plan analysis with fatigue modeling, and comprehensive visualization of progress trends.

## 🔧 Core Scripts

### 1. `main.py` - Training Plan Manager
Interactive training plan management with session viewing and plan generation.
```bash
python main.py
```

### 2. `extract_watch_data.py` - Smart Watch Data Extraction
OCR-based extraction of training data from Mi Fitness app screenshots.
```bash
python extract_watch_data.py --folder mi_data
```
- **Input**: Screenshots in `mi_data/` folder (format: `Session_W{week}_D{day}.JPG`)
- **Output**: Extracted data in `mi_data_extracted/` folder (JSON format)
- **Features**: Robust OCR pattern matching, handles format variations

### 3. `analyze_training_plan.py` - Progressive Overload Analysis
Theoretical analysis of training plan with fatigue modeling and progressive overload calculations.
```bash
python analyze_training_plan.py
```
- **Features**: Distance progression analysis, fatigue modeling, speed adjustments
- **Output**: Training plan statistics and fatigue-adjusted distances

### 4. `compare_actual_vs_planned.py` - Actual vs Planned Comparison
Compares extracted smart watch data with planned training sessions.
```bash
python compare_actual_vs_planned.py
```
- **Features**: Session-by-session comparison, HR zone analysis, progress trends
- **Output**: `training_progress_analysis.png` with 2x2 visualization (HR, pace, distance, duration)

### 5. `training_overview.py` - Complete Analysis Summary
Runs all analysis tools and provides comprehensive overview.
```bash
python training_overview.py
```
- **Features**: Tool status checking, automated analysis runs, next steps guidance

---

## Features

🏃‍♂️ **Interactive Training Plan**: View your personalized 7-week training schedule  
📝 **Performance Logging**: Track pace, distance, recovery, and notes  
🔄 **Adaptive Adjustments**: Get personalized recommendations based on your performance  
⏱️ **5K Time Prediction**: See projected race times based on your progress  
📊 **Progress Visualization**: Beautiful graphs showing your improvement  
📋 **Training History**: Complete log of all your training sessions  
⚙️ **Plan Management**: Reset or export your training data  

---

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/KyzalasStavros/RunnerApp.git
   cd RunnerApp
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the Interactive App
```bash
python main.py
```

### Command Line Help
```bash
python main.py --help
```

---

## How to Use the Application

### 1. **View Training Plan**
   - Check your current week's workouts
   - See the complete remaining training schedule
   - Each workout includes heart rate guidelines

### 2. **Log Weekly Performance**
   Use the interactive prompts to input:
   - **Pace**: average pace in minutes per kilometer
   - **Distance**: longest run distance that week (km)
   - **Recovery**: how you felt after workouts (1 = very tired, 10 = fully recovered)
   - **Skipped**: whether you missed major workouts
   - **Comments**: any notes you want to record

### 3. **Get Plan Adjustments**
   The app analyzes your performance and provides recommendations:
   - Missed workouts → reduce intensity next week
   - Low recovery (<4) → add extra rest or easier workouts
   - High recovery (>8) → consider slightly harder workouts
   - Pace improvements → motivational feedback

### 4. **Track Progress**
   - **5K Time Prediction**: estimates based on recent performance
   - **Progress Graphs**: visual charts showing pace, distance, recovery trends
   - **Training History**: complete log of all sessions

### 5. **Manage Your Plan**
   - **Reset**: start over with a clean slate
   - **Export**: backup your training data

---

## Training Plan Structure

### Week 1-2: Foundation Building
- Run/walk intervals to build base fitness (start with 12–16 sets, increase as able)
- Use run/walk intervals for all easy jog and long run sessions until you can jog continuously
- Introduction to bodyweight strength training
- Focus on consistency and form

### Week 3-4: Endurance Development
- Continue run/walk intervals, gradually increasing run time and reducing walk time
- Plyometric exercises for power development
- Building cardiovascular base

### Week 5-6: Speed Introduction
- Structured interval training at brisk pace
- Circuit training for strength
- Use run/walk intervals for longer runs if needed
- Peak training load

### Week 7: Race Preparation
- Tapering and final preparation
- Focus on mobility and recovery
- Use run/walk intervals for shakeout jogs if needed
- Race day strategy

---

## Terminology & Heart Rate Guidelines

### **Run/Walk Intervals**
- **Run**: faster, purposeful running (HR: 140–160 bpm)
- **Walk**: active recovery, comfortable pace (HR: 100–120 bpm)

### **Jog vs Run**
- **Jog/Easy pace**: conversational speed, RPE 3–4 (HR: 100–130 bpm)
- **Run/Brisk pace**: faster, effortful pace, RPE 6–8 (HR: 140–160 bpm)

### **Strides**
- Short bursts (15–20s) near sprint pace, RPE 7–9 (HR: 150–170 bpm)

### **Tempo Run**
- Steady, moderately hard pace, RPE 6–7 (HR: 140–160 bpm)

### **Long Run**
- Slower, endurance-focused run, RPE 3–5 (HR: 110–140 bpm)

### **Strength Training (Bodyweight)**
- Squats, lunges, planks, push-ups, burpees
- Focus on functional movement patterns
- 20-30 minutes, 2-3 times per week

### **Cross-Training Alternatives**
- Plyometrics: jump squats, box jumps, skipping rope
- Yoga/Mobility: improves flexibility and recovery
- Stair climbing: excellent cardio alternative
- Brisk walking: active recovery option

### **Training Schedule**
- **4 main running days**: Monday, Wednesday, Thursday, Friday
- **3 rest/strength days**: Tuesday, Saturday, Sunday
- Same total weekly volume as traditional 5-day plans
- Better recovery and injury prevention

---

## Development

This project uses:
- Python 3.9+
- Virtual environment for dependency management
- Matplotlib for data visualization
- NumPy for statistical calculations
- JSON for data persistence

### Project Structure
```
RunnerApp/
├── main.py              # Main application entry point
├── src/
│   ├── __init__.py      # Package initialization
│   └── training_plan.py # Core training plan logic
├── tests/
│   └── test_runner.py   # Test suite
├── requirements.txt     # Python dependencies
├── .env                 # Configuration file
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

### Running Tests
```bash
python -m pytest tests/ -v
```

---

## Tips for Success

**Run/walk intervals are recommended for all sessions until you can jog continuously.**
Increase the number of sets or running time as your fitness improves, but always listen to your body.

- **Consistency is key**: Better to run regularly at an easy pace than to skip runs
- **Listen to your body**: Adjust intensity and interval volume based on how you feel
- **Stay hydrated**: Drink water before, during, and after runs
- **Get adequate rest**: Recovery is when your body adapts and improves
- **Track your progress**: Use the app's logging features to stay motivated

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Submit a pull request

---

## License

This project is open source and available under the MIT License.

---

**Ready to crush that 5K? Let's get started! 🏃‍♂️💪**

*Remember: Every step counts, and every run brings you closer to your goal!*
