import json

# File paths
INPUT_FILE = "./static/data/geoguessr_clues.json"
OUTPUT_FILE = "./static/data/geoguessr_ordered.json"

# Define categories
CATEGORIES = {
    "Identity & symbols": [
        "language", "capital", "capital_status", "tld", "flag", "culture", "miscellaneous"
    ],
    "Environment & landscape": [
        "coverage", "foliage", "topography", "environment", "infrastructure"
    ],
    "Roads & transportation": [
        "cars", "driving", "signs", "bollards", "poles", "stop"
    ]
}

def categorize_clues(clues):
    """
    Group geoguessr_clues into predefined categories.
    """
    categorized_clues = {category: {} for category in CATEGORIES}

    for key, value in clues.items():
        for category, fields in CATEGORIES.items():
            if key in fields:
                categorized_clues[category][key] = value
                break

    return categorized_clues

def order_clues(clues, order):
    """
    Reorder clues based on the specified order: 'custom' or 'alphabetical'.
    """
    if order == "custom":
        # Use predefined categories
        return categorize_clues(clues)
    elif order == "alphabetical":
        # Alphabetical order
        return dict(sorted(clues.items()))
    else:
        raise ValueError("Invalid order type. Choose 'custom' or 'alphabetical'.")

def process_geoguessr_data(input_file, output_file, order="custom"):
    """
    Process the geoguessr.json file to reorder geoguessr_clues for all countries.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for country, details in data.items():
        if "geoguessr_clues" in details:
            details["geoguessr_clues"] = order_clues(details["geoguessr_clues"], order)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Reordered geoguessr_clues saved to {output_file}")

# Main Execution
if __name__ == "__main__":
    # Choose "custom" or "alphabetical" for ordering
    process_geoguessr_data(INPUT_FILE, OUTPUT_FILE, order="custom")
