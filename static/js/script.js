// Enhanced AGROX AI JavaScript with Chat Integration

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    animateSteps();
});

function initializeApp() {
    setupFileUpload();
    setupChatBot();
    setupVoiceAssistant();
    setupNavigation();
}

// Chat functionality
function askAI() {
    const chatInput = document.getElementById('chatInput');
    const question = chatInput.value.trim();
    
    if (!question) {
        showAlert('Please enter a question', 'error');
        return;
    }
    
    if (!resultData.llm_available) {
        showAlert('AI Assistant is offline', 'error');
        return;
    }
    
    // Add user message to chat
    addChatMessage('user', question);
    chatInput.value = '';
    
    // Show typing indicator
    const typingId = addChatMessage('ai', 'Thinking...', true);
    
    // Send to AI
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            context: {
                disease_name: resultData.disease,
                treatment: resultData.treatment,
                pesticide: resultData.pesticide,
                cost: resultData.cost
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove typing indicator
        removeTypingMessage(typingId);
        
        if (data.error) {
            addChatMessage('ai', `Sorry, there was an error: ${data.error}`);
        } else {
            addChatMessage('ai', data.response);
        }
    })
    .catch(error => {
        removeTypingMessage(typingId);
        addChatMessage('ai', 'Sorry, I could not process your request. Please try again.');
        console.error('Chat error:', error);
    });
}

function askSuggestion(question) {
    document.getElementById('chatInput').value = question;
    askAI();
}

function addChatMessage(sender, message, isTyping = false) {
    const chatHistory = document.getElementById('chatHistory');
    const messageDiv = document.createElement('div');
    const messageId = 'msg-' + Date.now();
    
    messageDiv.id = messageId;
    messageDiv.className = `chat-message ${sender}${isTyping ? ' typing' : ''}`;
    
    const icon = sender === 'user' ? '👤' : '🤖';
    const name = sender === 'user' ? 'You' : 'AI Assistant';
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-icon">${icon}</span>
            <strong class="message-sender">${name}</strong>
            <span class="message-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="message-content">
            ${isTyping ? '<div class="typing-dots"><span></span><span></span><span></span></div>' : message}
        </div>
    `;
    
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    return messageId;
}

function removeTypingMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// Enhanced text-to-speech with steps
function speakResults() {
    if ('speechSynthesis' in window && typeof resultData !== 'undefined') {
        const speakBtn = document.getElementById('speakBtn');
        
        speakBtn.disabled = true;
        speakBtn.innerHTML = '🔇 Speaking...';
        
        let audioText = `Disease Analysis Complete. 
                        Detected condition: ${resultData.disease}. 
                        Confidence level: ${resultData.confidence} percent. 
                        
                        Treatment recommendation: ${resultData.treatment}. 
                        Recommended pesticide: ${resultData.pesticide}. 
                        Dosage: ${resultData.dosage}. 
                        Estimated cost: ${resultData.cost}.
                        
                        Step by step instructions: `;
        
        // Add steps
        if (resultData.steps) {
            resultData.steps.forEach((step, index) => {
                audioText += `Step ${index + 1}: ${step}. `;
            });
        }
        
        audioText += `Best timing: ${resultData.timing}. 
                     Safety precautions: ${resultData.safety}. 
                     Prevention measures: ${resultData.prevention}.`;
        
        const utterance = new SpeechSynthesisUtterance(audioText);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        
        utterance.onend = function() {
            speakBtn.disabled = false;
            speakBtn.innerHTML = '🔊 Play Audio Guide';
        };
        
        utterance.onerror = function() {
            speakBtn.disabled = false;
            speakBtn.innerHTML = '🔊 Play Audio Guide';
            showAlert('Audio playback failed', 'error');
        };
        
        speechSynthesis.speak(utterance);
    } else {
        showAlert('Text-to-speech not supported in this browser', 'error');
    }
}

// Enhanced download report
function downloadReport() {
    if (typeof resultData !== 'undefined') {
        const reportContent = generateDetailedReport();
        const blob = new Blob([reportContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `agrox-ai-detailed-report-${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        showAlert('Detailed report downloaded successfully', 'success');
    }
}

function generateDetailedReport() {
    let stepsText = '';
    if (resultData.steps) {
        resultData.steps.forEach((step, index) => {
            stepsText += `${index + 1}. ${step}\n`;
        });
    }

    return `
AGROX AI - COMPREHENSIVE PLANT DISEASE DETECTION REPORT
======================================================

Generated: ${new Date().toLocaleString()}
Analysis Model: Advanced AI Disease Detection System
AI Assistant: ${resultData.llm_available ? 'Available' : 'Offline'}

DISEASE ANALYSIS RESULTS
========================
Detected Disease: ${resultData.disease}
Confidence Level: ${resultData.confidence}%
Analysis Accuracy: High Confidence Detection

TREATMENT RECOMMENDATIONS
=========================
Primary Treatment: ${resultData.treatment}
Recommended Pesticide: ${resultData.pesticide}
Precise Dosage: ${resultData.dosage}
Estimated Treatment Cost: ${resultData.cost}

STEP-BY-STEP APPLICATION INSTRUCTIONS
=====================================
${stepsText}

TIMING & SAFETY GUIDELINES
==========================
Optimal Application Timing:
${resultData.timing}

Essential Safety Precautions:
${resultData.safety}

PREVENTION STRATEGIES
====================
${resultData.prevention}

ADDITIONAL RESOURCES
===================
For video tutorials and detailed guidance:
- Search YouTube for disease-specific treatments
- Visit agricultural extension services
- Consult with local plant pathology experts

DISCLAIMER & EXPERT CONSULTATION
================================
This AI analysis provides preliminary diagnosis and treatment suggestions.
For critical decisions or persistent problems, please consult:
- Local agricultural extension officers
- Plant pathology specialists
- Certified crop advisors

The accuracy of this analysis is ${resultData.confidence}%. Always verify
with multiple sources before applying treatments to valuable crops.

ABOUT AGROX AI
==============
AGROX AI is an advanced agricultural intelligence platform that combines
machine learning, IoT monitoring, and expert knowledge to support farmers
in making informed crop management decisions.

For more information: Visit our platform
Contact: Agricultural Support Team

Report ID: ${Math.random().toString(36).substr(2, 9).toUpperCase()}
    `.trim();
}

// Animate step items
function animateSteps() {
    const stepItems = document.querySelectorAll('.step-item');
    stepItems.forEach((item, index) => {
        item.style.setProperty('--step-index', index);
        item.style.animationDelay = `${index * 0.1}s`;
    });
}

// File upload functionality
function setupFileUpload() {
    const fileInput = document.getElementById('imageInput');
    const filePreview = document.getElementById('filePreview');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                displayFilePreview(file, filePreview);
                validateFileSize(file);
            }
        });
    }
}

function displayFilePreview(file, previewContainer) {
    const reader = new FileReader();
    reader.onload = function(e) {
        previewContainer.innerHTML = `
            <div class="preview-content">
                <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 150px; border-radius: 8px;">
                <p><strong>File:</strong> ${file.name}</p>
                <p><strong>Size:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
        `;
        previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function validateFileSize(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        showAlert('File size must be less than 16MB', 'error');
        document.getElementById('imageInput').value = '';
        document.getElementById('filePreview').style.display = 'none';
    }
}

// Alert system
function showAlert(message, type = 'info') {
    const existingAlerts = document.querySelectorAll('.flash-message');
    existingAlerts.forEach(alert => alert.remove());
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `flash-message flash-${type}`;
    alertDiv.innerHTML = `
        <span class="flash-icon">${type === 'error' ? '⚠️' : '✅'}</span>
        ${message}
        <button class="flash-close" onclick="this.parentElement.style.display='none'">&times;</button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.style.opacity = '0';
                setTimeout(() => alertDiv.remove(), 300);
            }
        }, 5000);
    }
}

// Navigation setup
function setupNavigation() {
    // Add any navigation-specific functionality here
}

// Voice assistant setup
function setupVoiceAssistant() {
    // Add voice assistant functionality here if needed
}

// Initialize chat input events
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                askAI();
            }
        });
    }
});


// ✅ Fixed browser recording with supported format
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                sampleRate: 44100,  // Use standard sample rate
                channelCount: 1,    // Mono audio
                echoCancellation: true,
                noiseSuppression: true
            }
        });
        
        // ✅ Use supported MIME type
        let options = { mimeType: 'audio/webm;codecs=opus' };
        
        // ✅ Fallback for different browsers
        if (!MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            if (MediaRecorder.isTypeSupported('audio/webm')) {
                options = { mimeType: 'audio/webm' };
            } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
                options = { mimeType: 'audio/ogg;codecs=opus' };
            } else {
                options = {}; // Use browser default
            }
        }
        
        mediaRecorder = new MediaRecorder(stream, options);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: options.mimeType || 'audio/webm' });
            sendAudioToServer(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        updateRecordingUI(true);

    } catch (error) {
        console.error('Recording setup error:', error);
        alert('Microphone access denied. Please enable microphone permissions and refresh the page.');
    }
}


