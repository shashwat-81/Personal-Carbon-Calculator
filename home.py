import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from chatbot import CarbonFootprintChatbot

# Set wide layout and page name (must be first Streamlit command)
st.set_page_config(layout="wide", page_title="Carbon Calculator")

# Add custom CSS for background and styling
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        min-height: 100vh;
        color: #e0e0e0;
        font-family: 'Arial', sans-serif;
        font-size: 1.1rem;
        padding-top: 0;
    }

    /* Add a subtle pattern overlay */
    .stApp::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
        pointer-events: none;
    }

    /* Title styling */
    .big-font {
        font-size: 2.5rem !important;
        font-weight: 800;
        color: #76c7c0;  /* Vibrant teal for headers */
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 10px 20px;
        margin: 0 5px;
        color: #e0e0e0;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.2) !important;
        color: #76c7c0 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        font-weight: 700;
    }

    /* Button styling */
    .stButton>button {
        background: #76c7c0;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        text-transform: none;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }

    .stButton>button:hover {
        background: #5aa89b;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
    }

    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 12px;
        padding: 15px 20px;
        background: rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        border: 2px solid rgba(255, 255, 255, 0.2);
        font-size: 1.1rem;
        transition: all 0.2s ease;
    }

    .stTextInput>div>div>input:focus {
        border-color: #76c7c0;
        box-shadow: 0 0 0 3px rgba(118, 199, 192, 0.3);
    }

    /* Chat message styling */
    .chat-message {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        color: #e0e0e0;
        font-size: 1.1rem;
    }

    /* Plotly chart container */
    .js-plotly-plot {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }

    /* Emission previews */
    .emission-preview {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        text-align: center;
        transition: all 0.3s ease;
    }

    .emission-preview:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
    }

    .emission-preview p {
        margin: 0;
        font-size: 1rem;
        color: #76c7c0;
    }

    /* Total emissions */
    .total-emissions {
        background: rgba(118, 199, 192, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        border: 2px solid rgba(118, 199, 192, 0.3);
    }

    .total-emissions h3 {
        margin: 0;
        color: #76c7c0;
        font-size: 1.5rem;
    }

    /* Certificate modal styling */
    .certificate-modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        z-index: 1000;
        justify-content: center;
        align-items: center;
    }

    .certificate-content {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        max-width: 800px;
        width: 90%;
        position: relative;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
    }

    .certificate-title {
        font-size: 3rem;
        color: #76c7c0;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }

    .certificate-name {
        font-size: 2.5rem;
        color: #e0e0e0;
        margin-bottom: 10px;
    }

    .certificate-description {
        font-size: 1.2rem;
        color: #e0e0e0;
        margin-bottom: 30px;
        line-height: 1.6;
    }

    .certificate-date {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 20px;
    }

    .certificate-seal {
        position: absolute;
        bottom: 20px;
        right: 20px;
        font-size: 3rem;
        color: #76c7c0;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 6px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(118, 199, 192, 0.4);
        border-radius: 6px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(118, 199, 192, 0.6);
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.15);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #76c7c0;
        margin: 10px 0;
    }

    .metric-comparison {
        font-size: 0.9rem;
        color: #888;
    }

    .status-good {
        color: #2ecc71 !important;
    }

    .status-bad {
        color: #e74c3c !important;
    }

    /* Recommendation Cards */
    .recommendation-card {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }

    .recommendation-card:hover {
        transform: translateX(5px);
        background: rgba(255, 255, 255, 0.15);
    }

    .rec-icon {
        font-size: 2rem;
        margin-right: 15px;
        min-width: 50px;
        text-align: center;
    }

    .rec-content h4 {
        margin: 0;
        color: #76c7c0;
    }

    .rec-content p {
        margin: 5px 0 0 0;
        font-size: 0.9rem;
    }

    .progress-bar {
        width: 100%;
        height: 20px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress {
        height: 100%;
        background-color: #4CAF50;
        transition: width 0.3s ease;
    }
    
    .stCard {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid rgba(76, 175, 80, 0.3);
    }
    
    .stCard h4 {
        color: #4CAF50;
        margin-bottom: 10px;
    }

    .certificate-card {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .certificate-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    .certificate-modal {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        position: relative;
        max-width: 800px;
        margin: 0 auto;
        border: 3px solid gold;
    }
    
    .certificate-title {
        font-size: 2.5rem;
        color: gold;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .certificate-icon {
        font-size: 4rem;
        margin-bottom: 20px;
    }
    
    .certificate-name {
        font-size: 2rem;
        color: white;
        margin-bottom: 10px;
    }
    
    .certificate-description {
        color: #e0e0e0;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    
    .certificate-seal {
        position: absolute;
        bottom: 20px;
        right: 20px;
        font-size: 5rem;
        opacity: 0.5;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize services
chatbot = CarbonFootprintChatbot()

# Define emission factors (kg CO2e per unit)
EMISSION_FACTORS = {
    "India": {
        # Transportation (kg CO2e per km)
        "Car": 0.2,
        "Bus": 0.1,
        "Train": 0.05,
        "Motorcycle": 0.1,
        "Airplane": 0.25,
        
        # Energy (kg CO2e per kWh)
        "Electricity": 0.85,
        "LPG": 2.5,
        "CNG": 2.2,
        
        # Diet (kg CO2e per meal)
        "Vegan": 0.5,
        "Vegetarian": 0.8,
        "Non-vegetarian": 1.5,
        
        # Waste (kg CO2e per kg)
        "Organic": 0.5,
        "Plastic": 2.5,
        "Paper": 1.0,
        "Metal": 2.0
    }
}

# Initialize session state variables
if 'calculation_results' not in st.session_state:
    st.session_state.calculation_results = None
if 'emissions_data' not in st.session_state:
    st.session_state.emissions_data = None
if 'challenges' not in st.session_state:
    st.session_state.challenges = []
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
if 'carbon_journey' not in st.session_state:
    st.session_state.carbon_journey = []
if 'certificates' not in st.session_state:
    st.session_state.certificates = []
if 'certificate_progress' not in st.session_state:
    st.session_state.certificate_progress = {
        'Green Novice': {'earned': False, 'progress': 0},
        'Eco Warrior': {'earned': False, 'progress': 0},
        'Climate Champion': {'earned': False, 'progress': 0},
        'Earth Guardian': {'earned': False, 'progress': 0}
    }
if 'show_certificate' not in st.session_state:
    st.session_state.show_certificate = None
if 'show_results_page' not in st.session_state:
    st.session_state.show_results_page = False
if 'viewing_certificate' not in st.session_state:
    st.session_state.viewing_certificate = None

# Add weekly challenge to session state initialization
if 'weekly_challenge' not in st.session_state:
    st.session_state.weekly_challenge = {
        'title': '🚶‍♂️ Walk or Cycle to Work',
        'description': 'Replace your usual commute with walking or cycling for at least 3 days this week.',
        'carbon_saving': '2.5 kg CO2',
        'progress': 0,
        'days': 7
    }

# Add function to save and load progress
def save_progress():
    progress_data = {
        'certificates': st.session_state.certificate_progress,
        'challenges': st.session_state.challenges,
        'achievements': st.session_state.achievements,
        'carbon_journey': st.session_state.carbon_journey,
        'weekly_challenge': st.session_state.weekly_challenge
    }
    with open('user_progress.json', 'w') as f:
        json.dump(progress_data, f)

def load_progress():
    if os.path.exists('user_progress.json'):
        with open('user_progress.json', 'r') as f:
            progress_data = json.load(f)
            st.session_state.certificate_progress = progress_data['certificates']
            st.session_state.challenges = progress_data['challenges']
            st.session_state.achievements = progress_data['achievements']
            st.session_state.carbon_journey = progress_data['carbon_journey']
            if 'weekly_challenge' in progress_data:
                st.session_state.weekly_challenge = progress_data['weekly_challenge']

# Add after session state initialization
if 'progress_loaded' not in st.session_state:
    load_progress()
    st.session_state.progress_loaded = True

# Main title with custom class
st.markdown('<h1 class="big-font">🌍 Carbon Footprint Calculator</h1>', unsafe_allow_html=True)

# Create tabs for different sections with reduced spacing
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Calculate", "📈 Dashboard", "🌱 Offset", "💬 Chat", "🎮 Challenges"])

with tab1:
    # Main calculation section
    st.markdown('<h2 class="stHeader">Calculate Your Carbon Footprint</h2>', unsafe_allow_html=True)
    
    # Create two columns for inputs
    col1, col2 = st.columns(2)
    
    # Initialize session state for real-time updates
    if 'transport_emissions' not in st.session_state:
        st.session_state.transport_emissions = 0
    if 'energy_emissions' not in st.session_state:
        st.session_state.energy_emissions = 0
    if 'waste_emissions' not in st.session_state:
        st.session_state.waste_emissions = 0
    if 'diet_emissions' not in st.session_state:
        st.session_state.diet_emissions = 0
    
    with col1:
        st.markdown('<h3 class="stSubheader">🚗 Transportation</h3>', unsafe_allow_html=True)
        transport_type = st.selectbox(
            "Select your primary mode of transport",
            ["Car", "Bus", "Train", "Motorcycle", "Airplane"]
        )
        distance = st.slider("Daily commute distance (km)", 0.0, 100.0, 10.0)
        if transport_type == "Airplane":
            flights = st.number_input("Number of flights per year", 0, 50, 0)
        
        # Real-time transport emissions calculation
        transport_emissions = distance * 365 * EMISSION_FACTORS["India"][transport_type]
        if transport_type == "Airplane":
            transport_emissions += flights * 1000 * EMISSION_FACTORS["India"]["Airplane"]
        st.session_state.transport_emissions = transport_emissions
        
        # Show transport emissions preview
        st.markdown(f"""
            <div class="emission-preview">
                <p>Estimated transport emissions: {transport_emissions/1000:.1f} t CO2/year</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<h3 class="stSubheader">💡 Energy</h3>', unsafe_allow_html=True)
        electricity = st.slider("Monthly electricity (kWh)", 0.0, 1000.0, 200.0)
        cooking_fuel = st.selectbox(
            "Select your cooking fuel",
            ["LPG", "CNG", "Electric"]
        )
        if cooking_fuel in ["LPG", "CNG"]:
            fuel_consumption = st.slider(f"Monthly {cooking_fuel} consumption (kg)", 0.0, 50.0, 10.0)
        
        # Real-time energy emissions calculation
        energy_emissions = electricity * 12 * EMISSION_FACTORS["India"]["Electricity"]
        if cooking_fuel in ["LPG", "CNG"]:
            energy_emissions += fuel_consumption * 12 * EMISSION_FACTORS["India"][cooking_fuel]
        st.session_state.energy_emissions = energy_emissions
        
        # Show energy emissions preview
        st.markdown(f"""
            <div class="emission-preview">
                <p>Estimated energy emissions: {energy_emissions/1000:.1f} t CO2/year</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<h3 class="stSubheader">🗑️ Waste</h3>', unsafe_allow_html=True)
        waste_types = {
            "Organic": st.slider("Weekly organic waste (kg)", 0.0, 20.0, 2.0),
            "Plastic": st.slider("Weekly plastic waste (kg)", 0.0, 10.0, 1.0),
            "Paper": st.slider("Weekly paper waste (kg)", 0.0, 10.0, 1.0),
            "Metal": st.slider("Weekly metal waste (kg)", 0.0, 5.0, 0.5)
        }
        
        # Real-time waste emissions calculation
        waste_emissions = sum(waste * 52 * EMISSION_FACTORS["India"][waste_type] 
                            for waste_type, waste in waste_types.items())
        st.session_state.waste_emissions = waste_emissions
        
        # Show waste emissions preview
        st.markdown(f"""
            <div class="emission-preview">
                <p>Estimated waste emissions: {waste_emissions/1000:.1f} t CO2/year</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<h3 class="stSubheader">🍽️ Diet</h3>', unsafe_allow_html=True)
        diet_type = st.selectbox(
            "Select your diet type",
            ["Vegan", "Vegetarian", "Non-vegetarian"]
        )
        meals_per_day = st.slider("Number of meals per day", 1, 5, 3)
        
        # Real-time diet emissions calculation
        diet_emissions = meals_per_day * 365 * EMISSION_FACTORS["India"][diet_type]
        st.session_state.diet_emissions = diet_emissions
        
        # Show diet emissions preview
        st.markdown(f"""
            <div class="emission-preview">
                <p>Estimated diet emissions: {diet_emissions/1000:.1f} t CO2/year</p>
            </div>
        """, unsafe_allow_html=True)

    # Add CSS for emission previews
    st.markdown("""
        <style>
        .emission-preview {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .emission-preview:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }
        
        .emission-preview p {
            margin: 0;
            font-size: 1rem;
            color: #4a90e2;
        }
        </style>
    """, unsafe_allow_html=True)

        # Calculate total emissions
    total_emissions = (st.session_state.transport_emissions + 
                      st.session_state.energy_emissions + 
                      st.session_state.waste_emissions + 
                      st.session_state.diet_emissions)

    # Show real-time total emissions
    st.markdown(f"""
        <div class="total-emissions">
            <h3>Current Total Emissions: {total_emissions/1000:.1f} t CO2/year</h3>
        </div>
    """, unsafe_allow_html=True)

    # Add CSS for total emissions
    st.markdown("""
        <style>
        .total-emissions {
            background: rgba(74, 144, 226, 0.2);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            border: 2px solid rgba(74, 144, 226, 0.3);
        }
        
        .total-emissions h3 {
            margin: 0;
            color: #4a90e2;
            font-size: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Calculate button with animation
    if st.button("Calculate Final Carbon Footprint", key="calculate_button"):
        # Store results in session state
        st.session_state.calculation_results = {
            "total": total_emissions,
            "transport": st.session_state.transport_emissions,
            "energy": st.session_state.energy_emissions,
            "waste": st.session_state.waste_emissions,
            "diet": st.session_state.diet_emissions
        }
        
        # Award certificates based on achievements
        if not st.session_state.certificate_progress['Green Novice']['earned']:
            st.session_state.certificate_progress['Green Novice']['earned'] = True
            st.session_state.certificate_progress['Green Novice']['progress'] = 1
        
        if total_emissions/1000 < 4.79:  # Below global average
            st.session_state.certificate_progress['Eco Warrior']['earned'] = True
            st.session_state.certificate_progress['Eco Warrior']['progress'] = 1
        
        if total_emissions/1000 < 1.9:  # Below India average
            st.session_state.certificate_progress['Climate Champion']['earned'] = True
            st.session_state.certificate_progress['Climate Champion']['progress'] = 1
        
        if total_emissions/1000 < 1.0:  # Very low emissions
            st.session_state.certificate_progress['Earth Guardian']['earned'] = True
            st.session_state.certificate_progress['Earth Guardian']['progress'] = 1
        
        # Save progress after each calculation
        save_progress()
        
        # Create data for visualization
        emissions_data = {
            'Category': ['Transportation', 'Energy', 'Waste', 'Diet'],
            'Emissions (t CO2)': [
                st.session_state.transport_emissions/1000,
                st.session_state.energy_emissions/1000,
                st.session_state.waste_emissions/1000,
                st.session_state.diet_emissions/1000
            ]
        }
        st.session_state.emissions_data = pd.DataFrame(emissions_data)
        
        st.rerun()

    # Display results if available
    if st.session_state.calculation_results is not None:
        st.markdown('<h2 class="stHeader">📊 Your Carbon Footprint Results</h2>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<h3 class="stSubheader">Carbon Emissions by Category</h3>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="stMarkdown">
                    <p>🚗 Transportation: {st.session_state.calculation_results['transport']/1000:.2f} t CO2 per year</p>
                    <p>💡 Energy: {st.session_state.calculation_results['energy']/1000:.2f} t CO2 per year</p>
                    <p>🍽 Diet: {st.session_state.calculation_results['diet']/1000:.2f} t CO2 per year</p>
                    <p>🗑 Waste: {st.session_state.calculation_results['waste']/1000:.2f} t CO2 per year</p>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown('<h3 class="stSubheader">Total Carbon Footprint</h3>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="stMarkdown">
                    <p>🌍 Your total carbon footprint is: {st.session_state.calculation_results['total']/1000:.2f} t CO2 per year</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Add comparison with global average
            global_average = 4.79  # Global average CO2 emissions per capita in 2021 (in tonnes)
            india_average = 1.9    # India's average CO2 emissions per capita in 2021 (in tonnes)
            
            st.markdown('<h3 class="stSubheader">📈 Comparison with Averages</h3>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="stMarkdown">
                    <p>🌐 Global Average: {global_average} t CO2 per capita</p>
                    <p>🇮🇳 India Average: {india_average} t CO2 per capita</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Calculate percentage of global average
            percentage_of_global = (st.session_state.calculation_results['total']/1000 / global_average) * 100
            st.markdown(f"""
                <div class="stMarkdown">
                    <p>Your emissions are {percentage_of_global:.1f}% of the global average</p>
                </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown('<h2 class="stHeader">📈 Carbon Footprint Dashboard</h2>', unsafe_allow_html=True)
    
    # Create three columns for key metrics
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
            st.markdown("""
            <div class="metric-card">
                <h3>Total Emissions</h3>
                <div class="metric-value">
                    {:.1f} t CO2/year
                    </div>
                <div class="metric-comparison">
                    {:.1f}% of Global Average
                    </div>
                    </div>
        """.format(
            st.session_state.calculation_results['total']/1000 if st.session_state.calculation_results else 0,
            (st.session_state.calculation_results['total']/1000 / 4.79 * 100) if st.session_state.calculation_results else 0
        ), unsafe_allow_html=True)

    with metric_col2:
        st.markdown("""
            <div class="metric-card">
                <h3>Highest Category</h3>
                <div class="metric-value">
                    {}
                        </div>
                <div class="metric-comparison">
                    {:.1f}% of Total
                        </div>
                    </div>
        """.format(
            max(
                ('Transportation', st.session_state.transport_emissions),
                ('Energy', st.session_state.energy_emissions),
                ('Waste', st.session_state.waste_emissions),
                ('Diet', st.session_state.diet_emissions),
                key=lambda x: x[1]
            )[0] if st.session_state.calculation_results else 'N/A',
            max(
                st.session_state.transport_emissions,
                st.session_state.energy_emissions,
                st.session_state.waste_emissions,
                st.session_state.diet_emissions
            ) / st.session_state.calculation_results['total'] * 100 if st.session_state.calculation_results else 0
        ), unsafe_allow_html=True)

    with metric_col3:
        st.markdown("""
            <div class="metric-card">
                <h3>Carbon Status</h3>
                <div class="metric-value status-{}">
                    {}
                        </div>
                <div class="metric-comparison">
                    Based on Global Average
                        </div>
                    </div>
        """.format(
            'good' if st.session_state.calculation_results and st.session_state.calculation_results['total']/1000 < 4.79 else 'bad',
            'Below Average' if st.session_state.calculation_results and st.session_state.calculation_results['total']/1000 < 4.79 else 'Above Average'
        ), unsafe_allow_html=True)

    # Add trends section
    st.markdown('<h3 class="stSubheader">Emission Trends</h3>', unsafe_allow_html=True)
    
    # Create three columns with adjusted widths
    chart_col1, chart_col2, chart_col3 = st.columns([1.2, 1.2, 1])
    
    with chart_col1:
        if st.session_state.emissions_data is not None:
            # Category breakdown bar chart
            fig1 = px.bar(
                st.session_state.emissions_data,
                x='Category',
                y='Emissions (t CO2)',
                title='Emissions by Category',
                color='Category',
                color_discrete_sequence=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f']
            )
            fig1.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                title_font_size=16,
                height=300,  # Reduced height
                margin=dict(t=30, b=20, l=20, r=20),
                showlegend=False,
                xaxis=dict(title=''),
                yaxis=dict(title='t CO2/year')
            )
            st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        if st.session_state.emissions_data is not None:
            # Pie chart with adjusted layout
            fig_pie = px.pie(
                st.session_state.emissions_data, 
                values='Emissions (t CO2)', 
                names='Category',
                title='Distribution of Emissions',
                color_discrete_sequence=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f']
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                title_font_size=16,
                height=300,  # Reduced height
                margin=dict(t=30, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(color='white', size=11)
                )
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with chart_col3:
        if st.session_state.emissions_data is not None:
            # Comparison with benchmarks
            comparison_data = pd.DataFrame({
                'Source': ['Your Emissions', 'Global Average', 'India Average'],
                'Emissions': [
                    st.session_state.calculation_results['total']/1000,
                    4.79,  # Global average
                    1.9    # India average
                ]
            })
            fig2 = px.bar(
                comparison_data,
                x='Source',
                y='Emissions',
                title='Emissions Comparison',
                color='Source',
                color_discrete_sequence=['#76c7c0', '#666666', '#888888']
            )
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                title_font_size=16,
                height=300,  # Reduced height
                margin=dict(t=30, b=20, l=20, r=20),
                showlegend=False,
                xaxis=dict(title='', tickangle=45),
                yaxis=dict(title='t CO2/year')
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Add recommendations section
    st.markdown('<h3 class="stSubheader">Personalized Recommendations</h3>', unsafe_allow_html=True)
    
    if st.session_state.calculation_results:
        # Identify areas for improvement
        recommendations = []
        if st.session_state.transport_emissions/1000 > 2:
            recommendations.append({
                'category': 'Transportation',
                'icon': '🚗',
                'tip': 'Consider using public transport or carpooling to reduce emissions.'
            })
        if st.session_state.energy_emissions/1000 > 1.5:
            recommendations.append({
                'category': 'Energy',
                'icon': '💡',
                'tip': 'Switch to energy-efficient appliances and LED lighting.'
            })
        if st.session_state.waste_emissions/1000 > 0.5:
            recommendations.append({
                'category': 'Waste',
                'icon': '🗑️',
                'tip': 'Increase recycling and composting efforts.'
            })
        if st.session_state.diet_emissions/1000 > 1:
            recommendations.append({
                'category': 'Diet',
                'icon': '🍽️',
                'tip': 'Consider reducing meat consumption and choosing local produce.'
            })

        # Display recommendations
        for rec in recommendations:
                st.markdown(f"""
                <div class="recommendation-card">
                    <div class="rec-icon">{rec['icon']}</div>
                    <div class="rec-content">
                        <h4>{rec['category']}</h4>
                        <p>{rec['tip']}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
with tab3:
    st.markdown('<h2 class="stHeader">🌱 Carbon Offset Options</h2>', unsafe_allow_html=True)
    
    if st.session_state.calculation_results:
        total_emissions = st.session_state.calculation_results["total"]
        st.markdown(f'<h3 class="stSubheader">Your Annual Carbon Footprint: {total_emissions:.2f} kg CO2e</h3>', unsafe_allow_html=True)
        
        # Offset options
        st.markdown('<h3 class="stSubheader">Offset Your Carbon Footprint</h3>', unsafe_allow_html=True)
        
        # Tree planting option
        trees_needed = total_emissions / 20  # Assuming each tree absorbs 20 kg CO2 per year
        st.markdown(f"""
        <div class="stMarkdown">
            <h4>🌳 Option 1: Plant Trees</h4>
            <p>• Number of trees needed: {trees_needed:.0f}</p>
            <p>• Estimated cost: ₹{trees_needed * 100:.2f} (₹100 per tree)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Renewable energy option
        solar_panels = total_emissions / 500  # Assuming each panel reduces 500 kg CO2 per year
        st.markdown(f"""
        <div class="stMarkdown">
            <h4>☀️ Option 2: Install Solar Panels</h4>
            <p>• Number of panels needed: {solar_panels:.0f}</p>
            <p>• Estimated cost: ₹{solar_panels * 15000:.2f} (₹15,000 per panel)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Carbon credits option
        credits_needed = total_emissions / 1000  # 1 credit = 1000 kg CO2
        st.markdown(f"""
        <div class="stMarkdown">
            <h4>💳 Option 3: Purchase Carbon Credits</h4>
            <p>• Number of credits needed: {credits_needed:.2f}</p>
            <p>• Estimated cost: ₹{credits_needed * 1000:.2f} (₹1,000 per credit)</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Please calculate your carbon footprint first in the Calculate tab.")

with tab4:
    st.markdown('<h2 class="stHeader">💬 Chat with Eco Assistant</h2>', unsafe_allow_html=True)
    
    # Initialize chat history if not exists
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'message_counter' not in st.session_state:
        st.session_state.message_counter = 0
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.container():
            message_class = 'user' if message['is_user'] else 'bot'
            st.markdown(f"""
                <div class="stMarkdown">
                    <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                        <span style='font-size: 1.2rem; margin-right: 0.5rem;'>
                            {'👤' if message['is_user'] else '🌱'}
                        </span>
                        <strong style='color: {'#4CAF50' if message['is_user'] else '#2196F3'};'>
                            {'You' if message['is_user'] else 'Assistant'}
                        </strong>
                    </div>
                    <div style='padding: 1rem; background-color: #2D2D2D; border-radius: 10px;'>
                        {message['content']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Display suggestions if no chat history
    if not st.session_state.chat_history:
        st.subheader("Suggested Questions:")
        suggestions = chatbot.get_suggestions()
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                    st.session_state.chat_history.append({
                        'is_user': True,
                        'content': suggestion
                    })
                    response = chatbot.get_response(suggestion)
                    st.session_state.chat_history.append({
                        'is_user': False,
                        'content': response
                    })
                    st.session_state.message_counter += 1
                    st.rerun()
    
    # Add a clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.message_counter = 0
        st.rerun()
    
    # Chat input
    user_input = st.text_input(
        "Ask a question:",
        placeholder="Type your question here..."
    )
    
    # Handle user input
    if user_input:
        if st.session_state.message_counter < 10:  # Limit the number of messages
            # Add user message
            st.session_state.chat_history.append({
                'is_user': True,
                'content': user_input
            })
            
            # Get and add bot response
            response = chatbot.get_response(user_input)
            st.session_state.chat_history.append({
                'is_user': False,
                'content': response
            })
            
            # Increment message counter
            st.session_state.message_counter += 1
            
            # Rerun to update the display
            st.rerun()
        else:
            st.warning("You've reached the maximum number of messages. Please clear the chat to continue.")

with tab5:
    st.markdown('<h2 class="stHeader">🎮 Carbon Footprint Challenges</h2>', unsafe_allow_html=True)
    
    # Create columns for the reset buttons at the top
    reset_col1, reset_col2, reset_col3 = st.columns([1, 1, 1])
    with reset_col1:
        if st.button("🔄 Reset Weekly Challenge", key="reset_weekly"):
            st.session_state.weekly_challenge['progress'] = 0
            save_progress()
            st.rerun()
    
    with reset_col2:
        if st.button("🔄 Reset All Progress", key="reset_progress"):
            st.session_state.certificate_progress = {
                'Green Novice': {'earned': False, 'progress': 0},
                'Eco Warrior': {'earned': False, 'progress': 0},
                'Climate Champion': {'earned': False, 'progress': 0},
                'Earth Guardian': {'earned': False, 'progress': 0}
            }
            st.session_state.challenges = []
            st.session_state.achievements = []
            st.session_state.carbon_journey = []
            st.session_state.weekly_challenge['progress'] = 0
            save_progress()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h3 class="stSubheader">Weekly Challenge</h3>', unsafe_allow_html=True)
    
    if st.button("Mark Day as Complete", key="challenge_button"):
        st.session_state.weekly_challenge['progress'] += 1
        if st.session_state.weekly_challenge['progress'] >= st.session_state.weekly_challenge['days']:
            st.session_state.certificate_progress['Eco Warrior']['progress'] += 1
            if st.session_state.certificate_progress['Eco Warrior']['progress'] >= 3:
                st.session_state.certificate_progress['Eco Warrior']['earned'] = True
        save_progress()
        st.rerun()

    st.markdown(f"""
<div class="stCard">
    <h4>{st.session_state.weekly_challenge['title']}</h4>
    <p>{st.session_state.weekly_challenge['description']}</p>
    <p>Potential carbon saving: {st.session_state.weekly_challenge['carbon_saving']}</p>
    <div class="progress-bar">
        <div class="progress" style="width: {(st.session_state.weekly_challenge['progress']/st.session_state.weekly_challenge['days'])*100}%"></div>
    </div>
    <p>Days completed: {st.session_state.weekly_challenge['progress']}/{st.session_state.weekly_challenge['days']}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown('<h3 class="stSubheader">🏆 Your Achievements</h3>', unsafe_allow_html=True)
    achievements = [
        {'name': '🌱 Green Starter', 'description': 'First carbon footprint calculation', 'icon': '🌱'},
        {'name': '🚶‍♂️ Eco Walker', 'description': 'Walked/cycled 10km', 'icon': '🚶‍♂️'},
        {'name': '💡 Energy Saver', 'description': 'Reduced energy consumption by 20%', 'icon': '💡'},
        {'name': '♻️ Recycling Master', 'description': 'Properly sorted waste for 1 month', 'icon': '♻️'}
    ]
    
    cols = st.columns(4)
    for i, achievement in enumerate(achievements):
        with cols[i]:
            st.markdown(f"""
<div class="achievement-card">
    <div class="achievement-icon">{achievement['icon']}</div>
    <h4>{achievement['name']}</h4>
    <p>{achievement['description']}</p>
</div>
""", unsafe_allow_html=True)

    # Certificates Section
    st.markdown('<h3 class="stSubheader">🏆 Certificates</h3>', unsafe_allow_html=True)
    
    # Create a grid layout for certificates
    cert_col1, cert_col2 = st.columns(2)
    
    # Certificate definitions
    certificates = {
        'Green Novice': {
            'icon': '🌱',
            'description': 'Awarded for taking the first step in calculating your carbon footprint',
            'requirements': ['Complete your first carbon footprint calculation'],
            'color': '#4CAF50'
        },
        'Eco Warrior': {
            'icon': '⚔️',
            'description': 'Keep emissions below global average or complete weekly challenges',
            'requirements': ['Emissions below 4.79 tonnes CO2/year', 'OR Complete 7 daily challenges'],
            'color': '#2196F3'
        },
        'Climate Champion': {
            'icon': '🏆',
            'description': 'Maintain emissions below India\'s average',
            'requirements': ['Emissions below 1.9 tonnes CO2/year'],
            'color': '#FFC107'
        },
        'Earth Guardian': {
            'icon': '🌍',
            'description': 'Achieve extremely low carbon emissions',
            'requirements': ['Emissions below 1.0 tonnes CO2/year'],
            'color': '#9C27B0'
        }
    }
    
    # Display certificates in grid
    for i, (cert_name, cert_data) in enumerate(certificates.items()):
        with cert_col1 if i % 2 == 0 else cert_col2:
            progress = st.session_state.certificate_progress[cert_name]
            is_earned = progress['earned']
            
            st.markdown(f"""
            <div class="certificate-card" style="
                background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
                border: 2px solid {cert_data['color']};
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                text-align: center;
            ">
                <div style="font-size: 3rem; margin-bottom: 10px;">{cert_data['icon']}</div>
                <h3 style="color: {cert_data['color']}; margin-bottom: 10px;">{cert_name}</h3>
                <p style="color: #e0e0e0; margin-bottom: 15px;">{cert_data['description']}</p>
                <div style="
                    background: rgba(0,0,0,0.2);
                    border-radius: 10px;
                    padding: 10px;
                    margin-bottom: 15px;
                ">
                    <div class="progress-bar" style="
                        background: rgba(255,255,255,0.1);
                        border-radius: 5px;
                        height: 10px;
                        overflow: hidden;
                    ">
                        <div style="
                            width: {100 if is_earned else 0}%;
                            height: 100%;
                            background: {cert_data['color']};
                            transition: width 0.5s ease;
                        "></div>
                    </div>
                    <p style="
                        color: {cert_data['color']};
                        margin-top: 5px;
                        font-size: 0.9rem;
                    ">{100 if is_earned else 0}% Complete</p>
                </div>
                <div style="
                    background: {cert_data['color'] if is_earned else 'rgba(255,255,255,0.1)'};
                    color: {'white' if is_earned else '#888'};
                    padding: 8px 15px;
                    border-radius: 20px;
                    display: inline-block;
                    font-size: 0.9rem;
                    margin-top: 10px;
                ">
                    {f'✨ {cert_name} Earned!' if is_earned else '🔒 Complete requirements to unlock'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if is_earned:
                if st.button(f"View Certificate", key=f"view_{cert_name}"):
                    st.session_state.show_certificate = {
                        'name': cert_name,
                        'icon': cert_data['icon'],
                        'description': cert_data['description'],
                        'requirements': cert_data['requirements']
                    }
                    st.rerun()

# Add interactive tips section
with st.expander("💡 Interactive Tips"):
    st.markdown('<h3 class="stSubheader">Tips to Reduce Your Carbon Footprint</h3>', unsafe_allow_html=True)
    tip_categories = {
        "Transportation": [
            "Use public transport or carpool",
            "Walk or cycle for short distances",
            "Maintain your vehicle properly",
            "Consider electric or hybrid vehicles"
        ],
        "Energy": [
            "Switch to LED bulbs",
            "Use energy-efficient appliances",
            "Install solar panels",
            "Properly insulate your home"
        ],
        "Waste": [
            "Reduce, reuse, and recycle",
            "Compost organic waste",
            "Avoid single-use plastics",
            "Buy products with minimal packaging"
        ],
        "Diet": [
            "Reduce meat consumption",
            "Buy local and seasonal produce",
            "Minimize food waste",
            "Grow your own vegetables"
        ]
    }
    
    selected_category = st.selectbox("Select a category:", list(tip_categories.keys()))
    for tip in tip_categories[selected_category]:
        st.checkbox(tip)

# Add certificate modal
if st.session_state.show_certificate:
    cert = st.session_state.show_certificate
    st.markdown(f"""
        <div class="certificate-modal" style="display: flex;">
            <div class="certificate-content">
                <div class="certificate-close" onclick="document.querySelector('.certificate-modal').style.display='none'">×</div>
                <div class="certificate-border">
                    <div class="certificate-icon">{cert['icon']}</div>
                    <h1 class="certificate-title">Certificate of Achievement</h1>
                    <h2 class="certificate-name">{cert['name']}</h2>
                    <p class="certificate-description">{cert['description']}</p>
                    <div class="certificate-requirements">
                        <h3 style="color: white; margin-bottom: 10px;">Requirements Met:</h3>
                        <ul style="list-style-type: none; padding-left: 0; color: white;">
                            {''.join([f'<li>✓ {req}</li>' for req in cert['requirements']])}
                        </ul>
                    </div>
                    <p class="certificate-date">Awarded on {datetime.now().strftime('%B %d, %Y')}</p>
                    <div class="certificate-seal">🌍</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Add JavaScript to handle modal closing
    st.markdown("""
        <script>
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('certificate-modal')) {
                e.target.style.display = 'none';
            }
        });
        </script>
    """, unsafe_allow_html=True)
