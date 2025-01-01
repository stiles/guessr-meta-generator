mapboxgl.accessToken = 'pk.eyJ1Ijoic3RpbGVzIiwiYSI6ImNsd3Rpc3V2aTAzeXUydm9sMHdoN210b2oifQ.66AJmPYxe2ixku1o7Rwdlg';

// Load country data dynamically
fetch('./static/data/countries_regions.json')
    .then(response => response.json())
    .then(countryData => {
        let currentStyle = 'mapbox://styles/stiles/cm3v3manm000901sl7na56rhr';
        const satelliteStyle = 'mapbox://styles/stiles/cm3uqt9ft00d301sv0lww7k2m';

        const map = new mapboxgl.Map({
            container: 'quiz-map',
            style: currentStyle,
            center: [0, 0],
            zoom: 3,
            minZoom: 2,
            maxZoom: 8,
        });

        map.addControl(new mapboxgl.NavigationControl(), 'top-left');

        const toggleButton = document.getElementById('toggle-button');
        toggleButton.addEventListener('click', () => {
            if (currentStyle === satelliteStyle) {
                currentStyle = 'mapbox://styles/stiles/cm3v3manm000901sl7na56rhr';
                toggleButton.textContent = 'Satellite map';
            } else {
                currentStyle = satelliteStyle;
                toggleButton.textContent = 'Default map';
            }
            map.setStyle(currentStyle);
        });

        let markers = [];
        let score = 0;
        let questionCount = 0;
        const maxQuestions = 10;

        // Get a random country, optionally filtering by exclusion or region
        function getRandomCountry(exclude = null, region = null) {
            let filtered = countryData.filter(c => c.code !== exclude);
            if (region) {
                filtered = filtered.filter(c => c.region === region);
            }
            return filtered[Math.floor(Math.random() * filtered.length)];
        }

        function generateQuiz() {
            if (questionCount >= maxQuestions) {
                showScore();
                return;
            }

            questionCount++;
            const correctCountry = getRandomCountry();

            markers.forEach(marker => marker.remove());
            markers = [];

            const marker = new mapboxgl.Marker({ color: 'var(--jasper)' })
                .setLngLat([correctCountry.lon, correctCountry.lat])
                .addTo(map);
            markers.push(marker);

            map.flyTo({
                center: [correctCountry.lon, correctCountry.lat],
                zoom: 4,
            });

            const questionEl = document.getElementById('question');
            const optionsEl = document.getElementById('options');
            const answerDisplay = document.getElementById('answer-display');

            questionEl.innerHTML = `Which country is this? <p class="counter">(Question ${questionCount} of ${maxQuestions})</p>`;
            answerDisplay.textContent = '';

            const options = [correctCountry];

            while (options.length < 2) {
                const sameRegionCountry = getRandomCountry(correctCountry.code, correctCountry.region);
                if (!options.some(o => o.code === sameRegionCountry.code)) {
                    options.push(sameRegionCountry);
                }
            }

            while (options.length < 4) {
                const randomCountry = getRandomCountry(correctCountry.code);
                if (!options.some(o => o.code === randomCountry.code)) {
                    options.push(randomCountry);
                }
            }

            options.sort(() => Math.random() - 0.5);

            optionsEl.innerHTML = '';
            options.forEach(option => {
                const btn = document.createElement('button');
                btn.classList.add('option');
                btn.innerHTML = `<img src="https://flagcdn.com/w160/${option.code}.png" class="flag"><p>${option.name}</p>`;
                btn.addEventListener('click', () => {
                    if (option.code === correctCountry.code) {
                        answerDisplay.innerHTML = `<span class="correct">YES!</span> That's <span class="highlight">${correctCountry.name}</span>.`;
                        score++;
                    } else {
                        answerDisplay.innerHTML = `<span class="incorrect">OOPS!</span> The country is actually <span class="highlight">${correctCountry.name}</span>.`;
                    }
                    setTimeout(generateQuiz, 2500);
                });
                optionsEl.appendChild(btn);
            });
        }

        function showScore() {
            const questionEl = document.getElementById('question');
            const optionsEl = document.getElementById('options');
            const answerDisplay = document.getElementById('answer-display');

            questionEl.textContent = `All done!`;
            optionsEl.innerHTML = '';
            answerDisplay.innerHTML = `You scored <span class="correct">${score}</span> out of <span class="highlight">${maxQuestions}</span>.`;
        }

        map.on('load', generateQuiz);
    })
    .catch(error => console.error('Error loading country data:', error));