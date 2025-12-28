# WiseWhisk 🦉🥗
**AI-Native Ingredient Co-Pilot**  
*Built for EnCode 2026 Hackathon at IIT Guwahati*  

> WiseWhisk reimagines how consumers understand food ingredients. Instead of menu-driven apps and data dumps, WiseWhisk acts as an intelligent co-pilot that **infers your intent**, **reasons through tradeoffs**, and **communicates uncertainty honestly**—all at the moment of decision.

---

## The Problem We Solve

Food labels are **regulatory documents, not human interfaces**. Consumers face:

- Long ingredient lists with chemical names like "sodium benzoate"
- Unfamiliar additives ("carrageenan", "MSG", "HFCS")  
- Conflicting health advice across sources
- **No context** about *why* something matters

**Traditional apps fail** because they:
- Require manual input/forms
- Surface raw data instead of insight
- Treat AI as an add-on, not the core interface

---

## AI-Native Experience

WiseWhisk delivers exactly what EnCode demands:

### **Intent-First Interaction** 
- **User:** "Is this safe for diabetics? Sugar, HFCS, wheat flour"
↓ No forms needed
- **WiseWhisk:** "🚨 HIGH RISK: 35g sugar/100g + HFCS spikes blood glucose rapidly.
Wheat adds carbs. Swap for stevia-sweetened alternative."


### **Reasoning-Driven Output**
Instead of "Sugar: 10g", WiseWhisk explains:

| **Why it matters** | **Tradeoffs** | **Uncertainty** |
|--------------------|---------------|-----------------|
| "HFCS metabolizes differently than table sugar, linked to insulin resistance" | "Palm oil extends shelf life but raises LDL cholesterol 7-10%" | "Limited studies on carrageenan; some evidence of gut inflammation" |

### **Zero Cognitive Load**
- 💬 **Chat interface** (text + voice)
- 📱 **Barcode scan** (Open Food Facts API)
- 👤 **Profile** remembers goals/allergies
- 📱 **Mobile-responsive**, no login required

---


---

## 📊 Technical Architecture


### **Data Sources**
| Source | Coverage | Use Case |
|--------|----------|----------|
| **Open Food Facts API** | 1M+ products | Primary (live lookup) |
| **`foods.csv`** | 100+ foods | Offline fallback |
| **`api_research.py`** | 10K+ foods | Data generation |

### **Key Libraries**
streamlit # UI
plotly # Nutri-Score gauge
requests # API calls
pandas # CSV processing
fpdf # PDF export
speechrecognition # Voice input

---

## 🎨 UI/UX Highlights

- **Dark theme**, mobile-responsive
- **Sidebar menu**: Scan → Profile → History → Add Custom Ingredient
- **Chat bubbles** with WiseWhisk owl avatar 🦉
- **Interactive cards**: Click to expand "Why this matters"
- **Voice input**: Click mic → "Check this soda label"

---

## 🔧 Quick Start
git clone https://github.com/khushi1508999/WiseWhisk.git
cd WiseWhisk
pip install -r requirements.txt
streamlit run app.py

**🌐 Live Demo**: [![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 📈 Data Pipeline (Reproducible)

Your `foods.csv` contains **100 high-quality foods**. To scale to 10K+: python api_research.py
Generates wisewhisk_foods_10k.csv from Open Food Facts

**Both work offline**—perfect for demo stability.

---

## 📱 Deployment Options

### **Streamlit Cloud** (Recommended, Free)
1. Connect GitHub repo
2. Set `app.py` as entrypoint  
3. Auto-deploys on every push

### **Local Development**
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

## 🤝 Acknowledgments

- **EnCode 2026** @ IIT Guwahati
- **Open Food Facts** (CC0 dataset)
- **Thesys** (hackathon partner)

## 📄 License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---
**Built by Khushi Kaul, MBA Business Analytics @ SIBM Bangalore**  
**EnCode 2026 — January 5, 2026**


