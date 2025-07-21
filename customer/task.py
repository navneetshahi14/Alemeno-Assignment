import pandas as pd
from datetime import datetime
import os
from celery import shared_task

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
loan_df = pd.read_excel(os.path.join(BASE_DIR, 'data', 'loan_data.xlsx'))

@shared_task
def calculate_credit_score_task(customer_id, approved_limit):
    customer_loans = loan_df[loan_df['Customer ID'] == customer_id]
    
    total_current_loans = customer_loans['Loan Amount'].sum()
    if total_current_loans > approved_limit:
        return 0

    paid_on_time_ratio = customer_loans['EMIs paid on Time'].sum() / len(customer_loans) if len(customer_loans) > 0 else 0
    num_loans = len(customer_loans)
    current_year = datetime.now().year
    current_year_loans = customer_loans[pd.to_datetime(customer_loans['Date of Approval']).dt.year == current_year]
    current_year_activity = len(current_year_loans)
    loan_volume = customer_loans['Loan Amount'].sum()

    score = (
        paid_on_time_ratio * 40 +
        min(num_loans * 5, 15) +
        min(current_year_activity * 10, 15) +
        min(loan_volume / 1000000 * 30, 30)
    )

    return round(score)
