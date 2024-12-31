import json
import os
from slugify import slugify
from fuzzywuzzy import process

# Paths to input files
GEOJSON_PATH = "./data/geo/countries.geojson"
CLUES_PATH = "./static/data/geoguessr_clues.json"
OUTPUT_DIR = "./static/data/geo"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the GeoJSON data
with open(GEOJSON_PATH, "r") as geojson_file:
    geojson_data = json.load(geojson_file)

# Load the clues data
with open(CLUES_PATH, "r") as clues_file:
    clues_data = json.load(clues_file)

# Create a mapping of country names to their GeoJSON geometries
geojson_country_map = {
    feature["properties"]["country"]: feature
    for feature in geojson_data["features"]
}

# Name corrections for mismatches
name_corrections = {
    "Antarctica": None,
    "Cocos (Keeling) Islands": "Cocos Islands",
    "DR Congo": "Democratic Republic of the Congo",
    "Côte d'Ivoire (Ivory Coast)": "Ivory Coast",
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
    "Kosovo": None
}

name_corrections.update({
    "Brunei": "Brunei Darussalam",
    "DR Congo": "Democratic Republic of the Congo",
    "Republic of the Congo": "Congo",
    "Western Sahara": "Sahrawi Arab Democratic Republic",
    "Hong Kong": "Hong Kong",
    "Heard Island/McDonald Islands": "Heard Island and McDonald Islands",
    "Macau": "Macao",
    "Palestine": "Palestinian Territory",
    "Russia": "Russian Federation",
    "Saint Helena, Ascension and Tristan da Cunha": "Saint Helena",
    "Taiwan": "Taiwan",
    "United States Virgin Islands": "US Virgin Islands",
    "Wallis and Futuna": "Wallis and Futuna",
    "Russia": "Russia"
})

# Track missing countries
missing_countries = []

# Export GeoJSON files
for country_name, details in clues_data.items():
    corrected_name = name_corrections.get(country_name, country_name)
    slugified_name = slugify(country_name)

    if corrected_name is None:
        print(f"Skipping: {country_name} (No geometry available)")
        continue

    if corrected_name in geojson_country_map:
        country_feature = geojson_country_map[corrected_name]
        output_geojson = {
            "type": "FeatureCollection",
            "features": [country_feature],
        }
        output_path = os.path.join(OUTPUT_DIR, f"{slugified_name}.geojson")
        with open(output_path, "w") as output_file:
            json.dump(output_geojson, output_file, indent=2)
        print(f"Exported: {country_name} -> {output_path}")
    else:
        missing_countries.append(country_name)

# Fuzzy matching for remaining missing countries
geojson_country_names = list(geojson_country_map.keys())
for missed_country in missing_countries:
    best_match = process.extractOne(missed_country, geojson_country_names)
    if best_match and best_match[1] > 85:
        print(f"Suggested match for {missed_country}: {best_match[0]} (Score: {best_match[1]})")
    else:
        print(f"No match found for: {missed_country}")

# Log missing countries
with open("missing_countries.log", "w") as log_file:
    for missed_country in missing_countries:
        log_file.write(f"{missed_country}\n")
