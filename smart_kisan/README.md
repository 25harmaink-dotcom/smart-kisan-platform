# 🌾 Smart Kisan Platform

A multilingual (English + Hindi) web platform for Indian farmers to access government schemes, get smart irrigation recommendations, and manage complaints.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🔐 Default Credentials

### Admin Login
- **Username:** `admin`
- **Password:** `admin`

### Farmer Login
- Register as a new farmer using any 10-digit phone number

---

## 📁 Project Structure

```
smart_kisan/
├── app.py                 # Main entry point, routing
├── auth.py                # Login & registration
├── farmer_dashboard.py    # All farmer features
├── admin_dashboard.py     # All admin features
├── ai_logic.py            # Rule-based AI logic
├── database.py            # SQLite setup & CRUD
├── translations.py        # English + Hindi strings
├── requirements.txt
└── smart_kisan.db         # Auto-created SQLite database
```

---

## ✨ Features

### Farmer Features
- 🌐 Multilingual: English + Hindi
- 👤 Profile with crop, soil, water, and area details
- 💧 Smart Irrigation Planner (rule-based, crop + soil specific)
- 🔄 Crop Rotation Advisor
- 🏛️ Government Scheme Matching (state/crop/category aware)
- 📋 Complaint system with auto priority + department routing
- 📚 Tutorial mode for new users

### Admin Features
- 📊 Dashboard with charts and metrics
- 📋 Complaint management: filter, update status, reassign dept
- 🏛️ Scheme management: add, edit, delete
- 🗺️ Map views: complaint heatmap, water scarcity, scheme adoption
- 📜 Activity log for all admin actions

---

## 🌐 Deploying on Streamlit Cloud

1. Push this folder to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file path to `app.py`
5. Deploy!

> **Note:** For persistent data on Streamlit Cloud, consider using a hosted database (Supabase/PlanetScale free tier) instead of SQLite.

---

## 📦 Technology Stack
- **Frontend:** Streamlit with custom dark CSS
- **Database:** SQLite (local)
- **Maps:** Folium + streamlit-folium
- **Charts:** Plotly
- **Auth:** bcrypt password hashing
- **AI:** Rule-based logic (no API needed)
