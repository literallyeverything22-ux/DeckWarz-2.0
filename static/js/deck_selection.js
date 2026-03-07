// Deck Selection Logic

document.addEventListener('DOMContentLoaded', () => {
    const deckWrappers = document.querySelectorAll('.deck-wrapper');
    const actionBar = document.getElementById('action-bar');
    const selectedCountSpan = document.getElementById('selected-count');
    const MAX_SELECTIONS = 5;
    let selectedDecks = [];

    deckWrappers.forEach(wrapper => {
        wrapper.addEventListener('click', () => {
            const countryName = wrapper.querySelector('.country-label').innerText;

            // If it's already selected, deselect it
            if (wrapper.classList.contains('selected')) {
                wrapper.classList.remove('selected');
                selectedDecks = selectedDecks.filter(name => name !== countryName);
            } else {
                // If it's NOT selected, check if we've hit the limit
                if (selectedDecks.length >= MAX_SELECTIONS) {
                    // Provide a visual shake or feedback
                    wrapper.classList.add('error-shake');
                    setTimeout(() => wrapper.classList.remove('error-shake'), 300);
                    return; // Stop selection
                }

                // Add selected class
                wrapper.classList.add('selected');
                selectedDecks.push(countryName);
            }

            // Update UI State
            selectedCountSpan.innerText = selectedDecks.length;

            if (selectedDecks.length > 0) {
                actionBar.classList.remove('hidden');
            } else {
                actionBar.classList.add('hidden');
            }
        });
    });

    // Start War Button Event Listener (Placeholder for next step)
    const startWarBtn = document.getElementById('start-war-btn');
    if (startWarBtn) {
        startWarBtn.addEventListener('click', () => {
            console.log("Starting War with nations:", selectedDecks);
            // Drafting logic will go here
        });
    }
});
