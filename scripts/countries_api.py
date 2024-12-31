import os
import json
import requests

# Define file paths relative to the script
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "../data/national_provincial_capitals.json")
output_file = os.path.join(script_dir, "../data/national_provincial_capitals_extended.json")

# Base URL for REST Countries API
api_base_url = "https://restcountries.com/v3.1/name/"

# Manual lookup for territories and protectorates
manual_tld_lookup = {
    "Wallis & Futuna": ".wf",
    "Cook Is.": ".ck",
    "Pitcairn Is.": ".pn",
    "Falkland Is.": ".fk",
    "St. Helena": ".sh",
    "Cayman Is.": ".ky",
    "Netherlands Antilles": ".an",
    "Turks & Caicos Is.": ".tc",
    "The Bahamas": ".bs",
    "Bosnia & Herzegovina": ".ba",
    "Marshall Is.": ".mh",
    "Northern Mariana Is.": ".mp",
    "Cocos Is.": ".cc",
    "Christmas I.": ".cx",
    "Timor Leste": ".tl",
    "Norfolk I.": ".nf",
    "Trinidad & Tobago": ".tt",
    "British Virgin Is.": ".vg",
    "Virgin Is.": ".vi",
    "St. Kitts & Nevis": ".kn",
    "Antigua & Barbuda": ".ag",
    "St. Lucia": ".lc",
    "St. Vincent & the Grenadines": ".vc",
    "St. Pierre & Miquelon": ".pm",
    "Faroe Is.": ".fo",
    "The Gambia": ".gm",
    "Cote d'Ivoire": ".ci",
    "Sao Tome & Principe": ".st",
    "Svalbard": ".no",
    "Congo": ".cg",
    "Congo, DRC": ".cd",
    "Reunion": ".re",
    "Solomon Is.": ".sb",
}

# Load the data from the JSON file
with open(input_file, "r") as f:
    capitals_data = json.load(f)

# Loop through each country to fetch TLDs
for country in capitals_data:
    country_name = country.get("cntry_name")
    
    if not country_name:
        print(f"[ERROR] No country name found for entry: {country}")
        continue

    # Check manual lookup first
    if country_name in manual_tld_lookup:
        country["tld"] = manual_tld_lookup[country_name]
        print(f"[INFO] Found TLD for {country_name} in manual lookup: {manual_tld_lookup[country_name]}")
        continue

    try:
        # Make an API request to fetch country details
        response = requests.get(f"{api_base_url}{country_name}", params={"fullText": "true"})
        response.raise_for_status()
        country_info = response.json()

        # Extract the TLD
        tld = country_info[0].get("tld", [None])[0]
        if tld:
            country["tld"] = tld
        else:
            print(f"[ERROR] No TLD found for country: {country_name}")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch data for country: {country_name} | Error: {e}")

# Save the extended dataset
with open(output_file, "w") as f:
    json.dump(capitals_data, f, indent=4)
    print(f"[INFO] Extended dataset saved to {output_file}")
