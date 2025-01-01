document.addEventListener("DOMContentLoaded", () => {
    const flashcards = document.querySelectorAll(".flashcard");
    const nextButton = document.getElementById("next-card");
    const hintButton = document.getElementById("show-hint");
    const regionHint = document.getElementById("region-hint");
    const subregionHint = document.getElementById("subregion-hint");
    const clueHint = document.getElementById("clue-hint");

    let currentIndex = 0;
    let currentHintIndex = 0;

    function showFlashcard(index) {
        flashcards.forEach((card, i) => {
            card.style.display = i === index ? "block" : "none";
            // Reset any flips
            card.querySelector(".flashcard-inner").style.transform = "rotateY(0deg)";
        });
        resetHints();
    }

    function resetHints() {
        regionHint.textContent = "";
        subregionHint.textContent = "";
        clueHint.textContent = "";
        currentHintIndex = 0;
    }

    function showHint() {
        const currentCard = flashcards[currentIndex];
        const hints = [
            `<span class="hint-category">Region:</span> ${currentCard.dataset.region}`,
            `<span class="hint-category">Sub-region:</span> ${currentCard.dataset.subregion}`,
            `<span class="hint-category">Language:</span> ${currentCard.dataset.language}`,
            `<span class="hint-category">Culture:</span> ${currentCard.dataset.culture}`,
            `<span class="hint-category">Bonus:</span> ${currentCard.dataset.bonus}`
        ];
    
        if (currentHintIndex < hints.length) {
            clueHint.innerHTML = hints[currentHintIndex]; // Use innerHTML for bold descriptions
            currentHintIndex++;
        } else {
            clueHint.innerHTML = "<span class='hint-category'>No more hints:</span> Guess already!";
        }
    }

    // Add click event to flip flashcards back and forth
    flashcards.forEach(card => {
        const cardInner = card.querySelector(".flashcard-inner");
        card.addEventListener("click", () => {
            const isFlipped = cardInner.style.transform === "rotateY(180deg)";
            cardInner.style.transform = isFlipped ? "rotateY(0deg)" : "rotateY(180deg)";
        });
    });

    nextButton.addEventListener("click", () => {
        currentIndex = (currentIndex + 1) % flashcards.length;
        showFlashcard(currentIndex);
    });

    hintButton.addEventListener("click", showHint);

    // Show the first flashcard
    showFlashcard(currentIndex);
});