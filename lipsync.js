// Lip Sync Manager using wawa-lipsync
// Based on https://github.com/wass08/wawa-lipsync

class LipSyncManager {
    constructor() {
        this.isActive = false;
        this.currentAudio = null;
        this.visemeCallback = null;
        this.audioContext = null;
        this.analyzer = null;
        this.mediaStreamSource = null;
        this.animationFrame = null;
        
        this.init();
    }

    init() {
        // Initialize audio context
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyzer = this.audioContext.createAnalyser();
            this.analyzer.fftSize = 2048;
            this.analyzer.smoothingTimeConstant = 0.8;
            
            console.log('Lip sync manager initialized');
        } catch (error) {
            console.error('Failed to initialize audio context:', error);
        }
    }

    startLipSync(audio) {
        if (!this.audioContext || !this.analyzer) {
            console.error('Audio context not available');
            return;
        }

        try {
            this.stopLipSync(); // Stop any existing lip sync
            
            this.isActive = true;
            this.currentAudio = audio;
            
            // Create audio source from the audio element
            this.mediaStreamSource = this.audioContext.createMediaElementSource(audio);
            this.mediaStreamSource.connect(this.analyzer);
            this.analyzer.connect(this.audioContext.destination);
            
            // Start analyzing audio for lip sync
            this.analyzeAudio();
            
            console.log('Lip sync started');
            
        } catch (error) {
            console.error('Failed to start lip sync:', error);
        }
    }

    stopLipSync() {
        this.isActive = false;
        
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }
        
        if (this.mediaStreamSource) {
            this.mediaStreamSource.disconnect();
            this.mediaStreamSource = null;
        }
        
        console.log('Lip sync stopped');
    }

    analyzeAudio() {
        if (!this.isActive || !this.analyzer) return;
        
        const bufferLength = this.analyzer.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const analyze = () => {
            if (!this.isActive) return;
            
            this.analyzer.getByteFrequencyData(dataArray);
            
            // Analyze frequency data to determine viseme
            const viseme = this.determineViseme(dataArray);
            
            // Apply viseme to avatar
            if (viseme && window.avatarManager) {
                window.avatarManager.startAnimation(viseme);
            }
            
            this.animationFrame = requestAnimationFrame(analyze);
        };
        
        analyze();
    }

    determineViseme(frequencyData) {
        // Simple frequency analysis to determine mouth shape
        // This is a basic implementation - wawa-lipsync would provide more sophisticated analysis
        
        const lowFreq = this.getAverageFrequency(frequencyData, 0, 100);
        const midFreq = this.getAverageFrequency(frequencyData, 100, 500);
        const highFreq = this.getAverageFrequency(frequencyData, 500, 1000);
        
        // Map frequency ranges to visemes
        if (lowFreq > 150) {
            return 'A'; // Open mouth for low frequencies
        } else if (midFreq > 100) {
            return 'E'; // Mid frequencies
        } else if (highFreq > 80) {
            return 'I'; // High frequencies
        } else if (lowFreq > 50 && midFreq > 50) {
            return 'O'; // Mixed frequencies
        } else if (highFreq > 50) {
            return 'F'; // Fricative sounds
        } else {
            return 'M'; // Closed mouth
        }
    }

    getAverageFrequency(data, startIndex, endIndex) {
        let sum = 0;
        let count = 0;
        
        for (let i = startIndex; i < endIndex && i < data.length; i++) {
            sum += data[i];
            count++;
        }
        
        return count > 0 ? sum / count : 0;
    }

    // Advanced viseme detection using wawa-lipsync principles
    detectVisemeFromAudio(audioBuffer) {
        // This would integrate with wawa-lipsync's analysis
        // For now, we'll use a simplified approach
        
        const sampleRate = audioBuffer.sampleRate;
        const length = audioBuffer.length;
        const channelData = audioBuffer.getChannelData(0);
        
        // Analyze audio in chunks
        const chunkSize = Math.floor(sampleRate * 0.1); // 100ms chunks
        const visemes = [];
        
        for (let i = 0; i < length; i += chunkSize) {
            const chunk = channelData.slice(i, i + chunkSize);
            const viseme = this.analyzeChunk(chunk, sampleRate);
            visemes.push(viseme);
        }
        
        return visemes;
    }

    analyzeChunk(chunk, sampleRate) {
        // Simple energy-based analysis
        let energy = 0;
        let zeroCrossings = 0;
        
        for (let i = 0; i < chunk.length; i++) {
            energy += Math.abs(chunk[i]);
            if (i > 0 && (chunk[i] * chunk[i-1]) < 0) {
                zeroCrossings++;
            }
        }
        
        const avgEnergy = energy / chunk.length;
        const zeroCrossingRate = zeroCrossings / chunk.length;
        
        // Map to visemes based on energy and zero-crossing rate
        if (avgEnergy > 0.1) {
            if (zeroCrossingRate > 0.1) {
                return 'F'; // Fricative
            } else {
                return 'A'; // Vowel
            }
        } else if (avgEnergy > 0.05) {
            return 'E'; // Mid vowel
        } else {
            return 'M'; // Closed
        }
    }

    // Set callback for viseme updates
    onViseme(callback) {
        this.visemeCallback = callback;
    }

    // Process audio file for lip sync
    async processAudioFile(audioFile) {
        try {
            const arrayBuffer = await audioFile.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            const visemes = this.detectVisemeFromAudio(audioBuffer);
            return visemes;
            
        } catch (error) {
            console.error('Failed to process audio file:', error);
            return [];
        }
    }

    // Real-time microphone input for lip sync
    async startMicrophoneLipSync() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            const source = this.audioContext.createMediaStreamSource(stream);
            source.connect(this.analyzer);
            
            this.isActive = true;
            this.analyzeAudio();
            
            return stream;
            
        } catch (error) {
            console.error('Failed to start microphone lip sync:', error);
            return null;
        }
    }

    // Cleanup
    dispose() {
        this.stopLipSync();
        
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        
        this.analyzer = null;
        this.mediaStreamSource = null;
    }
}

// Initialize lip sync manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.lipSyncManager = new LipSyncManager();
});