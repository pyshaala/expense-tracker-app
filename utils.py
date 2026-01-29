# ---------------------------------
# STANDARD BUDGET MAP
# ---------------------------------

def get_budget_map():

    return {

        "Rent + Utilities": 25,
        "Household + Groceries": 15,
        "Insurance + Health": 10,
        "EMI + Debt": 20,
        "Savings + Investment": 15,
        "Lifestyle + Personal": 10,
        "Emergency Fund": 5
    }


# ---------------------------------
# CATEGORY → BUCKET MAP
# ---------------------------------

def get_category_bucket_map():

    return {

        "Food": "Household + Groceries",
        "Bills": "Rent + Utilities",
        "EMI": "EMI + Debt",
        "Health": "Insurance + Health",
        "Savings": "Savings + Investment",
        "Personal": "Lifestyle + Personal",
        "Family": "Lifestyle + Personal",
        "Transport": "Lifestyle + Personal",

        # Default
        "Miscellaneous": "Lifestyle + Personal"
    }

# ---------------------------------
# BUCKET → CATEGORY LIST
# ---------------------------------

def get_bucket_categories():

    mapping = get_category_bucket_map()

    bucket_map = {}

    for cat, bucket in mapping.items():

        if bucket not in bucket_map:
            bucket_map[bucket] = []

        bucket_map[bucket].append(cat)

    return bucket_map


# ---------------------------------
# FIND BUCKET
# ---------------------------------

def map_to_bucket(category):

    mapping = get_category_bucket_map()

    return mapping.get(
        category,
        "Lifestyle + Personal"
    )
