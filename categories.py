import json
from pathlib import Path


FILE = Path("data/categories.json")


# ---------------------------------
# LOAD
# ---------------------------------

def load_categories():

    if not FILE.exists():
        return {}

    with open(FILE, "r") as f:
        return json.load(f)


# ---------------------------------
# SAVE
# ---------------------------------

def save_categories(data):

    FILE.parent.mkdir(exist_ok=True)

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------------
# GET BUCKET
# ---------------------------------

def get_bucket(category, subcategory):

    data = load_categories()

    if category in data:
        if subcategory in data[category]:
            return data[category][subcategory]

    return "Lifestyle"   # default


# ---------------------------------
# ADD NEW CATEGORY
# ---------------------------------

def add_category(cat, sub, bucket="Lifestyle"):

    data = load_categories()

    if cat not in data:
        data[cat] = {}

    data[cat][sub] = bucket

    save_categories(data)
