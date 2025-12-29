import streamlit as st
import pandas as pd
import json
import requests
import os
from PIL import Image
import plotly.graph_objects as go
from datetime import datetime
import re

# Force English language
os.environ['LANG'] = 'en_US.UTF-8'

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
    
    [data-testid="stSidebar"] {
        background: rgba(248, 249, 250, 0.85);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(30, 86, 102, 0.1);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
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
    
    .comparison-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 24px;
        padding: 2rem;
        border: 2px solid rgba(212, 175, 55, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .comparison-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(30, 86, 102, 0.1) 0%, rgba(212, 175, 55, 0.05) 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid #d4af37;
        margin: 1rem 0;
    }
    
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
    
    h2 {
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
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
    
    .dataframe {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    
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
        .comparison-card {
            padding: 1.5rem;
        }
    }
    
    .icon-button {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
    }
    
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
    st.session_state.profile = {
        "goals": "Stay healthy and active",
        "allergies": [],
        "dietary_preferences": []
    }
if 'custom_ingredients' not in st.session_state:
    st.session_state.custom_ingredients = []
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Welcome to WiseWhisk - Your Intelligent Ingredient Co-Pilot! I am powered by a comprehensive food database and ready to help you make smarter, healthier food choices. How can I assist you today?"
        }
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

def get_data_analytics():
    """Generate data analytics for sidebar"""
    df = load_optimized_data()
    custom = st.session_state.custom_ingredients
    
    total_foods = len(df) + len(custom)
    avg_calories = df['calories'].mean() if not df.empty else 0
    
    return {
        "total_foods": total_foods,
        "database_foods": len(df),
        "custom_foods": len(custom),
        "avg_calories": round(avg_calories, 1),
        "analyses": st.session_state.analysis_count,
        "comparisons": st.session_state.comparisons_made
    }

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
    query = str(query).strip()
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
    text = re.sub(r'^(ingredients?:?|contains:?)', '', str(raw_text).lower(), flags=re.IGNORECASE).strip()
    ingredients = re.split(r'[,;]|\sand\s', text)
    
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
    query = str(query).lower()
    if any(word in query for word in ["compare", "vs", "versus", "difference", "better than", "side by side"]):
        return "comparison"
    elif any(word in query for word in ["safe", "diabetic", "allergic", "risk", "bad for", "warning", "danger"]):
        return "safety_check"
    elif any(word in query for word in ["nutrition", "calories", "info", "protein", "sugar", "carbs", "nutrients", "healthy", "how much"]):
        return "nutrition_info"
    else:
        return "general_query"

def generate_enhanced_nutri_score_viz(score, product_data=None):
    """Enhanced Nutri-Score visualization with breakdown"""
    colors = {'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02', 'D': '#EE8100', 'E': '#E63E11'}
    score = str(score).upper() if score and str(score).upper() in colors else 'C'
    
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

def add_to_history(action_type, details):
    """Add detailed action to history"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append({
        "timestamp": timestamp,
        "action_type": action_type,
        "details": details
    })

def calculate_health_score(nutriments):
    """Calculate a simple health score based on nutrients"""
    score = 50
    
    if nutriments.get('proteins_100g', 0) > 10:
        score += 15
    if nutriments.get('fiber_100g', 0) > 3:
        score += 10
    
    if nutriments.get('sugars_100g', 0) > 15:
        score -= 15
    if nutriments.get('saturated-fat_100g', 0) > 5:
        score -= 10
    if nutriments.get('sodium_100g', 0) > 0.5:
        score -= 10
    
    return max(0, min(100, score))

# --- Sidebar Menu ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">
            <h1>WiseWhisk</h1>
            <p style="color: #d4af37; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;">Intelligent Ingredient Co-Pilot</p>
        </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio(
        "Navigation",
        ["Command Center", "Chat Interface", "Scan Label", "Quick Ask", "My Profile", "Add Ingredient", "Data Analytics", "History"],
        index=0
    )
    
    st.divider()
    
    # Data Analytics Widget
    analytics = get_data_analytics()
    st.markdown(f"""
        <div style="background: rgba(30, 86, 102, 0.1); padding: 1rem; border-radius: 12px; margin-top: 1rem;">
            <p style="margin: 0; font-size: 0.85rem; color: #1e5666;">
                <strong>Session Statistics</strong><br>
                Total Foods: {analytics['total_foods']}<br>
                Analyses: {analytics['analyses']}<br>
                Comparisons: {analytics['comparisons']}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.caption("EnCode 2026 Submission | WiseWhisk v2.0")

# --- Main Area Logic ---

if menu == "Command Center":
    st.markdown("<h1>Command Center</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <h3 style="margin-top: 0;">Welcome to WiseWhisk!</h3>
            <p style="font-size: 1.1rem; color: #555; line-height: 1.7;">
                Your intelligent co-pilot for making smarter food choices. Start by exploring your health profile, 
                analyzing ingredients, or comparing products side-by-side.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
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
    
    st.markdown("<h2>Your Health Profile</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: #1e5666; margin-top: 0;">Health Goals</h4>
                <p style="font-size: 1.05rem; line-height: 1.7;">{st.session_state.profile['goals']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        allergies_display = ", ".join(st.session_state.profile['allergies']) if st.session_state.profile['allergies'] else "None set"
        st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: #1e5666; margin-top: 0;">Allergies and Restrictions</h4>
                <p style="font-size: 1.05rem; line-height: 1.7;">{allergies_display}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h2>Recent Activity</h2>", unsafe_allow_html=True)
    
    if st.session_state.history:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(f"""
                <div style="padding: 0.8rem; background: rgba(30, 86, 102, 0.05); border-radius: 12px; margin-bottom: 0.8rem;">
                    <strong style="color: #1e5666;">[{item['timestamp']}]</strong> {item['details']}
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="glass-card">
                <p style="text-align: center; color: #999; font-style: italic;">No recent activity. Start analyzing ingredients!</p>
            </div>
        """, unsafe_allow_html=True)

elif menu == "Chat Interface":
    st.markdown("<h1>Intelligent Chat</h1>", unsafe_allow_html=True)
    
    if st.session_state.profile['allergies']:
        st.markdown(f"""
            <div style="background: rgba(212, 175, 55, 0.1); padding: 1rem; border-radius: 12px; border-left: 4px solid #d4af37; margin-bottom: 1.5rem;">
                <strong>Active Protection:</strong> Monitoring for {', '.join(st.session_state.profile['allergies'])}
            </div>
        """, unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask WiseWhisk about ingredients, nutrition, or product comparisons..."):
        prompt = str(prompt).strip()
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        intent = infer_intent(prompt)
        st.session_state.analysis_count += 1
        
        with st.chat_message("assistant"):
            if intent == "comparison":
                st.markdown("### Product Comparison")
                
                items = prompt.lower().replace("compare", "").replace("versus", "vs").replace("side by side", "").split(" vs ")
                if len(items) < 2:
                    items = prompt.lower().split(" and ")
                
                if len(items) >= 2:
                    item1, item2 = items[0].strip(), items[1].strip()
                    
                    with st.spinner("Fetching product data..."):
                        d1 = search_open_food_facts(item1)
                        d2 = search_open_food_facts(item2)
                    
                    if d1 and d2:
                        st.session_state.comparisons_made += 1
                        
                        score1 = calculate_health_score(d1.get('nutriments', {}))
                        score2 = calculate_health_score(d2.get('nutriments', {}))
                        
                        st.markdown('<div class="vs-container"><div class="vs-badge">VS</div></div>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        colors = {'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02', 'D': '#EE8100', 'E': '#E63E11'}
                        
                        with col1:
                            st.markdown(f"""
                                <div class="comparison-card">
                                    <h3 style="margin-top: 0; color: #1e5666;">{d1.get('product_name', item1.title())}</h3>
                                    <p><strong>Brand:</strong> {d1.get('brands', 'N/A')}</p>
                                    <p><strong>Nutri-Score:</strong> <span style="font-size: 1.5rem; font-weight: 800; color: {colors.get(str(d1.get('nutriscore_grade', 'C')).upper(), '#ccc')};">{str(d1.get('nutriscore_grade', 'N/A')).upper()}</span></p>
                                    <p><strong>Energy:</strong> {d1.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g</p>
                                    <p><strong>Protein:</strong> {d1.get('nutriments', {}).get('proteins_100g', 'N/A')} g</p>
                                    <p><strong>Sugar:</strong> {d1.get('nutriments', {}).get('sugars_100g', 'N/A')} g</p>
                                    <p><strong>Health Score:</strong> <span style="font-size: 1.3rem; font-weight: 700; color: #d4af37;">{score1}/100</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if d1.get('nutriscore_grade'):
                                st.plotly_chart(generate_enhanced_nutri_score_viz(d1.get('nutriscore_grade')), use_container_width=True)
                        
                        with col2:
                            st.markdown(f"""
                                <div class="comparison-card">
                                    <h3 style="margin-top: 0; color: #1e5666;">{d2.get('product_name', item2.title())}</h3>
                                    <p><strong>Brand:</strong> {d2.get('brands', 'N/A')}</p>
                                    <p><strong>Nutri-Score:</strong> <span style="font-size: 1.5rem; font-weight: 800; color: {colors.get(str(d2.get('nutriscore_grade', 'C')).upper(), '#ccc')};">{str(d2.get('nutriscore_grade', 'N/A')).upper()}</span></p>
                                    <p><strong>Energy:</strong> {d2.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g</p>
                                    <p><strong>Protein:</strong> {d2.get('nutriments', {}).get('proteins_100g', 'N/A')} g</p>
                                    <p><strong>Sugar:</strong> {d2.get('nutriments', {}).get('sugars_100g', 'N/A')} g</p>
                                    <p><strong>Health Score:</strong> <span style="font-size: 1.3rem; font-weight: 700; color: #d4af37;">{score2}/100</span></p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if d2.get('nutriscore_grade'):
                                st.plotly_chart(generate_enhanced_nutri_score_viz(d2.get('nutriscore_grade')), use_container_width=True)
                        
                        report_text = f"""WiseWhisk Comparison Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PRODUCT 1: {d1.get('product_name', item1.title())}
Health Score: {score1}/100
Nutri-Score: {d1.get('nutriscore_grade', 'N/A')}

PRODUCT 2: {d2.get('product_name', item2.title())}
Health Score: {score2}/100
Nutri-Score: {d2.get('nutriscore_grade', 'N/A')}

Analyzed by WiseWhisk AI Co-Pilot
EnCode 2026 Submission"""
                        
                        st.download_button(
                            label="Export Comparison",
                            data=report_text,
                            file_name=f"wisewhisk_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                        
                        add_to_history("Comparison", f"Compared {item1} vs {item2}")
                    else:
                        st.warning("Could not fetch data. Try different product names.")
                else:
                    st.info("Please specify two products: 'Compare Coke vs Pepsi'")
            
            elif intent == "nutrition_info":
                st.markdown("### Nutritional Information")
                
                with st.spinner("Searching..."):
                    data = search_open_food_facts(prompt)
                
                if data:
                    st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="margin-top: 0; color: #1e5666;">{data.get('product_name', 'Unknown')}</h3>
                            <p><strong>Brand:</strong> {data.get('brands', 'N/A')}</p>
                            <p><strong>Energy:</strong> {data.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g</p>
                            <p><strong>Protein:</strong> {data.get('nutriments', {}).get('proteins_100g', 'N/A')} g</p>
                            <p><strong>Sugar:</strong> {data.get('nutriments', {}).get('sugars_100g', 'N/A')} g</p>
                            <p><strong>Nutri-Score:</strong> {str(data.get('nutriscore_grade', 'N/A')).upper()}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if data.get('nutriscore_grade'):
                        st.plotly_chart(generate_enhanced_nutri_score_viz(data.get('nutriscore_grade')), use_container_width=True)
                    
                    add_to_history("Nutrition Query", f"Searched: {prompt}")
                else:
                    st.info("Product not found. Try a different search term.")
            
            elif intent == "safety_check":
                st.markdown("### Safety Analysis")
                
                with st.spinner("Checking safety..."):
                    data = search_open_food_facts(prompt)
                
                if data:
                    st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="margin-top: 0; color: #1e5666;">{data.get('product_name', 'Product')}</h3>
                            <p><strong>Nutri-Score:</strong> {str(data.get('nutriscore_grade', 'N/A')).upper()}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if "diabetic" in prompt.lower():
                        sugar = data.get('nutriments', {}).get('sugars_100g', 0)
                        if sugar and float(sugar) < 5:
                            st.success("Diabetic-Friendly: Low sugar content (less than 5g per 100g)")
                        else:
                            st.warning("Not Ideal for Diabetics: Contains moderate to high sugar")
                    
                    if data.get('nutriscore_grade'):
                        st.plotly_chart(generate_enhanced_nutri_score_viz(data.get('nutriscore_grade')), use_container_width=True)
                    
                    add_to_history("Safety Check", f"Checked: {prompt}")
                else:
                    st.info("Product not found.")
            
            else:
                st.markdown("### General Search")
                
                with st.spinner("Searching..."):
                    data = search_open_food_facts(prompt)
                
                if data:
                    st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="margin-top: 0; color: #1e5666;">{data.get('product_name', 'Product')}</h3>
                            <p><strong>Brand:</strong> {data.get('brands', 'N/A')}</p>
                            <p><strong>Nutri-Score:</strong> {str(data.get('nutriscore_grade', 'N/A')).upper()}</p>
                            <p><strong>Energy:</strong> {data.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g</p>
                            <p><strong>Protein:</strong> {data.get('nutriments', {}).get('proteins_100g', 'N/A')} g</p>
                            <p><strong>Sugar:</strong> {data.get('nutriments', {}).get('sugars_100g', 'N/A')} g</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if data.get('nutriscore_grade'):
                        st.plotly_chart(generate_enhanced_nutri_score_viz(data.get('nutriscore_grade')), use_container_width=True)
                else:
                    st.markdown("""
                        ### Try asking:
                        - "Compare Coke vs Pepsi"
                        - "Nutrition info about banana"
                        - "Is milk safe for diabetics?"
                        - "How healthy is oat milk?"
                    """)
                
                add_to_history("General Query", prompt)

elif menu == "Scan Label":
    st.markdown("<h1>Product Scanner</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Scan any product barcode to get detailed nutritional information and allergen warnings.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    barcode = st.text_input("Enter Barcode Number", placeholder="e.g., 3017620422003")
    
    if st.button("Fetch Product Details", use_container_width=True):
        if barcode:
            with st.spinner("Scanning..."):
                data = fetch_open_food_facts(barcode)
            
            if data and data.get('status') == 1:
                p = data.get('product', {})
                st.session_state.analysis_count += 1
                
                st.success(f"Found: {p.get('product_name', 'Unknown')}")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if p.get('image_url'):
                        st.image(p.get('image_url'), use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x300?text=No+Image", use_container_width=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="margin-top: 0; color: #1e5666;">{p.get('product_name', 'Unknown')}</h3>
                            <p><strong>Brand:</strong> {p.get('brands', 'N/A')}</p>
                            <p><strong>Categories:</strong> {p.get('categories', 'N/A')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<h3>Nutritional Facts per 100g</h3>", unsafe_allow_html=True)
                
                nutriments = p.get('nutriments', {})
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                        <div class="metric-tile">
                            <div class="metric-value">{nutriments.get('energy-kcal_100g', 'N/A')}</div>
                            <div class="metric-label">Calories</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-tile">
                            <div class="metric-value">{nutriments.get('proteins_100g', 'N/A')}</div>
                            <div class="metric-label">Protein (g)</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="metric-tile">
                            <div class="metric-value">{nutriments.get('sugars_100g', 'N/A')}</div>
                            <div class="metric-label">Sugar (g)</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                if p.get('nutriscore_grade'):
                    st.plotly_chart(generate_enhanced_nutri_score_viz(p.get('nutriscore_grade')), use_container_width=True)
                
                ingredients_text = p.get('ingredients_text', 'Not available')
                parsed_ingredients = parse_ingredient_list(ingredients_text) if ingredients_text else []
                
                st.markdown(f"<h3>Ingredients ({len(parsed_ingredients)})</h3>", unsafe_allow_html=True)
                st.markdown(f"<div class='glass-card'><p>{', '.join(parsed_ingredients) if parsed_ingredients else 'Unable to parse'}</p></div>", unsafe_allow_html=True)
                
                if st.session_state.profile['allergies'] and parsed_ingredients:
                    detected_allergens = check_allergens(parsed_ingredients, st.session_state.profile['allergies'])
                    if detected_allergens:
                        st.markdown(f"""
                            <div class="alert-banner">
                                <span class="alert-icon">Alert</span>
                                <div><strong>ALLERGEN DETECTED!</strong><br>{', '.join(detected_allergens)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                add_to_history("Scan", f"Scanned {p.get('product_name', 'product')}")
            else:
                st.error("Product not found.")
        else:
            st.warning("Please enter a barcode.")

elif menu == "Quick Ask":
    st.markdown("<h1>Quick Ask</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Quick questions about ingredients and nutrition. Get instant answers!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    question = st.text_input("Ask a question", placeholder="e.g., Is oat milk healthy?")
    
    if st.button("Get Answer", use_container_width=True):
        if question:
            st.session_state.analysis_count += 1
            
            with st.spinner("Finding answer..."):
                data = search_open_food_facts(question)
            
            if data:
                st.markdown(f"""
                    <div class="glass-card">
                        <h3 style="margin-top: 0; color: #1e5666;">{data.get('product_name', 'Result')}</h3>
                        <p><strong>Nutri-Score:</strong> {str(data.get('nutriscore_grade', 'N/A')).upper()}</p>
                        <p><strong>Energy:</strong> {data.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal</p>
                        <p><strong>Protein:</strong> {data.get('nutriments', {}).get('proteins_100g', 'N/A')} g</p>
                        <p><strong>Sugar:</strong> {data.get('nutriments', {}).get('sugars_100g', 'N/A')} g</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if data.get('nutriscore_grade'):
                    st.plotly_chart(generate_enhanced_nutri_score_viz(data.get('nutriscore_grade')), use_container_width=True)
            else:
                st.info("No data found. Try a different query.")
            
            add_to_history("Quick Ask", question)

elif menu == "My Profile":
    st.markdown("<h1>Your Health Profile</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Customize your profile for personalized recommendations.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        goals = st.text_area("Health Goals", value=st.session_state.profile['goals'], height=100)
        st.session_state.profile['goals'] = goals
    
    with col2:
        allergies = st.multiselect(
            "Allergies and Restrictions",
            ["Peanuts", "Dairy", "Gluten", "Soy", "Eggs"],
            default=st.session_state.profile['allergies']
        )
        st.session_state.profile['allergies'] = allergies
    
    dietary = st.multiselect(
        "Dietary Preferences",
        ["Vegetarian", "Vegan", "Keto", "Low-Sugar", "High-Protein"],
        default=st.session_state.profile['dietary_preferences']
    )
    st.session_state.profile['dietary_preferences'] = dietary
    
    if st.button("Save Profile", use_container_width=True):
        st.success("Profile updated successfully!")
        add_to_history("Profile Update", "Updated health profile")

elif menu == "Add Ingredient":
    st.markdown("<h1>Add Custom Ingredient</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Add custom ingredients to your database.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Manual Entry", "Paste List"])
    
    with tab1:
        with st.form("add_ingredient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name", placeholder="e.g., Homemade Granola")
                calories = st.number_input("Calories per 100g", min_value=0, value=0)
                protein = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1)
            
            with col2:
                brand = st.text_input("Brand (optional)")
                fat = st.number_input("Fat (g)", min_value=0.0, value=0.0, step=0.1)
                sugar = st.number_input("Sugar (g)", min_value=0.0, value=0.0, step=0.1)
            
            labels = st.multiselect("Labels", ["Organic", "Vegan", "Gluten-Free", "High-Protein", "Low-Sugar", "Dairy-Free"])
            notes = st.text_area("Notes", placeholder="Any special notes...")
            
            submitted = st.form_submit_button("Save Ingredient", use_container_width=True)
            
            if submitted:
                if name:
                    new_ingredient = {
                        "name": name,
                        "brand": brand,
                        "calories": calories,
                        "protein": protein,
                        "fat": fat,
                        "sugar": sugar,
                        "labels": labels,
                        "notes": notes,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.custom_ingredients.append(new_ingredient)
                    st.success(f"{name} added to your database!")
                    add_to_history("Add Ingredient", f"Added: {name}")
                    st.rerun()
                else:
                    st.error("Please enter a product name")
    
    with tab2:
        raw_ingredients = st.text_area("Paste Ingredients", placeholder="Water, Oats, Honey, Almonds...", height=150)
        ingredient_name = st.text_input("Item Name", placeholder="e.g., My Granola")
        
        if st.button("Parse and Save", use_container_width=True):
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
                st.success(f"{ingredient_name} saved with {len(parsed)} ingredients!")
                add_to_history("Parse Ingredients", f"Parsed {len(parsed)} from {ingredient_name}")
                st.rerun()
            else:
                st.error("Please enter both ingredient list and name")

elif menu == "Data Analytics":
    st.markdown("<h1>Data Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    analytics = get_data_analytics()
    df = load_optimized_data()
    
    st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.05rem; line-height: 1.7;">
                Overview of all food data and custom ingredients in your database.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Overview Section
    st.markdown("<h2>Database Overview</h2>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{analytics['total_foods']}</div>
                <div class="metric-label">Total Foods</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{analytics['database_foods']}</div>
                <div class="metric-label">Database Foods</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{analytics['custom_foods']}</div>
                <div class="metric-label">Custom Items</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{analytics['avg_calories']}</div>
                <div class="metric-label">Avg Calories</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Breakdown by Data Type
    st.markdown("<h2>Data Breakdown</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class="stat-box">
                <h4>Open Food Facts Database</h4>
                <p><strong>Total Records:</strong> {analytics['database_foods']}</p>
                <p><strong>Average Calories:</strong> {analytics['avg_calories']} kcal/100g</p>
                <p><strong>Coverage:</strong> Global food products database</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-box">
                <h4>Custom Ingredients</h4>
                <p><strong>Total Custom Items:</strong> {analytics['custom_foods']}</p>
                <p><strong>User Contributions:</strong> Locally added foods</p>
                <p><strong>Personalization:</strong> Enhanced with personal recipes</p>
            </div>
        """, unsafe_allow_html=True)
    
    # User Activity Metrics
    st.markdown("<h2>User Activity Metrics</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="stat-box">
                <h4>Total Analyses</h4>
                <p style="font-size: 2rem; color: #d4af37; font-weight: 800;">{analytics['analyses']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-box">
                <h4>Comparisons Made</h4>
                <p style="font-size: 2rem; color: #d4af37; font-weight: 800;">{analytics['comparisons']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-box">
                <h4>History Items</h4>
                <p style="font-size: 2rem; color: #d4af37; font-weight: 800;">{len(st.session_state.history)}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Custom Ingredients List
    if st.session_state.custom_ingredients:
        st.markdown("<h2>Your Custom Ingredients</h2>", unsafe_allow_html=True)
        
        custom_df = pd.DataFrame(st.session_state.custom_ingredients)
        
        # Display as formatted list
        for idx, item in enumerate(st.session_state.custom_ingredients):
            st.markdown(f"""
                <div class="stat-box">
                    <h4>{item.get('name', 'Unknown')}</h4>
                    <p><strong>Added:</strong> {item.get('timestamp', 'N/A')}</p>
                    {f"<p><strong>Calories:</strong> {item.get('calories', 'N/A')} kcal</p>" if item.get('calories') else ""}
                    {f"<p><strong>Ingredients Count:</strong> {item.get('ingredient_count', 'N/A')}</p>" if item.get('ingredient_count') else ""}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="glass-card">
                <p style="text-align: center; color: #999; font-style: italic;">No custom ingredients added yet. Start adding items to build your personal database!</p>
            </div>
        """, unsafe_allow_html=True)

elif menu == "History":
    st.markdown("<h1>Analysis History</h1>", unsafe_allow_html=True)
    
    if st.session_state.history:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        for item in reversed(st.session_state.history):
            st.markdown(f"""
                <div style="padding: 1rem; background: rgba(30, 86, 102, 0.05); border-radius: 12px; margin-bottom: 1rem; border-left: 4px solid #d4af37;">
                    <strong style="color: #1e5666;">{item['action_type']}</strong> - {item['timestamp']}<br>
                    <span style="color: #666;">{item['details']}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.markdown("""
            <div class="glass-card">
                <p style="text-align: center; color: #999; font-style: italic;">No history yet!</p>
            </div>
        """, unsafe_allow_html=True)
