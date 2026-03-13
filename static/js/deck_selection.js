// Deck Selection Logic — respects dynamic nation count set in step 2
document.addEventListener('DOMContentLoaded', () => {
    const deckWrappers = document.querySelectorAll('.deck-wrapper');
    const actionBar = document.getElementById('action-bar');
    const selectedCountSpan = document.getElementById('selected-count');
    let selectedDecks = [];

    // MAX_SELECTIONS is set by the step-2 screen via window._maxSelections
    function getMax() { return window._maxSelections || 5; }

    deckWrappers.forEach(wrapper => {
        wrapper.addEventListener('click', () => {
            const countryName = wrapper.querySelector('.country-label').innerText;

            if (wrapper.classList.contains('selected')) {
                wrapper.classList.remove('selected');
                selectedDecks = selectedDecks.filter(name => name !== countryName);
            } else {
                if (selectedDecks.length >= getMax()) {
                    wrapper.classList.add('error-shake');
                    setTimeout(() => wrapper.classList.remove('error-shake'), 300);
                    return;
                }
                wrapper.classList.add('selected');
                selectedDecks.push(countryName);
            }

            selectedCountSpan.innerText = selectedDecks.length;
            document.getElementById('max-count').innerText = getMax();

            if (selectedDecks.length > 0) {
                actionBar.classList.remove('hidden');
            } else {
                actionBar.classList.add('hidden');
            }

            // Enable Start War only when exactly the right count is selected
            const startBtn = document.getElementById('start-war-btn');
            if (startBtn) {
                const ready = selectedDecks.length === getMax();
                startBtn.style.opacity = ready ? '1' : '0.5';
                startBtn.style.pointerEvents = ready ? 'auto' : 'none';
            }
        });
    });

    // Check if we are joining a room (invite link)
    const urlParams = new URLSearchParams(window.location.search);
    const existingRoomId = urlParams.get('room');

    const startWarBtn = document.getElementById('start-war-btn');
    const actionDesc = document.getElementById('action-desc');

    if (existingRoomId && startWarBtn && actionDesc) {
        startWarBtn.innerText = 'JOIN WAR';
        actionDesc.innerText = "Join your friend's game room";
    }

    if (startWarBtn) {
        startWarBtn.addEventListener('click', () => {
            if (selectedDecks.length < 1) return;
            const query = encodeURIComponent(JSON.stringify(selectedDecks));
            const roomId = existingRoomId || ('room_' + Math.random().toString(36).substring(2, 8));
            // Pass username along so the game page can use it
            const username = localStorage.getItem('dw_username') || '';
            window.location.href = `/game?room=${roomId}&decks=${query}&user=${encodeURIComponent(username)}`;
        });
    }
});
