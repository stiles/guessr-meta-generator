// Utility Functions
function adjustLngLat(coord, bounds) {
    // Normalize longitude values to handle International Date Line
    let [lng, lat] = coord;
    if (lng > 180) lng -= 360;
    if (lng < -180) lng += 360;
    bounds.extend([lng, lat]);
}

function toggleVisibility(gridItems, filterValue) {
    gridItems.forEach(item => {
        const countryName = item.getAttribute("data-name").toLowerCase();
        item.style.display = countryName.includes(filterValue) ? "" : "none";
    });
}

function toggleRegionVisibility(regionSections) {
    regionSections.forEach(section => {
        const visibleItems = section.querySelectorAll(".grid-item:not([style*='display: none'])");
        section.style.display = visibleItems.length > 0 ? "block" : "none";
    });
}

// Filter Initialization
function initializeFilter() {
    const filterInput = document.getElementById("filter-input");
    if (!filterInput) {
        return;
    }

    console.log("Filter input element found");

    filterInput.addEventListener("input", () => {
        console.log("Filter input changed");
        const filterValue = filterInput.value.toLowerCase();
        const gridItems = document.querySelectorAll(".grid-item");
        const regionSections = document.querySelectorAll(".region-section");

        toggleVisibility(gridItems, filterValue);
        toggleRegionVisibility(regionSections);
    });
}

// Map Initialization
function initializeMap() {
    mapboxgl.accessToken = 'pk.eyJ1Ijoic3RpbGVzIiwiYSI6ImNsd3Rpc3V2aTAzeXUydm9sMHdoN210b2oifQ.66AJmPYxe2ixku1o7Rwdlg';

    const mapContainer = document.getElementById("country-map");
    if (!mapContainer) {
        console.warn("Map container not found. Skipping map initialization.");
        return;
    }

    const mapLat = parseFloat(mapContainer.getAttribute("data-lat"));
    const mapLon = parseFloat(mapContainer.getAttribute("data-lon"));
    const countryName = mapContainer.getAttribute("data-name");
    const basePath = window.location.pathname.includes('/guessr-meta-generator/')
        ? '/guessr-meta-generator'
        : '';
    const geojsonUrl = `${basePath}/static/data/geo/${countryName}.geojson`;

    console.log(`Initializing map for ${countryName} at [${mapLat}, ${mapLon}].`);

    const map = new mapboxgl.Map({
        container: 'country-map',
        style: 'mapbox://styles/stiles/cm5cvawys00ti01su1mxw905f',
        center: [mapLon, mapLat],
        zoom: 4,
        minZoom: 3,
        maxZoom: 10,
        worldCopyJump: true,
    });

    map.on('load', () => {
        map.addSource('country-boundary', { type: 'geojson', data: geojsonUrl });

        map.addLayer({
            id: 'country-boundary-layer',
            type: 'line',
            source: 'country-boundary',
            paint: { 'line-color': '#c8553d', 'line-width': 2 },
        });

        fetch(geojsonUrl)
            .then(response => response.json())
            .then(geojsonData => {
                const bounds = new mapboxgl.LngLatBounds();
                geojsonData.features.forEach(feature => {
                    const coordinates = feature.geometry.coordinates;
                    if (feature.geometry.type === 'Polygon') {
                        coordinates[0].forEach(coord => adjustLngLat(coord, bounds));
                    } else if (feature.geometry.type === 'MultiPolygon') {
                        coordinates.forEach(polygon => {
                            polygon[0].forEach(coord => adjustLngLat(coord, bounds));
                        });
                    }
                });
                map.fitBounds(bounds, { padding: 20, maxZoom: 10 });
            })
            .catch(error => console.error("Error loading GeoJSON:", error));
    });
}

// DOM Ready Event
document.addEventListener("DOMContentLoaded", function () {
    console.log("Script loaded and DOM fully parsed");

    // Initialize the map if the map container is present
    const mapContainer = document.getElementById("country-map");
    if (mapContainer) {
        initializeMap();
    }

    // Initialize the filter if the filter input is present
    const filterInput = document.getElementById("filter-input");
    if (filterInput) {
        initializeFilter();
    }
});