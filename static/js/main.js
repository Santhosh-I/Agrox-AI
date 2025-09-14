// Mobile Navigation
document.addEventListener('DOMContentLoaded', function() {
    const navHamburger = document.getElementById('navHamburger');
    const navMenu = document.getElementById('navMenu');

    if (navHamburger && navMenu) {
        navHamburger.addEventListener('click', function() {
            navHamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navHamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });

    // Animated counters for stats
    const animateCounters = () => {
        const counters = document.querySelectorAll('.stat-number');
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            const increment = target / 100;
            let current = 0;

            const updateCounter = () => {
                if (current < target) {
                    current += increment;
                    counter.textContent = Math.ceil(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };

            // Start animation when element is visible
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        updateCounter();
                        observer.unobserve(entry.target);
                    }
                });
            });

            observer.observe(counter);
        });
    };

    // Initialize counter animation
    animateCounters();

    // File upload handling
    const fileInput = document.getElementById('fileInput');
    const fileUploadDisplay = document.getElementById('fileUploadDisplay');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const removeImage = document.getElementById('removeImage');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                // Validate file type
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
                if (!validTypes.includes(file.type)) {
                    alert('Please select a valid image file (JPG, JPEG, or PNG)');
                    fileInput.value = '';
                    return;
                }

                // Validate file size (16MB max)
                const maxSize = 16 * 1024 * 1024;
                if (file.size > maxSize) {
                    alert('File size must be less than 16MB');
                    fileInput.value = '';
                    return;
                }

                // Show image preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    fileUploadDisplay.style.display = 'none';
                    imagePreview.classList.add('show');
                    analyzeBtn.disabled = false;
                };
                reader.readAsDataURL(file);
            }
        });

        // Remove image
        if (removeImage) {
            removeImage.addEventListener('click', function() {
                fileInput.value = '';
                previewImg.src = '';
                fileUploadDisplay.style.display = 'block';
                imagePreview.classList.remove('show');
                analyzeBtn.disabled = true;
            });
        }

        // Drag and drop functionality
        const uploadWrapper = document.querySelector('.file-upload-wrapper');
        
        if (uploadWrapper) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadWrapper.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                uploadWrapper.addEventListener(eventName, highlight, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                uploadWrapper.addEventListener(eventName, unhighlight, false);
            });

            function highlight(e) {
                uploadWrapper.style.border = '2px dashed var(--primary-green)';
            }

            function unhighlight(e) {
                uploadWrapper.style.border = '2px dashed var(--border-color)';
            }

            uploadWrapper.addEventListener('drop', handleDrop, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                
                if (files.length > 0) {
                    fileInput.files = files;
                    const event = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(event);
                }
            }
        }
    }

    // Form submission handling
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="loading"></i> Analyzing...';
                submitBtn.disabled = true;
            }
        });
    }

    // Voice Assistant Functionality
    const startListening = document.getElementById('startListening');
    const stopListening = document.getElementById('stopListening');
    const voiceStatus = document.getElementById('voiceStatus');
    const spokenText = document.getElementById('spokenText');
    const voiceVisualizer = document.getElementById('voiceVisualizer');

    let recognition = null;
    let isListening = false;

    // Check if Web Speech API is supported
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = function() {
            isListening = true;
            voiceStatus.innerHTML = '<p>Listening... Speak now!</p>';
            voiceVisualizer.classList.add('listening');
            startListening.style.display = 'none';
            stopListening.style.display = 'inline-flex';
        };

        recognition.onresult = function(event) {
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }

            if (finalTranscript) {
                spokenText.textContent = finalTranscript;
                processVoiceCommand(finalTranscript);
            }
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            voiceStatus.innerHTML = '<p>Error: ' + event.error + '</p>';
            resetVoiceInterface();
        };

        recognition.onend = function() {
            resetVoiceInterface();
        };
    }

    if (startListening) {
        startListening.addEventListener('click', function() {
            if (recognition) {
                recognition.start();
            } else {
                voiceStatus.innerHTML = '<p>Speech recognition not supported in this browser</p>';
            }
        });
    }

    if (stopListening) {
        stopListening.addEventListener('click', function() {
            if (recognition && isListening) {
                recognition.stop();
            }
        });
    }

    function resetVoiceInterface() {
        isListening = false;
        voiceVisualizer.classList.remove('listening');
        startListening.style.display = 'inline-flex';
        stopListening.style.display = 'none';
        voiceStatus.innerHTML = '<p>Click the microphone to start listening</p>';
    }

    function processVoiceCommand(command) {
        const lowerCommand = command.toLowerCase();
        
        // Send command to backend
        fetch('/api/voice_command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: lowerCommand })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                voiceStatus.innerHTML = '<p>' + data.message + '</p>';
                
                if (data.action === 'redirect' && data.url) {
                    setTimeout(() => {
                        window.location.href = data.url;
                    }, 1500);
                }
            }
        })
        .catch(error => {
            console.error('Error processing voice command:', error);
            voiceStatus.innerHTML = '<p>Error processing command</p>';
        });
    }

    // Contact form handling
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData.entries());
            
            // Simulate form submission (replace with actual backend endpoint)
            console.log('Contact form data:', data);
            
            // Show success message
            alert('Thank you for your message! We will get back to you soon.');
            contactForm.reset();
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-dismiss flash messages
    setTimeout(() => {
        const flashMessages = document.querySelector('.flash-messages');
        if (flashMessages) {
            flashMessages.style.opacity = '0';
            setTimeout(() => {
                flashMessages.remove();
            }, 300);
        }
    }, 5000);

    // Add loading state to buttons on click
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.type === 'submit' && !this.disabled) {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="loading"></i> Loading...';
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 3000);
            }
        });
    });
});

// Add CSS class for listening state
const style = document.createElement('style');
style.textContent = `
    .voice-visualizer.listening .pulse-circle {
        animation: pulse-ring 1s infinite;
        border-color: #00D084;
    }
    
    .voice-visualizer.listening .mic-icon {
        background: linear-gradient(45deg, #00D084, #4CAF50);
        animation: pulse 2s infinite;
    }
`;
document.head.appendChild(style);
