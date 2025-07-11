class LocalAIAvatarUI {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.config = {};
        this.backendUrl = window.electronAPI ? window.electronAPI.getBackendUrl() : 'http://localhost:5000';

        this.initializeElements();
        this.loadConfig();
        this.setupEventListeners();
    }

    async initializeElements() {
        this.input = document.getElementById('input');
        this.chat = document.getElementById('chat');
        this.status = document.getElementById('status');
        this.micBtn = document.getElementById('mic-btn');
        this.avatarCanvas = document.getElementById('avatar-canvas');
        this.settingsBtn = document.getElementById('settings-btn');
        
        if (!this.input || !this.chat || !this.status || !this.micBtn) {
            console.error('Required UI elements not found');
            return;
        }
    }

    async loadConfig() {
        try {
            // Try to load from Electron API first
            if (window.electronAPI) {
                this.config = await window.electronAPI.getConfig();
                console.log('Config loaded from Electron:', this.config);
                return;
            }

            // Fallback to HTTP API
            const response = await fetch(`${this.backendUrl}/get_config`);
            if (response.ok) {
                this.config = await response.json();
                console.log('Config loaded from HTTP:', this.config);
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Failed to load config:', error);
            this.config = {
                email_mode: "local",
                calendar_mode: "local",
                financial_api: "yfinance",
                enable_3d: false
            };
        }
    }

    setupEventListeners() {
        // Text input handling
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && this.input.value.trim()) {
                this.processQuery(this.input.value.trim());
                this.input.value = '';
            }
        });

        // Microphone button
        this.micBtn.addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });

        // Settings button
        if (this.settingsBtn) {
            this.settingsBtn.addEventListener('click', () => {
                this.openSettingsPanel();
            });
        }

        // Handle avatar upload
        this.setupAvatarUpload();
    }

    setupAvatarUpload() {
        // Create file input for avatar upload
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);

        // Add upload button to UI
        const uploadBtn = document.createElement('button');
        uploadBtn.innerHTML = '📷';
        uploadBtn.className = 'upload-btn';
        uploadBtn.style.cssText = `
            position: absolute;
            top: 4px;
            right: 60px;
            background: rgba(0, 191, 255, 0.2);
            border: 1px solid #00bfff;
            color: #00bfff;
            padding: 8px;
            border-radius: 4px;
            cursor: pointer;
        `;
        document.getElementById('avatar-container').appendChild(uploadBtn);

        uploadBtn.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.uploadAvatar(file);
            }
        });
    }

    async uploadAvatar(file) {
        try {
            this.updateStatus('Uploading avatar...');

            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch(`${this.backendUrl}/landmarks`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                if (data.landmarks) {
                    // Initialize avatar with landmarks
                    if (window.avatarManager) {
                        window.avatarManager.setLandmarks(data.landmarks);
                    }
                    this.updateStatus('Avatar uploaded successfully');
                } else {
                    this.updateStatus('No landmarks detected');
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Avatar upload error:', error);
            this.updateStatus('Avatar upload failed');
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                await this.processAudioInput(audioBlob);
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateStatus('Listening...');
            this.micBtn.innerHTML = '⏹️';
            this.micBtn.style.backgroundColor = '#ff4444';
            
        } catch (error) {
            console.error('Failed to start recording:', error);
            this.updateStatus('Microphone access denied');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            this.isRecording = false;
            this.micBtn.innerHTML = '🎤';
            this.micBtn.style.backgroundColor = '';
        }
    }

    async processAudioInput(audioBlob) {
        try {
            this.updateStatus('Transcribing...');

            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');

            const response = await fetch(`${this.backendUrl}/transcribe`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                if (data.text) {
                    this.addMessage('User', data.text);
                    await this.processQuery(data.text);
                } else {
                    this.updateStatus('No speech detected');
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }

        } catch (error) {
            console.error('Audio processing error:', error);
            this.updateStatus('Transcription failed');
        }
    }

    async processQuery(query) {
        try {
            this.updateStatus('Processing...');

            const response = await fetch(`${this.backendUrl}/generate_response`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.response) {
                    this.addMessage('AI', data.response);
                    await this.generateSpeech(data.response);
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }

        } catch (error) {
            console.error('Query processing error:', error);
            this.updateStatus('Processing failed');
            this.addMessage('AI', 'I apologize, but I encountered an error processing your request.');
        }
    }

    async generateSpeech(text) {
        try {
            this.updateStatus('Generating speech...');

            const response = await fetch(`${this.backendUrl}/tts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });

            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);

                // Start lip sync when audio plays
                audio.addEventListener('play', () => {
                    this.updateStatus('Speaking...');
                    this.startLipSync(audio);
                });

                audio.addEventListener('ended', () => {
                    this.updateStatus('Idle');
                    if (window.avatarManager) {
                        window.avatarManager.stopAnimation();
                    }
                    // Clean up blob URL
                    URL.revokeObjectURL(audioUrl);
                });

                audio.play();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }

        } catch (error) {
            console.error('Speech generation error:', error);
            this.updateStatus('Speech generation failed');
        }
    }

    startLipSync(audio) {
        try {
            // Use wawa-lipsync for real-time lip sync
            if (window.lipSyncManager) {
                window.lipSyncManager.startLipSync(audio);
            } else {
                console.warn('Lip sync manager not available');
            }
        } catch (error) {
            console.error('Lip sync error:', error);
        }
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        messageDiv.innerHTML = `
            <span class="sender">${sender}:</span>
            <span class="text">${text}</span>
        `;
        
        this.chat.appendChild(messageDiv);
        this.chat.scrollTop = this.chat.scrollHeight;
    }

    updateStatus(status) {
        if (this.status) {
            this.status.textContent = status;
        }
    }

    openSettingsPanel() {
        if (window.settingsPanel) {
            window.settingsPanel.open();
        } else {
            console.warn('Settings panel not available');
        }
    }
}

// Initialize UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ui = new LocalAIAvatarUI();
});