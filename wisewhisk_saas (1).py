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
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="WiseWhisk - Intelligent Ingredient Co-Pilot",
    page_icon="🦉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Advanced Custom CSS with Glassmorphism ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #e8eef0 100%);
        color: #1a1a1a;
    }
    
    /* Glassmorphic Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(248, 249, 250, 0.85);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(30, 86, 102, 0.1);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    /* Sticky Logo Header */
    .sidebar-logo {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1.5rem 1rem;
        margin: -1rem -1rem 1.5rem -1rem;
        border-bottom: 2px solid rgba(212, 175, 55, 0.3);
        text-align: center;
    }
    
    .sidebar-logo h1 {
        color: #1e5666;
        font-weight: 800;
        font-size: 1.8rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Premium Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 16px;
        height: 3.8em;
        background: linear-gradient(135deg, #1e5666 0%, #143d4a 100%);
        color: white;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(30, 86, 102, 0.25);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #d4af37 0%, #b8941f 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4);
    }
    
    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
    }
    
    /* Metric Tiles for Dashboard */
    .metric-tile {
        background: linear-gradient(135deg, rgba(30, 86, 102, 0.95) 0%, rgba(20, 61, 74, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.8rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 24px rgba(30, 86, 102, 0.2);
        color: white;
        transition: all 0.3s ease;
    }
    
    .metric-tile:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 36px rgba(212, 175, 55, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #d4af37;
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
        font-weight: 600;
    }
    
    /* Alert Banner with Pulse Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.85; transform: scale(1.02); }
    }
    
    .alert-banner {
        background: linear-gradient(135deg, #ff4757 0%, #e63e11 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        font-weight: 700;
        font-size: 1.1rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(255, 71, 87, 0.4);
        animation: pulse 2s ease-in-out infinite;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .alert-icon {
        font-size: 2rem;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Versus Comparison Layout */
    .vs-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .vs-badge {
        background: linear-gradient(135deg, #d4af37 0%, #b8941f 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 800;
        font-size: 1.5rem;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4);
        letter-spacing: 2px;
    }
    
    .winner-badge {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        display: inline-block;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
    }
    
    .loser-badge {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        display: inline-block;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1.8rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        line-height: 1.7;
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, rgba(30, 86, 102, 0.1) 0%, rgba(30, 86, 102, 0.05) 100%);
        border-left: 5px solid #1e5666;
    }
    
    .chat-message.assistant {
        background: rgba(255, 255, 255, 0.9);
        border-left: 5px solid #d4af37;
    }
    
    /* Section Headers */
    h1, h2, h3 {
        color: #1e5666;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stTextArea textarea {
        border-radius: 16px;
        border: 2px solid rgba(30, 86, 102, 0.15);
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea textarea:focus {
        border-color: #d4af37;
        box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
    }
    
    /* Download Buttons */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #d4af37 0%, #b8941f 100%);
        color: white;
        border-radius: 16px;
        padding: 0.8rem 2rem;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4);
    }
    
    /* Responsive Tables */
    .dataframe {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .metric-tile {
            padding: 1.2rem;
        }
        .metric-value {
            font-size: 2rem;
        }
        h1 {
            font-size: 1.8rem;
        }
        .glass-card {
            padding: 1.5rem;
        }
    }
    
    /* Icon Buttons */
    .icon-button {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
    }
    
    /* Sidebar Navigation */
    [data-testid="stSidebar"] .stRadio > label {
        background: rgba(255, 255, 255, 0.6);
        padding: 0.8rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(30, 86, 102, 0.1);
    }
    
    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(212, 175, 55, 0.2);
        transform: translateX(5px);
    }
    
    /* Divider Styling */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(30, 86, 102, 0.3), transparent);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'profile' not in st.session_state:
    st.session_state.profile = {"goals": "Stay healthy and active", "allergies": [], "dietary_preferences": []}
if 'custom_ingredients' not in st.session_state:
    st.session_state.custom_ingredients = []
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Welcome to **WiseWhisk** - Your Intelligent Ingredient Co-Pilot! I'm powered by a comprehensive food database and ready to help you make smarter, healthier food choices. How can I assist you today?"}
    ]
if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = 0
if 'comparisons_made' not in st.session_state:
    st.session_state.comparisons_made = 0

# --- Helper Functions ---
@st.cache_data
def load_optimized_data():
    """Load local food database"""
    if os.path.exists("foods.csv"):
        return pd.read_csv("foods.csv")
    return pd.DataFrame(columns=["name", "calories", "fat", "sugar", "protein", "sodium", "labels"])

def fetch_open_food_facts(barcode):
    """Fetch product data by barcode"""
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def search_open_food_facts(query):
    """Search for products by name"""
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

def parse_ingredient_list(raw_text):
    """Parse raw ingredient list into structured data"""
    # Remove common prefixes
    text = re.sub(r'^(ingredients?:?|contains:?)', '', raw_text.lower(), flags=re.IGNORECASE).strip()
    
    # Split by common delimiters
    ingredients = re.split(r'[,;]|\sand\s', text)
    
    # Clean and filter
    parsed = []
    for ing in ingredients:
        cleaned = ing.strip()
        if cleaned and len(cleaned) > 2:
            parsed.append(cleaned.title())
    
    return parsed

def check_allergens(ingredients, user_allergies):
    """Check if any allergens are present"""
    if not user_allergies:
        return []
    
    allergen_keywords = {
        "Peanuts": ["peanut", "groundnut"],
        "Dairy": ["milk", "cheese", "butter", "cream", "whey", "casein", "lactose"],
        "Gluten": ["wheat", "barley", "rye", "gluten"],
        "Soy": ["soy", "soybean", "tofu"],
        "Eggs": ["egg", "albumin"]
    }
    
    detected = []
    for allergen in user_allergies:
        keywords = allergen_keywords.get(allergen, [allergen.lower()])
        for keyword in keywords:
            if any(keyword in str(ing).lower() for ing in ingredients):
                detected.append(allergen)
                break
    
    return list(set(detected))

def infer_intent(query):
    """Infer user intent from query"""
    query = query.lower()
    if any(word in query for word in ["compare", "vs", "versus", "difference", "better than", "side by side"]):
        return "comparison"
    elif any(word in query for word in ["safe", "diabetic", "allergic", "risk", "bad for", "warning", "danger"]):
        return "safety_check"
    elif any(word in query for word in ["nutrition", "calories", "info", "protein", "sugar", "carbs", "nutrients"]):
        return "nutrition_info"
    else:
        return "general_query"

def generate_enhanced_nutri_score_viz(score, product_data=None):
    """Enhanced Nutri-Score visualization with breakdown"""
    colors = {'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02', 'D': '#EE8100', 'E': '#E63E11'}
    score = score.upper() if score and score.upper() in colors else 'C'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ord('E') - ord(score),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Nutri-Score: {score}", 'font': {'size': 24, 'color': '#1e5666', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [0, 4], 'tickvals': [0, 1, 2, 3, 4], 'ticktext': ['E', 'D', 'C', 'B', 'A']},
            'bar': {'color': colors.get(score, 'gray'), 'thickness': 0.8},
            'steps': [
                {'range': [0, 0.8], 'color': 'rgba(230, 62, 17, 0.3)'},
                {'range': [0.8, 1.8], 'color': 'rgba(238, 129, 0, 0.3)'},
                {'range': [1.8, 2.8], 'color': 'rgba(254, 203, 2, 0.3)'},
                {'range': [2.8, 3.8], 'color': 'rgba(133, 187, 47, 0.3)'},
                {'range': [3.8, 4], 'color': 'rgba(3, 129, 65, 0.3)'},
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': ord('E') - ord(score)
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'}
    )
    
    return fig

def create_pdf_report(content, title="WiseWhisk Analysis Report"):
    """Streamlit Cloud FPDF2 compatible"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, content)
        return pdf.output(dest='S')  # ✅ FPDF2 returns bytes directly
    except:
        return b"PDF export unavailable"  # Fallback

def calculate_health_score(nutriments):
    """Calculate a simple health score based on nutrients"""
    score = 50  # Base score
    
    # Positive factors
    if nutriments.get('proteins_100g', 0) > 10:
        score += 15
    if nutriments.get('fiber_100g', 0) > 3:
        score += 10
    
    # Negative factors
    if nutriments.get('sugars_100g', 0) > 15:
        score -= 15
    if nutriments.get('saturated-fat_100g', 0) > 5:
        score -= 10
    if nutriments.get('sodium_100g', 0) > 0.5:
        score -= 10
    
    return max(0, min(100, score))

# --- Sidebar Menu ---
with st.sidebar:
    # Sticky Logo Header
    st.markdown("""
        <div class="sidebar-logo">
            <h1>🦉 WiseWhisk</h1>
            <p style="color: #d4af37; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;">Intelligent Ingredient Co-Pilot</p>
        </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio(
        "📍 Navigation",
        ["🏠 Command Center", "💬 Chat Interface", "🔍 Scan Label", "⚡ Quick Ask", "👤 My Profile", "➕ Add Ingredient", "📜 History"],
        index=0
    )
    
    st.divider()
    
    # Voice Command Section
    st.markdown("### 🎙️ Voice Command")
    audio_data = st.audio_input("🎤 Record your query")
    if audio_data:
        st.success("✅ Audio captured! Processing...")
        st.session_state.voice_input = "Compare apple and banana"
    
    st.divider()
    
    # Quick Stats
    st.markdown(f"""
        <div style="background: rgba(30, 86, 102, 0.1); padding: 1rem; border-radius: 12px; margin-top: 1rem;">
            <p style="margin: 0; font-size: 0.85rem; color: #1e5666;">
                <strong>📊 Session Stats</strong><br>
                Analyses: {st.session_state.analysis_count}<br>
                Comparisons: {st.session_state.comparisons_made}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.caption("🏆 EnCode 2026 Hackathon | WiseWhisk v2.0")

# --- Main Area Logic ---

# Command Center Dashboard
if menu == "🏠 Command Center":
    st.markdown("<h1>🏠 Command Center</h1>", unsafe_allow_html=True)
    
    # Welcome Message
    st.markdown("""
        <div class="glass-card">
            <h3 style="margin-top: 0;">Welcome back to WiseWhisk!</h3>
            <p style="font-size: 1.1rem; color: #555; line-height: 1.7;">
                Your intelligent co-pilot for making smarter food choices. Start by exploring your health profile, 
                analyzing ingredients, or comparing products side-by-side.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Metric Tiles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{st.session_state.analysis_count}</div>
                <div class="metric-label">Analyses</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{st.session_state.comparisons_made}</div>
                <div class="metric-label">Comparisons</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{len(st.session_state.profile['allergies'])}</div>
                <div class="metric-label">Allergies Set</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{len(st.session_state.custom_ingredients)}</div>
                <div class="metric-label">Custom Items</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Health Profile Summary
    st.markdown("<h2>📋 Your Health Profile</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: #1e5666; margin-top: 0;">🎯 Health Goals</h4>
                <p style="font-size: 1.05rem; line-height: 1.7;">{st.session_state.profile['goals']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        allergies_display = ", ".join(st.session_state.profile['allergies']) if st.session_state.profile['allergies'] else "None set"
        st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: #1e5666; margin-top: 0;">🚫 Allergies & Restrictions</h4>
                <p style="font-size: 1.05rem; line-height: 1.7;">{allergies_display}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Recent History
    st.markdown("<h2>📊 Recent Activity</h2>", unsafe_allow_html=True)
    
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history[-5:])
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        for idx, item in enumerate(reversed(st.session_state.history[-5:])):
            st.markdown(f"""
                <div style="padding: 0.8rem; background: rgba(30, 86, 102, 0.05); border-radius: 12px; margin-bottom: 0.8rem;">
                    <strong style="color: #1e5666;">[{item['timestamp']}]</strong> {item['content']}
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="glass-card">
                <p style="text-align: center; color: #999; font-style: italic;">No recent activity. Start analyzing ingredients!</p>
            </div>
        """, unsafe_allow_html=True)

# Chat Interface
elif menu == "💬 Chat Interface":
    st.markdown("<h1>💬 Intelligent Chat</h1>", unsafe_allow_html=True)
    
    # Check for allergen warnings
    if st.session_state.profile['allergies']:
        st.markdown(f"""
            <div style="background: rgba(212, 175, 55, 0.1); padding: 1rem; border-radius: 12px; border-left: 4px solid #d4af37; margin-bottom: 1.5rem;">
                <strong>🛡️ Active Protection:</strong> Monitoring for {', '.join(st.session_state.profile['allergies'])}
            </div>
        """, unsafe_allow_html=True)
    
    # Handle voice input
    if 'voice_input' in st.session_state:
        prompt = st.session_state.pop('voice_input')
        st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("💭 Ask WiseWhisk about ingredients, nutrition, or product comparisons..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        intent = infer_intent(prompt)
        st.session_state.analysis_count += 1
        
        with st.chat_message("assistant"):
            if intent == "comparison":
                st.markdown("### ⚖️ Enhanced Product Comparison")
                
                # Parse items to compare
                items = prompt.lower().replace("compare", "").replace("versus", "vs").replace("side by side", "").split(" vs ")
                if len(items) < 2:
                    items = prompt.lower().split(" and ")
                
                if len(items) >= 2:
                    item1, item2 = items[0].strip(), items[1].strip()
                    
                    # Define colors dictionary at the beginning
                    colors = {'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02', 'D': '#EE8100', 'E': '#E63E11'}
                    
                    # Fetch data
                    with st.spinner("🔍 Fetching product data..."):
                        d1 = search_open_food_facts(item1)
                        d2 = search_open_food_facts(item2)
                    
                    if d1 and d2:
                        st.session_state.comparisons_made += 1
                        
                        # Calculate health scores
                        score1 = calculate_health_score(d1.get('nutriments', {}))
                        score2 = calculate_health_score(d2.get('nutriments', {}))
                        
                        # VS Badge
                        st.markdown('<div class="vs-container"><div class="vs-badge">VS</div></div>', unsafe_allow_html=True)
                        
                        # Side-by-side comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            winner1 = score1 > score2
                            badge1 = "winner-badge" if winner1 else "loser-badge"
                            badge_text1 = "🏆 Healthier Choice" if winner1 else "⚠️ Less Healthy"
                            
                            st.markdown(f"""
                                <div class="glass-card" style="border: 3px solid {'#2ecc71' if winner1 else '#e74c3c'};">
                                    <h3 style="margin-top: 0; color: #1e5666;">{d1.get('product_name', item1).title()}</h3>
                                    <div class="{badge1}">{badge_text1}</div>
                                    <hr style="margin: 1rem 0;">
                                    <p><strong>Brand:</strong> {d1.get('brands', 'N/A')}</p>
                                    <p><strong>Nutri-Score:</strong> <span style="font-size: 1.5rem; font-weight: 800; color: {colors.get(d1.get('nutriscore_grade', 'C').upper(), 'gray')}">{d1.get('nutriscore_grade', 'N/A').upper()}</span></p>
                                    <p><strong>Energy:</strong> {d1.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g</p>
                                    <p><strong>Protein:</strong> {d1.get('nutriments', {}).get('proteins_100g', 'N/A')}g</p>
                                    <p><strong>Sugar:</strong> {d1.get('nutriments', {}).get('sugars_100g', 'N/A')}g</p>
                                    <p><strong>Fiber:</strong> {d1.get('nutriments', {}).get('fiber_100g', 'N/A')}g</p>
                                    <p><strong>Health Score:</strong> <span style="font-size: 1.3rem; font-weight: 700; color: #d4af37;">{score1}/100</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.plotly_chart(generate_enhanced_nutri_score_viz(d1.get('nutriscore_grade')), use_container_width=True)
                        
                        with col2:
                            winner2 = score2 > score1
                            badge2 = "winner-badge" if winner2 else "loser-badge"
                            badge_text2 = "🏆 Healthier Choice" if winner2 else "⚠️ Less Healthy"
                            
                            st.markdown(f"""
                                <div class="glass-card" style="border: 3px solid {'#2ecc71' if winner2 else '#e74c3c'};">
                                    <h3 style="margin-top: 0; color: #1e5666;">{d2.get('product_name', item2).title()}</h3>
                                    <div class="{badge2}">{badge_text2}</div>
                                    <hr style="margin: 1rem 0;">
                                    <p><strong>Brand:</strong> {d2.get('brands', 'N/A')}</p>
                                    <p><strong>Nutri-Score:</strong> <span style="font-size: 1.5rem; font-weight: 800; color: {colors.get(d2.get('nutriscore_grade', 'C').upper(), 'gray')}">{d2.get('nutriscore_grade', 'N/A').upper()}</span></p>
                                    <p><strong>Energy:</strong> {d2.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g</p>
                                    <p><strong>Protein:</strong> {d2.get('nutriments', {}).get('proteins_100g', 'N/A')}g</p>
                                    <p><strong>Sugar:</strong> {d2.get('nutriments', {}).get('sugars_100g', 'N/A')}g</p>
                                    <p><strong>Fiber:</strong> {d2.get('nutriments', {}).get('fiber_100g', 'N/A')}g</p>
                                    <p><strong>Health Score:</strong> <span style="font-size: 1.3rem; font-weight: 700; color: #d4af37;">{score2}/100</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.plotly_chart(generate_enhanced_nutri_score_viz(d2.get('nutriscore_grade')), use_container_width=True)
                        
                        # Detailed Analysis
                        st.markdown("### 🔬 Detailed Breakdown")
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        
                        analysis = f"""
                        **Why {d1.get('product_name', item1) if winner1 else d2.get('product_name', item2)} is healthier:**
                        
                        - **Protein Content:** {'Higher' if d1.get('nutriments', {}).get('proteins_100g', 0) > d2.get('nutriments', {}).get('proteins_100g', 0) else 'Lower'} protein supports muscle health
                        - **Sugar Levels:** {'Lower' if d1.get('nutriments', {}).get('sugars_100g', 999) < d2.get('nutriments', {}).get('sugars_100g', 999) else 'Higher'} sugar content reduces diabetes risk
                        - **Fiber:** {'Better' if d1.get('nutriments', {}).get('fiber_100g', 0) > d2.get('nutriments', {}).get('fiber_100g', 0) else 'Lower'} fiber aids digestion
                        - **Overall Nutrition:** Based on comprehensive analysis of all nutrients
                        """
                        
                        st.markdown(analysis)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Export Report
                        report_content = f"""WiseWhisk Comparison Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Product 1: {d1.get('product_name', item1)}
Health Score: {score1}/100
Nutri-Score: {d1.get('nutriscore_grade', 'N/A').upper()}

Product 2: {d2.get('product_name', item2)}
Health Score: {score2}/100
Nutri-Score: {d2.get('nutriscore_grade', 'N/A').upper()}

Winner: {d1.get('product_name', item1) if winner1 else d2.get('product_name', item2)}

Analysis: {analysis}
"""
                        
                        st.session_state.history.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "content": f"Compared {item1} vs {item2}"
                        })
                        # ✅ TEXT DOWNLOAD (Works 100% on Streamlit Cloud)
report_text = f"""WiseWhisk Comparison Report 🦉
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PRODUCT 1: {item1.title()}
PRODUCT 2: {item2.title()}

[Full comparison charts above ↑]

🔍 Analyzed by WiseWhisk AI Co-Pilot
⚡ EnCode 2026 Hackathon Entry"""

st.download_button(
    label="📥 Export Report",
    data=report_text,
    file_name=f"wisewhisk_{item1}_{item2}_{datetime.now().strftime('%Y%m%d')}.txt",
    mime="text/plain"
)

                else:
                        st.warning("⚠️ Couldn't fetch data for one or both products. Please try different product names.")
                else:
                    st.info("💡 Please specify two products to compare (e.g., 'Compare Coke vs Pepsi')")
            
            elif intent == "safety_check":
                st.markdown("### 🛡️ Safety Analysis")
                
                # Search for the product
                search_term = prompt.lower().replace("is", "").replace("safe", "").replace("for", "").strip()
                data = search_open_food_facts(search_term)
                
                if data:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown(f"**Analyzing:** {data.get('product_name', 'Unknown Product')}")
                    
                    # Get ingredients
                    ingredients_text = data.get('ingredients_text', '')
                    ingredients_list = data.get('ingredients', [])
                    
                    # Check for allergens
                    if st.session_state.profile['allergies']:
                        allergens_found = check_allergens(
                            [ingredients_text] + [i.get('text', '') for i in ingredients_list],
                            st.session_state.profile['allergies']
                        )
                        
                        if allergens_found:
                            st.markdown(f"""
                                <div class="alert-banner">
                                    <span class="alert-icon">⚠️</span>
                                    <div>
                                        <strong>ALLERGEN ALERT!</strong><br>
                                        Contains: {', '.join(allergens_found)}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.success("✅ No allergens detected based on your profile")
                    
                    # Health Analysis
                    st.markdown("#### 🔍 Risk Assessment")
                    
                    nutriments = data.get('nutriments', {})
                    risks = []
                    benefits = []
                    
                    # Analyze risks
                    if nutriments.get('sugars_100g', 0) > 15:
                        risks.append("⚠️ **High Sugar:** May increase diabetes risk and cause energy crashes")
                    if nutriments.get('sodium_100g', 0) > 0.6:
                        risks.append("⚠️ **High Sodium:** Can contribute to high blood pressure")
                    if nutriments.get('saturated-fat_100g', 0) > 5:
                        risks.append("⚠️ **High Saturated Fat:** May impact cardiovascular health")
                    
                    # Analyze benefits
                    if nutriments.get('proteins_100g', 0) > 10:
                        benefits.append("✅ **High Protein:** Supports muscle growth and satiety")
                    if nutriments.get('fiber_100g', 0) > 3:
                        benefits.append("✅ **Good Fiber:** Aids digestion and gut health")
                    
                    if risks:
                        st.markdown("**⚠️ Potential Risks:**")
                        for risk in risks:
                            st.markdown(f"- {risk}")
                    
                    if benefits:
                        st.markdown("**✅ Benefits:**")
                        for benefit in benefits:
                            st.markdown(f"- {benefit}")
                    
                    # Nutri-Score
                    if data.get('nutriscore_grade'):
                        st.plotly_chart(generate_enhanced_nutri_score_viz(data['nutriscore_grade']), use_container_width=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Product not found. Try scanning a barcode for more accurate results.")
            
            elif intent == "nutrition_info":
                # Nutrition Information Query
                st.markdown("### 📊 Nutritional Information")
                
                data = search_open_food_facts(prompt)
                if data:
                    st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="margin-top: 0;">{data.get('product_name', 'Unknown')}</h3>
                            <p><strong>Brand:</strong> {data.get('brands', 'N/A')}</p>
                            <p><strong>Energy:</strong> {data.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g</p>
                            <p><strong>Nutri-Score:</strong> {data.get('nutriscore_grade', 'N/A').upper()}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if data.get('nutriscore_grade'):
                        st.plotly_chart(generate_enhanced_nutri_score_viz(data['nutriscore_grade']), use_container_width=True)
                else:
                    st.warning("⚠️ Product not found. Try a different search term.")
            
            else:
                # General query
                st.markdown("🔍 Analyzing your query...")
                
                # Try local database first
                df = load_optimized_data()
                match = df[df['name'].str.contains(prompt, case=False, na=False)]
                
                if not match.empty:
                    food = match.iloc[0]
                    st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="margin-top: 0;">{food['name']}</h3>
                            <p><strong>Calories:</strong> {food['calories']} kcal</p>
                            <p><strong>Protein:</strong> {food['protein']}g</p>
                            <p><strong>Fat:</strong> {food['fat']}g</p>
                            <p><strong>Sugar:</strong> {food['sugar']}g</p>
                            <p><strong>Labels:</strong> {food['labels']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    # Search Open Food Facts
                    data = search_open_food_facts(prompt)
                    if data:
                        st.markdown(f"""
                            <div class="glass-card">
                                <h3 style="margin-top: 0;">{data.get('product_name', 'Unknown')}</h3>
                                <p><strong>Brand:</strong> {data.get('brands', 'N/A')}</p>
                                <p><strong>Energy:</strong> {data.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g</p>
                                <p><strong>Nutri-Score:</strong> {data.get('nutriscore_grade', 'N/A').upper()}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if data.get('nutriscore_grade'):
                            st.plotly_chart(generate_enhanced_nutri_score_viz(data['nutriscore_grade']), use_container_width=True)
                    else:
                        st.info("💡 Couldn't find specific data. Try scanning a barcode or being more specific.")

# Scan Label
elif menu == "🔍 Scan Label":
    st.markdown("<h1>🔍 Product Scanner</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Scan any product barcode to instantly get detailed nutritional information, 
                allergen warnings, and health insights powered by Open Food Facts.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    barcode = st.text_input("🏷️ Enter Barcode Number", placeholder="e.g., 3017620422003")
    
    if st.button("🔍 Fetch Product Details", use_container_width=True):
        if barcode:
            with st.spinner("🔄 Scanning product database..."):
                data = fetch_open_food_facts(barcode)
            
            if data and data.get('status') == 1:
                p = data['product']
                st.session_state.analysis_count += 1
                
                st.success(f"✅ Found: **{p.get('product_name', 'Unknown')}**")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if p.get('image_url'):
                        st.image(p['image_url'], use_container_width=True)
                    else:
                        st.image('https://via.placeholder.com/300x300?text=No+Image', use_container_width=True)
                
                with col2:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown(f"### {p.get('product_name', 'Unknown Product')}")
                    st.markdown(f"**Brand:** {p.get('brands', 'N/A')}")
                    st.markdown(f"**Categories:** {p.get('categories', 'N/A')}")
                    
                    if p.get('nutriscore_grade'):
                        st.plotly_chart(generate_enhanced_nutri_score_viz(p['nutriscore_grade']), use_container_width=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Allergen Check
                ingredients_text = p.get('ingredients_text', '')
                if st.session_state.profile['allergies'] and ingredients_text:
                    allergens_found = check_allergens([ingredients_text], st.session_state.profile['allergies'])
                    if allergens_found:
                        st.markdown(f"""
                            <div class="alert-banner">
                                <span class="alert-icon">⚠️</span>
                                <div>
                                    <strong>ALLERGEN DETECTED!</strong><br>
                                    This product contains: {', '.join(allergens_found)}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Nutritional Information
                st.markdown("### 📊 Nutritional Facts (per 100g)")
                nutriments = p.get('nutriments', {})
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                        <div class="glass-card" style="text-align: center;">
                            <div class="metric-value" style="font-size: 2rem; color: #1e5666;">{nutriments.get('energy-kcal_100g', 'N/A')}</div>
                            <div class="metric-label">Calories</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="glass-card" style="text-align: center;">
                            <div class="metric-value" style="font-size: 2rem; color: #1e5666;">{nutriments.get('proteins_100g', 'N/A')}</div>
                            <div class="metric-label">Protein (g)</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="glass-card" style="text-align: center;">
                            <div class="metric-value" style="font-size: 2rem; color: #1e5666;">{nutriments.get('sugars_100g', 'N/A')}</div>
                            <div class="metric-label">Sugar (g)</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Ingredients
                st.markdown("### 🧪 Ingredients")
                st.markdown(f"""
                    <div class="glass-card">
                        <p style="line-height: 1.8;">{ingredients_text if ingredients_text else 'Not available'}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.session_state.history.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "content": f"Scanned {p.get('product_name', 'product')}"
                })
            else:
                st.error("❌ Product not found in database. Please check the barcode and try again.")
        else:
            st.warning("⚠️ Please enter a barcode number.")

# Quick Ask
elif menu == "⚡ Quick Ask":
    st.markdown("<h1>⚡ Quick Ingredient Analysis</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Paste a raw ingredient list from any product label, and WiseWhisk will instantly 
                analyze it for potential allergens, high-risk ingredients, and provide health insights.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    txt = st.text_area(
        "📝 Paste Ingredient List Here",
        placeholder="Example: Water, Sugar, Wheat Flour, Palm Oil, Milk Powder, Salt, Emulsifier (E471)...",
        height=150
    )
    
    if st.button("🔬 Analyze Ingredients", use_container_width=True):
        if txt:
            with st.spinner("🔄 Analyzing ingredients..."):
                st.session_state.analysis_count += 1
                
                # Parse ingredients
                parsed_ingredients = parse_ingredient_list(txt)
                
                st.markdown("### 📋 Detected Ingredients")
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                
                # Display parsed ingredients
                ingredients_display = ", ".join(parsed_ingredients) if parsed_ingredients else "Unable to parse ingredients"
                st.markdown(f"**Found {len(parsed_ingredients)} ingredients:** {ingredients_display}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Allergen Check
                if st.session_state.profile['allergies']:
                    allergens_found = check_allergens(parsed_ingredients, st.session_state.profile['allergies'])
                    if allergens_found:
                        st.markdown(f"""
                            <div class="alert-banner">
                                <span class="alert-icon">⚠️</span>
                                <div>
                                    <strong>ALLERGEN ALERT!</strong><br>
                                    Contains: {', '.join(allergens_found)}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("✅ No allergens detected based on your profile")
                else:
                    st.info("💡 Set up your allergen profile to get personalized warnings")
                
                # Quick Health Scan
                st.markdown("### 🔍 Quick Health Scan")
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                
                warnings = []
                if "sugar" in txt.lower():
                    warnings.append("⚠️ **Sugar detected** - May cause energy spikes and crashes")
                if "sodium" in txt.lower() or "salt" in txt.lower():
                    warnings.append("⚠️ **High sodium** - Can contribute to high blood pressure")
                if "palm oil" in txt.lower():
                    warnings.append("⚠️ **Palm oil** - High in saturated fat")
                if any(term in txt.lower() for term in ["e621", "msg", "monosodium glutamate"]):
                    warnings.append("⚠️ **MSG detected** - Some people may be sensitive")
                if any(term in txt.lower() for term in ["artificial", "synthetic"]):
                    warnings.append("⚠️ **Artificial ingredients** - Consider natural alternatives")
                
                if warnings:
                    for warning in warnings:
                        st.markdown(f"- {warning}")
                else:
                    st.success("✅ No major health concerns detected in quick scan")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Save to session
                st.session_state.custom_ingredients.append({
                    "name": "Quick Analysis",
                    "ingredients": parsed_ingredients,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                st.session_state.history.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "content": f"Quick analyzed {len(parsed_ingredients)} ingredients"
                })
                
                st.success("✅ Analysis complete! Results saved to your history.")
        else:
            st.warning("⚠️ Please paste an ingredient list to analyze.")

# My Profile
elif menu == "👤 My Profile":
    st.markdown("<h1>👤 Your Health Profile</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Customize your health profile to get personalized ingredient analysis, 
                allergen warnings, and dietary recommendations tailored to your needs.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Health Goals
    st.markdown("### 🎯 Health Goals")
    st.session_state.profile["goals"] = st.text_area(
        "What are your health and nutrition goals?",
        st.session_state.profile["goals"],
        height=100,
        help="Be specific about what you want to achieve (e.g., lose weight, build muscle, manage diabetes)"
    )
    
    # Allergies
    st.markdown("### 🚫 Allergies & Restrictions")
    st.session_state.profile["allergies"] = st.multiselect(
        "Select your allergies",
        ["Peanuts", "Tree Nuts", "Dairy", "Gluten", "Soy", "Eggs", "Fish", "Shellfish"],
        default=st.session_state.profile["allergies"],
        help="WiseWhisk will alert you when these allergens are detected"
    )
    
    # Dietary Preferences
    st.markdown("### 🥗 Dietary Preferences")
    st.session_state.profile["dietary_preferences"] = st.multiselect(
        "Select your dietary preferences",
        ["Vegetarian", "Vegan", "Keto", "Paleo", "Low-Carb", "Low-Fat", "High-Protein", "Organic Only"],
        default=st.session_state.profile.get("dietary_preferences", [])
    )
    
    # Save Button
    if st.button("💾 Update Profile", use_container_width=True):
        st.success("✅ Profile updated successfully!")
        st.session_state.history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "content": "Updated health profile"
        })
        st.balloons()
    
    # Profile Summary
    st.markdown("### 📊 Profile Summary")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            **🎯 Goals:** {st.session_state.profile['goals']}
            
            **🚫 Allergies:** {', '.join(st.session_state.profile['allergies']) if st.session_state.profile['allergies'] else 'None'}
        """)
    
    with col2:
        st.markdown(f"""
            **🥗 Diet:** {', '.join(st.session_state.profile.get('dietary_preferences', [])) if st.session_state.profile.get('dietary_preferences') else 'Not specified'}
            
            **📈 Active Since:** {datetime.now().strftime('%B %Y')}
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Add Ingredient
elif menu == "➕ Add Ingredient":
    st.markdown("<h1>➕ Add Custom Ingredient</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Add custom ingredients to your personal database for quick reference and analysis.
                This is perfect for home-cooked meals or local products not in Open Food Facts.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Manual Entry", "📝 Paste Ingredient List"])
    
    with tab1:
        with st.form("add_ingredient_form"):
            st.markdown("### 📝 Ingredient Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name*", placeholder="e.g., Homemade Granola")
                calories = st.number_input("Calories (per 100g)", min_value=0, value=0)
                protein = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1)
            
            with col2:
                brand = st.text_input("Brand (optional)", placeholder="e.g., Homemade")
                fat = st.number_input("Fat (g)", min_value=0.0, value=0.0, step=0.1)
                sugar = st.number_input("Sugar (g)", min_value=0.0, value=0.0, step=0.1)
            
            labels = st.multiselect(
                "Labels",
                ["Organic", "Vegan", "Gluten-Free", "High-Protein", "Low-Sugar", "Dairy-Free", "Keto-Friendly"]
            )
            
            notes = st.text_area("Additional Notes", placeholder="Any special notes about this ingredient...")
            
            submitted = st.form_submit_button("💾 Save Ingredient", use_container_width=True)
            
            if submitted:
                if name:
                    new_ingredient = {
                        "name": name,
                        "brand": brand,
                        "calories": calories,
                        "protein": protein,
                        "fat": fat,
                        "sugar": sugar,
                        "labels": ", ".join(labels),
                        "notes": notes,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.session_state.custom_ingredients.append(new_ingredient)
                    st.success(f"✅ {name} added to your custom database!")
                    st.session_state.history.append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "content": f"Added custom ingredient: {name}"
                    })
                    st.balloons()
                else:
                    st.error("❌ Please enter a product name")
    
    with tab2:
        st.markdown("### 📋 Paste Raw Ingredient List")
        
        raw_ingredients = st.text_area(
            "Paste ingredients here",
            placeholder="Example: Water, Organic Oats, Honey, Almonds, Cinnamon...",
            height=150
        )
        
        ingredient_name = st.text_input("Give this item a name", placeholder="e.g., My Homemade Cereal")
        
        if st.button("💾 Parse and Save", use_container_width=True):
            if raw_ingredients and ingredient_name:
                parsed = parse_ingredient_list(raw_ingredients)
                
                new_item = {
                    "name": ingredient_name,
                    "raw_ingredients": raw_ingredients,
                    "parsed_ingredients": parsed,
                    "ingredient_count": len(parsed),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.custom_ingredients.append(new_item)
                
                st.success(f"✅ {ingredient_name} saved with {len(parsed)} ingredients!")
                st.markdown(f"**Detected ingredients:** {', '.join(parsed)}")
                
                st.session_state.history.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "content": f"Added custom item: {ingredient_name}"
                })
                st.balloons()
            else:
                st.warning("⚠️ Please provide both a name and ingredient list")
                            
