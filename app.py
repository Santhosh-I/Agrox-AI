from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'agrox-ai-secret-key-2025'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load your trained model (using your working approach)
print("Loading AI model...")
try:
    model = load_model('model/plant_disease_model.h5')  # Using your path
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# Your comprehensive disease information (from your working project)
disease_info = {
    # 🍎 Apple
    "Apple__Apple_scab": {
        "pesticide": "Captan",
        "dosage": "1.5 g/litre",
        "cost": "₹40",
        "treatment": "Apply Captan fungicide spray",
        "prevention": "Improve air circulation, remove infected leaves"
    },
    "Apple__Black_rot": {
        "pesticide": "Thiophanate-methyl",
        "dosage": "1 g/litre", 
        "cost": "₹50",
        "treatment": "Apply Thiophanate-methyl fungicide",
        "prevention": "Prune infected branches, avoid wounding fruit"
    },
    "Apple__Cedar_apple_rust": {
        "pesticide": "Myclobutanil",
        "dosage": "0.5 g/litre",
        "cost": "₹30",
        "treatment": "Apply Myclobutanil during spring",
        "prevention": "Remove nearby cedar trees if possible"
    },
    "Apple__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring"
    },

    # 🌽 Corn (Maize)
    "Corn_(maize)__Cercospora_leaf_spot Gray_leaf_spot": {
        "pesticide": "Propiconazole",
        "dosage": "1 ml/litre",
        "cost": "₹40",
        "treatment": "Apply Propiconazole fungicide spray",
        "prevention": "Crop rotation, avoid overhead irrigation"
    },
    "Corn_(maize)__Common_rust_": {
        "pesticide": "Azoxystrobin",
        "dosage": "1 ml/litre",
        "cost": "₹45",
        "treatment": "Apply Azoxystrobin at early infection stage",
        "prevention": "Plant resistant varieties, avoid late planting"
    },
    "Corn_(maize)__Northern_Leaf_Blight": {
        "pesticide": "Tebuconazole",
        "dosage": "1 ml/litre",
        "cost": "₹50",
        "treatment": "Apply Tebuconazole fungicide",
        "prevention": "Use resistant hybrids, crop rotation"
    },
    "Corn_(maize)__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring"
    },

    # 🍇 Grape
    "Grape__Black_rot": {
        "pesticide": "Mancozeb",
        "dosage": "2 g/litre",
        "cost": "₹35",
        "treatment": "Apply Mancozeb fungicide spray",
        "prevention": "Remove mummified berries, improve air circulation"
    },
    "Grape__Esca_(Black_Measles)": {
        "pesticide": "No effective cure – prune infected vines",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "Prune infected parts, no chemical cure available",
        "prevention": "Avoid wounding, proper pruning techniques"
    },
    "Grape__Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "pesticide": "Copper Oxychloride",
        "dosage": "2 g/litre",
        "cost": "₹40",
        "treatment": "Apply Copper Oxychloride spray",
        "prevention": "Improve air circulation, avoid overhead watering"
    },
    "Grape__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring"
    },

    # 🌶️ Pepper Bell
    "Pepper__bell__Bacterial_spot": {
        "pesticide": "Copper Hydroxide",
        "dosage": "2 g/litre",
        "cost": "₹45",
        "treatment": "Apply Copper Hydroxide spray",
        "prevention": "Use certified seeds, avoid overhead irrigation"
    },
    "Pepper__bell__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring"
    },

    # 🥔 Potato
    "Potato__Early_blight": {
        "pesticide": "Chlorothalonil",
        "dosage": "2 ml/litre",
        "cost": "₹50",
        "treatment": "Apply Chlorothalonil fungicide",
        "prevention": "Crop rotation, remove plant debris"
    },
    "Potato__Late_blight": {
        "pesticide": "Metalaxyl + Mancozeb",
        "dosage": "2.5 g/litre",
        "cost": "₹60",
        "treatment": "Apply Metalaxyl + Mancozeb combination",
        "prevention": "Avoid overhead watering, ensure good ventilation"
    },
    "Potato__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring"
    },

    # 🍅 Tomato
    "Tomato__Bacterial_spot": {
        "pesticide": "Copper Hydroxide",
        "dosage": "2 g/litre",
        "cost": "₹45",
        "treatment": "Apply Copper Hydroxide spray",
        "prevention": "Use certified seeds, avoid overhead irrigation"
    },
    "Tomato__Early_blight": {
        "pesticide": "Chlorothalonil",
        "dosage": "2 ml/litre",
        "cost": "₹50",
        "treatment": "Apply Chlorothalonil fungicide",
        "prevention": "Crop rotation, remove infected debris"
    },
    "Tomato__Late_blight": {
        "pesticide": "Metalaxyl + Mancozeb",
        "dosage": "2.5 g/litre",
        "cost": "₹60",
        "treatment": "Apply Metalaxyl + Mancozeb combination",
        "prevention": "Avoid overhead watering, ensure good ventilation"
    },
    "Tomato__Leaf_Mold": {
        "pesticide": "Copper Fungicide",
        "dosage": "2 g/litre",
        "cost": "₹40",
        "treatment": "Apply Copper-based fungicide",
        "prevention": "Improve greenhouse ventilation"
    },
    "Tomato__Septoria_leaf_spot": {
        "pesticide": "Mancozeb",
        "dosage": "2 g/litre",
        "cost": "₹45",
        "treatment": "Apply Mancozeb fungicide spray",
        "prevention": "Avoid overhead watering, crop rotation"
    },
    "Tomato__Spider_mites_Two-spotted_spider_mite": {
        "pesticide": "Abamectin or Neem Oil",
        "dosage": "1 ml/litre",
        "cost": "₹30",
        "treatment": "Apply Abamectin or organic Neem Oil",
        "prevention": "Maintain proper humidity, avoid drought stress"
    },
    "Tomato__Target_Spot": {
        "pesticide": "Azoxystrobin",
        "dosage": "1 ml/litre",
        "cost": "₹55",
        "treatment": "Apply Azoxystrobin fungicide",
        "prevention": "Improve air circulation, avoid leaf wetness"
    },
    "Tomato__Tomato_mosaic_virus": {
        "pesticide": "No cure – remove infected plants",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "Remove and destroy infected plants",
        "prevention": "Use certified seeds, control aphid vectors"
    },
    "Tomato__Tomato_Yellow_Leaf_Curl_Virus": {
        "pesticide": "Imidacloprid (for whiteflies)",
        "dosage": "0.5 ml/litre",
        "cost": "₹30",
        "treatment": "Control whiteflies with Imidacloprid",
        "prevention": "Use reflective mulches, control whitefly population"
    },
    "Tomato__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring"
    }
}

# Your disease classes (from your working model)
classes = list(disease_info.keys())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path, target_size=(224, 224)):
    """Preprocess image using your working approach"""
    try:
        img_tensor = image.load_img(image_path, target_size=target_size)
        img_tensor = image.img_to_array(img_tensor) / 255.0
        img_tensor = np.expand_dims(img_tensor, axis=0)
        return img_tensor
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def get_disease_info(disease_name):
    """Get comprehensive treatment information"""
    info = disease_info.get(disease_name, {
        'pesticide': 'Consult agricultural expert',
        'dosage': 'N/A',
        'cost': 'Varies',
        'treatment': 'Consult with agricultural expert for specific treatment',
        'prevention': 'Monitor plant health regularly'
    })
    return info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect_disease():
    if 'image' not in request.files:
        flash('No image file uploaded', 'error')
        return redirect(url_for('index'))

    file = request.files['image']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('Please upload a valid image file (PNG, JPG, JPEG, GIF)', 'error')
        return redirect(url_for('index'))

    if model is None:
        flash('AI model not available. Please try again later.', 'error')
        return redirect(url_for('index'))

    try:
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Preprocess image using your working method
        processed_image = preprocess_image(filepath)
        if processed_image is None:
            flash('Error processing image. Please try another image.', 'error')
            return redirect(url_for('index'))

        # Make prediction using your working approach
        pred = model.predict(processed_image)[0]
        pred_idx = np.argmax(pred)
        confidence = float(np.max(pred) * 100)
        
        # Get disease name and comprehensive info
        disease_name = classes[pred_idx]
        disease_data = get_disease_info(disease_name)
        
        # Prepare result data for the professional UI
        result = {
            'disease_name': disease_name.replace("__", " → ").replace("_(", " ("),
            'confidence': round(confidence, 2),
            'image_path': f'uploads/{filename}',
            'treatment': disease_data['treatment'],
            'prevention': disease_data['prevention'],
            'pesticide': disease_data['pesticide'],
            'dosage': disease_data['dosage'],
            'cost': disease_data['cost'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return render_template('detect.html', result=result)

    except Exception as e:
        print(f"Error during prediction: {e}")
        flash('Error analyzing image. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'total_diseases': len(classes),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
