// Placeholder for Wawa; assume library installed
const Lipsync = require('wawa-lipsync');  // npm install wawa-lipsync

function startLipSync(audioPath) {
  const lipsync = new Lipsync();
  const audio = new Audio(audioPath);
  audio.play();
  lipsync.start(audio);
  lipsync.on('viseme', viseme => {
    // Call from avatar.js
    updateMorph(viseme);
  });
}

module.exports = startLipSync;