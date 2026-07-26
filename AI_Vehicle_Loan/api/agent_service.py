# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AI_Vehicle_Loan — api (agent_service.py)
# Date: 2025-12-31
# ---------------------------------------------------------------------------
import re
from .data_service import data_service
from .loan_engine import loan_engine
from .vector_db_stub import vector_db


class SimulatedAgent:
    # Function: process_message
    def process_message(self, message: str, history: list):
        msg_lower = message.lower()

        # --- Intent 1: Check Eligibility ---
        if re.search(r"(eligible|qualify|can i get|my score|status)", msg_lower):
            # 1. Simulate fetching customer data
            profile = data_service.generate_customer_profile()
            # 2. Run through loan engine
            result = loan_engine.evaluate_eligibility(profile)

            if result["status"] == "Declined":
                return f"I've analyzed your profile (Credit Score: {profile['credit_score']}). Unfortunately, based on current criteria, we cannot offer a pre-approval at this time. We recommend reviewing your debt-to-income ratio."

            return (
                f"Good news, {profile['name']}! Based on a soft pull of your credit score (**{profile['credit_score']}**), "
                f"you are **{result['status']}** for our {result['tier']} tier. "
                f"Your estimated APR is **{result['estimated_rate']}** with a maximum loan amount of approx. **${result['max_loan_amount']:,}**.")

        # --- Intent 2: Vehicle Discovery (Simulated Vector Search) ---
        # Looks for vehicle types, brands, or specific features
        if re.search(r"(looking for|interested in|show me|find|price of|cost of|tesla|suv|truck|sedan|electric)",
                     msg_lower):
            # perform simulated vector search
            hits = vector_db.search_vehicles(msg_lower)

            if not hits:
                return "I couldn't find vehicles matching that specific description in our immediate inventory. Could you try different keywords, perhaps 'electric SUV' or 'reliable sedan'?"

            response = "Based on your request, here are top matches from our inventory analysis:\n\n"
            for hit in hits:
                response += f"- **{hit['make']} {hit['model']}** ({hit['type']}): Starting around **${hit['price']:,}**. (Match Score: {hit['similarity_score']})\n"
            response += "\nWould you like to see financing options for any of these?"
            return response

        # --- Fallback / Greeting ---
        return "I'm your AI Vehicle Loan Assistant. I can help you check your **loan eligibility** in real-time or **find vehicles** that match your preferences. What would you like to do?"


agent_service = SimulatedAgent()