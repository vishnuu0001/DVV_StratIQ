# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AI_Vehicle_Loan — api (loan_engine.py)
# Date: 2026-04-19
# ---------------------------------------------------------------------------
class LoanEngine:
    # Function: evaluate_eligibility
    def evaluate_eligibility(self, profile):
        score = profile['credit_score']
        dti = profile['debt_to_income_ratio']
        income = profile['annual_income']

        tier = "Standard"
        rate = 0.12
        status = "Conditional"
        max_loan = income * 0.35

        if score >= 760 and dti < 0.35:
            tier = "Platinum Prime"
            rate = 0.045
            status = "Pre-Approved"
            max_loan = income * 0.50
        elif score >= 700 and dti < 0.45:
            tier = "Gold"
            rate = 0.065
            status = "Approved"
            max_loan = income * 0.45
        elif score >= 640 and dti < 0.50:
            tier = "Silver"
            rate = 0.09
            status = "Approved"
            max_loan = income * 0.40
        elif score < 600 or dti > 0.55:
            tier = "N/A"
            status = "Declined"
            rate = 0.0
            max_loan = 0

        return {
            "status": status,
            "tier": tier,
            "estimated_rate": f"{rate*100:.1f}%",
            "max_loan_amount": int(max_loan),
            "customer_profile": profile
        }

loan_engine = LoanEngine()