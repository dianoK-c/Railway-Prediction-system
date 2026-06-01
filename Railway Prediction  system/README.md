# 🚆 RailTrack AI — Railway Tracking & Arrival Time Prediction System

An interactive, ML-powered ETA prediction dashboard built with **Python + Streamlit + scikit-learn**.

---

## 📁 Project Structure

```
railway_tracker/
├── app.py                  ← Main Streamlit dashboard (entry point)
├── requirements.txt        ← Python dependencies
├── README.md
│
├── utils/
│   ├── distance.py         ← Haversine / geodesic distance calculation
│   ├── eta.py              ← Physics-based ETA + arrival time computation
│   └── simulation.py       ← Real-time journey simulation engine
│
├── models/
│   └── ml_model.py         ← LinearRegression training, prediction, persistence
│
└── data/
    ├── stations.py         ← 20+ pre-loaded station registry (Indian + international)
    ├── eta_model.pkl       ← (auto-generated) trained model
    ├── scaler.pkl          ← (auto-generated) StandardScaler
    └── history.csv         ← (auto-generated) journey log for retraining
```

---

## ⚙️ Installation

### 1. Clone / download the project
```bash
cd railway_tracker
```

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

For the interactive Folium map (optional):
```bash
pip install folium streamlit-folium
```

---

## 🚀 Running the App

```bash
streamlit run app.py
```

The app opens in your browser at **http://localhost:8501**

---

## 🎯 Features

| Feature | Description |
|---|---|
| **ETA Prediction** | Physics-based + ML-enhanced ETA, displayed side by side |
| **Speed Sensitivity Chart** | See how ETA changes across a speed range |
| **Live Simulation** | Animated tick-by-tick journey from origin to destination |
| **Interactive Map** | Folium dark-mode map with all stations plotted |
| **History & Logging** | Log completed journeys, view distribution charts |
| **ML Info** | Model metrics, feature coefficient bar chart, retrain button |

---

## 🧠 ML Model

- **Algorithm:** Linear Regression (scikit-learn)  
- **Features:** `distance_km`, `speed_kmh`, `delay_minutes`  
- **Target:** `actual_eta_minutes`  
- **Pre-processing:** StandardScaler  
- **Training data:** 2,000 synthetic records + any real logged journeys  
- **Typical MAE:** ~30 min (improves with real data via the History tab)

---

## 📦 Dependencies

```
streamlit>=1.32
numpy>=1.24
pandas>=2.0
scikit-learn>=1.3
geopy>=2.4
plotly>=5.18
folium>=0.15          (optional, for interactive map)
streamlit-folium>=0.18 (optional, for interactive map)
```

---

## 🗺 Supported Stations (pre-loaded)

Mumbai CST, Pune, Nashik, Surat, Vadodara, Ahmedabad, New Delhi, Agra, Mathura, Jaipur,
Chennai Central, Bangalore City, Hyderabad, Kolkata Howrah, Bhubaneswar, Visakhapatnam,
London Paddington, Paris Gare du Nord, Tokyo Station, New York Penn Station.

---

## 💡 Usage Tips

1. Select a **Train Preset** from the sidebar or enter a custom train ID.
2. Adjust **current lat/lon** to simulate the train being mid-journey.
3. Change **speed** to see the ETA update instantly.
4. Switch to the **Live Simulation** tab and click **Start Simulation** for an animated run.
5. After arrival, log the actual time in the **History** tab to improve the model.
6. Click **Retrain Model Now** in the ML Info tab to incorporate new data.

---

*Built with ❤️ using Python, Streamlit, and scikit-learn.*
