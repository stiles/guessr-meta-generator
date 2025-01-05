// Adjust longitude to handle countries spanning the International Date Line
function adjustLngLat(coord, bounds) {
    let [lng, lat] = coord;

    // Normalize longitudes to handle the International Date Line
    if (lng > 180) lng -= 360;
    if (lng < -180) lng += 360;

    bounds.extend([lng, lat]);
}

document.addEventListener("DOMContentLoaded", function () {
    mapboxgl.accessToken = 'pk.eyJ1Ijoic3RpbGVzIiwiYSI6ImNsd3Rpc3V2aTAzeXUydm9sMHdoN210b2oifQ.66AJmPYxe2ixku1o7Rwdlg';

    const mapContainer = document.getElementById("country-map");
    const filterInput = document.getElementById("filter-input");

    // Initialize the map only if the map container exists
    if (mapContainer) {
        const mapLat = parseFloat(mapContainer.getAttribute("data-lat"));
        const mapLon = parseFloat(mapContainer.getAttribute("data-lon"));
        const countryName = mapContainer.getAttribute("data-name");

        // Dynamically determine the base path
        const basePath = window.location.pathname.includes('/guessr-meta-generator/')
            ? '/guessr-meta-generator'
            : '';

        // Construct the GeoJSON URL
        const geojsonUrl = `${basePath}/static/data/geo/${countryName}.geojson`;

        console.log("GeoJSON URL:", geojsonUrl);

        // Initialize the main map
        const map = new mapboxgl.Map({
            container: 'country-map',
            style: 'mapbox://styles/stiles/cm5cvawys00ti01su1mxw905f',
            center: [mapLon, mapLat],
            zoom: 4,
            minZoom: 3,
            maxZoom: 10,
            worldCopyJump: true // Ensures wrapping for maps crossing the Date Line
        });

        map.on('load', function () {
            // Load country boundary GeoJSON
            map.addSource('country-boundary', {
                type: 'geojson',
                data: geojsonUrl,
            });

            map.addLayer({
                id: 'country-boundary-layer',
                type: 'line',
                source: 'country-boundary',
                paint: {
                    'line-color': '#c8553d',
                    'line-width': 2,
                },
            });

            // Fetch the GeoJSON to dynamically set bounds
            fetch(geojsonUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to fetch GeoJSON: ${response.statusText}`);
                    }
                    return response.json();
                })
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

                    // Apply bounds to the map with maxZoom
                    map.fitBounds(bounds, {
                        padding: 20,
                        maxZoom: 10
                    });
                })
                .catch(error => {
                    console.error("Error loading GeoJSON:", error);
                });
        });

        // Dynamically adjust inset map for mobile
        function adjustInsetMapLayout() {
            const insetContainer = document.createElement('div');
            insetContainer.id = 'inset-map';
            mapContainer.appendChild(insetContainer);

            const insetMap = new mapboxgl.Map({
                container: 'inset-map',
                style: 'mapbox://styles/mapbox/light-v10',
                center: [mapLon, mapLat],
                zoom: 1,
                interactive: false,
            });

            insetMap.on('load', () => {
                insetMap.addSource('main-map-bounds', {
                    type: 'geojson',
                    data: {
                        type: 'FeatureCollection',
                        features: [],
                    },
                });

                insetMap.addLayer({
                    id: 'bounding-box',
                    type: 'line',
                    source: 'main-map-bounds',
                    paint: {
                        'line-color': '#FF0000',
                        'line-width': 2,
                    },
                });

                // Update the bounding box on the inset map whenever the main map moves
                function updateInsetMap() {
                    const bounds = map.getBounds();
                    const bbox = {
                        type: 'Feature',
                        geometry: {
                            type: 'Polygon',
                            coordinates: [[
                                [bounds.getSouthWest().lng, bounds.getSouthWest().lat],
                                [bounds.getNorthWest().lng, bounds.getNorthWest().lat],
                                [bounds.getNorthEast().lng, bounds.getNorthEast().lat],
                                [bounds.getSouthEast().lng, bounds.getSouthEast().lat],
                                [bounds.getSouthWest().lng, bounds.getSouthWest().lat], // Close the polygon
                            ]],
                        },
                    };

                    // Update the source on the inset map
                    insetMap.getSource('main-map-bounds').setData({
                        type: 'FeatureCollection',
                        features: [bbox],
                    });

                    // Synchronize the inset map center
                    insetMap.setCenter(map.getCenter());
                }

                // Call updateInsetMap initially and whenever the main map moves
                map.on('move', updateInsetMap);
                updateInsetMap();
            });
        }

        adjustInsetMapLayout();
    }

    // Filter countries by name (only if the filter input exists)
    if (filterInput) {
        filterInput.addEventListener("input", function () {
            const filterValue = filterInput.value.toLowerCase();
            const gridItems = document.querySelectorAll(".grid-item");
            const regionSections = document.querySelectorAll(".region-section");

            gridItems.forEach(item => {
                const countryName = item.getAttribute("data-name").toLowerCase();
                if (countryName.includes(filterValue)) {
                    item.style.display = "block";
                } else {
                    item.style.display = "none";
                }
            });

            regionSections.forEach(regionSection => {
                const subregionTitles = regionSection.querySelectorAll(".subregion-title");
                let regionHasVisibleItems = false;

                subregionTitles.forEach(subregionTitle => {
                    const gridContainer = subregionTitle.nextElementSibling;
                    const visibleItems = gridContainer.querySelectorAll(".grid-item:not([style*='display: none'])");
                    if (visibleItems.length > 0) {
                        subregionTitle.style.display = "block";
                        gridContainer.style.display = "grid";
                        regionHasVisibleItems = true;
                    } else {
                        subregionTitle.style.display = "none";
                        gridContainer.style.display = "none";
                    }
                });

                if (regionHasVisibleItems) {
                    regionSection.style.display = "block";
                } else {
                    regionSection.style.display = "none";
                }
            });
        });
    }
});
