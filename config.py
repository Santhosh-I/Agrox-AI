import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'agrox-ai-secret-key-2025'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Model configuration
    MODEL_PATH = 'models/plant_disease_model.h5'
    IMAGE_SIZE = (224, 224)  # Adjust based on your model
    
    # Add more configuration as needed for IoT, Voice, etc.
