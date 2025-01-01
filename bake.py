import psutil  # Add this import at the top
import baker
import json
import os
import re
import unicodedata
import shutil
from jinja2 import Environment, FileSystemLoader
import http.server
import socketserver
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time

# Set up Jinja2 environment for rendering templates
env = Environment(loader=FileSystemLoader("templates"))

# Load and process country data
with open("./static/data/geoguessr_clues.json", "r") as f:
    country_data = json.load(f)

# Group countries by region and sub-region
regions = {}
for code, country in country_data.items():  # Iterate over the dictionary items
    region = country.get("region", "Unknown")
    subregion = country.get("sub-region", "Other")

    if region not in regions:
        regions[region] = {}
    if subregion not in regions[region]:
        regions[region][subregion] = []

    regions[region][subregion].append(country)



def slugify(value):
    """Converts a string to a slug-friendly format."""
    if not value:  # Handle None or empty values
        return "uncategorized"
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')  # Remove accents
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()  # Remove non-alphanumeric characters
    value = re.sub(r'[-\s]+', '-', value)  # Replace spaces and repeated dashes with a single dash
    return value

# Add the slugify function as a custom Jinja2 filter
env.filters['slugify'] = slugify

# Directory to store output files
output_dir = "docs"

class RebuildHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # Ignore changes in the `build` folder
        if "docs" in event.src_path:
            return
        if event.is_directory or event.event_type not in ('created', 'modified', 'deleted'):
            return
        print("Changes detected. Rebuilding...")
        subprocess.run(["python", "bake.py", "build_all"])

@baker.command
def watch():
    """Watch for changes and rebuild automatically."""
    path = "."  # Watch the current directory
    event_handler = RebuildHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("Watching for file changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

@baker.command
def serve(port=8000):
    """Start a local test server for live preview."""
    os.chdir(output_dir)  # Change directory to the build folder
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://127.0.0.1:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.shutdown()

@baker.command
def kill(port=8000):
    """Kill the process using the specified port."""
    try:
        output = subprocess.check_output(["lsof", "-i", f":{port}"], text=True).splitlines()
        for line in output[1:]:  # Skip the header row
            parts = line.split()
            pid = int(parts[1])
            print(f"Killing process {parts[0]} (PID {pid}) using port {port}")
            os.kill(pid, 9)
        print(f"All processes using port {port} have been terminated.")
    except subprocess.CalledProcessError:
        print(f"No process found using port {port}.")


def copy_static_files():
    """Copy static assets to the build directory."""
    static_src = "static"
    static_dest = os.path.join(output_dir, "static")
    if os.path.exists(static_dest):
        shutil.rmtree(static_dest)
    shutil.copytree(static_src, static_dest)
    print(f"Copied static files to {static_dest}")

@baker.command
def build_index():
    """Generate the homepage and copy static files."""
    template = env.get_template("index.html")
    output_path = os.path.join(output_dir, "index.html")
    os.makedirs(output_dir, exist_ok=True)

    # Organize countries by region and sub-region
    regions = {}
    for code, country in country_data.items():
        region = country.get("region", "Unknown")
        sub_region = country.get("sub-region", "Other")
        if region not in regions:
            regions[region] = {}
        if sub_region not in regions[region]:
            regions[region][sub_region] = []
        regions[region][sub_region].append(country)

    # Copy static files to build directory
    copy_static_files()

    # Render the index with regions and sub-regions
    rendered_index = template.render(regions=regions)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_index)
    print(f"Generated homepage: {output_path}")

@baker.command
def build_regions():
    """Generate region pages."""
    template = env.get_template("region.html")
    for region, subregions in regions.items():
        output_path = os.path.join(output_dir, region.lower().replace(" ", "-"), "index.html")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(template.render(region_name=region, subregions=subregions))
        print(f"Generated region page: {output_path}")

@baker.command
def build_subregions():
    """Generate subregion pages."""
    template = env.get_template("subregion.html")
    for region, subregions in regions.items():
        for subregion, countries in subregions.items():
            output_path = os.path.join(
                output_dir, region.lower().replace(" ", "-"),
                subregion.lower().replace(" ", "-"), "index.html"
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(template.render(subregion_name=subregion, countries=countries))
            print(f"Generated subregion page: {output_path}")

@baker.command
def build_quiz():
    """Generate the quiz page."""
    template = env.get_template("quiz.html")
    output_path = os.path.join(output_dir, "quiz.html")
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template.render())
    print(f"Generated quiz page: {output_path}")

@baker.command
def build_countries():
    """Generate individual country pages."""
    template = env.get_template("country.html")

    for code, country in country_data.items():
        slug = slugify(country["name"])
        output_path = os.path.join(output_dir, slug, "index.html")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(template.render(country=country))
        print(f"Generated page for {country['name']}: {output_path}")

@baker.command
def build_quiz():
    """Generate the quiz page."""
    template = env.get_template("quiz.html")
    output_path = os.path.join(output_dir, "quiz.html")
    os.makedirs(output_dir, exist_ok=True)

    # Render and save the quiz page
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template.render())
    print(f"Generated quiz page: {output_path}")

@baker.command
def build_all():
    """Build the entire site."""
    build_index()
    build_countries()
    build_quiz()
    build_regions()
    build_subregions()
    print("All pages built successfully!")

if __name__ == "__main__":
    baker.run()
