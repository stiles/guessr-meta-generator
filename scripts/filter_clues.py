import json

# File paths
INPUT_FILE = "./static/data/geoguessr_clues.json"
OUTPUT_FILE = "./static/data/geoguessr_coverage.json"

def extract_coverage(input_file, output_file):
    """
    Extract countries with "coverage" set to "True" in geoguessr_clues.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    coverage_data = {}

    for country, details in data.items():
        clues = details.get("geoguessr_clues", {})
        environment = clues.get("Environment & landscape", {})
        if environment.get("coverage", "").strip() == "True":
            # Include country if "coverage" is "True"
            coverage_data[country] = details

    # Write the filtered data to a new file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(coverage_data, f, indent=4, ensure_ascii=False)
    print(f"Coverage data saved to {output_file}")

# Main Execution
if __name__ == "__main__":
    extract_coverage(INPUT_FILE, OUTPUT_FILE)