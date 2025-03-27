import streamlit as st
from typing import Dict, List

class CarbonFootprintChatbot:
    def __init__(self):
        self.responses = {
            'greeting': [
                "👋 Hello! I'm your Eco-Friendly Assistant. I can help you:\n\n"
                "1. 📊 Calculate your carbon footprint\n"
                "2. 🌱 Get personalized eco-tips\n"
                "3. 🚗 Learn about sustainable transportation\n"
                "4. 💡 Discover energy-saving solutions\n"
                "5. 🍽️ Explore sustainable diet options\n\n"
                "What would you like to know?"
            ],
            'carbon_footprint_definition': [
                "🌍 Understanding Your Carbon Footprint:\n\n"
                "Your carbon footprint is the total greenhouse gases (mainly CO2) you emit annually. Here's what contributes to it:\n\n"
                "1. 🚗 Transportation (25%)\n"
                "   • Cars, buses, flights\n"
                "   • Daily commute\n"
                "   • Travel choices\n\n"
                "2. 💡 Energy (30%)\n"
                "   • Electricity usage\n"
                "   • Heating/cooling\n"
                "   • Appliance efficiency\n\n"
                "3. 🍽️ Diet (20%)\n"
                "   • Food choices\n"
                "   • Meat consumption\n"
                "   • Food waste\n\n"
                "4. 🗑️ Waste (10%)\n"
                "   • Recycling habits\n"
                "   • Waste management\n"
                "   • Product choices\n\n"
                "5. 💧 Water (10%)\n"
                "   • Water usage\n"
                "   • Hot water heating\n"
                "   • Water conservation\n\n"
                "6. 🛍️ Shopping (5%)\n"
                "   • Consumer choices\n"
                "   • Product lifecycle\n"
                "   • Sustainable shopping\n\n"
                "📊 Current Averages:\n"
                "• Global: 4.79 tonnes CO2/person/year\n"
                "• India: 1.9 tonnes CO2/person/year\n\n"
                "Would you like to calculate your carbon footprint or learn more about any specific category?"
            ],
            'transportation': [
                "🚗 Sustainable Transportation Guide:\n\n"
                "1. 🚌 Public Transport Options:\n"
                "   • Bus: 0.1 kgCO2/km\n"
                "   • Train: 0.05 kgCO2/km\n"
                "   • Metro: 0.03 kgCO2/km\n\n"
                "2. 🚗 Private Vehicles:\n"
                "   • Car: 0.2 kgCO2/km\n"
                "   • Motorcycle: 0.1 kgCO2/km\n"
                "   • Electric Vehicle: 0.05 kgCO2/km\n\n"
                "3. ✈️ Air Travel:\n"
                "   • Domestic: 0.2 kgCO2/km\n"
                "   • International: 0.25 kgCO2/km\n\n"
                "🌱 Eco-Friendly Tips:\n"
                "1. Short-term actions:\n"
                "   • Use public transport\n"
                "   • Carpool with colleagues\n"
                "   • Walk or cycle for short distances\n\n"
                "2. Long-term actions:\n"
                "   • Switch to electric vehicles\n"
                "   • Move closer to work\n"
                "   • Work from home when possible\n\n"
                "Would you like to calculate your transportation emissions or get more specific tips?"
            ],
            'energy': [
                "💡 Energy Conservation Guide:\n\n"
                "1. 🏠 Home Energy:\n"
                "   • Grid power: 0.82 kgCO2/kWh\n"
                "   • Solar power: 0.05 kgCO2/kWh\n"
                "   • Wind power: 0.02 kgCO2/kWh\n\n"
                "2. 🔥 Cooking:\n"
                "   • LPG: 2.1 kgCO2/kg\n"
                "   • CNG: 2.2 kgCO2/kg\n"
                "   • Electric: 0.82 kgCO2/kWh\n\n"
                "🌱 Energy-Saving Tips:\n"
                "1. Lighting:\n"
                "   • Use LED bulbs (saves 80% energy)\n"
                "   • Use natural light when possible\n"
                "   • Install motion sensors\n\n"
                "2. Appliances:\n"
                "   • Choose 5-star rated appliances\n"
                "   • Regular maintenance\n"
                "   • Use power-saving mode\n\n"
                "3. Heating/Cooling:\n"
                "   • Set optimal temperature\n"
                "   • Use ceiling fans\n"
                "   • Insulate your home\n\n"
                "Would you like to calculate your energy emissions or get more specific tips?"
            ],
            'diet': [
                "🍽️ Sustainable Diet Guide:\n\n"
                "1. 🥬 Food Types:\n"
                "   • Vegan: 0.3 kgCO2/meal\n"
                "   • Vegetarian: 0.5 kgCO2/meal\n"
                "   • Non-vegetarian: 1.5 kgCO2/meal\n\n"
                "2. 🌾 Food Production:\n"
                "   • Local produce: Lower emissions\n"
                "   • Imported food: Higher emissions\n"
                "   • Organic farming: Lower emissions\n\n"
                "🌱 Sustainable Eating Tips:\n"
                "1. Food choices:\n"
                "   • Eat more plant-based foods\n"
                "   • Choose local produce\n"
                "   • Reduce processed foods\n\n"
                "2. Shopping habits:\n"
                "   • Buy in bulk\n"
                "   • Use reusable bags\n"
                "   • Plan meals to reduce waste\n\n"
                "3. Storage:\n"
                "   • Proper refrigeration\n"
                "   • Use airtight containers\n"
                "   • Regular cleaning\n\n"
                "Would you like to calculate your diet-related emissions or get more specific tips?"
            ],
            'waste': [
                "🗑️ Waste Management Guide:\n\n"
                "1. 🗑️ Waste Types:\n"
                "   • Organic: 0.1 kgCO2/kg\n"
                "   • Plastic: 0.5 kgCO2/kg\n"
                "   • Paper: 0.3 kgCO2/kg\n"
                "   • Metal: 0.8 kgCO2/kg\n\n"
                "2. ♻️ Management Methods:\n"
                "   • Recycling: Lowest emissions\n"
                "   • Composting: Low emissions\n"
                "   • Landfill: Highest emissions\n\n"
                "🌱 Waste Reduction Tips:\n"
                "1. Reduce:\n"
                "   • Buy only what you need\n"
                "   • Choose products with less packaging\n"
                "   • Use reusable items\n\n"
                "2. Reuse:\n"
                "   • Repair items\n"
                "   • Donate unused items\n"
                "   • Use refillable containers\n\n"
                "3. Recycle:\n"
                "   • Separate waste properly\n"
                "   • Use recycling bins\n"
                "   • Support recycling programs\n\n"
                "Would you like to calculate your waste-related emissions or get more specific tips?"
            ],
            'water': [
                "💧 Water Conservation Guide:\n\n"
                "1. 💧 Water Usage:\n"
                "   • Drinking water: 0.344 kgCO2/m³\n"
                "   • Hot water: Additional emissions\n"
                "   • Wastewater treatment: 0.5 kgCO2/m³\n\n"
                "2. 🌱 Conservation Tips:\n"
                "   • Fix leaking taps\n"
                "   • Use water-efficient fixtures\n"
                "   • Collect rainwater\n"
                "   • Reuse greywater\n\n"
                "3. 🏠 Room-specific tips:\n"
                "   • Bathroom: Low-flow fixtures, shorter showers\n"
                "   • Kitchen: Efficient dishwashing, fix leaks\n"
                "   • Laundry: Full loads, cold water\n\n"
                "Would you like to calculate your water-related emissions or get more specific tips?"
            ],
            'shopping': [
                "🛍️ Sustainable Shopping Guide:\n\n"
                "1. 🛍️ Common Items:\n"
                "   • Clothing: 2.5 kgCO2/item\n"
                "   • Electronics: 15.0 kgCO2/item\n"
                "   • Furniture: 20.0 kgCO2/item\n\n"
                "2. 🌱 Sustainable Shopping:\n"
                "   • Buy second-hand\n"
                "   • Choose durable items\n"
                "   • Support local businesses\n"
                "   • Avoid fast fashion\n\n"
                "3. 💡 Smart Shopping Tips:\n"
                "   • Before buying: Need vs. want\n"
                "   • While shopping: Eco-friendly products\n"
                "   • After purchase: Proper maintenance\n\n"
                "Would you like to calculate your shopping-related emissions or get more specific tips?"
            ],
            'default': [
                "🌍 I'm here to help you understand your environmental impact. Here are some topics I can help with:\n\n"
                "1. 📊 Carbon Footprint Calculation\n"
                "2. 🚗 Sustainable Transportation\n"
                "3. 💡 Energy Conservation\n"
                "4. 🍽️ Sustainable Diet\n"
                "5. 🗑️ Waste Management\n"
                "6. 💧 Water Conservation\n"
                "7. 🛍️ Sustainable Shopping\n\n"
                "What would you like to learn more about?"
            ]
        }

        self.keywords = {
            'greeting': ['hi', 'hello', 'hey', 'greetings', 'help', 'start'],
            'carbon_footprint_definition': ['what is carbon footprint', 'define carbon footprint', 'explain carbon footprint', 'carbon footprint meaning', 'carbon footprint definition'],
            'transportation': ['car', 'bus', 'train', 'transport', 'drive', 'commute', 'vehicle', 'travel', 'flight'],
            'energy': ['power', 'energy', 'electric', 'light', 'bulb', 'appliance', 'power consumption', 'electricity', 'lpg', 'cng'],
            'diet': ['food', 'eat', 'diet', 'meal', 'vegetarian', 'vegan', 'meat', 'produce', 'cooking'],
            'waste': ['waste', 'garbage', 'trash', 'recycle', 'reuse', 'disposal', 'landfill', 'compost'],
            'water': ['water', 'shower', 'bath', 'tap', 'faucet', 'laundry', 'washing'],
            'shopping': ['shop', 'buy', 'purchase', 'clothes', 'electronics', 'furniture', 'items']
        }

    def get_response(self, user_input: str) -> str:
        user_input = user_input.lower().strip()
        
        # Check for greetings
        if any(word in user_input for word in self.keywords['greeting']):
            return self.responses['greeting'][0]
        
        # Check for carbon footprint definition first
        if any(phrase in user_input for phrase in self.keywords['carbon_footprint_definition']):
            return self.responses['carbon_footprint_definition'][0]
        
        # Check for specific topics
        for topic, keywords in self.keywords.items():
            if topic not in ['greeting', 'carbon_footprint_definition']:
                if any(word in user_input for word in keywords):
                    return self.responses[topic][0]
        
        # For random questions, provide a helpful default response
        return self.responses['default'][0]

    def get_suggestions(self) -> List[str]:
        """Return a list of suggested questions for the user."""
        return [
            "What is carbon footprint?",
            "How can I reduce my transportation emissions?",
            "What are some energy-saving tips?",
            "How can I make my diet more sustainable?",
            "What are some waste reduction tips?",
            "How can I save water?",
            "What are sustainable shopping tips?",
            "How do I calculate my carbon footprint?"
        ]

    def get_paper_bgcolor(self):
        return 'rgba(0,1,0,0)' if st.session_state.dark_mode else 'white' 