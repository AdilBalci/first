// Ses ve metin senkronizasyonu
const audio = document.getElementById('audioPlayer');
const playPauseBtn = document.getElementById('playPauseBtn');
const textContent = document.getElementById('textContent');
let currentWordIndex = 0;

// Touch eventleri için
let initialFontSize = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--base-font-size'));

// Ses kontrolü
playPauseBtn.addEventListener('click', () => {
    if (audio.paused) {
        audio.play();
        playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
        startTextHighlighting();
    } else {
        audio.pause();
        playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
    }
});

// Metin vurgulama fonksiyonu
function startTextHighlighting() {
    const words = textContent.textContent.split(' ');
    audio.addEventListener('timeupdate', () => {
        const currentTime = audio.currentTime;
        // Zaman damgalarına göre kelime indeksini güncelle
        currentWordIndex = Math.floor((currentTime / audio.duration) * words.length);
        updateHighlightedText(words);
    });
}

// Font boyutu ayarlama (pinch zoom)
document.addEventListener('touchmove', (e) => {
    if (e.touches.length === 2) {
        e.preventDefault();
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const currentDistance = Math.hypot(
            touch2.pageX - touch1.pageX,
            touch2.pageY - touch1.pageY
        );
        
        const newFontSize = initialFontSize * (currentDistance / 100);
        document.documentElement.style.setProperty('--base-font-size', `${Math.max(1, Math.min(3, newFontSize))}rem`);
    }
}); 