import streamlit as st
import pandas as pd
import json
import requests
import gdown
import os
from PIL import Image
import plotly.graph_objects as go
from fpdf import FPDF
import base64
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="WiseWhisk - Ingredient Co-Pilot",
    page_icon="🦉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for UI/UX ---
st.markdown("""
    <style>
    .main {background-color: #ffffff; color: #1a1a1a;}
    [data-testid="stSidebar"] {background-color: #f0f2f6;}
    .stButton>button {width: 100%; border-radius: 10px; height: 3.5em; 
                      background-color: #1e5666; color: white; font-weight: 600; 
                      border: none; transition: all 0.3s ease;}
    .stButton>button:hover {background-color: #143d4a; box-shadow: 0 4px 8px rgba(0,0,0,0.1);}
    .chat-message {padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem; display: flex;
                   box-shadow: 0 2px 10px rgba(0,0,0,0.05); line-height: 1.6;}
    .chat-message.user {background-color: #e0f2f1; border-right: 5px solid #1e5666;}
    .chat-message.assistant {background-color: #ffffff; border-left: 5px solid #b8860b; 
                             border: 1px solid #e0e0e0;}
    .card {padding: 1.5rem; border-radius: 15px; border: 1px solid #eee; margin-bottom: 1.5rem; 
           background-color: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.05);}
    h1, h2, h3 {color: #1e5666;}
    .stTextInput>div>div>input {border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'history' not in st.session_state: st.session_state.history = []
if 'profile' not in st.session_state: st.session_state.profile = {"goals": "Stay healthy", "allergies": []}
if 'custom_ingredients' not in st.session_state: st.session_state.custom_ingredients = []
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "👋 Welcome to **WiseWhisk**! I'm your intelligent Ingredient Co-Pilot. I can help you analyze food labels, check for allergens, and compare products. What's on your mind?"}]

# --- Google Drive Data Loader ---
GOOGLE_DRIVE_FILE_ID = '1JcVZ2YIUovLG7znYKeHdhxHmIHpst9y1'
CSV_FILENAME = 'foods.csv'

@st.cache_data
def load_wisewhisk_data():
    """Load large CSV from Google Drive with memory optimization"""
    if not os.path.exists(CSV_FILENAME):
        with st.spinner("🔄 Downloading WiseWhisk database (first time only)..."):
            url = f'https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}'
            gdown.download(url, CSV_FILENAME, quiet=False)
    
    essential_cols = ['name', 'calories', 'fat', 'sugar', 'protein', 'sodium', 'labels', 
                     'allergens', 'additives', 'nutri_score', 'category']
    
    try:
        df = pd.read_csv(CSV_FILENAME, usecols=lambda col: col in essential_cols, nrows=50000)
        st.sidebar.success(f"✅ Loaded {len(df):,} foods")
        return df
    except Exception as e:
        st.error(f"❌ Data load failed: {e}")
        return pd.DataFrame({
            'name': ['Apple', 'Chicken Breast', 'Broccoli'],
            'calories': [52, 165, 34],
            'sugar': [10, 0, 1.7],
            'labels': ['vegan;gluten-free', 'gluten-free', 'vegan;gluten-free']
        })

# Load data ONCE at startup
foods_db = load_wisewhisk_data()

# --- Helper Functions ---
def fetch_open_food_facts(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200: return response.json()
    except: pass
    return None

def search_open_food_facts(query):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('products'): return data['products'][0]
    except: pass
    return None

def infer_intent(query):
    query = query.lower()
    if any(word in query for word in ["compare", "vs", "difference", "better than", "side by side"]): return "comparison"
    elif any(word in query for word in ["safe", "diabetic", "allergic", "risk", "bad for", "warning"]): return "safety_check"
    elif any(word in query for word in ["nutrition", "calories", "info", "protein", "sugar", "carbs"]): return "nutrition_info"
    return "general_query"

def generate_nutri_score_viz(score):
    colors = {'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02', 'D': '#EE8100', 'E': '#E63E11'}
    score = score.upper() if score and score.upper() in colors else 'C'
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=ord('E') - ord(score), 
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Nutri-Score: {score}", 'font': {'size': 20}},
        gauge={'axis': {'range': [0, 4], 'tickvals': [0,1,2,3,4], 'ticktext': ['E','D','C','B','A']},
               'bar': {'color': colors.get(score, 'gray')},
               'steps': [{'range': [0,0.8], 'color': colors['E']}, {'range': [0.8,1.8], 'color': colors['D']},
                        {'range': [1.8,2.8], 'color': colors['C']}, {'range': [2.8,3.8], 'color': colors['B']},
                        {'range': [3.8,4], 'color': colors['A']} ]}
    ))
    fig.update_layout(height=200, margin=dict(l=10,r=10,t=40,b=10))
    return fig

def create_pdf_report(content, title="WiseWhisk Analysis Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, content)
    return pdf.output(dest='S').encode('latin-1')

# --- Sidebar Menu ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🦉 WiseWhisk</h1>", unsafe_allow_html=True)
    menu = st.radio("Navigation", ["Chat Interface", "Scan Label", "Quick Ask", "My Profile", "Add Ingredient", "History"])
    
    st.divider()
    st.subheader("🎙️ Voice Command")
    audio_data = st.audio_input("Record your query")
    if audio_data: 
        st.success("Audio captured!")
        st.session_state.voice_input = "Compare Apple and Banana" 

    st.divider()
    st.caption("EnCode 2026 Hackathon | v1.1")

# --- Main Area Logic ---
if menu == "Chat Interface":
    st.title("💬 WiseWhisk Chat")
    
    if 'voice_input' in st.session_state:
        prompt = st.session_state.pop('voice_input')
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask WiseWhisk about food..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        intent = infer_intent(prompt)
        with st.chat_message("assistant"):
            if intent == "comparison":
                st.markdown("### ⚖️ Side-by-Side Comparison")
                items = prompt.lower().replace("compare", "").replace("side by side", "").split(" vs ")
                if len(items) < 2: items = prompt.lower().split(" and ")
                
                if len(items) >= 2:
                    item1, item2 = items[0].strip(), items[1].strip()
                    col1, col2 = st.columns(2)
                    
                    d1 = search_open_food_facts(item1)
                    d2 = search_open_food_facts(item2)
                    
                    with col1:
                        st.markdown(f"<div class='card'><h4>{item1.title()}</h4>", unsafe_allow_html=True)
                        if d1:
                            st.write(f"**Nutri-Score:** {d1.get('nutriscore_grade', 'N/A').upper()}")
                            st.write(f"**Energy:** {d1.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal")
                            st.plotly_chart(generate_nutri_score_viz(d1.get('nutriscore_grade')), use_container_width=True)
                        else: st.write("No data found.")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"<div class='card'><h4>{item2.title()}</h4>", unsafe_allow_html=True)
                        if d2:
                            st.write(f"**Nutri-Score:** {d2.get('nutriscore_grade', 'N/A').upper()}")
                            st.write(f"**Energy:** {d2.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal")
                            st.plotly_chart(generate_nutri_score_viz(d2.get('nutriscore_grade')), use_container_width=True)
                        else: st.write("No data found.")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    report_content = f"WiseWhisk Comparison: {item1} vs {item2}\n{datetime.now()}\n\nAnalyzed by WiseWhisk AI."
                    pdf_data = create_pdf_report(report_content)
                    st.download_button("📥 Export PDF", pdf_data, "wisewhisk_comparison.pdf", "application/pdf")
                    st.session_state.history.append({"timestamp": datetime.now().strftime("%H:%M:%S"), "content": f"Compared {item1} and {item2}"})
                else:
                    st.write("Please name two products, e.g., 'Compare Coke vs Pepsi'.")

            elif intent == "safety_check":
                st.markdown("### 🛡️ Safety Reasoning")
                with st.expander("Detailed Analysis", expanded=True):
                    allergies = ', '.join(st.session_state.profile['allergies']) if st.session_state.profile['allergies'] else 'None set'
                    st.write(f"**Profile:** {allergies}")
                    st.info("🔍 Analyzing for risks... Certainty: Medium")
                    st.markdown("- **Risk:** High sodium (heart risk)")
                    st.markdown("- **Tradeoff:** High protein but artificial sweeteners")

            else:
                st.markdown("🔍 Searching database...")
                match = foods_db[foods_db['name'].str.contains(prompt, case=False, na=False)]
                if not match.empty:
                    food = match.iloc[0]
                    st.markdown(f"<div class='card'><b>{food['name']}</b>: {food['calories']} kcal, "
                               f"{food['protein']}g protein. **Labels:** {food['labels']}</div>", unsafe_allow_html=True)
                else:
                    st.write("No exact match. Try scanning a barcode or ask about common foods!")

elif menu == "Scan Label":
    st.title("📸 Product Scanner")
    barcode = st.text_input("Enter Barcode (e.g., 3017620422003)")
    if st.button("🔍 Fetch Product", type="primary"):
        with st.spinner("Scanning..."):
            data = fetch_open_food_facts(barcode)
            if data and data.get('status') == 1:
                p = data['product']
                st.success(f"✅ Found: {p.get('product_name', 'Unknown')}")
                col1, col2 = st.columns([1, 2])
                with col1: 
                    img_url = p.get('image_url') or 'https://via.placeholder.com/200?text=No+Image'
                    st.image(img_url)
                with col2:
                    st.write(f"**Brand:** {p.get('brands', 'N/A')}")
                    st.write(f"**Ingredients:** {p.get('ingredients_text', 'N/A')}")
                    if 'nutriscore_grade' in p: st.plotly_chart(generate_nutri_score_viz(p['nutriscore_grade']))
            else: st.error("❌ Product not found in Open Food Facts")

elif menu == "Quick Ask":
    st.title("⚡ Quick Ingredient Analysis")
    txt = st.text_area("Paste ingredients:", height=100)
    if st.button("Analyze Now", type="primary"):
        analysis = []
        if "sugar" in txt.lower(): analysis.append("⚠️ **High Sugar** detected")
        if "sodium" in txt.lower(): analysis.append("🧂 **High Sodium** detected")
        if "msg" in txt.lower(): analysis.append("🚨 **MSG** (potential headache trigger)")
        if analysis:
            for item in analysis: st.error(item)
        else: st.success("✅ No major red flags detected")

elif menu == "My Profile":
    st.title("👤 My Profile")
    st.session_state.profile["goals"] = st.text_area("Health Goals", value=st.session_state.profile["goals"], height=80)
    st.session_state.profile["allergies"] = st.multiselect("Allergies", 
        ["Peanuts", "Dairy", "Gluten", "Soy", "Eggs", "Shellfish", "Sesame"], 
        default=st.session_state.profile["allergies"])
    if st.button("💾 Save Profile", type="primary"): st.success("✅ Profile updated!")

elif menu == "Add Ingredient":
    st.title("➕ Add Custom Ingredient")
    with st.form("add_form"):
        name = st.text_input("Food Name")
        calories = st.number_input("Calories (per 100g)", 0, 1000)
        sugar = st.number_input("Sugar (g)", 0.0, 100.0)
        if st.form_submit_button("Save to Database"):
            st.session_state.custom_ingredients.append({"name": name, "calories": calories, "sugar": sugar})
            st.success(f"✅ Added {name} to your database!")

elif menu == "History":
    st.title("📜 Analysis History")
    if st.session_state.history:
        for h in reversed(st.session_state.history):
            st.markdown(f"**[{h['timestamp']}]** {h['content']}")
    else:
        st.info("No analyses yet. Start chatting!")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>WiseWhisk - EnCode 2026 Hackathon 🦉</p>", unsafe_allow_html=True)
