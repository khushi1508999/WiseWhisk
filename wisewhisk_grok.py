import streamlit as st
import pandas as pd
import json
import requests
import os
from PIL import Image
import plotly.graph_objects as go
import base64
from datetime import datetime
import re
import speech_recognition as sr

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
        {"role": "assistant", "content": """👋 **Welcome to WiseWhisk** - Your Intelligent Ingredient Co-Pilot!

I'm powered by a comprehensive food database and ready to help you make smarter, healthier food choices.

**Here's what I can help you with:**

🔄 **Compare products** - "Compare Coke vs Pepsi"
🥗 **Nutrition info** - "Tell me about banana nutrition"
⚠️ **Safety check** - "Is this safe for diabetics?"
📸 **Scan barcodes** - "Scan this product"
👤 **Update profile** - "Add allergy information"

How can I assist you today?"""}
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
    text = re.sub(r'^(ingredients?:?|contains:?)', '', raw_text.lower(), flags=re.IGNORECASE).strip()
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

def get_database_stats():
    """Get statistics about the database"""
    df = load_optimized_data()
    custom_count = len(st.session_state.custom_ingredients)
    
    stats = {
        "total_items": len(df) + custom_count,
        "database_items": len(df),
        "custom_items": custom_count,
        "categories": {}
    }
    
    # Categorize by labels
    if not df.empty and 'labels' in df.columns:
        for labels in df['labels'].dropna():
            for label in str(labels).split(','):
                label = label.strip()
                if label:
                    stats['categories'][label] = stats['categories'].get(label, 0) + 1
    
    return stats

# --- Sidebar Menu ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h1>🦉 WiseWhisk</h1>
        <p style="color: #d4af37; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;">Intelligent Ingredient Co-Pilot</p>
    </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio(
        "🧭 Navigation",
        ["🏠 Command Center", "💬 Chat Interface", "📸 Scan Label", "⚡ Quick Ask", "👤 My Profile", "➕ Add Ingredient", "📊 Database Stats", "📜 History"],
        index=0
    )
    
    st.divider()
    
    # Voice Command Section
    st.markdown("### 🎙️ Voice Command")
    audio_data = st.audio_input("🎤 Record your query")
    if audio_data:
        st.success("✅ Audio captured! Processing...")
        r = sr.Recognizer()
        try:
            with sr.AudioFile(audio_data) as source:
                audio = r.record(source)
            text = r.recognize_google(audio, language='en-US')
            st.success(f"You said: {text}")
            st.session_state.voice_input = text
        except sr.UnknownValueError:
            st.error("Could not understand audio.")
        except sr.RequestError as e:
            st.error(f"Speech recognition error: {e}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
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
    st.caption("🏆 EnCode 2026 Hackathon Submission | WiseWhisk v2.0")

# --- Main Area Logic ---

# Command Center Dashboard
if menu == "🏠 Command Center":
    st.markdown("<h1>🏠 Command Center</h1>", unsafe_allow_html=True)
    
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
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(f"""
            <div style="padding: 0.8rem; background: rgba(30, 86, 102, 0.05); border-radius: 12px; margin-bottom: 0.8rem;">
                <strong style="color: #1e5666;">[{item['timestamp']}]</strong> {item['action_type']}: {item['details']}
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
                
                items = prompt.lower().replace("compare", "").replace("versus", "vs").replace("side by side", "").split(" vs ")
                if len(items) < 2:
                    items = prompt.lower().split(" and ")
                
                if len(items) >= 2:
                    item1, item2 = items[0].strip(), items[1].strip()
                    
                    with st.spinner("🔍 Fetching product data from Open Food Facts..."):
                        d1 = search_open_food_facts(item1)
                        d2 = search_open_food_facts(item2)
                    
                    if d1 and d2:
                        st.session_state.comparisons_made += 1
                        
                        score1 = calculate_health_score(d1.get('nutriments', {}))
                        score2 = calculate_health_score(d2.get('nutriments', {}))
                        
                        st.markdown('<div class="vs-container"><div class="vs-badge">VS</div></div>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="glass-card">
                                <h3 style="color: #1e5666; margin-top: 0;">{d1.get('product_name', item1.title())}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if d1.get('nutriscore_grade'):
                                st.plotly_chart(generate_enhanced_nutri_score_viz(d1.get('nutriscore_grade')), use_container_width=True)
                            
                            st.markdown(f"""
                            **Calories:** {d1.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g  
                            **Protein:** {d1.get('nutriments', {}).get('proteins_100g', 'N/A')} g  
                            **Sugar:** {d1.get('nutriments', {}).get('sugars_100g', 'N/A')} g  
                            **Fat:** {d1.get('nutriments', {}).get('fat_100g', 'N/A')} g  
                            **Health Score:** {score1}/100
                            """)
                            
                            if score1 > score2:
                                st.markdown('<div class="winner-badge">✅ Better Choice</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="loser-badge">❌ Less Healthy</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="glass-card">
                                <h3 style="color: #1e5666; margin-top: 0;">{d2.get('product_name', item2.title())}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if d2.get('nutriscore_grade'):
                                st.plotly_chart(generate_enhanced_nutri_score_viz(d2.get('nutriscore_grade')), use_container_width=True)
                            
                            st.markdown(f"""
                            **Calories:** {d2.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g  
                            **Protein:** {d2.get('nutriments', {}).get('proteins_100g', 'N/A')} g  
                            **Sugar:** {d2.get('nutriments', {}).get('sugars_100g', 'N/A')} g  
                            **Fat:** {d2.get('nutriments', {}).get('fat_100g', 'N/A')} g  
                            **Health Score:** {score2}/100
                            """)
                            
                            if score2 > score1:
                                st.markdown('<div class="winner-badge">✅ Better Choice</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="loser-badge">❌ Less Healthy</div>', unsafe_allow_html=True)
                        
                        add_to_history("Comparison", f"Compared {item1} vs {item2}")
                        
                        response_text = f"✅ Comparison complete! Based on the nutritional analysis, **{item1 if score1 > score2 else item2}** appears to be the healthier choice with a health score of **{max(score1, score2)}/100**."
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    elif d1:
                        st.warning(f"Found data for {item1}, but couldn't find {item2} in Open Food Facts database.")
                        st.markdown(f"**{d1.get('product_name', item1.title())}** - {d1.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g")
                    elif d2:
                        st.warning(f"Found data for {item2}, but couldn't find {item1} in Open Food Facts database.")
                        st.markdown(f"**{d2.get('product_name', item2.title())}** - {d2.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal/100g")
                    else:
                        st.error("❌ Couldn't find either product in the Open Food Facts database. Try using the barcode scanner or check the product names.")
                        response_text = "I couldn't find data for those products. Try scanning their barcodes using the '📸 Scan Label' feature!"
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    st.warning("Please specify two products to compare, e.g., 'Compare Coke vs Pepsi'")
            
            elif intent == "safety_check":
                st.markdown("### 🛡️ Safety Analysis")
                
                with st.spinner("Analyzing safety for your profile..."):
                    data = search_open_food_facts(prompt.split()[-1])
                
                if data:
                    ingredients = parse_ingredient_list(data.get('ingredients_text', ''))
                    allergens = check_allergens(ingredients, st.session_state.profile['allergies'])
                    
                    if allergens:
                        st.markdown(f"""
                        <div class="alert-banner">
                            <span class="alert-icon">⚠️</span>
                            <div>
                                <strong>ALLERGEN WARNING!</strong><br>
                                This product contains: {', '.join(allergens)}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        response_text = f"⚠️ **Warning!** This product contains allergens you're sensitive to: {', '.join(allergens)}. I recommend avoiding it."
                    else:
                        st.success("✅ No allergens detected based on your profile!")
                        response_text = "✅ This product appears safe for your dietary restrictions. No allergens detected!"
                    
                    nutriments = data.get('nutriments', {})
                    if nutriments.get('sugars_100g', 0) > 15:
                        st.warning("⚠️ High sugar content detected - may not be suitable for diabetics")
                        response_text += "\n\n⚠️ High sugar content - exercise caution if diabetic."
                    
                    if nutriments.get('sodium_100g', 0) > 0.5:
                        st.warning("⚠️ High sodium content - may affect blood pressure")
                        response_text += "\n\n⚠️ High sodium - monitor if you have blood pressure concerns."
                    
                    add_to_history("Safety Check", prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    st.error("Couldn't find product data. Try scanning the barcode!")
                    st.session_state.messages.append({"role": "assistant", "content": "I couldn't find safety data for that product. Try using the barcode scanner!"})
            
            elif intent == "nutrition_info":
                st.markdown("### 📊 Nutrition Information")
                
                with st.spinner("Fetching nutrition data from Open Food Facts..."):
                    data = search_open_food_facts(prompt)
                
                if data:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h3 style="color: #1e5666; margin-top: 0;">{data.get('product_name', 'Product')}</h3>
                        <p><strong>Brand:</strong> {data.get('brands', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if data.get('nutriscore_grade'):
                        st.plotly_chart(generate_enhanced_nutri_score_viz(data.get('nutriscore_grade')), use_container_width=True)
                    
                    nutriments = data.get('nutriments', {})
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Calories", f"{nutriments.get('energy-kcal_100g', 'N/A')} kcal")
                        st.metric("Protein", f"{nutriments.get('proteins_100g', 'N/A')} g")
                    
                    with col2:
                        st.metric("Carbs", f"{nutriments.get('carbohydrates_100g', 'N/A')} g")
                        st.metric("Sugar", f"{nutriments.get('sugars_100g', 'N/A')} g")
                    
                    with col3:
                        st.metric("Fat", f"{nutriments.get('fat_100g', 'N/A')} g")
                        st.metric("Sodium", f"{nutriments.get('sodium_100g', 'N/A')} g")
                    
                    response_text = f"📊 Here's the nutrition info for **{data.get('product_name')}**: {nutriments.get('energy-kcal_100g', 'N/A')} kcal, {nutriments.get('proteins_100g', 'N/A')}g protein, {nutriments.get('sugars_100g', 'N/A')}g sugar per 100g."
                    
                    add_to_history("Nutrition Query", prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    df = load_optimized_data()
                    match = df[df['name'].str.contains(prompt, case=False, na=False)]
                    
                    if not match.empty:
                        food = match.iloc[0]
                        st.markdown(f"""
                        <div class="glass-card">
                            <h4>{food['name']}</h4>
                            <p><strong>Calories:</strong> {food['calories']} kcal</p>
                            <p><strong>Protein:</strong> {food['protein']}g</p>
                            <p><strong>Fat:</strong> {food['fat']}g</p>
                            <p><strong>Sugar:</strong> {food['sugar']}g</p>
                            <p><strong>Labels:</strong> {food['labels']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        response_text = f"📊 From local database: **{food['name']}** has {food['calories']} kcal, {food['protein']}g protein. Labels: {food['labels']}"
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                    else:
                        st.error("❌ Couldn't find nutrition data for that item.")
                        st.session_state.messages.append({"role": "assistant", "content": "I couldn't find nutrition data. Try being more specific or use the barcode scanner!"})
            
            else:
                st.markdown("### 💡 General Query")
                
                df = load_optimized_data()
                match = df[df['name'].str.contains(prompt, case=False, na=False)]
                
                if not match.empty:
                    food = match.iloc[0]
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>{food['name']}</h4>
                        <p>{food['calories']} kcal | {food['protein']}g protein | {food['sugar']}g sugar</p>
                        <p><strong>Labels:</strong> {food['labels']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    response_text = f"I found **{food['name']}** in the database: {food['calories']} kcal, {food['protein']}g protein. {food['labels']}"
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    with st.spinner("Searching Open Food Facts database..."):
                        data = search_open_food_facts(prompt)
                    
                    if data:
                        st.markdown(f"""
                        <div class="glass-card">
                            <h4>{data.get('product_name', 'Product')}</h4>
                            <p>{data.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal per 100g</p>
                            <p><strong>Nutri-Score:</strong> {data.get('nutriscore_grade', 'N/A').upper()}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        response_text = f"Found **{data.get('product_name')}** on Open Food Facts: {data.get('nutriments', {}).get('energy-kcal_100g', 'N/A')} kcal, Nutri-Score {data.get('nutriscore_grade', 'N/A').upper()}"
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                    else:
                        response_text = "I couldn't find specific data. Try:\n- Comparing products ('Compare X vs Y')\n- Scanning a barcode\n- Asking about nutrition\n- Checking safety for your profile"
                        st.info(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})

# Scan Label
elif menu == "📸 Scan Label":
    st.markdown("<h1>📸 Product Scanner</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card">
        <p style="font-size: 1.1rem;">Enter a product barcode to fetch detailed nutritional information from Open Food Facts database.</p>
    </div>
    """, unsafe_allow_html=True)
    
    barcode = st.text_input("🔢 Enter Barcode (e.g., 3017620422003)", placeholder="Enter barcode...")
    
    if st.button("🔍 Fetch Product Details"):
        if barcode:
            with st.spinner("Fetching product data..."):
                data = fetch_open_food_facts(barcode)
            
            if data and data.get('status') == 1:
                p = data['product']
                st.success(f"✅ Found: {p.get('product_name', 'Unknown Product')}")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if p.get('image_url'):
                        st.image(p.get('image_url'), use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/200?text=No+Image", use_container_width=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h3>{p.get('product_name', 'Unknown')}</h3>
                        <p><strong>Brand:</strong> {p.get('brands', 'N/A')}</p>
                        <p><strong>Categories:</strong> {p.get('categories', 'N/A')}</p>
                        <p><strong>Ingredients:</strong> {p.get('ingredients_text', 'N/A')[:200]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if p.get('nutriscore_grade'):
                    st.plotly_chart(generate_enhanced_nutri_score_viz(p.get('nutriscore_grade')), use_container_width=True)
                
                st.markdown("### 📊 Nutritional Facts (per 100g)")
                nutriments = p.get('nutriments', {})
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Energy", f"{nutriments.get('energy-kcal_100g', 'N/A')} kcal")
                with col2:
                    st.metric("Protein", f"{nutriments.get('proteins_100g', 'N/A')} g")
                with col3:
                    st.metric("Carbs", f"{nutriments.get('carbohydrates_100g', 'N/A')} g")
                with col4:
                    st.metric("Fat", f"{nutriments.get('fat_100g', 'N/A')} g")
                
                # Check allergens
                if st.session_state.profile['allergies']:
                    ingredients = parse_ingredient_list(p.get('ingredients_text', ''))
                    allergens = check_allergens(ingredients, st.session_state.profile['allergies'])
                    
                    if allergens:
                        st.markdown(f"""
                        <div class="alert-banner">
                            <span class="alert-icon">⚠️</span>
                            <div>
                                <strong>ALLERGEN WARNING!</strong><br>
                                Contains: {', '.join(allergens)}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                add_to_history("Barcode Scan", f"Scanned {p.get('product_name', barcode)}")
            else:
                st.error("❌ Product not found in Open Food Facts database. Try a different barcode.")
        else:
            st.warning("Please enter a barcode first!")

# Quick Ask
elif menu == "⚡ Quick Ask":
    st.markdown("<h1>⚡ Quick Ingredient Analysis</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card">
        <p style="font-size: 1.1rem;">Paste an ingredient list to get instant analysis for potential health concerns.</p>
    </div>
    """, unsafe_allow_html=True)
    
    txt = st.text_area("📝 Paste ingredients here:", height=200, placeholder="e.g., Sugar, Salt, Wheat Flour, Artificial Flavors...")
    
    if st.button("🔬 Analyze Now"):
        if txt:
            with st.spinner("Analyzing ingredients..."):
                ingredients = parse_ingredient_list(txt)
                
                st.markdown("### 📋 Detected Ingredients")
                st.write(", ".join(ingredients))
                
                warnings = []
                
                if any("sugar" in ing.lower() for ing in ingredients):
                    warnings.append("⚠️ **High Sugar** detected - May spike blood glucose levels")
                
                if any("sodium" in ing.lower() or "salt" in ing.lower() for ing in ingredients):
                    warnings.append("🧂 **High Sodium** detected - Monitor if you have blood pressure concerns")
                
                if any("artificial" in ing.lower() or "flavor" in ing.lower() for ing in ingredients):
                    warnings.append("🧪 **Artificial ingredients** detected - Consider natural alternatives")
                
                if any("palm oil" in ing.lower() for ing in ingredients):
                    warnings.append("🌴 **Palm Oil** detected - Environmental and health concerns")
                
                # Check allergens
                if st.session_state.profile['allergies']:
                    allergens = check_allergens(ingredients, st.session_state.profile['allergies'])
                    if allergens:
                        warnings.append(f"🚨 **ALLERGEN ALERT**: Contains {', '.join(allergens)}")
                
                if warnings:
                    st.markdown("### ⚠️ Health Warnings")
                    for warning in warnings:
                        st.warning(warning)
                else:
                    st.success("✅ No major health concerns detected based on your profile!")
                
                add_to_history("Quick Analysis", f"Analyzed {len(ingredients)} ingredients")
        else:
            st.warning("Please paste some ingredients first!")

# My Profile
elif menu == "👤 My Profile":
    st.markdown("<h1>👤 User Profile</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card">
        <p style="font-size: 1.1rem;">Customize your health profile to get personalized recommendations and allergen warnings.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("profile_form"):
        st.markdown("### 🎯 Health Goals")
        goals = st.text_area(
            "What are your health goals?",
            value=st.session_state.profile["goals"],
            height=100,
            placeholder="e.g., Lose weight, Build muscle, Manage diabetes..."
        )
        
        st.markdown("### 🚫 Allergies & Dietary Restrictions")
        allergies = st.multiselect(
            "Select your allergies:",
            ["Peanuts", "Dairy", "Gluten", "Soy", "Eggs", "Shellfish", "Tree Nuts", "Fish"],
            default=st.session_state.profile["allergies"]
        )
        
        st.markdown("### 🥗 Dietary Preferences")
        dietary = st.multiselect(
            "Select your dietary preferences:",
            ["Vegetarian", "Vegan", "Keto", "Low-Carb", "Low-Fat", "High-Protein", "Paleo"],
            default=st.session_state.profile.get("dietary_preferences", [])
        )
        
        submitted = st.form_submit_button("💾 Update Profile")
        
        if submitted:
            st.session_state.profile["goals"] = goals
            st.session_state.profile["allergies"] = allergies
            st.session_state.profile["dietary_preferences"] = dietary
            
            st.success("✅ Profile updated successfully!")
            add_to_history("Profile Update", "Updated health profile")
            st.balloons()
    
    st.markdown("### 📊 Your Current Profile")
    st.markdown(f"""
    <div class="glass-card">
        <p><strong>Goals:</strong> {st.session_state.profile['goals']}</p>
        <p><strong>Allergies:</strong> {', '.join(st.session_state.profile['allergies']) if st.session_state.profile['allergies'] else 'None'}</p>
        <p><strong>Dietary Preferences:</strong> {', '.join(st.session_state.profile.get('dietary_preferences', [])) if st.session_state.profile.get('dietary_preferences') else 'None'}</p>
    </div>
    """, unsafe_allow_html=True)

# Add Ingredient
elif menu == "➕ Add Ingredient":
    st.markdown("<h1>➕ Add Custom Ingredient</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card">
        <p style="font-size: 1.1rem;">Add custom ingredients to your personal database for offline access.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("add_ingredient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("🏷️ Ingredient Name", placeholder="e.g., Organic Honey")
            calories = st.number_input("🔥 Calories (per 100g)", min_value=0, value=0)
            protein = st.number_input("💪 Protein (g)", min_value=0.0, value=0.0, step=0.1)
        
        with col2:
            fat = st.number_input("🥑 Fat (g)", min_value=0.0, value=0.0, step=0.1)
            sugar = st.number_input("🍬 Sugar (g)", min_value=0.0, value=0.0, step=0.1)
            sodium = st.number_input("🧂 Sodium (g)", min_value=0.0, value=0.0, step=0.01)
        
        labels = st.text_input("🏷️ Labels (comma-separated)", placeholder="e.g., Organic, Vegan, Gluten-Free")
        
        submitted = st.form_submit_button("➕ Add to Database")
        
        if submitted:
            if name:
                new_ingredient = {
                    "name": name,
                    "calories": calories,
                    "protein": protein,
                    "fat": fat,
                    "sugar": sugar,
                    "sodium": sodium,
                    "labels": labels
                }
                
                st.session_state.custom_ingredients.append(new_ingredient)
                st.success(f"✅ Added **{name}** to your custom database!")
                add_to_history("Add Ingredient", f"Added {name}")
                st.balloons()
            else:
                st.error("Please enter an ingredient name!")
    
    if st.session_state.custom_ingredients:
        st.markdown("### 📦 Your Custom Ingredients")
        
        df_custom = pd.DataFrame(st.session_state.custom_ingredients)
        st.dataframe(df_custom, use_container_width=True)
        
        if st.button("🗑️ Clear All Custom Ingredients"):
            st.session_state.custom_ingredients = []
            st.rerun()

# Database Stats
elif menu == "📊 Database Stats":
    st.markdown("<h1>📊 Database Statistics</h1>", unsafe_allow_html=True)
    
    stats = get_database_stats()
    
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top: 0;">📈 Data Overview</h3>
        <p style="font-size: 1.1rem;">Real-time statistics about your ingredient database.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-value">{stats['total_items']}</div>
            <div class="metric-label">Total Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-value">{stats['database_items']}</div>
            <div class="metric-label">Database Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-tile">
            <div class="metric-value">{stats['custom_items']}</div>
            <div class="metric-label">Custom Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    if stats['categories']:
        st.markdown("### 🏷️ Category Breakdown")
        
        # Create a bar chart for categories
        categories_df = pd.DataFrame(list(stats['categories'].items()), columns=['Category', 'Count'])
        categories_df = categories_df.sort_values('Count', ascending=False).head(10)
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories_df['Category'],
                y=categories_df['Count'],
                marker_color='#1e5666',
                text=categories_df['Count'],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="Top 10 Food Categories",
            xaxis_title="Category",
            yaxis_title="Number of Items",
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 📊 Data Sources")
    st.markdown("""
    <div class="glass-card">
        <p><strong>🌐 Open Food Facts:</strong> Real-time access to 2M+ products worldwide</p>
        <p><strong>💾 Local Database:</strong> {db_items} pre-loaded items for offline access</p>
        <p><strong>➕ Custom Entries:</strong> {custom_items} items added by you</p>
    </div>
    """.format(db_items=stats['database_items'], custom_items=stats['custom_items']), unsafe_allow_html=True)

# History
elif menu == "📜 History":
    st.markdown("<h1>📜 Activity History</h1>", unsafe_allow_html=True)
    
    if st.session_state.history:
        st.markdown("""
        <div class="glass-card">
            <p style="font-size: 1.1rem;">Your complete activity log with WiseWhisk.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
        
        st.markdown("### 📋 Recent Activities")
        
        for idx, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"[{item['timestamp']}] {item['action_type']}", expanded=(idx < 3)):
                st.markdown(f"""
                <div class="glass-card">
                    <p><strong>Action:</strong> {item['action_type']}</p>
                    <p><strong>Details:</strong> {item['details']}</p>
                    <p><strong>Time:</strong> {item['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Export history
        history_df = pd.DataFrame(st.session_state.history)
        csv = history_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download History (CSV)",
            data=csv,
            file_name=f"wisewhisk_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.markdown("""
        <div class="glass-card">
            <p style="text-align: center; color: #999; font-style: italic; font-size: 1.2rem;">
                📭 No activity yet. Start analyzing ingredients!
            </p>
        </div>
        """, unsafe_allow_html=True)
