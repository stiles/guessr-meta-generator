import json

# Paths to input and output files
META_PATH = "./data/national_provincial_capitals_extended.json"
CLUES_PATH = "./static/data/geoguessr_clues.json"
CLUES_PATH_OUTPUT = "./static/data/geoguessr_clues_extended.json"

# Load the GeoJSON data
with open(META_PATH, "r") as geojson_file:
    geojson_data = json.load(geojson_file)

# Load the clues data
with open(CLUES_PATH, "r") as clues_file:
    clues_data = json.load(clues_file)

# Name corrections for mismatches
name_corrections = {
    "Antarctica": None,
    "Cocos (Keeling) Islands": "Cocos Islands",
    "DR Congo": "Democratic Republic of the Congo",
    "Côte d'Ivoire": "Ivory Coast",
    "Cape Verde": "Cabo Verde",
    "Western Sahara": "Sahrawi Arab Democratic Republic",
    "South Georgia": "South Georgia and South Sandwich Islands",
    "Hong Kong": "Hong Kong",
    "Macau": "Macao",
    "Pitcairn Islands": "Pitcairn",
    "Svalbard and Jan Mayen": "Svalbard",
    "São Tomé and Príncipe": "Sao Tome and Principe",
    "Eswatini (Swaziland)": "Eswatini",
    "French Southern and Antarctic Lands": "French Southern Territories",
    "Taiwan": "Taiwan",
    "Vatican City (Holy See)": "Vatican City",
    "Wallis and Futuna": "Wallis and Futuna",
    "Kosovo": None,
    "Brunei": "Brunei Darussalam",
    "Republic of the Congo": "Congo",
    "Heard Island/McDonald Islands": "Heard Island and McDonald Islands",
    "Palestine": "Palestinian Territory",
    "Russia": "Russian Federation",
    "Saint Helena, Ascension and Tristan da Cunha": "Saint Helena",
    "United States Virgin Islands": "US Virgin Islands",
}

# Create lookup dictionaries
geojson_lookup_cntry = {
    entry["cntry_name"].lower(): {
        "capital": entry.get("city_name", "Unknown"),
        "status": entry.get("status", "Unknown"),
        "tld": entry.get("tld", "Unknown")
    }
    for entry in geojson_data
}

geojson_lookup_admin = {
    entry["admin_name"].lower(): {
        "capital": entry.get("city_name", "Unknown"),
        "status": entry.get("status", "Unknown"),
        "tld": entry.get("tld", "Unknown")
    }
    for entry in geojson_data
}

# Merge the data into clues_data
unmatched_countries = []
for country_name, details in clues_data.items():
    # Apply name corrections
    corrected_name = name_corrections.get(country_name, country_name)
    if corrected_name is None:
        continue  # Skip countries explicitly set to None

    lookup_key = corrected_name.lower()

    # Check by `code` first
    country_code = details["code"].lower()
    geo_info = (
        geojson_lookup_cntry.get(country_code) or
        geojson_lookup_cntry.get(lookup_key) or
        geojson_lookup_admin.get(lookup_key)
    )

    if geo_info:
        # Add capital, status, and tld to geoguessr_clues
        geo_clues = details.setdefault("geoguessr_clues", {})
        geo_clues["capital"] = geo_info["capital"]
        geo_clues["capital_status"] = geo_info["status"]
        geo_clues["tld"] = geo_info["tld"]
    else:
        unmatched_countries.append({
            "name": country_name,
            "corrected_name": corrected_name,
            "code": details["code"],
            "region": details.get("region", "Unknown"),
        })

# Save the updated clues data to a new file
with open(CLUES_PATH_OUTPUT, "w") as output_file:
    json.dump(clues_data, output_file, indent=4)

# Log unmatched countries
if unmatched_countries:
    print("The following countries were not matched, even after corrections and admin_name fallback:")
    for unmatched in unmatched_countries:
        print(
            f"Country: {unmatched['name']}, Corrected Name: {unmatched['corrected_name']}, "
            f"Code: {unmatched['code']}, Region: {unmatched['region']}"
        )
else:
    print("All countries successfully matched.")

print(f"Extended clues saved to {CLUES_PATH_OUTPUT}")