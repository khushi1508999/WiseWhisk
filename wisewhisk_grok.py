import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
from PIL import Image
import speech_recognition as sr
import datetime
import re
import io
import os

os.environ['LANG'] = 'en_US.UTF-8'

st.set_page_config(layout="wide", page_title="WiseWhisk")

# Custom CSS
css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
body {
    font-family: 'Inter', sans-serif;
    background-color: #f8f9fa;
    color: #333;
}
.stApp {
    background-color: #f8f9fa;
}
.sidebar .sidebar-content {
    background-color: #ffffffaa;
    backdrop-filter: blur(10px);
}
/* Glassmorphic cards */
div.block-container {
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(10px);
    border-radius: 10px;
    box-shadow: 0 4px 30px rgba(0,0,0,0.1);
    padding: 20px;
    margin-bottom: 20px;
}
h1, h2, h3 {
    color: #1e5666;
    letter-spacing: -0.5px;
    font-weight: bold;
}
button {
    background-color: #1e5666;
    color: white;
}
button:hover {
    background-color: #d4af37;
    color: #1e5666;
}
/* Alert */
.alert {
    background-color: #ff4757;
    color: white;
    padding: 10px;
    border-radius: 5px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
/* Responsive */
@media (max-width: 768px) {
    .block-container {
        padding: 10px;
    }
}
"""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Helper Functions
def log_activity(action_type, details):
    st.session_state.history.append({
        'timestamp': datetime.datetime.now(),
        'action_type': action_type,
        'details': details
    })

def fetch_product_data(identifier, is_barcode=False):
    try:
        if is_barcode:
            url = f"https://world.openfoodfacts.org/api/v2/product/{identifier}.json"
        else:
            url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={requests.utils.quote(identifier)}&search_simple=1&action=process&json=1"
        response = requests.get(url, timeout=5)
        data = response.json()
        if is_barcode:
            if data.get('status') == 1:
                return data['product']
        else:
            if data.get('products'):
                return data['products'][0]
        return None
    except:
        return None

def process_product(product):
    if not product:
        return None
    nutriments = product.get('nutriments', {})
    data = {
        'product_name': product.get('product_name', 'Unknown'),
        'brands': product.get('brands', 'Unknown'),
        'nutriscore_grade': product.get('nutriscore_grade', 'unknown').upper(),
        'energy_kcal_100g': nutriments.get('energy-kcal_100g', 0),
        'proteins_100g': nutriments.get('proteins_100g', 0),
        'sugars_100g': nutriments.get('sugars_100g', 0),
        'fiber_100g': nutriments.get('fiber_100g', 0),
        'fat_saturated_100g': nutriments.get('saturated-fat_100g', 0),
        'sodium_100g': nutriments.get('sodium_100g', 0),
        'ingredients_text': product.get('ingredients_text', ''),
        'categories': product.get('categories', ''),
        'image_url': product.get('image_url', None)
    }
    data['health_score'] = calculate_health_score(data)
    return data

def calculate_health_score(data):
    score = 50
    if data['proteins_100g'] > 10:
        score += 15
    if data['fiber_100g'] > 3:
        score += 10
    if data['sugars_100g'] > 15:
        score -= 15
    if data['fat_saturated_100g'] > 5:
        score -= 10
    if data['sodium_100g'] > 0.5:
        score -= 10
    return max(0, min(100, score))

def detect_allergens(ingredients_text, allergies):
    if not allergies:
        return []
    ingredients = [i.strip().lower() for i in re.split(r'[,\;]', ingredients_text)]
    detected = []
    allergen_keywords = {
        'Peanuts': ['peanut', 'arachis'],
        'Dairy': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'lactose', 'casein', 'whey'],
        'Gluten': ['wheat', 'barley', 'rye', 'flour', 'bread', 'pasta', 'gluten'],
        'Soy': ['soy', 'soya', 'tofu', 'edamame'],
        'Eggs': ['egg', 'albumen', 'yolk', 'mayonnaise']
    }
    for allergy in allergies:
        for kw in allergen_keywords.get(allergy, []):
            if any(kw in ing for ing in ingredients):
                detected.append(allergy)
                break
    return detected

def parse_ingredient_list(raw_text):
    raw_text = re.sub(r'^\s*ingredients:\s*', '', raw_text, flags=re.I)
    items = re.split(r',\s*|\;\s*| and ', raw_text)
    return [item.strip().title() for item in items if item.strip()]

def infer_intent(query):
    query_lower = query.lower()
    if any(word in query_lower for word in ['compare', 'vs', 'versus', 'side by side']):
        return "COMPARISON"
    elif any(word in query_lower for word in ['safe', 'diabetic', 'allergic', 'warning', 'danger']):
        return "SAFETY_CHECK"
    elif any(word in query_lower for word in ['nutrition', 'calories', 'protein', 'sugar', 'healthy']):
        return "NUTRITION_INFO"
    else:
        return "GENERAL_QUERY"

def transcribe_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(audio, language='en-US')
            return text
        except sr.UnknownValueError:
            st.error("Could not understand audio.")
            return None
        except sr.RequestError:
            st.error("Speech recognition service error.")
            return None
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

def display_nutriscore_gauge(grade, title="Nutri-Score"):
    score_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'E': 0, 'UNKNOWN': 0}
    value = score_map.get(grade, 0)
    colors = ['#008000', '#00ff00', '#ffff00', '#ff9900', '#ff0000'][::-1]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, 4]},
            'bar': {'color': colors[value]},
            'steps': [
                {'range': [0, 1], 'color': "#ff0000"},
                {'range': [1, 2], 'color': "#ff9900"},
                {'range': [2, 3], 'color': "#ffff00"},
                {'range': [3, 4], 'color': "#00ff00"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': value}
        }
    ))
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_container_width=True)

def display_product_info(product, check_allergens=True):
    st.subheader(product['product_name'])
    st.text(f"Brand: {product['brands']}")
    col1, col2 = st.columns(2)
    with col1:
        display_nutriscore_gauge(product['nutriscore_grade'])
    with col2:
        st.metric("Health Score", product['health_score'])
        st.metric("Calories (100g)", round(product['energy_kcal_100g'], 1))
        st.metric("Proteins (100g)", round(product['proteins_100g'], 1))
        st.metric("Sugars (100g)", round(product['sugars_100g'], 1))
        st.metric("Fiber (100g)", round(product['fiber_100g'], 1))
        st.metric("Sat. Fat (100g)", round(product['fat_saturated_100g'], 1))
        st.metric("Sodium (100g)", round(product['sodium_100g'], 1))
    if product['image_url']:
        try:
            img_response = requests.get(product['image_url'], timeout=5)
            img = Image.open(io.BytesIO(img_response.content))
            st.image(img, width=200)
        except:
            pass
    if check_allergens:
        detected = detect_allergens(product['ingredients_text'], st.session_state.profile['allergies'])
        if detected:
            st.markdown('<div class="alert">ALLERGEN DETECTED: ' + ', '.join(detected) + '</div>', unsafe_allow_html=True)
    st.text("Ingredients: " + product['ingredients_text'][:500] + '...' if len(product['ingredients_text']) > 500 else product['ingredients_text'])
    st.text("Categories: " + product['categories'])

def process_query(query, is_chat=True, container=st):
    intent = infer_intent(query)
    details = ""
    action_type = intent
    if is_chat:
        st.session_state.messages.append({'role': 'user', 'content': query})
    if intent == "COMPARISON":
        vs_match = re.search(r'(.+?)\s*(vs|versus|compare to|compare)\s*(.+)', query, re.I)
        if vs_match:
            prod1 = vs_match.group(1).strip()
            prod2 = vs_match.group(3).strip()
            with container.spinner("Fetching products..."):
                data1 = fetch_product_data(prod1)
                p1 = process_product(data1) if data1 else None
                if p1:
                    st.session_state.queried_products[p1['product_name']] = p1
                data2 = fetch_product_data(prod2)
                p2 = process_product(data2) if data2 else None
                if p2:
                    st.session_state.queried_products[p2['product_name']] = p2
            if p1 and p2:
                container.subheader("Comparison")
                col1, col2 = container.columns(2)
                with col1:
                    display_product_info(p1)
                with col2:
                    display_product_info(p2)
                report = f"Comparison: {p1['product_name']} vs {p2['product_name']}\n\n"
                report += f"{p1['product_name']}:\nHealth Score: {p1['health_score']}\nCalories: {p1['energy_kcal_100g']}\nProteins: {p1['proteins_100g']}\nSugars: {p1['sugars_100g']}\n\n"
                report += f"{p2['product_name']}:\nHealth Score: {p2['health_score']}\nCalories: {p2['energy_kcal_100g']}\nProteins: {p2['proteins_100g']}\nSugars: {p2['sugars_100g']}\n"
                container.download_button("Export Report", data=report, file_name="comparison.txt")
                st.session_state.comparisons_made += 1
                details = f"Compared {prod1} vs {prod2}"
            else:
                container.error("Could not fetch one or both products.")
        else:
            container.error("Could not parse comparison query.")
    elif intent == "SAFETY_CHECK":
        prod = re.sub(r'(is|are|check)?\s*|\s*(safe|dangerous|allergic|for diabetic|warning|danger)?\s*\??', '', query, re.I).strip()
        with container.spinner("Fetching..."):
            data = fetch_product_data(prod)
            p = process_product(data) if data else None
            if p:
                st.session_state.queried_products[p['product_name']] = p
        if p:
            display_product_info(p)
            detected = detect_allergens(p['ingredients_text'], st.session_state.profile['allergies'])
            response = "Seems safe based on your profile." if not detected else "Not safe due to allergens: " + ", ".join(detected)
            if "diabetic" in query.lower() and p['sugars_100g'] > 15:
                response += " High sugar content, caution for diabetics."
            container.text(response)
            details = f"Safety check on {prod}"
        else:
            container.error("Product not found.")
    elif intent == "NUTRITION_INFO":
        prod = re.sub(r'\s*(nutrition|info|calories|protein|sugar|healthy|of|for)?\s*', '', query, re.I).strip()
        with container.spinner("Fetching..."):
            data = fetch_product_data(prod)
            p = process_product(data) if data else None
            if p:
                st.session_state.queried_products[p['product_name']] = p
        if p:
            display_product_info(p, check_allergens=False)
            details = f"Nutrition info on {prod}"
        else:
            container.error("Product not found.")
    else:  # GENERAL_QUERY
        with container.spinner("Fetching..."):
            data = fetch_product_data(query)
            p = process_product(data) if data else None
            if p:
                st.session_state.queried_products[p['product_name']] = p
        if p:
            display_product_info(p)
            details = f"General query on {query}"
        else:
            container.info("No product found. Try specifying a product name for analysis.")
    if details:
        log_activity(action_type, details)
        st.session_state.analysis_count += 1
    if is_chat:
        st.session_state.messages.append({'role': 'assistant', 'content': 'Response provided above.'})

# Initialize Session State
if 'profile' not in st.session_state:
    st.session_state.profile = {'goals': 'Stay healthy and active', 'allergies': [], 'dietary_preferences': []}
if 'custom_ingredients' not in st.session_state:
    st.session_state.custom_ingredients = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = 0
if 'comparisons_made' not in st.session_state:
    st.session_state.comparisons_made = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'queried_products' not in st.session_state:
    st.session_state.queried_products = {}

# Sidebar
st.sidebar.title("WiseWhisk")
st.sidebar.markdown("Intelligent Ingredient Co-Pilot")
page = st.sidebar.radio("Navigation", ["Command Center", "Chat Interface", "Scan Label", "Quick Ask", "My Profile", "Add Ingredient", "Data Analytics", "History"])
st.sidebar.markdown("---")
st.sidebar.markdown("Session Statistics")
database_count = len(st.session_state.queried_products)
custom_count = len(st.session_state.custom_ingredients)
total_foods = database_count + custom_count
all_cal = [p['energy_kcal_100g'] for p in st.session_state.queried_products.values()] + [ing.get('calories', 0) for ing in st.session_state.custom_ingredients]
avg_cal = np.mean(all_cal) if all_cal else 0
st.sidebar.text(f"Total Foods: {total_foods}")
st.sidebar.text(f"Analyses Count: {st.session_state.analysis_count}")
st.sidebar.text(f"Comparisons Count: {st.session_state.comparisons_made}")
st.sidebar.markdown("---")
st.sidebar.text("EnCode 2026 Submission")

# Main Content
if page == "Command Center":
    st.title("Command Center")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Key Metrics")
        st.metric("Total Foods", total_foods)
        st.metric("Database Foods", database_count)
        st.metric("Custom Items", custom_count)
        st.metric("Analyses Performed", st.session_state.analysis_count)
        st.metric("Comparisons Made", st.session_state.comparisons_made)
        st.metric("Average Calories (100g)", round(avg_cal, 1))
    with col2:
        st.subheader("Health Profile")
        st.text("Goals: " + st.session_state.profile['goals'])
        st.text("Allergies: " + (", ".join(st.session_state.profile['allergies']) or "None"))
        st.text("Dietary Preferences: " + (", ".join(st.session_state.profile['dietary_preferences']) or "None"))
    st.subheader("Recent Activities")
    recent = sorted(st.session_state.history, key=lambda x: x['timestamp'], reverse=True)[:5]
    for act in recent:
        st.markdown(f"**{act['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}** - {act['action_type']}: {act['details']}")
elif page == "Chat Interface":
    st.title("Chat Interface")
    if st.session_state.profile['allergies']:
        st.info("Active Protection: Allergies enabled")
    for msg in st.session_state.messages:
        align = 'right' if msg['role'] == 'user' else 'left'
        color = '#1e5666' if msg['role'] == 'user' else '#d4af37'
        st.markdown(f"<div style='text-align: {align}; color: {color};'><b>{msg['role'].capitalize()}:</b> {msg['content']}</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([8, 2])
    with col1:
        query = st.text_input("Type your query here", key="chat_input")
    with col2:
        voice_button = st.button("Voice Input")
    if voice_button:
        text = transcribe_voice()
        if text:
            st.success(f"You said: {text}")
            process_query(text)
            st.rerun()
    if query:
        process_query(query)
        st.rerun()
elif page == "Scan Label":
    st.title("Scan Label")
    barcode = st.text_input("Enter Barcode")
    if barcode:
        with st.spinner("Fetching..."):
            data = fetch_product_data(barcode, is_barcode=True)
            p = process_product(data) if data else None
            if p:
                st.session_state.queried_products[p['product_name']] = p
        if p:
            display_product_info(p)
            log_activity("Scan", f"Scanned barcode {barcode}")
            st.session_state.analysis_count += 1
        else:
            st.error("Product not found.")
elif page == "Quick Ask":
    st.title("Quick Ask")
    col1, col2 = st.columns([8, 2])
    with col1:
        query = st.text_input("Type your quick question", key="quick_input")
    with col2:
        voice_button = st.button("Voice")
    if voice_button:
        text = transcribe_voice()
        if text:
            st.success(f"You said: {text}")
            process_query(text, is_chat=False)
    if query:
        process_query(query, is_chat=False)
elif page == "My Profile":
    st.title("My Profile")
    goals = st.text_area("Health Goals", value=st.session_state.profile['goals'])
    allergies = st.multiselect("Allergies", ["Peanuts", "Dairy", "Gluten", "Soy", "Eggs"], default=st.session_state.profile['allergies'])
    dietary_preferences = st.multiselect("Dietary Preferences", ["Vegetarian", "Vegan", "Keto", "Low-Sugar", "High-Protein"], default=st.session_state.profile['dietary_preferences'])
    if st.button("Save Profile"):
        st.session_state.profile = {'goals': goals, 'allergies': allergies, 'dietary_preferences': dietary_preferences}
        log_activity("Profile Update", "Updated health profile")
        st.success("Profile saved.")
elif page == "Add Ingredient":
    st.title("Add Ingredient")
    tab1, tab2 = st.tabs(["Manual Entry", "Batch Paste"])
    with tab1:
        name = st.text_input("Name")
        calories = st.number_input("Calories (100g)", min_value=0.0)
        protein = st.number_input("Protein (100g)", min_value=0.0)
        fat = st.number_input("Saturated Fat (100g)", min_value=0.0)
        sugar = st.number_input("Sugar (100g)", min_value=0.0)
        brand = st.text_input("Brand")
        labels = st.text_input("Labels")
        notes = st.text_area("Notes")
        if st.button("Add"):
            if name:
                ing = {
                    'name': name,
                    'calories': calories,
                    'protein': protein,
                    'fat_saturated': fat,
                    'sugar': sugar,
                    'brand': brand,
                    'labels': labels,
                    'notes': notes,
                    'timestamp': datetime.datetime.now()
                }
                st.session_state.custom_ingredients.append(ing)
                log_activity("Add Ingredient", f"Added {name}")
                st.success("Ingredient added.")
            else:
                st.error("Name is required.")
    with tab2:
        raw_text = st.text_area("Paste ingredient list")
        if st.button("Parse and Add"):
            if raw_text:
                parsed = parse_ingredient_list(raw_text)
                added_count = 0
                for item in parsed:
                    ing = {
                        'name': item,
                        'calories': 0.0,
                        'protein': 0.0,
                        'fat_saturated': 0.0,
                        'sugar': 0.0,
                        'brand': '',
                        'labels': '',
                        'notes': 'From batch paste',
                        'timestamp': datetime.datetime.now()
                    }
                    st.session_state.custom_ingredients.append(ing)
                    added_count += 1
                log_activity("Parse Ingredients", f"Added {added_count} ingredients from batch")
                st.success(f"Added {added_count} ingredients.")
            else:
                st.error("Please paste a list.")
elif page == "Data Analytics":
    st.title("Data Analytics")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Real-time Statistics")
        st.metric("Total Foods", total_foods)
        st.metric("Database Foods (Open Food Facts count)", database_count)
        st.metric("Custom Items (user-added count)", custom_count)
        st.metric("Average Calories (100g)", round(avg_cal, 1))
        st.metric("Total Analyses Performed", st.session_state.analysis_count)
        st.metric("Total Comparisons Made", st.session_state.comparisons_made)
        st.metric("Activity History Count", len(st.session_state.history))
    with col2:
        if all_cal:
            fig = px.histogram(all_cal, nbins=20, title="Calories Distribution (100g)", labels={'value': 'Calories'})
            st.plotly_chart(fig, use_container_width=True)
    st.subheader("Custom Ingredients List")
    if st.session_state.custom_ingredients:
        df_data = [{
            'Name': ing['name'],
            'Timestamp': ing['timestamp'].strftime('%Y-%m-%d %H:%M'),
            'Calories': ing['calories'],
            'Ingredient Count': 1  # Each is individual
        } for ing in st.session_state.custom_ingredients]
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No custom ingredients added yet.")
elif page == "History":
    st.title("History")
    if st.session_state.history:
        sorted_history = sorted(st.session_state.history, key=lambda x: x['timestamp'], reverse=True)
        for act in sorted_history:
            st.markdown(f"**{act['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}** - {act['action_type']}: {act['details']}")
        if st.button("Clear History"):
            confirm = st.checkbox("Confirm clearing all history?")
            if confirm:
                st.session_state.history = []
                st.session_state.messages = []
                st.session_state.analysis_count = 0
                st.session_state.comparisons_made = 0
                st.rerun()
    else:
        st.info("No activities logged yet.")
