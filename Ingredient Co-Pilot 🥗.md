# Ingredient Co-Pilot 🥗

Ingredient Co-Pilot is a complete Streamlit web application built for the **EnCode 2026 Hackathon**. It helps users analyze food ingredients, check for allergens, and compare products side-by-side using real-time data from the Open Food Facts API.

## Features 🚀

- **Chat Interface**: Interactive AI-powered chat to ask about ingredients and health risks.
- **Scan Label**: Fetch product details using barcodes via Open Food Facts API.
- **Side-by-Side Comparison**: Compare two products and export the analysis as a PDF.
- **Voice Input**: Integrated voice command support for hands-free queries.
- **Personalized Profile**: Store health goals and allergies to get tailored warnings.
- **Mobile Responsive**: Clean, modern UI designed for both desktop and mobile.
- **Fallback Database**: Includes a local CSV of 100+ common foods for offline use.

## Installation 🛠️

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ingredient-copilot.git
   cd ingredient-copilot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Tech Stack 💻

- **Frontend**: Streamlit
- **Data**: Open Food Facts API, Nutritionix (optional)
- **Visualization**: Plotly (Nutri-Score gauge)
- **Export**: FPDF (PDF generation)
- **Voice**: SpeechRecognition

## License 📄

MIT License. Built for EnCode 2026.
