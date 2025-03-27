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

# Main title
st.title("🌍 Carbon Footprint Calculator")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Calculate", "🌍 Air Quality", "💬 Chat"])

with tab1:
    # Main calculation section
    st.header("Calculate Your Carbon Footprint")
    
    # Create two columns for inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚗 Transportation")
        transport_type = st.selectbox(
            "Select your primary mode of transport",
            ["Car", "Bus", "Train", "Motorcycle", "Airplane"]
        )
        distance = st.slider("Daily commute distance (km)", 0.0, 100.0, 10.0)
        if transport_type == "Airplane":
            flights = st.number_input("Number of flights per year", 0, 50, 0)
        
        st.subheader("💡 Energy")
        electricity = st.slider("Monthly electricity (kWh)", 0.0, 1000.0, 200.0)
        cooking_fuel = st.selectbox(
            "Select your cooking fuel",
            ["LPG", "CNG", "Electric"]
        )
        if cooking_fuel in ["LPG", "CNG"]:
            fuel_consumption = st.slider(f"Monthly {cooking_fuel} consumption (kg)", 0.0, 50.0, 10.0)
    
    with col2:
        st.subheader("🗑️ Waste")
        waste_types = {
            "Organic": st.slider("Weekly organic waste (kg)", 0.0, 20.0, 2.0),
            "Plastic": st.slider("Weekly plastic waste (kg)", 0.0, 10.0, 1.0),
            "Paper": st.slider("Weekly paper waste (kg)", 0.0, 10.0, 1.0),
            "Metal": st.slider("Weekly metal waste (kg)", 0.0, 5.0, 0.5)
        }
        
        st.subheader("🍽️ Diet")
        diet_type = st.selectbox(
            "Select your diet type",
            ["Vegan", "Vegetarian", "Non-vegetarian"]
        )
        meals = st.number_input("Meals per day", 0, 6, 3)

    # Calculate button
    if st.button("Calculate My Carbon Footprint"):
        # Normalize inputs
        if distance > 0:
            distance = distance * 365  # Convert daily distance to yearly
        if electricity > 0:
            electricity = electricity * 12  # Convert monthly electricity to yearly
        if meals > 0:
            meals = meals * 365  # Convert daily meals to yearly
        for waste_type, amount in waste_types.items():
            if amount > 0:
                waste_types[waste_type] = amount * 52  # Convert weekly waste to yearly

        # Calculate carbon emissions
        # Transportation
        if transport_type == "Airplane":
            transportation_emissions = (EMISSION_FACTORS["India"]["Airplane"] * distance * flights)
        else:
            transportation_emissions = EMISSION_FACTORS["India"][transport_type] * distance

        # Energy
        electricity_emissions = EMISSION_FACTORS["India"]["Electricity"] * electricity
        if cooking_fuel in ["LPG", "CNG"]:
            cooking_emissions = EMISSION_FACTORS["India"][cooking_fuel] * fuel_consumption * 12
            electricity_emissions += cooking_emissions

        # Diet
        diet_emissions = EMISSION_FACTORS["India"][diet_type] * meals

        # Waste
        waste_emissions = sum(
            EMISSION_FACTORS["India"][waste_type] * amount
            for waste_type, amount in waste_types.items()
        )

        # Convert emissions to tonnes and round off to 2 decimal points
        transportation_emissions = round(transportation_emissions / 1000, 2)
        electricity_emissions = round(electricity_emissions / 1000, 2)
        diet_emissions = round(diet_emissions / 1000, 2)
        waste_emissions = round(waste_emissions / 1000, 2)

        # Calculate total emissions
        total_emissions = round(
            transportation_emissions + electricity_emissions + diet_emissions + waste_emissions, 2
        )

        # Store results
        st.session_state.calculation_results = {
            'transportation': transportation_emissions,
            'electricity': electricity_emissions,
            'diet': diet_emissions,
            'waste': waste_emissions,
            'total': total_emissions
        }
        
        # Create data for visualization
        emissions_data = {
            'Category': ['Transportation', 'Electricity', 'Diet', 'Waste'],
            'Emissions (tonnes CO2)': [transportation_emissions, electricity_emissions, diet_emissions, waste_emissions]
        }
        st.session_state.emissions_data = pd.DataFrame(emissions_data)
        
        st.rerun()

    # Display results if available
    if st.session_state.calculation_results is not None:
        st.header("📊 Your Carbon Footprint Results")

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Carbon Emissions by Category")
            st.info(f"🚗 Transportation: {st.session_state.calculation_results['transportation']} tonnes CO2 per year")
            st.info(f"💡 Electricity: {st.session_state.calculation_results['electricity']} tonnes CO2 per year")
            st.info(f"🍽 Diet: {st.session_state.calculation_results['diet']} tonnes CO2 per year")
            st.info(f"🗑 Waste: {st.session_state.calculation_results['waste']} tonnes CO2 per year")

        with col4:
            st.subheader("Total Carbon Footprint")
            st.success(f"🌍 Your total carbon footprint is: {st.session_state.calculation_results['total']} tonnes CO2 per year")
            
            # Add comparison with global average
            global_average = 4.79  # Global average CO2 emissions per capita in 2021
            india_average = 1.9    # India's average CO2 emissions per capita in 2021
            
            st.subheader("📈 Comparison with Averages")
            st.info(f"🌐 Global Average: {global_average} tonnes CO2 per capita")
            st.info(f"🇮🇳 India Average: {india_average} tonnes CO2 per capita")
            
            # Calculate percentage of global average
            percentage_of_global = (st.session_state.calculation_results['total'] / global_average) * 100
            st.warning(f"Your emissions are {percentage_of_global:.1f}% of the global average")

        # Create and display pie chart
        fig = px.pie(st.session_state.emissions_data, values='Emissions (tonnes CO2)', names='Category',
                    title='Distribution of Your Carbon Emissions')
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("🌍 Air Quality Check")
    
    # Get user's location
    col1, col2 = st.columns(2)
    
    with col1:
        latitude = st.number_input("Enter your latitude", -90.0, 90.0, 20.5937)
    
    with col2:
        longitude = st.number_input("Enter your longitude", -180.0, 180.0, 78.9629)
    
    if st.button("Check Air Quality"):
        # Get location details
        location = location_services.get_location_from_coordinates(latitude, longitude)
        if location:
            st.info(f"📍 Location: {location}")
        else:
            st.error("❌ Could not find location details. Please check the coordinates.")
        
        # Get air quality data
        air_quality_data = location_services.get_air_quality_data(latitude, longitude)
        
        if air_quality_data:
            # Create a weather app-like layout
            st.markdown("""
                <style>
                .weather-card {
                    background-color: #2D2D2D;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 10px 0;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                .aqi-value {
                    font-size: 3rem;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0;
                }
                .aqi-label {
                    font-size: 1.2rem;
                    text-align: center;
                    margin-bottom: 20px;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Display AQI prominently
            aqi_status, aqi_message = location_services.calculate_health_impact(air_quality_data['aqi'])
            aqi_color = {
                "Good": "#00C853",
                "Moderate": "#FFD600",
                "Unhealthy for Sensitive Groups": "#FF9800",
                "Unhealthy": "#F44336",
                "Very Unhealthy": "#9C27B0",
                "Hazardous": "#880E4F"
            }.get(aqi_status, "#FFFFFF")
            
            st.markdown(f"""
                <div class='weather-card'>
                    <div class='aqi-value' style='color: {aqi_color};'>
                        {air_quality_data['aqi']}
                    </div>
                    <div class='aqi-label' style='color: {aqi_color};'>
                        {aqi_status}
                    </div>
                    <div style='text-align: center; color: #B0BEC5;'>
                        {aqi_message}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Display air quality metrics in a grid
            st.subheader("📊 Air Quality Metrics")
            col3, col4, col5 = st.columns(3)
            
            with col3:
                st.markdown(f"""
                    <div class='weather-card'>
                        <h3 style='text-align: center; color: #4CAF50;'>PM2.5</h3>
                        <div style='text-align: center; font-size: 1.5rem;'>
                            {air_quality_data['pm25']} µg/m³
                        </div>
                        <div style='text-align: center; color: #B0BEC5;'>
                            Fine particulate matter
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class='weather-card'>
                        <h3 style='text-align: center; color: #2196F3;'>PM10</h3>
                        <div style='text-align: center; font-size: 1.5rem;'>
                            {air_quality_data['pm10']} µg/m³
                        </div>
                        <div style='text-align: center; color: #B0BEC5;'>
                            Coarse particulate matter
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                    <div class='weather-card'>
                        <h3 style='text-align: center; color: #FF9800;'>Temperature</h3>
                        <div style='text-align: center; font-size: 1.5rem;'>
                            {air_quality_data['temperature']}°C
                        </div>
                        <div style='text-align: center; color: #B0BEC5;'>
                            Current temperature
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Display weather conditions in a grid
            st.subheader("🌤️ Weather Conditions")
            col6, col7, col8 = st.columns(3)
            
            with col6:
                st.markdown(f"""
                    <div class='weather-card'>
                        <h3 style='text-align: center; color: #00BCD4;'>Humidity</h3>
                        <div style='text-align: center; font-size: 1.5rem;'>
                            {air_quality_data['humidity']}%
                        </div>
                        <div style='text-align: center; color: #B0BEC5;'>
                            Relative humidity
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col7:
                st.markdown(f"""
                    <div class='weather-card'>
                        <h3 style='text-align: center; color: #9E9E9E;'>Wind Speed</h3>
                        <div style='text-align: center; font-size: 1.5rem;'>
                            {air_quality_data['wind_speed']} m/s
                        </div>
                        <div style='text-align: center; color: #B0BEC5;'>
                            Current wind speed
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col8:
                st.markdown(f"""
                    <div class='weather-card'>
                        <h3 style='text-align: center; color: #795548;'>Location</h3>
                        <div style='text-align: center; font-size: 1.2rem;'>
                            {location}
                        </div>
                        <div style='text-align: center; color: #B0BEC5;'>
                            Current location
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ Could not fetch air quality data. Please check your API key and try again.")
            st.info("💡 Make sure you have set up your OpenAQ API key in the .env file.")

with tab3:
    st.header("💬 Chat with Eco Assistant")
    
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
                <div class='chat-message {message_class}'>
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