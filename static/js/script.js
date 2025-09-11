// AGROX AI Frontend JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupFileUpload();
    setupFormSubmission();
    setupAudioFeatures();
}

// File Upload Functionality
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

// Form Submission with Loading State
function setupFormSubmission() {
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('analyzeBtn');
    
    if (form && submitBtn) {
        form.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('imageInput');
            if (!fileInput.files.length) {
                e.preventDefault();
                showAlert('Please select an image file', 'error');
                return;
            }
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.classList.add('form-loading');
            document.body.style.cursor = 'wait';
        });
    }
}

// Audio Features for Results Page
function setupAudioFeatures() {
    // Text-to-Speech functionality will be set up here
    if (typeof resultData !== 'undefined') {
        setupResultsPage();
    }
}

function setupResultsPage() {
    // Animate confidence bar
    const confidenceFill = document.querySelector('.confidence-fill');
    if (confidenceFill) {
        setTimeout(() => {
            confidenceFill.style.width = resultData.confidence + '%';
        }, 500);
    }
}

// Enhanced Text-to-Speech Function
function speakResults() {
    if ('speechSynthesis' in window && typeof resultData !== 'undefined') {
        const speakBtn = document.getElementById('speakBtn');
        
        speakBtn.disabled = true;
        speakBtn.innerHTML = '🔇 Speaking...';
        
        const text = `Disease Analysis Complete. 
                     Detected condition: ${resultData.disease}. 
                     Confidence level: ${resultData.confidence} percent. 
                     Recommended treatment: ${resultData.treatment}. 
                     Recommended pesticide: ${resultData.pesticide}. 
                     Dosage: ${resultData.dosage}. 
                     Estimated cost: ${resultData.cost}.
                     Prevention: ${resultData.prevention}`;
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        
        utterance.onend = function() {
            speakBtn.disabled = false;
            speakBtn.innerHTML = '🔊 Play Audio';
        };
        
        speechSynthesis.speak(utterance);
    } else {
        showAlert('Text-to-speech not supported in this browser', 'error');
    }
}

// Download Report Function
function downloadReport() {
    if (typeof resultData !== 'undefined') {
        const reportContent = generateReportContent();
        const blob = new Blob([reportContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `agrox-ai-report-${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        showAlert('Report downloaded successfully', 'success');
    }
}

function generateReportContent() {
    return `
AGROX AI - PLANT DISEASE DETECTION REPORT
==========================================

Generated: ${new Date().toLocaleString()}

ANALYSIS RESULTS
----------------
Disease Detected: ${resultData.disease}
Confidence Level: ${resultData.confidence}%

RECOMMENDED TREATMENT
---------------------
${resultData.treatment}

PREVENTION MEASURES
-------------------
${resultData.prevention}

COST ESTIMATE
-------------
${resultData.cost}

DISCLAIMER
----------
This analysis is based on AI image recognition and should be used
as a reference only. For critical decisions, please consult with
agricultural experts or extension services.

Generated by AGROX AI
Smart Agricultural Solutions
Visit: [Your Website URL]
Contact: [Your Contact Information]
    `.trim();
}

// Alert System
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.flash-message');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `flash-message flash-${type}`;
    alertDiv.innerHTML = `
        <span class="flash-icon">${type === 'error' ? '⚠️' : '✅'}</span>
        ${message}
        <button class="flash-close" onclick="this.parentElement.style.display='none'">&times;</button>
    `;
    
    // Insert alert
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.style.opacity = '0';
                setTimeout(() => alertDiv.remove(), 300);
            }
        }, 5000);
    }
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Service Worker Registration (for PWA functionality)
// if ('serviceWorker' in navigator) {
//     window.addEventListener('load', function() {
//         navigator.serviceWorker.register('/static/sw.js')
//             .then(function(registration) {
//                 console.log('✅ ServiceWorker registered successfully');
//             })
//             .catch(function(err) {
//                 console.log('❌ ServiceWorker registration failed: ', err);
//             });
//     });
// }

// Global error handling
window.addEventListener('error', function(e) {
    console.error('Application error:', e.error);
    showAlert('An unexpected error occurred. Please refresh the page.', 'error');
});

// Network status monitoring
window.addEventListener('online', function() {
    showAlert('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showAlert('Connection lost - some features may be limited', 'error');
});
