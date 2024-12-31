# GeoGuessr tips with AI

This repository contains a growing set of tools aimed at understanding and boosting play on GeoGuessr, a game that challenges users to recognize locations from Google Street View's panoramic images.

The project was born out of a desire to help my kids better understand geography, but it has turned into an experiment in using AI tools to generate structured data — in this case, hints for identifying world countries and US states on the roadways. It also helps explore your own GeoGuessr duels.

The project, for now, includes scripts to collect and generate game-specific metadata about countries and US states. It also contains code to create a simple country mapping quiz and a filterable grid of national flags, with country-specific pages baked into static files. In addition, there are scripts to fetch details about specific duels or to compile a dataframe of all of your duels.

*It's very new and a work in progress.*

## Features

### Ai-driven data generation
- Uses AI tools to create structured metadata for over 190 countries and all 50 US states.
- Generates clues for identifying locations on roadways, including details like language, signs, cars, and infrastructure.
- Employs natural language generation techniques to fill in geospatial details dynamically.

### Front-end features baked with baker
- Leverages the LA Times' [Baker tool](https://github.com/datadesk/baker-example-page-template) for static site generation.
- Creates:
  - A filterable grid of countries with flag images.
  - Individual country pages featuring maps, metadata, and AI-generated clues.
  - A country mapping quiz for geography practice.

### Duel analysis tools
- Scripts to fetch GeoGuessr duel details for deeper analysis.
- Compile your duels into a dataframe for statistical or visual exploration.

### Geospatial integration
- Uses GeoJSON data to dynamically highlight countries and US states on interactive maps.
- Integrates Mapbox for visualizing country boundaries and adding inset regional maps.

## How to use

### Installation
1. Clone this repository:
   ```
   git clone https://github.com/yourusername/guessr-meta-generator.git
   ```
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the project

#### Building the static site
1. Generate the entire site:
   ```
   python bake.py build_all
   ```
2. Serve the site locally for testing:
   ```
   python bake.py serve
   ```
3. Visit `http://127.0.0.1:8000` in your browser to explore the generated pages.

#### Using the duel analysis tools
- Run the duel fetching script:
  ```
  python scripts/fetch_duels.py
  ```
- Compile a dataframe of all your duels:
  ```
  python scripts/compile_duels.py
  ```

## Contributing
This project is a work in progress, and contributions are welcome! If you have ideas for new features or improvements, feel free to submit a pull request or open an issue.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- GeoGuessr for the inspiration behind this project.
- [LA Times Baker](https://github.com/datadesk/baker-example-page-template) for the static site generation tool.
- OpenAI for AI-driven metadata generation.