SUPPORTED_CROPS = [
    {"id": "Tomato", "name": "Tomato", "icon": "🍅"},
    {"id": "Potato", "name": "Potato", "icon": "🥔"},
    {"id": "Cotton", "name": "Cotton", "icon": "☁️"},
    {"id": "Rice", "name": "Paddy / Rice", "icon": "🌾"},
    {"id": "Wheat", "name": "Wheat", "icon": "🌾"},
    {"id": "Maize", "name": "Maize / Corn", "icon": "🌽"},
    {"id": "Onion", "name": "Onion", "icon": "🧅"},
    {"id": "Soybean", "name": "Soybean", "icon": "🌱"},
    {"id": "Chilli", "name": "Chilli", "icon": "🌶️"},
    {"id": "Grapes", "name": "Grapes", "icon": "🍇"}
]

KNOWLEDGE_BASE = {
    "Tomato": {
        "Early Blight": {
            "pathogen": "Alternaria solani",
            "symptoms": [
                "Dark brown circular lesions with target-like concentric rings",
                "Yellowing around affected leaf margins",
                "Premature dropping of lower senescent leaves"
            ],
            "severity": "Moderate",
            "recommendations": {
                "immediate": "Prune and dispose of lower infected leaves displaying target-spot lesions.",
                "monitoring": "Inspect surrounding tomato stems for dark sunken cankers twice weekly.",
                "prevention": "Apply mulch at plant base to prevent rain splash-back from soil and improve row spacing for airflow.",
                "expert_help": "If target-ring spots spread above mid-canopy within 48 hours, request an expert field inspection."
            }
        },
        "Late Blight": {
            "pathogen": "Phytophthora infestans",
            "symptoms": [
                "Water-soaked dark grayish lesions expanding rapidly",
                "White cottony fungal growth on lower leaf surface under high humidity",
                "Stem necrosis and dark brown fruit rot"
            ],
            "severity": "Severe",
            "recommendations": {
                "immediate": "Isolate affected section immediately and destroy severely blighted foliar tissues.",
                "monitoring": "Check morning relative humidity; high moisture (>90%) accelerates sporulation.",
                "prevention": "Ensure overhead irrigation is avoided; switch to drip tape to keep foliage dry.",
                "expert_help": "Late Blight spreads rapidly across farms; alert local agricultural Extension officer immediately."
            }
        },
        "Healthy": {
            "pathogen": "None (Target Organism Functional)",
            "symptoms": ["Lush green foliage", "Uniform leaf blade texture", "Zero necrotic or chlorotic spots"],
            "severity": "Healthy",
            "recommendations": {
                "immediate": "No corrective chemical intervention needed.",
                "monitoring": "Continue regular scouting once weekly for early pest signs.",
                "prevention": "Maintain balanced NPK fertigation schedule.",
                "expert_help": "Recheck if new chlorosis or leaf curling symptoms appear."
            }
        }
    },
    "Potato": {
        "Late Blight": {
            "pathogen": "Phytophthora infestans",
            "symptoms": [
                "Large irregular blackish-brown leaf blotches",
                "Pale green border halo surrounding active lesions",
                "Foul odor in canopy during damp weather"
            ],
            "severity": "Severe",
            "recommendations": {
                "immediate": "Remove infected haulms before tuber harvest to prevent sporangia wash down.",
                "monitoring": "Monitor soil moisture and air dew point temperatures.",
                "prevention": "Hill up soil around potato vines to protect tubers from airborne spores.",
                "expert_help": "Consult local Krishi Vigyan Kendra (KVK) for regional blight outbreak alerts."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "symptoms": ["Vigorous green compound leaves", "Intact leaf margins"],
            "severity": "Healthy",
            "recommendations": {
                "immediate": "Maintain current cultural practices.",
                "monitoring": "Inspect under-leaf sides for aphid vectors.",
                "prevention": "Ensure adequate soil hilling.",
                "expert_help": "Routine seasonal check recommended."
            }
        }
    },
    "Cotton": {
        "Bacterial Blight": {
            "pathogen": "Xanthomonas citri pv. malvacearum",
            "symptoms": [
                "Angular dark brown water-soaked leaf spots bounded by leaf veins",
                "Black arm lesion on petioles and stems",
                "Sunken water-soaked spots on bolls"
            ],
            "severity": "Moderate",
            "recommendations": {
                "immediate": "Remove severely infected bolls and leaves from field boundary.",
                "monitoring": "Scout field after monsoon rains when bacterial ooze disperses.",
                "prevention": "Use acid-delinted certified seeds for subsequent crop cycles.",
                "expert_help": "Consult agronomist if stem black arm lodging occurs."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "symptoms": ["Deep green palmate leaves", "Clean bolls"],
            "severity": "Healthy",
            "recommendations": {
                "immediate": "No action needed.",
                "monitoring": "Watch for bollworm egg laying.",
                "prevention": "Maintain balanced micronutrient sprays.",
                "expert_help": "Routine check."
            }
        }
    },
    "Default": {
        "Leaf Spot": {
            "pathogen": "Fungal / Bacterial Complex",
            "symptoms": ["Scattered necrotic spots on foliage", "Localized chlorosis around lesion edges"],
            "severity": "Moderate",
            "recommendations": {
                "immediate": "Prune severely affected leaf blades.",
                "monitoring": "Monitor new leaf flushes for symptom recurrence.",
                "prevention": "Improve field drainage and plant spacing.",
                "expert_help": "Consult an agricultural extension specialist if leaf drop increases."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "symptoms": ["Clean leaf surface", "Natural pigmentation"],
            "severity": "Healthy",
            "recommendations": {
                "immediate": "Continue standard field management.",
                "monitoring": "Routine weekly canopy check.",
                "prevention": "Maintain proper moisture balance.",
                "expert_help": "Recheck if new symptoms develop."
            }
        }
    }
}
