import os
import json
import logging
from datetime import datetime
from openai import OpenAI

# Define the new questions to append
NEW_QUESTIONS = [
    "language",
    "stop_signs",
    "bollards",
    "telephone_poles",
    "coverage",
    "foilage",
    "topography"
]

# Configure logging
def setup_logging():
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"geoguessr_clues_{timestamp}.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return log_file

# Load existing factbook
def load_existing_factbook(output_file):
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.info(f"No existing factbook found at {output_file}. Starting fresh.")
        return {}

# Generate GeoGuessr clues for missing fields
def generate_missing_clues(client, country, country_info, existing_clues):
    # Determine missing fields
    missing_fields = [q for q in NEW_QUESTIONS if q not in existing_clues]

    if not missing_fields:
        logging.info(f"No missing fields for {country}. Skipping API call.")
        return {}

    try:
        # Construct the prompt
        prompt_content = f"""For {country}, generate only the missing details for these fields:
{', '.join(missing_fields)}.

Provide the result in this JSON format:
{{
    "language": "Common languages and descriptions of alphabet and any special characters",
    "stop_signs": "Do stop signs read 'stop', 'pare', or 'arrêt' in {country}?",
    "bollards": "Describe any unique features about roadside bollards in {country}",
    "telephone_poles": "Describe any unique features about utility poles in {country}",
    "coverage": "True/False: Does {country} have official Google Street View coverage?",
    "foliage": "Describe common tree types and grasses in {country}",
    "topography": "Describe the major topographical characteristics in {country}, e.g., mountainous, hilly, or flat"
}}

Respond strictly in JSON format with only the requested fields."""
        
        # Make the API request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a geography expert creating structured insights for GeoGuessr players."},
                {"role": "user", "content": prompt_content}
            ],
            max_tokens=700,
            temperature=0.7
        )

        # Validate the response
        if not response.choices or not response.choices[0].message.content.strip():
            logging.error(f"Empty or invalid response for {country}.")
            return {}

        # Parse JSON response
        return json.loads(response.choices[0].message.content.strip())

    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error for {country}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Error generating clues for {country}: {e}")
        return {}


# Main function
def generate_geoguessr_clues(input_file, output_file):
    log_file = setup_logging()
    logging.info(f"Logging to {log_file}")
    
    client = OpenAI(api_key=os.environ.get("OPEN_AI"))
    country_data = load_input_file(input_file)
    geoguessr_clues = load_existing_factbook(output_file)

    processed_count, skipped_count, error_count = 0, 0, 0

    for country_info in country_data:
        country_name = country_info.get('name', '')
        if not country_name:
            logging.warning("Country without a name found. Skipping.")
            continue
        
        # Get existing clues or initialize them
        existing_clues = geoguessr_clues.get(country_name, {}).get("geoguessr_clues", {})

        # Generate missing fields
        new_clues = generate_missing_clues(client, country_name, country_info, existing_clues)
        if not new_clues:
            skipped_count += 1
            continue

        # Merge new clues with existing ones
        geoguessr_clues[country_name] = {
            **geoguessr_clues.get(country_name, {}),
            "geoguessr_clues": {**existing_clues, **new_clues}
        }
        processed_count += 1

        # Save progress periodically
        if processed_count % 10 == 0:
            save_progress(geoguessr_clues, output_file)

    # Final save and summary
    save_progress(geoguessr_clues, output_file)
    logging.info("=" * 50)
    logging.info("Processing Summary:")
    logging.info(f"Total Countries: {len(country_data)}")
    logging.info(f"Processed Countries: {processed_count}")
    logging.info(f"Skipped Countries: {skipped_count}")
    logging.info(f"Countries with Errors: {error_count}")
    logging.info(f"Output saved to: {output_file}")

# Helper functions
def load_input_file(input_file):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading input file {input_file}: {e}")
        raise

def save_progress(geoguessr_clues, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(geoguessr_clues, f, ensure_ascii=False, indent=4)
        logging.info(f"Progress saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving progress: {e}")

# Main execution
if __name__ == "__main__":
    input_file = "./static/data/countries_regions.json"
    output_file = "./static/data/geoguessr_clues.json"
    generate_geoguessr_clues(input_file, output_file)
