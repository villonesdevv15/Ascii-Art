// ASCII character sets 
const ASCII_CHARACTERS = {
  "1": " ░▒▓█".split(""),
  "2": ' `"+1n@L0qpdbo8$'.split(""),  
  "3": " .:-=+*#%@".split(""),
};

const asciiViewport = document.querySelector(".ascii_viewport");
const asciiPlayer = document.getElementById("ascii_player");
const videoInput = document.getElementById("video_input");
const playBtn = document.getElementById("play_btn");
const pauseBtn = document.getElementById("pause_btn");
const resetBtn = document.getElementById("reset_btn");
const status = document.getElementById("status");
const resolutionSelect = document.getElementById("resolution");
const charsetSelect = document.getElementById("charset");
const fontSizeInput = document.getElementById("font_size");
const fontSizeValue = document.getElementById("font_size_value");
const playbackSpeed = document.getElementById("playback_speed");
const speedValue = document.getElementById("speed_value");
const volumeControl = document.getElementById("volume");
const volumeValue = document.getElementById("volume_value");

let currentCharset = ASCII_CHARACTERS["1"];
let isPlaying = false;
let canvas;
let ctx;
let video;

function initializeCanvas() {
  canvas = document.createElement("canvas");
  ctx = canvas.getContext("2d");
}

// Keeps the canvas height in proportion to the video's shape
function getCanvasHeight(width, videoWidth, videoHeight) {
  return Math.floor((width * videoHeight) / videoWidth);
}

function getAsciiChar(brightness) {
  const index = Math.floor((brightness / 255) * (currentCharset.length - 1));
  return currentCharset[index];
}

// frame of pixels into ASCII characters
function convertToAscii(imgData, w, h) {
  let text = "";
  for (let y = 0; y < h; y += 2) {
    for (let x = 0; x < w; x++) {
      const pos = (y * w + x) * 4;
      const brightness = (imgData.data[pos] + imgData.data[pos + 1] + imgData.data[pos + 2]) / 3;
      text += getAsciiChar(brightness);
    }
    text += "\n";
  }
  return text;
}

function setFontSize(size) {
  asciiPlayer.style.fontSize = `${size}px`;
  asciiPlayer.style.lineHeight = `${size}px`;
  fontSizeValue.textContent = `${Number(size).toFixed(1)}px`;
}

// automatically fits the screen
function fitToScreen() {
  if (!canvas || !canvas.width) return;
  const available = asciiViewport.clientWidth - 16;
  const size = Math.floor((available / (canvas.width * 0.6)) * 10) / 10;
  const fitted = Math.max(2, Math.min(16, size));
  fontSizeInput.value = fitted;
  setFontSize(fitted);
}

function updateResolution() {
  if (!video) return;
  canvas.width = parseInt(resolutionSelect.value);
  canvas.height = getCanvasHeight(canvas.width, video.videoWidth, video.videoHeight);
  fitToScreen();
}

function processFrame() {
  if (!isPlaying) return;

  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const data = ctx.getImageData(0, 0, canvas.width, canvas.height);
  asciiPlayer.textContent = convertToAscii(data, canvas.width, canvas.height);

  requestAnimationFrame(processFrame);
}

// The Upload
videoInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;

  if (video) video.pause();
  isPlaying = false;

  video = document.createElement("video");
  video.playsInline = true;
  video.volume = volumeControl.value;
  video.src = URL.createObjectURL(file);

  video.addEventListener("loadedmetadata", () => {
    updateResolution();
    status.textContent = "Video loaded! Press Play to start.";
  });

  video.addEventListener("ended", () => {
    isPlaying = false;
    status.textContent = "Finished. Press Reset, then Play to watch again.";
  });
});

// Control Buttons
playBtn.addEventListener("click", () => {
  if (!video || isPlaying) return;
  video.playbackRate = parseFloat(playbackSpeed.value);
  video.play();
  isPlaying = true;
  processFrame();
  status.textContent = "Playing...";
});

pauseBtn.addEventListener("click", () => {
  if (!video) return;
  video.pause();
  isPlaying = false;
  status.textContent = "Paused";
});

resetBtn.addEventListener("click", () => {
  if (!video) return;
  video.currentTime = 0;
  if (!isPlaying) {
    status.textContent = "Reset to beginning";
  }
});

// Settings
resolutionSelect.addEventListener("change", updateResolution);

charsetSelect.addEventListener("change", (e) => {
  currentCharset = ASCII_CHARACTERS[e.target.value];
});

fontSizeInput.addEventListener("input", (e) => {
  setFontSize(e.target.value);
});

playbackSpeed.addEventListener("input", (e) => {
  const speed = e.target.value;
  if (video) video.playbackRate = speed;
  speedValue.textContent = `${speed}x`;
});

volumeControl.addEventListener("input", (e) => {
  const volume = e.target.value;
  if (video) video.volume = volume;
  volumeValue.textContent = `${Math.round(volume * 100)}%`;
});

window.addEventListener("resize", fitToScreen);

// Start
if (window.matchMedia("(max-width: 600px)").matches) {
  resolutionSelect.value = "60";
}
initializeCanvas();