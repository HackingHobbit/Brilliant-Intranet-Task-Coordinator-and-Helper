const axios = require('axios');
const { initAvatar } = require('./avatar');
const startLipSync = require('./lipsync');

document.addEventListener('DOMContentLoaded', () => {
  initAvatar('avatar-canvas', false);  // From config

  const input = document.getElementById('input');
  const chat = document.getElementById('chat');
  const status = document.getElementById('status');
  const micBtn = document.getElementById('mic-btn');

  micBtn.addEventListener('click', () => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      const recorder = new MediaRecorder(stream);
      recorder.start();
      status.textContent = 'Listening...';
      recorder.ondataavailable = e => {
        const formData = new FormData();
        formData.append('audio', e.data, 'audio.webm');
        axios.post('http://localhost:5000/transcribe', formData).then(res => processQuery(res.data.text));
      };
      setTimeout(() => recorder.stop(), 5000);
    });
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') processQuery(input.value);
  });

  function processQuery(query) {
    chat.innerHTML += `<p>User: ${query}</p>`;
    status.textContent = 'Thinking...';
    axios.post('http://localhost:5000/generate_response', { query }).then(res => {
      chat.innerHTML += `<p>AI: ${res.data.response}</p>`;
      status.textContent = 'Responding...';
      axios.post('http://localhost:5000/tts', { text: res.data.response }).then(ttsRes => {
        startLipSync(ttsRes.data.audio_path);
      });
    });
  }
});