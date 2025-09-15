from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3
import tensorflow as tf

# ---------------- Flask Setup ----------------
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------- Load Model ----------------
print("Loading AI model...")
try:
    model = load_model("model/plant_disease_model.h5")
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    model = None

# ---------------- Disease Classes ----------------
class_names = [
    'Apple__Apple_scab', 'Apple__Black_rot', 'Apple__Cedar_apple_rust', 'Apple__healthy',
    'Corn_(maize)__Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)__Common_rust_',
    'Corn_(maize)__Northern_Leaf_Blight', 'Corn_(maize)__healthy',
    'Grape__Black_rot', 'Grape__Esca_(Black_Measles)', 'Grape__Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape__healthy',
    'Pepper__bell__Bacterial_spot', 'Pepper__bell__healthy',
    'Potato__Early_blight', 'Potato__Late_blight', 'Potato__healthy',
    'Tomato__Bacterial_spot', 'Tomato__Early_blight', 'Tomato__Late_blight',
    'Tomato__Leaf_Mold', 'Tomato__Septoria_leaf_spot', 'Tomato__Spider_mites_Two-spotted_spider_mite',
    'Tomato__Target_Spot', 'Tomato__Tomato_mosaic_virus', 'Tomato__Tomato_Yellow_Leaf_Curl_Virus', 'Tomato__healthy'
]

# ---------------- Disease Info ----------------
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

# ---------------- Database Setup ----------------
def init_db():
    conn = sqlite3.connect('agrox_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS diagnoses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT NOT NULL,
                  predicted_disease TEXT NOT NULL,
                  confidence REAL NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# ---------------- Image Preprocessing ----------------
def preprocess_image(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

# ---------------- Prediction ----------------
def predict_disease(img_path):
    if model is None:
        return None, 0.0

    img_array = preprocess_image(img_path)
    if img_array is None:
        return None, 0.0

    try:
        predictions = model.predict(img_array)
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_index])
        predicted_disease = class_names[predicted_class_index]
        return predicted_disease, confidence
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None, 0.0

# ---------------- Routes ----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('agrox_database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM diagnoses ORDER BY timestamp DESC LIMIT 10')
    recent_diagnoses = c.fetchall()
    conn.close()
    return render_template('dashboard.html', recent_diagnoses=recent_diagnoses)

@app.route('/crop_doctor')
def crop_doctor():
    return render_template('crop_doctor.html')

@app.route('/voice_assistant')
def voice_assistant():
    return render_template('voice_assistant.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/diagnose', methods=['POST'])
def diagnose():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        predicted_disease, confidence = predict_disease(filepath)

        if predicted_disease:
            conn = sqlite3.connect('agrox_database.db')
            c = conn.cursor()
            c.execute('INSERT INTO diagnoses (filename, predicted_disease, confidence) VALUES (?, ?, ?)',
                     (filename, predicted_disease, confidence))
            conn.commit()
            conn.close()

            disease_details = disease_info.get(predicted_disease, {
                "pesticide": "Unknown",
                "dosage": "Consult expert",
                "cost": "N/A",
                "treatment": "Please consult an agricultural expert",
                "prevention": "General good agricultural practices",
                "steps": ["Consult local agricultural expert", "Follow recommended practices"],
                "timing": "As per expert advice",
                "safety": "Follow standard safety measures",
                "youtube_videos": []
            })

            return render_template('results.html',
                                   filename=filename,
                                   predicted_disease=predicted_disease,
                                   confidence=confidence*100,
                                   disease_details=disease_details)
        else:
            flash('Error processing image. Please try again.')
            return redirect(url_for('crop_doctor'))

@app.route('/api/voice_command', methods=['POST'])
def voice_command():
    data = request.get_json()
    command = data.get('command', '').lower()

    response = {'success': True, 'message': 'Command received', 'action': None}

    if 'diagnose' in command or 'crop dr' in command:
        response['action'] = 'redirect'
        response['url'] = url_for('crop_doctor')
        response['message'] = 'Redirecting to Crop Doctor...'
    elif 'dashboard' in command:
        response['action'] = 'redirect'
        response['url'] = url_for('dashboard')
        response['message'] = 'Redirecting to Dashboard...'
    elif 'home' in command:
        response['action'] = 'redirect'
        response['url'] = url_for('index')
        response['message'] = 'Redirecting to Home...'
    else:
        response['message'] = 'Voice command not recognized. Try saying "diagnose", "dashboard", or "home".'

    return jsonify(response)

# ---------------- Main ----------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
