// DeckWarz VibeCode Scrubber Logic

const teams = [
    { id: 'IND', name: 'India', color: '#0000FF' },
    { id: 'AUS', name: 'Australia', color: '#FFCD00' },
    { id: 'ENG', name: 'England', color: '#CE1126' },
    { id: 'SA', name: 'South Africa', color: '#007749' },
    { id: 'NZ', name: 'New Zealand', color: '#000000' },
    { id: 'PCB', name: 'Pakistan', color: '#01411C' },
    { id: 'SL', name: 'Sri Lanka', color: '#00008A' },
    { id: 'WI', name: 'West Indies', color: '#7B0041' },
    { id: 'BNG', name: 'Bangladesh', color: '#006A4E' },
    { id: 'AFG', name: 'Afghanistan', color: '#0044C7' },
    { id: 'IRE', name: 'Ireland', color: '#169B62' },
    { id: 'ZIM', name: 'Zimbabwe', color: '#D30027' }
];

let currentTeamIndex = 0;
let isAnimating = false;

// DOM Elements
const canvas = document.getElementById('vibe-canvas');
const ctx = canvas.getContext('2d');
const titleElem = document.getElementById('active-team-name');
const glowOrb = document.querySelector('.orb-center');
const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');

// State
let images = {}; // { 'IND': { start: Image, end: Image } }
let loadedImages = 0;
const totalImages = teams.length * 2;

// Load all images into memory for instant swapping
function preloadImages() {
    teams.forEach(team => {
        images[team.id] = { start: new Image(), end: new Image() };

        images[team.id].start.onload = imageLoaded;
        images[team.id].start.src = `Frames/${team.id} start.png`;

        images[team.id].end.onload = imageLoaded;
        images[team.id].end.src = `Frames/${team.id} end.png`;
    });
}

function imageLoaded() {
    loadedImages++;
    if (loadedImages === totalImages) {
        initCanvas();
        updateUI();
    }
}

function initCanvas() {
    // Set canvas resolution to match the high-res frames (assume standard for all)
    const sampleImg = images[teams[0].id].start;
    canvas.width = sampleImg.width;
    canvas.height = sampleImg.height;
    drawFrame(teams[0].id, 0); // initial draw
}

// Draw frame based on progress (0 = start, 1 = end completely destroyed)
function drawFrame(teamId, progress) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const startImg = images[teamId].start;
    const endImg = images[teamId].end;

    // We do a beautiful crossfade alpha blend based on the scroll/progress
    ctx.globalAlpha = 1 - progress;
    ctx.drawImage(startImg, 0, 0, canvas.width, canvas.height);

    ctx.globalAlpha = progress;
    ctx.drawImage(endImg, 0, 0, canvas.width, canvas.height);

    // Reset alpha
    ctx.globalAlpha = 1.0;
}

// Navigation Logic
function changeTeam(direction) {
    if (isAnimating) return;

    let newIndex = currentTeamIndex + direction;
    if (newIndex < 0) newIndex = teams.length - 1;
    if (newIndex >= teams.length) newIndex = 0;

    // Quick cinematic wipe to new team
    isAnimating = true;

    // Scale down current
    canvas.style.transform = 'scale(0.8) translateY(50px)';
    canvas.style.opacity = '0';

    setTimeout(() => {
        currentTeamIndex = newIndex;
        updateUI();
        currentProgress = 0; // reset scroll progress
        drawFrame(teams[currentTeamIndex].id, 0);

        // Scale up new
        canvas.style.transform = 'scale(1) translateY(0)';
        canvas.style.opacity = '1';

        setTimeout(() => {
            isAnimating = false;
        }, 500);
    }, 400);
}

function updateUI() {
    const team = teams[currentTeamIndex];
    titleElem.innerText = team.name;
    titleElem.style.color = team.color;
    titleElem.style.textShadow = `0 0 20px ${team.color}`;
    glowOrb.style.background = team.color;
}

// Scroll / Wheel interaction (The VibeCode secret sauce)
let currentProgress = 0;
let targetProgress = 0;
const scrollSensitivity = 0.002;

window.addEventListener('wheel', (e) => {
    // Determine scroll direction and magnitude
    targetProgress += e.deltaY * scrollSensitivity;

    // Clamp between 0 and 1
    targetProgress = Math.max(0, Math.min(1, targetProgress));
});

// Animation Loop for smooth interpolating scroll
function animLoop() {
    // Lerp (Linear Interpolation) for buttery smoothness
    currentProgress += (targetProgress - currentProgress) * 0.1;

    // Only redraw if there's a meaningful change
    if (Math.abs(targetProgress - currentProgress) > 0.001) {
        drawFrame(teams[currentTeamIndex].id, currentProgress);

        // Dynamic scale based on destruction progress (pops open)
        const scale = 1 + (currentProgress * 0.15);
        canvas.style.transform = `scale(${scale})`;
    }

    requestAnimationFrame(animLoop);
}

// Listeners
btnPrev.addEventListener('click', () => changeTeam(-1));
btnNext.addEventListener('click', () => changeTeam(1));

// Start
preloadImages();
animLoop();
