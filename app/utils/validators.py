def validate_campaign_data(data):
    if not data:
        return "No data provided"
    
    if not data.get('product_name'):
        return "Product name is required"
    
    budget = data.get('budget')
    if budget is not None:
        try:
            budget_float = float(budget)
            if budget_float < 0:
                return "Budget must be positive"
        except (ValueError, TypeError):
            return "Budget must be a valid number"
    
    return None
