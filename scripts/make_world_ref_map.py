import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.ticker import MultipleLocator, FuncFormatter
import os

# Define map regions, extents, and custom figure sizes
regions = {
    "world": {"extent": [-180, 180, -55, 70], "grid_spacing": (10, 5), "detailed_borders": True, "fig_size": (12, 6)},
    "russia_ukraine_baltics": {"extent": [20, 60, 45, 70], "grid_spacing": (5, 2), "detailed_borders": True, "fig_size": (12, 6)},
    "europe": {"extent": [-25, 45, 35, 71], "grid_spacing": (10, 5), "detailed_borders": True, "fig_size": (12, 6)},
    "united_kingdom": {"extent": [-10, 2, 49, 61], "grid_spacing": (2, 1), "detailed_borders": False, "fig_size": (12, 6)},
    "conus": {"extent": [-125, -66.5, 24, 49.5], "grid_spacing": (10, 5), "detailed_borders": False, "fig_size": (12, 6)},
    "southeast_asia": {"extent": [90, 155, -15, 25], "grid_spacing": (3, 1), "detailed_borders": True, "fig_size": (12, 6)},
    "south_america": {"extent": [-82, -34, -55, 13], "grid_spacing": (10, 5), "detailed_borders": True, "fig_size": (12, 6)},
    "oceania": {"extent": [110, 180, -50, 10], "grid_spacing": (5, 5), "detailed_borders": True, "fig_size": (12, 6)},
    "japan": {"extent": [122, 153, 24, 46], "grid_spacing": (3, 1), "detailed_borders": False, "fig_size": (12, 6)},
}

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "../images/maps")
os.makedirs(output_dir, exist_ok=True)

# Function to create and save the map
def create_map(region_name, extent, grid_spacing, detailed_borders, fig_size):
    # Create a map with the specified figure size
    fig, ax = plt.subplots(figsize=fig_size, subplot_kw={"projection": ccrs.Mercator()})
    
    # Set the extent for the region
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    
    # Add land with a light gray fill
    land = cfeature.NaturalEarthFeature(
        category="physical",
        name="land",
        scale="10m",
        facecolor="lightgray"
    )
    ax.add_feature(land, zorder=0)

    # Add coastlines
    ax.coastlines(resolution="10m", linewidth=0.5, color="black")
    
    # Add country boundaries
    if detailed_borders:
        country_borders = cfeature.NaturalEarthFeature(
            category="cultural",
            name="admin_0_boundary_lines_land",
            scale="10m",
            facecolor="none",
            edgecolor="black",
            linewidth=0.3,
        )
        ax.add_feature(country_borders, zorder=1)
    
    # Add states for US map
    if region_name == "conus":  # Match the key in the regions dictionary
        ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=0.3)

    # Add gridlines with the specified grid spacing
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.4,
        color="gray",
        alpha=0.7,
        linestyle="--",
    )
    gl.xlocator = MultipleLocator(grid_spacing[0])  # Longitude spacing
    gl.ylocator = MultipleLocator(grid_spacing[1])  # Latitude spacing
    gl.xlabel_style = {"size": 10, "color": "black"}
    gl.ylabel_style = {"size": 10, "color": "black"}
    
    # Remove degree symbols and directional labels
    gl.xformatter = FuncFormatter(lambda x, _: f"{x:.0f}")
    gl.yformatter = FuncFormatter(lambda y, _: f"{y:.0f}")
    
    # Save the plot
    output_path = os.path.join(output_dir, f"{region_name}.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved map for {region_name} at {output_path}")

# Loop through the regions and create maps
for region_name, region_info in regions.items():
    create_map(
        region_name, 
        region_info["extent"], 
        region_info["grid_spacing"], 
        region_info["detailed_borders"], 
        region_info["fig_size"]
    )