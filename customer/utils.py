def calculate_emi(principal, interest_rate, tenure):
    r = interest_rate / (12 * 100)
    emi = principal * r * (1 + r) ** tenure / ((1 + r) ** tenure - 1)
    return round(emi, 2)