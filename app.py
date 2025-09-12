from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from datetime import datetime
import uuid
import requests
import json

app = Flask(__name__)
app.secret_key = 'agrox-ai-secret-key-2025'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# LLM Configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "mistral"
LLM_AVAILABLE = False

# Test LLM availability
def test_llm_connection():
    try:
        response = requests.get("http://127.0.0.1:11434/api/version", timeout=5)
        return response.status_code == 200
    except:
        return False

LLM_AVAILABLE = test_llm_connection()
print(f"🤖 LLM Status: {'Available' if LLM_AVAILABLE else 'Offline - Using Database Only'}")

# Load ML model
print("Loading AI model...")
try:
    model = load_model('model/plant_disease_model.h5')
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# Enhanced disease information with step-by-step instructions
disease_info = {
    # 🍎 Apple Diseases
    "Apple__Apple_scab": {
        "pesticide": "Captan",
        "dosage": "1.5 g/litre",
        "cost": "₹40",
        "treatment": "Apply Captan fungicide spray",
        "prevention": "Improve air circulation, remove infected leaves",
        "steps": [
            "Mix 1.5g Captan with 1 liter of clean water",
            "Add a few drops of liquid soap as sticking agent",
            "Spray early morning or evening (avoid midday heat)",
            "Cover all leaf surfaces, especially undersides",
            "Repeat application after 10-14 days if needed",
            "Always wear protective gear during application"
        ],
        "timing": "Apply during cool hours (6-10 AM or 4-7 PM)",
        "safety": "Wear gloves, mask, and protective clothing. Avoid spraying on windy days.",
        "youtube_videos": [
            {"title": "Apple Scab Treatment Guide", "url": "https://www.youtube.com/results?search_query=apple+scab+fungicide+treatment"},
            {"title": "Fungicide Application Tips", "url": "https://www.youtube.com/results?search_query=captan+fungicide+application"}
        ]
    },
    
    "Apple__Black_rot": {
        "pesticide": "Thiophanate-methyl",
        "dosage": "1 g/litre", 
        "cost": "₹50",
        "treatment": "Apply Thiophanate-methyl fungicide",
        "prevention": "Prune infected branches, avoid wounding fruit",
        "steps": [
            "Dissolve 1g Thiophanate-methyl in 1 liter water",
            "Stir thoroughly until completely dissolved",
            "Apply as foliar spray covering entire plant",
            "Focus on fruit clusters and new growth",
            "Reapply every 15 days during growing season",
            "Remove and destroy infected plant parts"
        ],
        "timing": "Apply preventively before fruit formation",
        "safety": "Use protective equipment. Do not apply during flowering to protect bees.",
        "youtube_videos": [
            {"title": "Apple Black Rot Treatment", "url": "https://www.youtube.com/results?search_query=apple+black+rot+treatment+guide"},
            {"title": "Thiophanate-methyl Application", "url": "https://www.youtube.com/results?search_query=thiophanate+methyl+fungicide+usage"}
        ]
    },

    "Apple__Cedar_apple_rust": {
        "pesticide": "Myclobutanil",
        "dosage": "0.5 g/litre",
        "cost": "₹30",
        "treatment": "Apply Myclobutanil during spring",
        "prevention": "Remove nearby cedar trees if possible",
        "steps": [
            "Mix 0.5g Myclobutanil in 1 liter clean water",
            "Apply during early spring before symptoms appear",
            "Ensure complete coverage of all plant surfaces",
            "Repeat every 14-21 days during infection period",
            "Focus spraying on new growth and buds",
            "Wear protective clothing during application"
        ],
        "timing": "Best applied in early spring before bud break",
        "safety": "Avoid contact with skin and eyes. Use in well-ventilated areas.",
        "youtube_videos": [
            {"title": "Cedar Apple Rust Control", "url": "https://www.youtube.com/results?search_query=cedar+apple+rust+fungicide+control"},
            {"title": "Myclobutanil Usage Guide", "url": "https://www.youtube.com/results?search_query=myclobutanil+fungicide+application"}
        ]
    },

    "Apple__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring",
        "steps": [
            "Plant appears healthy - no treatment required",
            "Continue good agricultural practices",
            "Monitor regularly for early disease detection",
            "Maintain proper spacing for air circulation",
            "Water at soil level to avoid leaf wetness",
            "Remove fallen leaves to prevent fungal buildup"
        ],
        "timing": "Regular monitoring recommended weekly",
        "safety": "No chemical application needed",
        "youtube_videos": [
            {"title": "Healthy Apple Tree Care", "url": "https://www.youtube.com/results?search_query=healthy+apple+tree+maintenance+tips"},
            {"title": "Apple Tree Disease Prevention", "url": "https://www.youtube.com/results?search_query=apple+tree+disease+prevention"}
        ]
    },

    # 🌽 Corn (Maize) Diseases
    "Corn_(maize)__Cercospora_leaf_spot Gray_leaf_spot": {
        "pesticide": "Propiconazole",
        "dosage": "1 ml/litre",
        "cost": "₹40",
        "treatment": "Apply Propiconazole fungicide spray",
        "prevention": "Crop rotation, avoid overhead irrigation",
        "steps": [
            "Mix 1ml Propiconazole per liter of water",
            "Apply when first symptoms appear on lower leaves",
            "Spray thoroughly covering both leaf surfaces",
            "Repeat application every 10-14 days",
            "Focus on lower canopy where disease starts",
            "Use adequate water volume for good coverage"
        ],
        "timing": "Apply at first sign of spots, usually mid-season",
        "safety": "Wear respirator and gloves. Avoid drift to sensitive crops.",
        "youtube_videos": [
            {"title": "Corn Gray Leaf Spot Management", "url": "https://www.youtube.com/results?search_query=corn+gray+leaf+spot+fungicide+treatment"},
            {"title": "Propiconazole Application", "url": "https://www.youtube.com/results?search_query=propiconazole+fungicide+corn"}
        ]
    },

    "Corn_(maize)__Common_rust_": {
        "pesticide": "Azoxystrobin",
        "dosage": "1 ml/litre",
        "cost": "₹45",
        "treatment": "Apply Azoxystrobin at early infection stage",
        "prevention": "Plant resistant varieties, avoid late planting",
        "steps": [
            "Add 1ml Azoxystrobin to 1 liter water",
            "Include surfactant for better leaf penetration",
            "Apply when first rust pustules appear",
            "Cover both leaf surfaces thoroughly",
            "Time application before silking stage",
            "Monitor weather for reapplication needs"
        ],
        "timing": "Apply at early reproductive stages when rust first appears",
        "safety": "Low toxicity but use standard precautions. Avoid application before rain.",
        "youtube_videos": [
            {"title": "Corn Rust Disease Control", "url": "https://www.youtube.com/results?search_query=corn+rust+fungicide+azoxystrobin+spray"},
            {"title": "Corn Disease Management", "url": "https://www.youtube.com/results?search_query=corn+disease+management+techniques"}
        ]
    },

    "Corn_(maize)__Northern_Leaf_Blight": {
        "pesticide": "Tebuconazole",
        "dosage": "1 ml/litre",
        "cost": "₹50",
        "treatment": "Apply Tebuconazole fungicide",
        "prevention": "Use resistant hybrids, crop rotation",
        "steps": [
            "Mix 1ml Tebuconazole in 1 liter water",
            "Apply at first appearance of lesions",
            "Ensure thorough coverage of plant canopy",
            "Repeat every 14 days if conditions favor disease",
            "Focus on upper leaves during tasseling",
            "Use appropriate spray volume for penetration"
        ],
        "timing": "Apply when lesions first appear, usually pre-tasseling",
        "safety": "Moderately toxic. Use protective equipment and avoid inhalation.",
        "youtube_videos": [
            {"title": "Northern Leaf Blight Control", "url": "https://www.youtube.com/results?search_query=corn+northern+leaf+blight+fungicide"},
            {"title": "Tebuconazole Fungicide Use", "url": "https://www.youtube.com/results?search_query=tebuconazole+fungicide+application+corn"}
        ]
    },

    "Corn_(maize)__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring",
        "steps": [
            "Corn plants appear healthy - maintain good practices",
            "Monitor for pest and disease symptoms weekly",
            "Ensure adequate nutrition and water management",
            "Practice crop rotation to prevent soil-borne diseases",
            "Remove volunteer plants that can harbor diseases",
            "Keep field edges clean of weeds and debris"
        ],
        "timing": "Regular field monitoring throughout growing season",
        "safety": "No chemical application needed",
        "youtube_videos": [
            {"title": "Healthy Corn Production", "url": "https://www.youtube.com/results?search_query=healthy+corn+crop+management+tips"},
            {"title": "Corn Disease Prevention", "url": "https://www.youtube.com/results?search_query=corn+disease+prevention+strategies"}
        ]
    },

    # 🍇 Grape Diseases
    "Grape__Black_rot": {
        "pesticide": "Mancozeb",
        "dosage": "2 g/litre",
        "cost": "₹35",
        "treatment": "Apply Mancozeb fungicide spray",
        "prevention": "Remove mummified berries, improve air circulation",
        "steps": [
            "Mix 2g Mancozeb in 1 liter water with continuous stirring",
            "Apply protective sprays before infection periods",
            "Cover all green tissues thoroughly",
            "Start applications at bud break",
            "Repeat every 7-14 days during wet weather",
            "Remove and destroy infected berries"
        ],
        "timing": "Begin at bud break, continue through fruit development",
        "safety": "Wear protective clothing. May cause skin irritation.",
        "youtube_videos": [
            {"title": "Grape Black Rot Management", "url": "https://www.youtube.com/results?search_query=grape+black+rot+mancozeb+treatment"},
            {"title": "Grape Disease Control", "url": "https://www.youtube.com/results?search_query=grape+fungicide+application+techniques"}
        ]
    },

    "Grape__Esca_(Black_Measles)": {
        "pesticide": "No effective cure – prune infected vines",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "Prune infected parts, no chemical cure available",
        "prevention": "Avoid wounding, proper pruning techniques",
        "steps": [
            "Remove infected wood during dormant season",
            "Make clean cuts with sterilized tools",
            "Seal large pruning wounds with wound paste",
            "Remove infected berries and leaves",
            "Burn or bury all infected plant material",
            "Avoid mechanical damage to trunks and cordons"
        ],
        "timing": "Prune during dormant season (winter)",
        "safety": "Sterilize tools between cuts to prevent spread",
        "youtube_videos": [
            {"title": "Grape Esca Disease Management", "url": "https://www.youtube.com/results?search_query=grape+esca+disease+pruning+management"},
            {"title": "Grape Pruning Techniques", "url": "https://www.youtube.com/results?search_query=grape+pruning+disease+prevention"}
        ]
    },

    "Grape__Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "pesticide": "Copper Oxychloride",
        "dosage": "2 g/litre",
        "cost": "₹40",
        "treatment": "Apply Copper Oxychloride spray",
        "prevention": "Improve air circulation, avoid overhead watering",
        "steps": [
            "Mix 2g Copper Oxychloride in 1 liter water",
            "Add spreader-sticker for better adhesion",
            "Apply during early morning or late evening",
            "Cover both upper and lower leaf surfaces",
            "Repeat every 10-14 days during humid conditions",
            "Remove severely infected leaves"
        ],
        "timing": "Apply preventively before rainy season",
        "safety": "Copper can cause phytotoxicity. Use recommended rates only.",
        "youtube_videos": [
            {"title": "Grape Leaf Spot Control", "url": "https://www.youtube.com/results?search_query=grape+leaf+spot+copper+fungicide"},
            {"title": "Copper Fungicide Application", "url": "https://www.youtube.com/results?search_query=copper+oxychloride+fungicide+grapes"}
        ]
    },

    "Grape__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring",
        "steps": [
            "Vines appear healthy - maintain preventive practices",
            "Ensure good air circulation through proper pruning",
            "Monitor for early signs of disease development",
            "Practice good canopy management",
            "Remove water sprouts and suckers regularly",
            "Keep vineyard floor clean of fallen leaves"
        ],
        "timing": "Regular vineyard monitoring throughout growing season",
        "safety": "No chemical application needed",
        "youtube_videos": [
            {"title": "Healthy Grape Production", "url": "https://www.youtube.com/results?search_query=healthy+grape+vineyard+management"},
            {"title": "Grape Disease Prevention", "url": "https://www.youtube.com/results?search_query=grape+disease+prevention+practices"}
        ]
    },

    # 🌶️ Pepper Bell Diseases
    "Pepper__bell__Bacterial_spot": {
        "pesticide": "Copper Hydroxide",
        "dosage": "2 g/litre",
        "cost": "₹45",
        "treatment": "Apply Copper Hydroxide spray",
        "prevention": "Use certified seeds, avoid overhead irrigation",
        "steps": [
            "Mix 2g Copper Hydroxide in 1 liter water",
            "Add spreader for better coverage",
            "Apply when weather conditions favor disease",
            "Cover all plant surfaces including stems",
            "Repeat every 5-7 days during wet weather",
            "Avoid spraying during hot sunny conditions"
        ],
        "timing": "Begin applications before disease symptoms appear",
        "safety": "Copper can be phytotoxic in hot weather. Apply during cool hours.",
        "youtube_videos": [
            {"title": "Pepper Bacterial Spot Control", "url": "https://www.youtube.com/results?search_query=pepper+bacterial+spot+copper+treatment"},
            {"title": "Pepper Disease Management", "url": "https://www.youtube.com/results?search_query=bell+pepper+disease+control+methods"}
        ]
    },

    "Pepper__bell__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring",
        "steps": [
            "Pepper plants are healthy - continue good practices",
            "Monitor for insect pests that can spread diseases",
            "Ensure adequate spacing between plants",
            "Water at soil level to keep foliage dry",
            "Remove weeds that can harbor diseases",
            "Practice crop rotation with non-related crops"
        ],
        "timing": "Weekly monitoring throughout growing season",
        "safety": "No chemical application needed",
        "youtube_videos": [
            {"title": "Healthy Pepper Production", "url": "https://www.youtube.com/results?search_query=healthy+bell+pepper+cultivation"},
            {"title": "Pepper Plant Care", "url": "https://www.youtube.com/results?search_query=bell+pepper+plant+maintenance"}
        ]
    },

    # 🥔 Potato Diseases
    "Potato__Early_blight": {
        "pesticide": "Chlorothalonil",
        "dosage": "2 ml/litre",
        "cost": "₹50",
        "treatment": "Apply Chlorothalonil fungicide",
        "prevention": "Crop rotation, remove plant debris",
        "steps": [
            "Measure 2ml Chlorothalonil per liter of water",
            "Mix in spray tank with gentle agitation",
            "Test spray pattern before full application",
            "Apply systematic coverage from bottom to top",
            "Ensure spray reaches inner plant canopy",
            "Repeat every 10-14 days during disease pressure"
        ],
        "timing": "Apply before symptoms appear or at first sign of disease",
        "safety": "Moderately toxic - avoid inhalation and skin contact.",
        "youtube_videos": [
            {"title": "Potato Early Blight Management", "url": "https://www.youtube.com/results?search_query=potato+early+blight+chlorothalonil+treatment"},
            {"title": "Potato Disease Control", "url": "https://www.youtube.com/results?search_query=potato+fungicide+spray+techniques"}
        ]
    },

    "Potato__Late_blight": {
        "pesticide": "Metalaxyl + Mancozeb",
        "dosage": "2.5 g/litre",
        "cost": "₹60",
        "treatment": "Apply Metalaxyl + Mancozeb combination",
        "prevention": "Avoid overhead watering, ensure good ventilation",
        "steps": [
            "Mix 2.5g Metalaxyl+Mancozeb in 1 liter water",
            "Add spreader-sticker for better coverage",
            "Spray during early morning hours",
            "Ensure complete coverage of stems and leaves",
            "Focus on lower leaves where disease starts",
            "Apply every 7-10 days during humid conditions"
        ],
        "timing": "Apply preventively during humid weather or at first sign of disease",
        "safety": "Highly toxic - use full protective gear. Keep away from water sources.",
        "youtube_videos": [
            {"title": "Potato Late Blight Control", "url": "https://www.youtube.com/results?search_query=potato+late+blight+metalaxyl+mancozeb"},
            {"title": "Potato Blight Prevention", "url": "https://www.youtube.com/results?search_query=potato+blight+prevention+strategies"}
        ]
    },

    "Potato__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring",
        "steps": [
            "Potato crop appears healthy - maintain good practices",
            "Monitor fields regularly for disease symptoms",
            "Ensure proper hilling to protect tubers",
            "Practice crop rotation with non-host crops",
            "Remove volunteer potato plants",
            "Keep field edges free of weeds and debris"
        ],
        "timing": "Regular field monitoring twice weekly",
        "safety": "No chemical application needed",
        "youtube_videos": [
            {"title": "Healthy Potato Production", "url": "https://www.youtube.com/results?search_query=healthy+potato+crop+management"},
            {"title": "Potato Disease Prevention", "url": "https://www.youtube.com/results?search_query=potato+disease+prevention+tips"}
        ]
    },

    # 🍅 Tomato Diseases
    "Tomato__Bacterial_spot": {
        "pesticide": "Copper Hydroxide",
        "dosage": "2 g/litre",
        "cost": "₹45",
        "treatment": "Apply Copper Hydroxide spray",
        "prevention": "Use certified seeds, avoid overhead irrigation",
        "steps": [
            "Mix 2g Copper Hydroxide in 1 liter water",
            "Add spreader for improved coverage",
            "Apply during cool morning hours",
            "Cover all plant surfaces including fruit",
            "Repeat every 5-7 days during favorable conditions",
            "Remove severely infected plant parts"
        ],
        "timing": "Begin preventive applications before symptoms appear",
        "safety": "May cause leaf burn in hot weather. Apply during cool hours.",
        "youtube_videos": [
            {"title": "Tomato Bacterial Spot Control", "url": "https://www.youtube.com/results?search_query=tomato+bacterial+spot+copper+treatment"},
            {"title": "Tomato Disease Management", "url": "https://www.youtube.com/results?search_query=tomato+disease+control+methods"}
        ]
    },

    "Tomato__Early_blight": {
        "pesticide": "Chlorothalonil",
        "dosage": "2 ml/litre",
        "cost": "₹50",
        "treatment": "Apply Chlorothalonil fungicide",
        "prevention": "Crop rotation, remove infected debris",
        "steps": [
            "Mix 2ml Chlorothalonil per liter water",
            "Begin applications when plants are established",
            "Apply thorough coverage to all foliage",
            "Focus on lower leaves where disease starts",
            "Repeat every 7-10 days during humid periods",
            "Remove infected leaves promptly"
        ],
        "timing": "Start preventive sprays 4-6 weeks after transplanting",
        "safety": "Use protective equipment. Avoid spray drift to sensitive plants.",
        "youtube_videos": [
            {"title": "Tomato Early Blight Treatment", "url": "https://www.youtube.com/results?search_query=tomato+early+blight+fungicide+spray"},
            {"title": "Chlorothalonil Application", "url": "https://www.youtube.com/results?search_query=chlorothalonil+fungicide+tomato"}
        ]
    },

    "Tomato__Late_blight": {
        "pesticide": "Metalaxyl + Mancozeb",
        "dosage": "2.5 g/litre",
        "cost": "₹60",
        "treatment": "Apply Metalaxyl + Mancozeb combination",
        "prevention": "Avoid overhead watering, ensure good ventilation",
        "steps": [
            "Mix 2.5g Metalaxyl+Mancozeb in 1 liter water",
            "Add spreader-sticker for better coverage",
            "Spray during early morning hours",
            "Ensure complete coverage of stems and leaves",
            "Focus on lower leaves where disease starts",
            "Apply every 7-10 days during humid conditions"
        ],
        "timing": "Apply preventively during humid weather or at first sign of disease",
        "safety": "Highly toxic - use full protective gear. Keep away from water sources.",
        "youtube_videos": [
            {"title": "Tomato Late Blight Control", "url": "https://www.youtube.com/results?search_query=tomato+late+blight+metalaxyl+treatment"},
            {"title": "Fungicide Safety Guidelines", "url": "https://www.youtube.com/results?search_query=pesticide+safety+application"}
        ]
    },

    "Tomato__Leaf_Mold": {
        "pesticide": "Copper Fungicide",
        "dosage": "2 g/litre",
        "cost": "₹40",
        "treatment": "Apply Copper-based fungicide",
        "prevention": "Improve greenhouse ventilation",
        "steps": [
            "Mix 2g Copper fungicide in 1 liter water",
            "Apply when humidity is high in greenhouse",
            "Cover lower leaf surfaces thoroughly",
            "Increase ventilation to reduce humidity",
            "Remove lower leaves touching soil",
            "Apply every 7-14 days as needed"
        ],
        "timing": "Apply when environmental conditions favor disease",
        "safety": "Avoid applications during hot weather to prevent phytotoxicity.",
        "youtube_videos": [
            {"title": "Tomato Leaf Mold Control", "url": "https://www.youtube.com/results?search_query=tomato+leaf+mold+copper+fungicide"},
            {"title": "Greenhouse Tomato Diseases", "url": "https://www.youtube.com/results?search_query=greenhouse+tomato+disease+control"}
        ]
    },

    "Tomato__Septoria_leaf_spot": {
        "pesticide": "Mancozeb",
        "dosage": "2 g/litre",
        "cost": "₹45",
        "treatment": "Apply Mancozeb fungicide spray",
        "prevention": "Avoid overhead watering, crop rotation",
        "steps": [
            "Mix 2g Mancozeb in 1 liter water",
            "Begin applications early in growing season",
            "Apply thorough coverage to all foliage",
            "Focus on lower leaves first affected",
            "Repeat every 10-14 days during wet weather",
            "Remove infected leaves and debris"
        ],
        "timing": "Start preventive applications early in season",
        "safety": "May cause skin irritation. Use gloves and protective clothing.",
        "youtube_videos": [
            {"title": "Septoria Leaf Spot Management", "url": "https://www.youtube.com/results?search_query=tomato+septoria+leaf+spot+mancozeb"},
            {"title": "Tomato Leaf Disease Control", "url": "https://www.youtube.com/results?search_query=tomato+leaf+disease+fungicide"}
        ]
    },

    "Tomato__Spider_mites_Two-spotted_spider_mite": {
        "pesticide": "Abamectin or Neem Oil",
        "dosage": "1 ml/litre",
        "cost": "₹30",
        "treatment": "Apply Abamectin or organic Neem Oil",
        "prevention": "Maintain proper humidity, avoid drought stress",
        "steps": [
            "Mix 1ml Abamectin or Neem Oil in 1 liter water",
            "Add spreader for better coverage",
            "Spray undersides of leaves thoroughly",
            "Apply during early morning or evening",
            "Repeat every 7-10 days until control achieved",
            "Monitor for beneficial insects"
        ],
        "timing": "Apply at first sign of mite activity",
        "safety": "Neem oil is safer option. Abamectin requires protective equipment.",
        "youtube_videos": [
            {"title": "Spider Mite Control on Tomatoes", "url": "https://www.youtube.com/results?search_query=tomato+spider+mite+control+abamectin"},
            {"title": "Neem Oil Application", "url": "https://www.youtube.com/results?search_query=neem+oil+spray+spider+mites"}
        ]
    },

    "Tomato__Target_Spot": {
        "pesticide": "Azoxystrobin",
        "dosage": "1 ml/litre",
        "cost": "₹55",
        "treatment": "Apply Azoxystrobin fungicide",
        "prevention": "Improve air circulation, avoid leaf wetness",
        "steps": [
            "Mix 1ml Azoxystrobin in 1 liter water",
            "Include spreader-sticker for better retention",
            "Apply when disease pressure is high",
            "Cover all foliage including fruit",
            "Repeat every 14 days during humid conditions",
            "Rotate with other fungicide modes of action"
        ],
        "timing": "Apply preventively during warm, humid weather",
        "safety": "Low mammalian toxicity. Use standard protective measures.",
        "youtube_videos": [
            {"title": "Tomato Target Spot Control", "url": "https://www.youtube.com/results?search_query=tomato+target+spot+azoxystrobin"},
            {"title": "Strobilurin Fungicides", "url": "https://www.youtube.com/results?search_query=azoxystrobin+fungicide+application"}
        ]
    },

    "Tomato__Tomato_mosaic_virus": {
        "pesticide": "No cure – remove infected plants",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "Remove and destroy infected plants",
        "prevention": "Use certified seeds, control aphid vectors",
        "steps": [
            "Remove infected plants immediately",
            "Burn or bury infected plant material deeply",
            "Disinfect tools with 10% bleach solution",
            "Control aphids and other virus vectors",
            "Use virus-free certified seeds",
            "Avoid tobacco use near tomato plants"
        ],
        "timing": "Remove infected plants as soon as symptoms appear",
        "safety": "No chemical treatment available. Focus on prevention.",
        "youtube_videos": [
            {"title": "Tomato Mosaic Virus Management", "url": "https://www.youtube.com/results?search_query=tomato+mosaic+virus+control+prevention"},
            {"title": "Virus Disease Prevention", "url": "https://www.youtube.com/results?search_query=tomato+virus+disease+prevention"}
        ]
    },

    "Tomato__Tomato_Yellow_Leaf_Curl_Virus": {
        "pesticide": "Imidacloprid (for whiteflies)",
        "dosage": "0.5 ml/litre",
        "cost": "₹30",
        "treatment": "Control whiteflies with Imidacloprid",
        "prevention": "Use reflective mulches, control whitefly population",
        "steps": [
            "Mix 0.5ml Imidacloprid in 1 liter water",
            "Apply as soil drench or foliar spray",
            "Install yellow sticky traps for monitoring",
            "Use reflective silver mulches",
            "Remove infected plants immediately",
            "Control weeds that harbor whiteflies"
        ],
        "timing": "Begin whitefly control before virus symptoms appear",
        "safety": "Highly toxic to bees. Apply during evening hours.",
        "youtube_videos": [
            {"title": "Tomato Yellow Leaf Curl Management", "url": "https://www.youtube.com/results?search_query=tomato+yellow+leaf+curl+virus+whitefly+control"},
            {"title": "Whitefly Control Methods", "url": "https://www.youtube.com/results?search_query=whitefly+control+imidacloprid+tomato"}
        ]
    },

    "Tomato__healthy": {
        "pesticide": "None needed",
        "dosage": "N/A",
        "cost": "₹0",
        "treatment": "No treatment needed - plant is healthy!",
        "prevention": "Continue regular care and monitoring",
        "steps": [
            "Tomato plants appear healthy - maintain good practices",
            "Monitor regularly for early disease symptoms",
            "Ensure proper plant spacing for air circulation",
            "Water at soil level to keep foliage dry",
            "Remove suckers and lower leaves regularly",
            "Practice crop rotation and sanitation"
        ],
        "timing": "Regular monitoring 2-3 times per week",
        "safety": "No chemical application needed",
        "youtube_videos": [
            {"title": "Healthy Tomato Production", "url": "https://www.youtube.com/results?search_query=healthy+tomato+plant+care+tips"},
            {"title": "Tomato Disease Prevention", "url": "https://www.youtube.com/results?search_query=tomato+disease+prevention+practices"}
        ]
    }
}

# Your disease classes (from your working model)
classes = list(disease_info.keys())


def query_llm(prompt, context_data):
    """Query LLM for enhanced agricultural advice"""
    if not LLM_AVAILABLE:
        return "LLM service not available. Showing database recommendations only."
    
    try:
        # Create expert agricultural prompt
        expert_prompt = f"""
        You are an expert agricultural consultant helping Indian farmers. 
        
        Context:
        - Detected Disease: {context_data.get('disease_name', 'Unknown')}
        - Current Treatment: {context_data.get('treatment', 'Unknown')}
        - Pesticide: {context_data.get('pesticide', 'Unknown')}
        - Cost: {context_data.get('cost', 'Unknown')}
        
        Farmer's Question: {prompt}
        
        Provide a helpful, practical response focusing on:
        1. Direct answer to their question
        2. Safety considerations
        3. Cost-effective alternatives if relevant
        4. Prevention tips for Indian farming conditions
        
        Keep response concise and actionable (max 200 words).
        """
        
        payload = {
            "model": MODEL_NAME,
            "prompt": expert_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 200
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=100)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Unable to generate response")
        else:
            return f"LLM service error (Status: {response.status_code})"
            
    except requests.exceptions.Timeout:
        return "LLM service timeout. Please try again later."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to LLM service. Using database recommendations only."
    except Exception as e:
        return f"LLM service error: {str(e)}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path, target_size=(224, 224)):
    try:
        img_tensor = image.load_img(image_path, target_size=target_size)
        img_tensor = image.img_to_array(img_tensor) / 255.0
        img_tensor = np.expand_dims(img_tensor, axis=0)
        return img_tensor
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def get_disease_info(disease_name):
    return disease_info.get(disease_name, {
        'pesticide': 'Consult agricultural expert',
        'dosage': 'N/A',
        'cost': 'Varies',
        'treatment': 'Consult with agricultural expert',
        'prevention': 'Monitor plant health regularly',
        'steps': ['Contact local agricultural extension officer'],
        'timing': 'As recommended by expert',
        'safety': 'Follow expert guidance',
        'youtube_videos': [{"title": "General Plant Care", "url": "https://www.youtube.com/results?search_query=plant+disease+management"}]
    })

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/detect-disease')
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
        # Save uploaded file
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Preprocess and predict
        processed_image = preprocess_image(filepath)
        if processed_image is None:
            flash('Error processing image. Please try another image.', 'error')
            return redirect(url_for('index'))

        # Make prediction
        pred = model.predict(processed_image)[0]
        pred_idx = np.argmax(pred)
        confidence = float(np.max(pred) * 100)
        
        # Get disease information
        disease_name = classes[pred_idx]
        disease_data = get_disease_info(disease_name)
        
        # Prepare comprehensive result
        result = {
            'disease_name': disease_name.replace("__", " → ").replace("_(", " ("),
            'confidence': round(confidence, 2),
            'image_path': f'uploads/{filename}',
            'treatment': disease_data['treatment'],
            'prevention': disease_data['prevention'],
            'pesticide': disease_data['pesticide'],
            'dosage': disease_data['dosage'],
            'cost': disease_data['cost'],
            'steps': disease_data['steps'],
            'timing': disease_data['timing'],
            'safety': disease_data['safety'],
            'youtube_videos': disease_data['youtube_videos'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'llm_available': LLM_AVAILABLE
        }

        return render_template('detect.html', result=result)

    except Exception as e:
        print(f"Error during prediction: {e}")
        flash('Error analyzing image. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
def chat_with_ai():
    """Enhanced chat endpoint for LLM integration"""
    try:
        data = request.get_json()
        user_question = data.get('question', '')
        disease_context = data.get('context', {})
        
        if not user_question.strip():
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Get LLM response
        llm_response = query_llm(user_question, disease_context)
        
        return jsonify({
            'response': llm_response,
            'source': 'AI Assistant' if LLM_AVAILABLE else 'Database',
            'llm_available': LLM_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Chat service error: {str(e)}',
            'response': 'Sorry, I encountered an error. Please try again.',
            'source': 'Error Handler'
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'llm_available': LLM_AVAILABLE,
        'total_diseases': len(classes),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"🌱 AGROX AI Starting...")
    print(f"📊 Database: {len(classes)} diseases loaded")
    print(f"🤖 LLM Status: {'Available' if LLM_AVAILABLE else 'Offline'}")
    app.run(debug=True, host='0.0.0.0', port=5000)
