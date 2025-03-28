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
        background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%);
        min-height: 100vh;
        color: #2e4600;
        font-family: 'Arial', sans-serif;
        font-size: 1.1rem;
        padding-top: 0;
    }
    
    /* Add a subtle leaf pattern overlay */
    .stApp::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('https://www.transparenttextures.com/patterns/leaf.png');
        opacity: 0.1;
        pointer-events: none;
    }
    
    /* Title styling */
    .big-font {
        font-size: 2.5rem !important;
        font-weight: 800;
        color: #2e4600;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 10px 20px;
        margin: 0 5px;
        color: #2e4600;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.4) !important;
        color: #2e4600 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        font-weight: 700;
    }
    
    /* Remove extra padding from main container */
    .main .block-container {
        padding-top: 0;
        max-width: 100%;
    }
    
    /* Adjust header spacing */
    .stHeader {
        margin-bottom: 1rem;
        font-size: 2rem;
    }
    
    /* Adjust subheader spacing */
    .stSubheader {
        margin-bottom: 0.8rem;
        font-size: 1.5rem;
    }
    
    /* Adjust card spacing */
    .stCard {
        margin: 8px 0;
        padding: 15px;
    }
    
    /* Adjust expander spacing */
    .streamlit-expanderHeader {
        padding: 0.3rem 0.8rem;
    }
    
    /* Adjust container spacing */
    .stContainer {
        margin-bottom: 0.8rem;
    }
    
    /* Adjust column spacing */
    .row-widget.stHorizontal > div {
        margin-bottom: 0.8rem;
    }
    
    /* Button styling */
    .stButton>button {
        background: #56ab2f;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.2s ease;
        text-transform: none;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stButton>button:hover {
        background: #3b7a1f;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 12px;
        padding: 15px 20px;
        background: rgba(255, 255, 255, 0.2);
        color: #2e4600;
        border: 2px solid rgba(255, 255, 255, 0.4);
        font-size: 1.1rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #56ab2f;
        box-shadow: 0 0 0 3px rgba(86, 171, 47, 0.2);
    }
    
    /* Chat message styling */
    .chat-message {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        color: #2e4600;
        font-size: 1.1rem;
    }
    
    /* Plotly chart container */
    .js-plotly-plot {
        background: rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border: 2px solid rgba(255, 255, 255, 0.4);
    }
    
    /* Remove unwanted boxes */
    .stMarkdown {
        background: none;
        border: none;
        box-shadow: none;
        padding: 0;
        margin: 0;
        color: #ffffff;
        font-size: 1.1rem;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(86, 171, 47, 0.4);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(86, 171, 47, 0.6);
    }

    /* Select box styling */
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 15px 20px;
        color: #ffffff;
        font-size: 1.1rem;
    }

    /* Slider styling */
    .stSlider>div>div>div {
        background: #4a90e2;
    }

    /* Info message styling */
    .stInfo {
        background: rgba(33, 150, 243, 0.1);
        border: 2px solid rgba(33, 150, 243, 0.3);
        border-radius: 12px;
        padding: 20px;
        color: #64b5f6;
        font-size: 1.1rem;
    }

    /* Warning message styling */
    .stWarning {
        background: rgba(255, 152, 0, 0.1);
        border: 2px solid rgba(255, 152, 0, 0.3);
        border-radius: 12px;
        padding: 20px;
        color: #ffd54f;
        font-size: 1.1rem;
    }

    /* Success message styling */
    .stSuccess {
        background: rgba(76, 175, 80, 0.1);
        border: 2px solid rgba(76, 175, 80, 0.3);
        border-radius: 12px;
        padding: 20px;
        color: #81c784;
        font-size: 1.1rem;
    }

    /* Error message styling */
    .stError {
        background: rgba(244, 67, 54, 0.1);
        border: 2px solid rgba(244, 67, 54, 0.3);
        border-radius: 12px;
        padding: 20px;
        color: #e57373;
        font-size: 1.1rem;
    }

    /* Label styling */
    .stLabel {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
    }

    /* Checkbox styling */
    .stCheckbox>label {
        font-size: 1.1rem;
        color: #ffffff;
    }

    /* Achievement card styling */
    .achievement-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 2px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease;
    }
    
    .achievement-card:hover {
        transform: translateY(-5px);
    }
    
    .achievement-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    
    /* Progress bar styling */
    .progress-bar {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 20px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress {
        background: #4a90e2;
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Challenge card styling */
    .challenge-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
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
        color: #4a90e2;
    }

    /* Total emissions */
    .total-emissions {
        background: rgba(86, 171, 47, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        border: 2px solid rgba(86, 171, 47, 0.4);
    }
    
    .total-emissions h3 {
        margin: 0;
        color: #2e4600;
        font-size: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize services
chatbot = CarbonFootprintChatbot()

# Define emission factors (kg CO2e per unit)
EMISSION_FACTORS = {
    "India": {
        # Transportation (kg CO2e per km)
        "Car": 0.16422,
        "Bus": 0.56703,
        "Train": 0.05,
        "Motorcycle": 0.02779,
        "Airplane": 0.25,
        
        # Energy (kg CO2e per kWh)
        "Electricity": 0.82,
        "LPG": 2.98,
        "CNG": 2.2,
        
        # Diet (kg CO2e per meal)
        "Vegan": 1.5,
        "Vegetarian": 2.5,
        "Non-vegetarian": 3.5,
        
        # Waste (kg CO2e per kg)
        "Organic": 0.5,
        "Plastic": 6.0,
        "Paper": 1.2,
        "Metal": 1.5
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

# Main title with custom class
st.markdown('<h1 class="big-font">🌍 Carbon Footprint Calculator</h1>', unsafe_allow_html=True)

# Create tabs for different sections with reduced spacing
tab1, tab2, tab3, tab4 = st.tabs(["📊 Calculate", "🌱 Offset", "💬 Chat", "🎮 Challenges"])

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
            background: rgba(86, 171, 47, 0.2);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            border: 2px solid rgba(86, 171, 47, 0.4);
        }
        
        .total-emissions h3 {
            margin: 0;
            color: #2e4600;
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
        
        # Award Green Novice certificate for first calculation
        if not st.session_state.certificate_progress['Green Novice']['earned']:
            st.session_state.certificate_progress['Green Novice']['earned'] = True
            st.session_state.certificate_progress['Green Novice']['progress'] = 1
        
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

        # Create and display pie chart
        fig = px.pie(
            st.session_state.emissions_data, 
            values='Emissions (t CO2)', 
            names='Category',
            title='Distribution of Your Carbon Emissions',
            color_discrete_sequence=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14),
            title_font_color='white',
            title_font_size=24,
            height=600,  # Increased height
            width=800,   # Increased width
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color='white', size=14)
            ),
            margin=dict(t=50, b=50, l=50, r=50)
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
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

with tab3:
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

with tab4:
    st.markdown('<h2 class="stHeader">🎮 Carbon Footprint Challenges</h2>', unsafe_allow_html=True)
    
    # Weekly Challenge Section
    st.markdown('<h3 class="stSubheader">Weekly Challenge</h3>', unsafe_allow_html=True)
    weekly_challenge = {
        'title': '🚶‍♂️ Walk or Cycle to Work',
        'description': 'Replace your usual commute with walking or cycling for at least 3 days this week.',
        'carbon_saving': '2.5 kg CO2',
        'progress': 0,
        'days': 7
    }
    
    # Add challenge completion button
    if st.button("Mark Day as Complete", key="challenge_button"):
        weekly_challenge['progress'] += 1
        if weekly_challenge['progress'] >= weekly_challenge['days']:
            st.session_state.certificate_progress['Eco Warrior']['progress'] += 1
            if st.session_state.certificate_progress['Eco Warrior']['progress'] >= 3:
                st.session_state.certificate_progress['Eco Warrior']['earned'] = True
    
    st.markdown(f"""
        <div class="stCard">
            <h4>{weekly_challenge['title']}</h4>
            <p>{weekly_challenge['description']}</p>
            <p>Potential carbon saving: {weekly_challenge['carbon_saving']}</p>
            <div class="progress-bar">
                <div class="progress" style="width: {(weekly_challenge['progress']/weekly_challenge['days'])*100}%"></div>
            </div>
            <p>Days completed: {weekly_challenge['progress']}/{weekly_challenge['days']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Achievement Badges
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
    st.markdown('<h3 class="stSubheader">📜 Your Certificates</h3>', unsafe_allow_html=True)
    
    certificates = [
        {
            'name': '🌱 Green Novice',
            'description': 'Completed first carbon footprint calculation',
            'requirements': ['First calculation'],
            'icon': '🌱',
            'color': '#4CAF50',
            'progress': st.session_state.certificate_progress['Green Novice']
        },
        {
            'name': '🌿 Eco Warrior',
            'description': 'Reduced carbon footprint by 20%',
            'requirements': ['20% reduction'],
            'icon': '🌿',
            'color': '#8BC34A',
            'progress': st.session_state.certificate_progress['Eco Warrior']
        },
        {
            'name': '🌳 Climate Champion',
            'description': 'Maintained low carbon footprint for 3 months',
            'requirements': ['3 months low footprint'],
            'icon': '🌳',
            'color': '#2196F3',
            'progress': st.session_state.certificate_progress['Climate Champion']
        },
        {
            'name': '🌍 Earth Guardian',
            'description': 'Achieved carbon neutrality',
            'requirements': ['Carbon neutral'],
            'icon': '🌍',
            'color': '#9C27B0',
            'progress': st.session_state.certificate_progress['Earth Guardian']
        }
    ]
    
    # Display certificates in a grid
    cert_cols = st.columns(2)
    for i, cert in enumerate(certificates):
        with cert_cols[i % 2]:
            progress = cert['progress']
            earned_class = 'earned' if progress['earned'] else ''
            st.markdown(f"""
                <div class="certificate-card {earned_class}" style="background: {cert['color']}20; border: 2px solid {cert['color']};">
                    <div class="certificate-icon" style="font-size: 3rem; margin-bottom: 1rem;">{cert['icon']}</div>
                    <h4 style="color: {cert['color']}; margin-bottom: 0.5rem;">{cert['name']}</h4>
                    <p style="margin-bottom: 1rem;">{cert['description']}</p>
                    <div class="certificate-requirements">
                        <p style="font-size: 0.9rem; color: #888;">Requirements:</p>
                        <ul style="list-style-type: none; padding-left: 0;">
                            {''.join([f'<li>• {req}</li>' for req in cert['requirements']])}
                        </ul>
                        <div class="progress-bar" style="margin-top: 1rem;">
                            <div class="progress" style="width: {progress['progress']*100}%; background: {cert['color']};"></div>
                        </div>
                        <p style="font-size: 0.9rem; color: #888; margin-top: 0.5rem;">
                            Progress: {progress['progress']*100}%
                        </p>
                    </div>
                    <button class="certificate-button" style="
                        background: {cert['color']};
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 20px;
                        margin-top: 1rem;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        opacity: {1 if progress['earned'] else 0.5};
                    ">{'View Certificate' if progress['earned'] else 'Locked'}</button>
                </div>
            """, unsafe_allow_html=True)
    
    # Add CSS for certificates
    st.markdown("""
        <style>
        .certificate-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .certificate-card.earned {
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
        }
        
        .certificate-card:hover {
            transform: translateY(-5px);
        }
        
        .certificate-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .certificate-button:hover {
            opacity: 0.9;
            transform: scale(1.05);
        }
        
        .certificate-requirements {
            text-align: left;
            margin: 1rem 0;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

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