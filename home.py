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
from location_services import LocationServices

# Set wide layout and page name (must be first Streamlit command)
st.set_page_config(layout="wide", page_title="Carbon Calculator")

# Add custom CSS for background and styling
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        background-image: 
            linear-gradient(135deg, #000000 0%, #1a1a1a 100%),
            radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
        background-size: 100% 100%, 30px 30px;
        min-height: 100vh;
        color: #ffffff;
        position: relative;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            linear-gradient(45deg, transparent 48%, rgba(255, 255, 255, 0.03) 50%, transparent 52%),
            linear-gradient(-45deg, transparent 48%, rgba(255, 255, 255, 0.03) 50%, transparent 52%);
        background-size: 60px 60px;
        pointer-events: none;
        z-index: 0;
    }
    
    /* Title styling */
    .big-font {
        font-size: 3.5rem !important;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        letter-spacing: 1px;
        position: relative;
        z-index: 1;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
        position: relative;
        z-index: 1;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px 30px;
        margin: 0 5px;
        transition: all 0.3s ease;
        color: #ffffff;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        z-index: 1;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transform: translateY(-2px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Card styling */
    .stMarkdown {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        position: relative;
        z-index: 1;
    }
    
    /* Header styling */
    .stHeader {
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        letter-spacing: 0.5px;
        position: relative;
        z-index: 1;
    }
    
    /* Subheader styling */
    .stSubheader {
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 1rem;
        letter-spacing: 0.3px;
        position: relative;
        z-index: 1;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        z-index: 1;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0083b0 0%, #00b4db 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Input styling */
    .stSelectbox, .stSlider {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 1rem;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        z-index: 1;
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.2) 0%, rgba(40, 167, 69, 0.1) 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid rgba(40, 167, 69, 0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    /* Info message styling */
    .stInfo {
        background: linear-gradient(135deg, rgba(23, 162, 184, 0.2) 0%, rgba(23, 162, 184, 0.1) 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid rgba(23, 162, 184, 0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    /* Plotly chart container */
    .js-plotly-plot {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        z-index: 1;
    }
    
    /* Chat input styling */
    .stTextInput>div>div>input {
        border-radius: 30px;
        padding: 15px 25px;
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 1.1rem;
        position: relative;
        z-index: 1;
    }
    
    /* Chat message styling */
    .chat-message {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        border-radius: 20px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize services
chatbot = CarbonFootprintChatbot()
location_services = LocationServices()

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

# Main title with custom class
st.markdown('<h1 class="big-font">🌍 Carbon Footprint Calculator</h1>', unsafe_allow_html=True)

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Calculate", "🌱 Offset", "💬 Chat"])

with tab1:
    # Main calculation section
    st.markdown('<h2 class="stHeader">Calculate Your Carbon Footprint</h2>', unsafe_allow_html=True)
    
    # Create two columns for inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="stSubheader">🚗 Transportation</h3>', unsafe_allow_html=True)
        transport_type = st.selectbox(
            "Select your primary mode of transport",
            ["Car", "Bus", "Train", "Motorcycle", "Airplane"]
        )
        distance = st.slider("Daily commute distance (km)", 0.0, 100.0, 10.0)
        if transport_type == "Airplane":
            flights = st.number_input("Number of flights per year", 0, 50, 0)
        
        st.markdown('<h3 class="stSubheader">💡 Energy</h3>', unsafe_allow_html=True)
        electricity = st.slider("Monthly electricity (kWh)", 0.0, 1000.0, 200.0)
        cooking_fuel = st.selectbox(
            "Select your cooking fuel",
            ["LPG", "CNG", "Electric"]
        )
        if cooking_fuel in ["LPG", "CNG"]:
            fuel_consumption = st.slider(f"Monthly {cooking_fuel} consumption (kg)", 0.0, 50.0, 10.0)
    
    with col2:
        st.markdown('<h3 class="stSubheader">🗑️ Waste</h3>', unsafe_allow_html=True)
        waste_types = {
            "Organic": st.slider("Weekly organic waste (kg)", 0.0, 20.0, 2.0),
            "Plastic": st.slider("Weekly plastic waste (kg)", 0.0, 10.0, 1.0),
            "Paper": st.slider("Weekly paper waste (kg)", 0.0, 10.0, 1.0),
            "Metal": st.slider("Weekly metal waste (kg)", 0.0, 5.0, 0.5)
        }
        
        st.markdown('<h3 class="stSubheader">🍽️ Diet</h3>', unsafe_allow_html=True)
        diet_type = st.selectbox(
            "Select your diet type",
            ["Vegan", "Vegetarian", "Non-vegetarian"]
        )
        meals_per_day = st.slider("Number of meals per day", 1, 5, 3)

    # Calculate button
    if st.button("Calculate Carbon Footprint"):
        # Calculate total emissions
        transport_emissions = distance * 365 * EMISSION_FACTORS["India"][transport_type]
        if transport_type == "Airplane":
            transport_emissions += flights * 1000 * EMISSION_FACTORS["India"]["Airplane"]
        
        energy_emissions = electricity * 12 * EMISSION_FACTORS["India"]["Electricity"]
        if cooking_fuel in ["LPG", "CNG"]:
            energy_emissions += fuel_consumption * 12 * EMISSION_FACTORS["India"][cooking_fuel]
        
        waste_emissions = sum(waste * 52 * EMISSION_FACTORS["India"][waste_type] 
                            for waste_type, waste in waste_types.items())
        
        diet_emissions = meals_per_day * 365 * EMISSION_FACTORS["India"][diet_type]
        
        total_emissions = transport_emissions + energy_emissions + waste_emissions + diet_emissions
        
        # Store results in session state
        st.session_state.calculation_results = {
            "total": total_emissions,
            "transport": transport_emissions,
            "energy": energy_emissions,
            "waste": waste_emissions,
            "diet": diet_emissions
        }
        
        # Create data for visualization (convert to tonnes)
        emissions_data = {
            'Category': ['Transportation', 'Energy', 'Waste', 'Diet'],
            'Emissions (t CO2)': [
                transport_emissions/1000, 
                energy_emissions/1000, 
                waste_emissions/1000, 
                diet_emissions/1000
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