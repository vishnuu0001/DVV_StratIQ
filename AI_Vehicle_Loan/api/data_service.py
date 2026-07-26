# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AI_Vehicle_Loan — api (data_service.py)
# Date: 2025-07-26
# ---------------------------------------------------------------------------
import random
from faker import Faker

fake = Faker()

# Simulated "Huge Database" with external internet images
VEHICLE_DATABASE = [
    {"id": 1, "make": "TESLA", "model": "Model S Plaid", "type": "ELECTRIC", "price": 89990, "tags": ["AUTOPILOT", "EV", "PERFORMANCE"], "image": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=800"},
    {"id": 2, "make": "TOYOTA", "model": "Land Cruiser 300", "type": "SUV", "price": 85000, "tags": ["OFFROAD", "RELIABLE", "LUXURY"], "image": "https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?q=80&w=800"},
    {"id": 3, "make": "BMW", "model": "iX M60", "type": "ELECTRIC SUV", "price": 111500, "tags": ["LUXURY", "EV", "SPACIOUS"], "image": "https://images.unsplash.com/photo-1617469767053-d3b523a0b982?q=80&w=800"},
    {"id": 4, "make": "FORD", "model": "Mustang Mach-E", "type": "ELECTRIC", "price": 42995, "tags": ["SPORTY", "EV", "SUV"], "image": "https://images.unsplash.com/photo-1619767886558-efdc259cde1a?auto=format&fit=crop&q=80&w=800"},
    {"id": 5, "make": "PORSCHE", "model": "Taycan Turbo S", "type": "ELECTRIC", "price": 194900, "tags": ["PORSCHE", "FAST", "EV"], "image": "https://images.unsplash.com/photo-1614200187524-dc4b892acf16?q=80&w=800"},
    {"id": 6, "make": "MERCEDES-BENZ", "model": "EQS Sedan", "type": "LUXURY", "price": 104400, "tags": ["MERCEDES", "LUXURY", "EV"], "image": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?q=80&w=800"}
]

class SyntheticDataService:
    # Function: get_all_vehicles
    def get_all_vehicles(self):
        return VEHICLE_DATABASE

    # Function: generate_customer_profile
    def generate_customer_profile(self):
        """Simulates a real-time credit profile retrieval."""
        return {
            "name": fake.name(),
            "credit_score": random.choice([610, 645, 710, 755, 820]),
            "annual_income": random.randint(55000, 160000),
            "debt_to_income_ratio": random.uniform(0.15, 0.45)
        }

# Ensure this instance name matches your 'main.py' import
data_service = SyntheticDataService()