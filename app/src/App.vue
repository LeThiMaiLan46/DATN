<template>
  <div class="app-container">
    <div class="app-card">
      <div class="app-header">
        <h1 class="app-title">Text to Speech</h1>
        <div class="app-subtitle">Convert your text into natural-sounding speech</div>
      </div>
      
      <div class="text-input-container">
        <textarea 
          v-model="text" 
          placeholder="Enter your text here..." 
          class="text-input"
          :class="{ 'has-text': text.length > 0 }"
        ></textarea>
        <div class="character-count" :class="{ 'limit-warning': text.length > 200 }">
          {{ text.length }}/300 characters
        </div>
      </div>
      
      <div class="controls">
        <button 
          @click="convertTextToSpeech" 
          class="speak-button" 
          :disabled="!text.trim() || isLoading"
        >
          <span class="button-icon" v-if="!isLoading">🔊</span>
          <span class="loading-spinner" v-else></span>
          {{ isLoading ? 'Converting...' : 'Convert to Speech' }}
        </button>
        
        <button @click="clearText" class="clear-button" :disabled="!text.trim() || isLoading">
          Clear
        </button>
      </div>
      
      <div v-if="audioUrl" class="audio-player-container">
        <audio ref="audioPlayer" :src="audioUrl" class="audio-player" controls></audio>
        <div class="audio-player-header">
          <button @click="downloadAudio" class="download-button">
            Download
          </button>
        </div>
        <!-- <div class="debug-info" v-if="debugInfo">
          <p>Debug information:</p>
          <pre>{{ debugInfo }}</pre>
        </div> -->
      </div>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
    
    <footer class="app-footer">
      <p>Select voice type:</p>
      <div class="voice-options">
        <label v-for="(voice, index) in voices" :key="index" class="voice-option">
          <input 
            type="radio" 
            :value="voice.id" 
            v-model="selectedVoice" 
            name="voice"
          >
          <span class="voice-name">{{ voice.name }}</span>
        </label>
      </div>
    </footer>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'TextToSpeechApp',
  data() {
    return {
      text: '',
      audioUrl: '',
      isLoading: false,
      errorMessage: '',
      debugInfo: '',
      voices: [
        { id: 'female', name: 'Female' },
        { id: 'male', name: 'Male' },
        { id: 'child', name: 'Child' }
      ],
      selectedVoice: 'female'
    }
  },
  methods: {
    async convertTextToSpeech() {
      if (!this.text.trim()) return;
      
      this.isLoading = true;
      this.errorMessage = '';
      this.debugInfo = '';
      
      try {
        // First approach: Try using arraybuffer response type
        console.log('====== : ',this.text);
        
        const response = await axios({
          method: 'post',
          url: 'http://10.0.64.77:6061/api/v1/text/phonemize',
          data: {
            text: this.text,
            language: 'vi',
            audio_id: 'vi_sample3',
          },
          responseType: 'arraybuffer',
          headers: {
            'Accept': 'audio/wav, audio/*'
          }
        });
        
        // Log response headers for debugging
        const contentType = response.headers['content-type'];
        this.debugInfo = `Content-Type: ${contentType || 'not specified'}\n`;
        this.debugInfo += `Response size: ${response.data.byteLength} bytes\n`;
        
        // Check if the response is actually JSON (error message) in arraybuffer format
        let isJson = false;
        if (response.data.byteLength > 0) {
          try {
            // Try to interpret as JSON first (in case of error message)
            const textDecoder = new TextDecoder('utf-8');
            const text = textDecoder.decode(response.data);
            const jsonResponse = JSON.parse(text);
            isJson = true;
            this.errorMessage = `API returned JSON instead of audio: ${JSON.stringify(jsonResponse)}`;
            return;
          } catch (e) {
            // Not JSON, proceed with audio handling
            isJson = false;
          }
        }
        
        if (!isJson) {
          // Create a blob with explicit MIME type
          const audioBlob = new Blob([response.data], { type: contentType || 'audio/wav' });
          
          // Create object URL from blob
          const url = URL.createObjectURL(audioBlob);
          this.audioUrl = url;
          
          // When audio is ready, try to play it
          this.$nextTick(() => {
            if (this.$refs.audioPlayer) {
              this.$refs.audioPlayer.onloadedmetadata = () => {
                this.debugInfo += `Audio loaded successfully. Duration: ${this.$refs.audioPlayer.duration}s\n`;
              };
              
              this.$refs.audioPlayer.onerror = (e) => {
                this.debugInfo += `Audio error: ${this.$refs.audioPlayer.error.message}\n`;
                this.errorMessage = `Failed to play audio: ${this.$refs.audioPlayer.error.message}`;
              };
              
              // Load the audio
              this.$refs.audioPlayer.load();
              
              // Try to play (might be blocked by browser)
              this.$refs.audioPlayer.play()
                .then(() => {
                  this.debugInfo += "Playback started successfully.\n";
                })
                .catch(err => {
                  this.debugInfo += `Auto-play failed: ${err.message}\n`;
                  // This is often expected due to browser autoplay policies
                });
            }
          });
        }
      } catch (err) {
        console.error('API Error:', err);
        this.errorMessage = `API Error: ${err.message}`;
        if (err.response) {
          this.debugInfo += `Status: ${err.response.status}\n`;
          this.debugInfo += `Headers: ${JSON.stringify(err.response.headers)}\n`;
          
          // Try to parse response data if available
          if (err.response.data) {
            if (typeof err.response.data === 'string') {
              this.debugInfo += `Response: ${err.response.data}\n`;
            } else if (err.response.data instanceof ArrayBuffer) {
              const decoder = new TextDecoder('utf-8');
              try {
                const text = decoder.decode(err.response.data);
                this.debugInfo += `Response data: ${text}\n`;
              } catch (e) {
                this.debugInfo += `Could not decode response as text\n`;
              }
            } else {
              this.debugInfo += `Response: ${JSON.stringify(err.response.data)}\n`;
            }
          }
        }
      } finally {
        this.isLoading = false;
      }
    },
    
    clearText() {
      this.text = '';
      // If there was a previous blob URL, revoke it to free memory
      if (this.audioUrl && this.audioUrl.startsWith('blob:')) {
        URL.revokeObjectURL(this.audioUrl);
      }
      this.audioUrl = '';
      this.errorMessage = '';
      this.debugInfo = '';
    },
    
    downloadAudio() {
      if (!this.audioUrl) return;

      const link = document.createElement('a');
      link.href = this.audioUrl;
      link.download = 'speech-' + Date.now() + '.wav';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  },
  beforeDestroy() {
    // Clean up any blob URLs when component is destroyed
    if (this.audioUrl && this.audioUrl.startsWith('blob:')) {
      URL.revokeObjectURL(this.audioUrl);
    }
  }
}
</script>

<style>
/* Premium Modern CSS Styling */
:root {
  --primary-color: #4a6cf7;
  --primary-hover: #3b5de7;
  --secondary-color: #6c757d;
  --text-color: #2d3748;
  --light-text: #718096;
  --lightest-text: #a0aec0;
  --border-color: #e2e8f0;
  --bg-color: #f8fafc;
  --card-bg: #ffffff;
  --error-color: #e53e3e;
  --success-color: #38a169;
  --warning-color: #ed8936;
  --shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: var(--text-color);
  background-color: var(--bg-color);
  line-height: 1.6;
}

.app-container {
  width: 1000px;
  height: 500px;
  margin: 20%;
}

.app-card {
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 2rem;
  margin-bottom: 2rem;
}

.app-header {
  text-align: center;
  margin-bottom: 2rem;
}

.app-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.app-subtitle {
  color: var(--light-text);
  font-size: 1rem;
}

.text-input-container {
  position: relative;
  margin-bottom: 1.5rem;
}

.text-input {
  width: 100%;
  height: 180px;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--text-color);
  transition: var(--transition);
  resize: vertical;
  outline: none;
  font-family: inherit;
}

.text-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

.text-input.has-text {
  border-color: var(--primary-color);
}

.character-count {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  font-size: 0.75rem;
  color: var(--lightest-text);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.character-count.limit-warning {
  color: var(--warning-color);
}

.controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.clear-button{
  width: 20%;
  margin-left: 40%;
  height: 30px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
}

.download-button{
  width: 10%;
  height: 30px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
}

.speak-button {
  width: 20%;
  height: 30px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
}

.speak-button {
  
  background-color: var(--primary-color);
  color: white;
  flex: 1;
}

.speak-button:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.speak-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.clear-button {
  background-color: transparent;
  color: var(--secondary-color);
  border: 1px solid var(--border-color);
}

.clear-button:hover:not(:disabled) {
  background-color: var(--bg-color);
}

.clear-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.button-icon {
  font-size: 1.2rem;
}

.loading-spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.audio-player-container {
  background-color: var(--bg-color);
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.audio-player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.audio-player-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
}

.download-button {
  background-color: transparent;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
}

.download-button:hover {
  background-color: rgba(74, 108, 247, 0.1);
}

.audio-player {
  width: 100%;
  height: 40px;
  border-radius: 4px;
}

.error-message {
  color: var(--error-color);
  background-color: rgba(229, 62, 62, 0.1);
  padding: 0.75rem;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.debug-info {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f1f5f9;
  border-radius: 8px;
  font-family: monospace;
  font-size: 0.85rem;
  overflow-x: auto;
}

.debug-info pre {
  white-space: pre-wrap;
}

.app-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.app-footer p {
  font-weight: 600;
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.voice-options {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.voice-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.voice-option input[type="radio"] {
  accent-color: var(--primary-color);
  width: 1rem;
  height: 1rem;
}

.voice-name {
  font-size: 0.9rem;
  color: var(--text-color);
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .app-card {
    padding: 1.5rem 1rem;
  }
  
  .controls {
    display: flex;
    flex-direction: row;
    align-content: space-between;
    width: 50%;
    margin-left: 25%;
  }
  
  .clear-button {
    width: 100%;
  }
}
</style>