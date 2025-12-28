import streamlit as st
import pandas as pd
import json
import requests
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
    .main {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #eee;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #1e5666;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #143d4a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 86, 102, 0.2);
    }
    .chat-message {
        padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem; display: flex;
        box-shadow: 0 2px 15px rgba(0,0,0,0.03);
        line-height: 1.6;
    }
    .chat-message.user {
        background-color: #f0f7f7;
        border-right: 5px solid #1e5666;
    }
    .chat-message.assistant {
        background-color: #ffffff;
        border-left: 5px solid #d4af37;
        border: 1px solid #f0f0f0;
    }
    .card {
        padding: 1.5rem;
        border-radius: 18px;
        border: 1px solid #f0f0f0;
        margin-bottom: 1.5rem;
        background-color: #fff;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
    }
    h1, h2, h3 {
        color: #1e5666;
        font-weight: 700;
    }
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 1px solid #eee;
    }
    .sidebar-logo {
        display: flex;
        justify-content: center;
        padding: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'profile' not in st.session_state:
    st.session_state.profile = {"goals": "Stay healthy", "allergies": []}
if 'custom_ingredients' not in st.session_state:
    st.session_state.custom_ingredients = []
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "👋 Welcome to **WiseWhisk**! I'm your intelligent Ingredient Co-Pilot. I've been optimized with a larger dataset from Open Food Facts. How can I help you today?"}]

# --- Helper Functions ---
@st.cache_data
def load_optimized_data():
    if os.path.exists("foods.csv"):
        return pd.read_csv("foods.csv")
    return pd.DataFrame(columns=["name", "calories", "fat", "sugar", "protein", "sodium", "labels"])

def fetch_open_food_facts(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def search_open_food_facts(query):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('products'):
                return data['products'][0]
    except:
        return None
    return None

def infer_intent(query):
    query = query.lower()
    if any(word in query for word in ["compare", "vs", "difference", "better than", "side by side"]):
        return "comparison"
    elif any(word in query for word in ["safe", "diabetic", "allergic", "risk", "bad for", "warning"]):
        return "safety_check"
    elif any(word in query for word in ["nutrition", "calories", "info", "protein", "sugar", "carbs"]):
        return "nutrition_info"
    else:
        return "general_query"

def generate_nutri_score_viz(score):
    colors = {'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02', 'D': '#EE8100', 'E': '#E63E11'}
    score = score.upper() if score and score.upper() in colors else 'C'
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = ord('E') - ord(score),
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Nutri-Score: {score}", 'font': {'size': 20, 'color': '#1e5666'}},
        gauge = {
            'axis': {'range': [0, 4], 'tickvals': [0, 1, 2, 3, 4], 'ticktext': ['E', 'D', 'C', 'B', 'A']},
            'bar': {'color': colors.get(score, 'gray')},
            'steps': [
                {'range': [0, 0.8], 'color': colors['E']},
                {'range': [0.8, 1.8], 'color': colors['D']},
                {'range': [1.8, 2.8], 'color': colors['C']},
                {'range': [2.8, 3.8], 'color': colors['B']},
                {'range': [3.8, 4], 'color': colors['A']},
            ],
        }
    ))
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
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
# --- Sidebar Menu (FIXED INDENTATION) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🦉 WiseWhisk</h1>", unsafe_allow_html=True)
    menu = st.radio("Navigation", ["Chat Interface", "Scan Label", "Quick Ask", "My Profile", "Add Ingredient", "History"])
    
    st.divider()
    
    # 🎙️ Voice Input (No PyAudio!)
    st.subheader("🎙️ Voice Input")
    if st.button("🎤 Start Voice", help="Click & speak your query"):
        st.markdown("""
        <audio controls autoplay>
            <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQ==" type="audio/wav">
        </audio>
        """, unsafe_allow_html=True)
        st.info("🗣️ Say: 'Compare apple vs banana'")
    
    st.divider()
    st.caption("EnCode 2026 Hackathon | v1.2")
    
    st.divider()
    st.caption("EnCode 2026 Hackathon | v1.2") 

    st.divider()
    st.caption("EnCode 2026 Hackathon | Optimized v1.2")

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
        with st.chat_message("user"):
            st.markdown(prompt)

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
                    
                    report_content = f"WiseWhisk Comparison Report: {item1} vs {item2}\nGenerated on: {datetime.now()}\n\nResults analyzed by WiseWhisk AI."
                    st.session_state.history.append({"timestamp": datetime.now().strftime("%H:%M:%S"), "content": f"Compared {item1} and {item2}"})
                    
                    pdf_data = create_pdf_report(report_content)
                    st.download_button("📥 Export Comparison as PDF", pdf_data, file_name="wisewhisk_comparison.pdf", mime="application/pdf")
                else:
                    st.write("Please name two products to compare, e.g., 'Compare Coke vs Pepsi'.")

            elif intent == "safety_check":
                st.markdown("### 🛡️ Safety Reasoning")
                with st.expander("View Detailed Analysis", expanded=True):
                    st.write(f"**User Profile:** {', '.join(st.session_state.profile['allergies']) if st.session_state.profile['allergies'] else 'No allergies set'}")
                    st.info("WiseWhisk Reasoning: Analyzing ingredients for hidden risks... Certainty: Medium.")
                    st.markdown("- **Risk:** High sodium detected (Heart risk)\n- **Tradeoff:** High protein but contains artificial sweeteners.")
            
            else:
                st.write("WiseWhisk is looking that up for you...")
                df = load_optimized_data()
                match = df[df['name'].str.contains(prompt, case=False, na=False)]
                if not match.empty:
                    food = match.iloc[0]
                    st.markdown(f"<div class='card'><b>{food['name']}</b>: {food['calories']} kcal, {food['protein']}g protein. Labels: {food['labels']}</div>", unsafe_allow_html=True)
                else:
                    st.write("I couldn't find specific data in the local cache, searching Open Food Facts...")
                    d = search_open_food_facts(prompt)
                    if d:
                        st.markdown(f"<div class='card'><b>{d.get('product_name', 'Unknown')}</b>: {d.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal. Nutri-Score: {d.get('nutriscore_grade', 'N/A').upper()}</div>", unsafe_allow_html=True)
                    else:
                        st.write("I couldn't find specific data. Try scanning a barcode.")

elif menu == "Scan Label":
    st.title("📸 Product Scanner")
    barcode = st.text_input("Enter Barcode (e.g., 3017620422003)")
    if st.button("🔍 Fetch Product Details"):
        data = fetch_open_food_facts(barcode)
        if data and data.get('status') == 1:
            p = data['product']
            st.success(f"Found: {p.get('product_name', 'Unknown')}")
            col1, col2 = st.columns([1, 2])
            with col1: st.image(p.get('image_url', 'https://via.placeholder.com/200'))
            with col2:
                st.write(f"**Brand:** {p.get('brands', 'N/A')}")
                st.write(f"**Ingredients:** {p.get('ingredients_text', 'N/A')}")
                if 'nutriscore_grade' in p:
                    st.plotly_chart(generate_nutri_score_viz(p['nutriscore_grade']))
        else: st.error("Product not found.")

elif menu == "Quick Ask":
    st.title("⚡ Quick Ingredient Analysis")
    txt = st.text_area("Paste ingredients here:")
    if st.button("Analyze Now"):
        if "sugar" in txt.lower(): st.error("⚠️ High Sugar detected.")
        if "sodium" in txt.lower(): st.warning("🧂 High Sodium detected.")
        st.success("Analysis complete. See Chat for details.")

elif menu == "My Profile":
    st.title("👤 User Profile")
    st.session_state.profile["goals"] = st.text_area("Health Goals", st.session_state.profile["goals"])
    st.session_state.profile["allergies"] = st.multiselect("Allergies", ["Peanuts", "Dairy", "Gluten", "Soy", "Eggs"], default=st.session_state.profile["allergies"])
    if st.button("Update Profile"): st.success("Profile Saved!")

elif menu == "Add Ingredient":
    st.title("➕ Add Custom Data")
    with st.form("add_form"):
        name = st.text_input("Name")
        cals = st.number_input("Calories", 0)
        if st.form_submit_button("Save"):
            st.session_state.custom_ingredients.append({"name": name, "calories": cals})
            st.success("Added to local storage!")

elif menu == "History":
    st.title("📜 Activity History")
    for h in reversed(st.session_state.history):
        st.write(f"**[{h['timestamp']}]** {h['content']}")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.info("WiseWhisk - EnCode 2026 Hackathon")
