<template>
  <div id="app" class="container">
    <!-- Text Input Section -->
     <div class="main">
    <div class="section">
      <!-- <h2>Text to Speech</h2> -->
      <textarea 
        v-model="textInput" 
        placeholder="Nhập văn bản cần chuyển đổi thành giọng nói..."
        rows="4"
        class="text-input"
      ></textarea>
      <div v-if="generatedAudioUrl" class="section">
            <audio :src="generatedAudioUrl" controls></audio>
          </div>
      <button 
        @click="sendTextAndAudio" 
        :disabled="!textInput.trim() || isProcessing"
        class="btn btn-primary"
      >
        {{ isProcessing ? 'Đang xử lý...' : 'Send ᯓ➤' }}
      </button>
    </div>

    <!-- Sample Audio Section -->
    <div class="section">
      <!-- <h2>Sample Audio Files</h2> -->
      <div class="sample-audio-list">
        <div 
          v-for="(sample, index) in sampleAudios" 
          :key="index"
          class="sample-audio-item"
          :class="{ active: selectedSampleAudio === sample }"
          @click="selectSampleAudio(sample)"
        >
          <div class="audio-info">
            <h4>{{ sample.name }}</h4>
            <audio 
              :ref="el => audioRefs[index] = el" 
              :src="sample.url" 
              controls 
              @click.stop
            ></audio>

          </div>
          <div class="select-indicator">
            {{ selectedSampleAudio === sample ? '✓ Đã chọn' : 'Click để chọn' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Voice Recording Section -->
    <div class="section">
      <h2>Voice Recording</h2>
      <div class="recording-controls">
        <button 
          @click="startRecording" 
          :disabled="isRecording || !isMediaSupported"
          class="btn btn-success"
        >
          {{ isRecording ? 'Đang ghi âm...' : 'Record Voice' }}
        </button>
        
        <button 
          @click="stopRecording" 
          :disabled="!isRecording"
          class="btn btn-warning"
        >
          Stop Recording
        </button>
      </div>
      
      <!-- Recording Status -->
      <div v-if="isRecording" class="recording-status">
        🔴 Đang ghi âm... ({{ recordingTime }}s)
      </div>
      
      <!-- Audio Preview -->
      <div v-if="audioBlob" class="audio-preview">
        <h3>Recorded Audio Preview:</h3>
        <audio :src="audioUrl" controls></audio>
      </div>
    </div>

    <!-- Audio Selection Status -->
    <div class="section audio-selection-status">
      <!-- <h3>Audio được chọn để gửi:</h3> -->
      <div v-if="selectedSampleAudio" class="selected-audio">
        <span class="audio-type">📁 Sample Audio:</span>
        <span class="audio-name">{{ selectedSampleAudio.name }}</span>
        <button @click="clearSampleSelection" class="btn-clear">✕</button>
      </div>
      <div v-else-if="audioBlob" class="selected-audio">
        <span class="audio-type">🎙️ Recorded Audio:</span>
        <span class="audio-name">Bản ghi âm của bạn</span>
        <button @click="clearRecording" class="btn-clear">✕</button>
      </div>
      <div v-else class="no-audio">
        Chưa có audio nào được chọn
      </div>
    </div>
    <div v-if="statusMessage" class="status-message" :class="statusType">
      {{ statusMessage }}
    </div>
    
</div>
    <!-- Status Messages
    <div v-if="statusMessage" class="status-message" :class="statusType">
      {{ statusMessage }}
    </div> -->

    <!-- Media Support Warning -->
    <div v-if="!isMediaSupported" class="warning">
      ⚠️ Trình duyệt của bạn không hỗ trợ ghi âm hoặc cần cấp quyền truy cập microphone
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// Reactive data
const textInput = ref('')
const isRecording = ref(false)
const isProcessing = ref(false)
const isMediaSupported = ref(false)
const audioBlob = ref(null)
const audioUrl = ref('')
const statusMessage = ref('')
const statusType = ref('')
const recordingTime = ref(0)
const selectedSampleAudio = ref(null)
const audioRefs = ref([])
// const generatedAudioUrl = ref('')



// Sample audio files
const sampleAudios = ref([
  {
    name: 'Audio1',
    url: '/audio_sample/sample1.wav',
    filename: 'sample1.wav'
  },
  {
    name: 'Audio2',
    url: '/audio_sample/sample2.wav',
    filename: 'sample2.wav'
  },
  {
    name: 'Audio3',
    url: '/audio_sample/sample3.wav',
    filename: 'sample3.wav'
  }
])


// MediaRecorder related
let mediaRecorder = null
let audioChunks = []
let recordingTimer = null

// Backend API URLs - thay đổi theo địa chỉ backend của bạn

const API_BASE_URL = 'http://localhost:6065'

// Check media support on component mount
onMounted(async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    isMediaSupported.value = true
    // Stop the stream immediately after checking
    stream.getTracks().forEach(track => track.stop())
  } catch (error) {
    console.error('Media not supported or permission denied:', error)
    isMediaSupported.value = false
  }
})

// Cleanup on component unmount
onUnmounted(() => {
  if (recordingTimer) {
    clearInterval(recordingTimer)
  }
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
})

// Send text and audio to backend simultaneously
const generatedAudioUrl = ref('') // Thêm biến lưu URL tạm của audio từ backend

const sendTextAndAudio = async () => {
  if (!textInput.value.trim()) return;

  isProcessing.value = true;
  try {
    const formData = new FormData();
    formData.append('text', textInput.value);
    formData.append('language', 'vi');
    formData.append('audio_type', 'none');

    if (audioBlob.value) {
      formData.set('audio', audioBlob.value, 'recording.webm');
      formData.set('audio_type', 'recorded');
    } else if (selectedSampleAudio.value) {
      const audioResponse = await fetch(selectedSampleAudio.value.url);
      const sampleBlob = await audioResponse.blob();
      formData.set('audio', sampleBlob, selectedSampleAudio.value.filename);
      formData.set('audio_type', 'sample');
      formData.set('sample_name', selectedSampleAudio.value.name);
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/text/phonemize`, {
      method: 'POST',
      body: formData
    });

    if (response.ok) {
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      generatedAudioUrl.value = url  // 👈 Gán vào biến để hiển thị trên UI
      showStatus('Tạo audio thành công!', 'success');
    } else {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error('Error sending text and audio:', error);
    showStatus('Lỗi khi gửi text và audio: ' + error.message, 'error');
  } finally {
    isProcessing.value = false;
  }
};



const selectSampleAudio = (sample) => {
  selectedSampleAudio.value = sample

  // Clear recorded audio
  if (audioBlob.value) {
    audioBlob.value = null
    audioUrl.value = ''
  }

  // Phát audio sample tương ứng
  const index = sampleAudios.value.findIndex(s => s === sample)
  const audioElement = audioRefs.value[index]

  if (audioElement) {
    audioElement.currentTime = 0  // phát lại từ đầu
    audioElement.play()
  }

  showStatus(`Đã chọn audio mẫu: ${sample.name}`, 'info')
}


// Clear sample selection
const clearSampleSelection = () => {
  selectedSampleAudio.value = null
  showStatus('Đã bỏ chọn audio mẫu', 'info')
}

// Clear recording
const clearRecording = () => {
  audioBlob.value = null
  audioUrl.value = ''
  showStatus('Đã xóa bản ghi âm', 'info')
}

// Start recording audio
const startRecording = async () => {
  try {
    audioChunks = []
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 48000,
        sampleSize: 16 
      }
    })
    
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    })
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }
    
    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' })
      audioBlob.value = blob
      audioUrl.value = URL.createObjectURL(blob)
      
      // Clear sample selection when recording new audio
      selectedSampleAudio.value = null
      
      // Stop all tracks to release microphone
      stream.getTracks().forEach(track => track.stop())
      
      showStatus('Ghi âm hoàn tất!', 'success')
    }
    
    mediaRecorder.start(1000) // Collect data every 1000ms
    isRecording.value = true
    recordingTime.value = 0
    
    // Start timer
    recordingTimer = setInterval(() => {
      recordingTime.value++
    }, 1000)
    
    showStatus('Bắt đầu ghi âm...', 'info')
    
  } catch (error) {
    console.error('Error starting recording:', error)
    showStatus('Lỗi khi bắt đầu ghi âm: ' + error.message, 'error')
  }
}

// Stop recording audio
const stopRecording = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    isRecording.value = false
    
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
  }
}

// Send audio to backend
const sendAudio = async () => {
  if (!audioBlob.value) return
  
  isProcessing.value = true
  try {
    const formData = new FormData()
    formData.append('audio', audioBlob.value, 'recording.webm')
    
    const response = await fetch(`${API_BASE_URL}/upload-audio`, {
      method: 'POST',
      body: formData
    })
    
    if (response.ok) {
      const result = await response.json()
      showStatus('Audio đã được gửi thành công! ' + result.message, 'success')
    } else {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
  } catch (error) {
    console.error('Error sending audio:', error)
    showStatus('Lỗi khi gửi audio: ' + error.message, 'error')
  } finally {
    isProcessing.value = false
  }
}

// Show status message
const showStatus = (message, type) => {
  statusMessage.value = message
  statusType.value = type
  setTimeout(() => {
    statusMessage.value = ''
    statusType.value = ''
  }, 5000)
}
</script>

<style scoped>
.container {
  /* max-width: 800px; */
  /* margin: 0 auto; */
  /* padding: 20px; */
  font-family: 'Arial', sans-serif;
}

.main {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin-left: 25%;
}
.text-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 15px;
  height: 200px; /* Thêm dòng này */
}


h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.section {
  background: #f9f9f9;
  padding: 5px;
  margin: 5px 0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  width: 50vw; /* hoặc 60% viewport width */
  /* max-width: 800px; */
}

h2 {
  color: #555;
  margin-bottom: 15px;
}

.text-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 15px;
}

.text-input:focus {
  border-color: #007bff;
  outline: none;
}

.recording-controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #1e7e34;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
}

.btn-warning:hover:not(:disabled) {
  background-color: #e0a800;
}

.recording-status {
  background: #ffe6e6;
  color: #d63384;
  padding: 10px;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
  margin: 10px 0;
}

.audio-preview {
  margin-top: 15px;
}

.audio-preview h3 {
  margin-bottom: 10px;
  color: #555;
}

.audio-preview audio {
  width: 100%;
  max-width: 400px;
}

.status-message {
  padding: 12px;
  border-radius: 4px;
  margin: 15px 0;
  font-weight: bold;
}

.status-message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.status-message.info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* Sample Audio Styles */
.sample-audio-list {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 15px;
}

.sample-audio-item {
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
  width: 30%;
  height: 60%;
}

.sample-audio-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0,123,255,0.2);
}

.sample-audio-item.active {
  border-color: #28a745;
  background-color: #f8fff9;
}

.audio-info h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
}

.audio-info audio {
  width: 100%;
  margin-bottom: 10px;
}

.select-indicator {
  text-align: center;
  font-weight: bold;
  color: #666;
  font-size: 14px;
}

.sample-audio-item.active .select-indicator {
  color: #28a745;
}

/* Audio Selection Status Styles */
.audio-selection-status {
  background: #e9ecef;
  border-left: 4px solid #6c757d;
}

.selected-audio {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.audio-type {
  font-weight: bold;
  color: #495057;
}

.audio-name {
  flex: 1;
  color: #28a745;
  font-weight: 500;
}

.btn-clear {
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-clear:hover {
  background: #c82333;
}

.no-audio {
  text-align: center;
  color: #6c757d;
  font-style: italic;
  padding: 20px;
}

.warning {
  background-color: #fff3cd;
  color: #856404;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #ffeaa7;
  margin: 15px 0;
}

@media (max-width: 600px) {
  .container {
    padding: 10px;
  }
  
  .recording-controls {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
  
  .section {
    width: 90vw;
  }
  
  .selected-audio {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>