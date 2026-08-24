SUPPORTED_CROPS = [
    {"id": "Cotton", "name": "Cotton (कापूस)", "icon": "☁️", "state": "Maharashtra Core"},
    {"id": "Soybean", "name": "Soybean (सोयाबीन)", "icon": "🌱", "state": "Maharashtra Core"},
    {"id": "Sugarcane", "name": "Sugarcane (ऊस)", "icon": "🎋", "state": "Maharashtra Core"},
    {"id": "Onion", "name": "Onion (कांदा)", "icon": "🧅", "state": "Maharashtra Core"},
    {"id": "Grapes", "name": "Grapes (द्राक्षे)", "icon": "🍇", "state": "Maharashtra Core"},
    {"id": "Pomegranate", "name": "Pomegranate (डाळिंब)", "icon": "🍎", "state": "Maharashtra Core"},
    {"id": "Rice", "name": "Paddy / Rice (भात)", "icon": "🌾", "state": "Maharashtra Core"},
    {"id": "Tomato", "name": "Tomato (टोमॅटो)", "icon": "🍅", "state": "Solanaceous"},
    {"id": "Potato", "name": "Potato (बटाटा)", "icon": "🥔", "state": "Solanaceous"},
    {"id": "Maize", "name": "Maize / Corn (मका)", "icon": "🌽", "state": "Cereals"}
]

KNOWLEDGE_BASE = {
    "Tomato": {
        "Early Blight": {
            "pathogen": "Alternaria solani",
            "pathogen_class": "Fungal Ascomycota",
            "severity": "Moderate",
            "epiphytotic_triggers": {
                "temp_range": "24°C – 29°C",
                "humidity": "80% – 95% RH",
                "leaf_wetness": ">4 hours continuous wetness",
                "spread_vector": "Rain splash & windblown conidia from unmulched soil"
            },
            "symptoms": [
                "Dark brown circular target-board lesions with characteristic concentric rings",
                "Progressive chlorotic yellow halo surrounding active necrosis",
                "Lower canopy leaf senescence and premature defoliation",
                "Collar rot / sunken dark cankers on lower stems"
            ],
            "agronomic_prescription": {
                "field_sanitation": "Immediately prune and bag all lower infected leaves up to 20 cm from ground level. Burn or deeply bury debris—do NOT compost.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Amistar Top (Syngenta) / Custodia",
                        "active_ingredient": "Azoxystrobin 18.2% + Difenoconazole 11.4% SC",
                        "dosage_per_liter": "1.0 ml / L water",
                        "dosage_per_acre": "200 ml in 200 Liters water per Acre",
                        "frac_code": "FRAC 11 + FRAC 3 (Dual Systemic)",
                        "phi_days": 5,
                        "rei_hours": 24,
                        "technique": "Hollow cone nozzle at 45° angle targeting foliage underside; spray early morning before 9:00 AM."
                    },
                    "alternative": {
                        "brand_name": "Indofil M-45 / Dithane",
                        "active_ingredient": "Mancozeb 75% WP",
                        "dosage_per_liter": "2.5 g / L water",
                        "dosage_per_acre": "500 g in 200 Liters water per Acre",
                        "frac_code": "FRAC M03 (Multi-site Contact)",
                        "phi_days": 7,
                        "rei_hours": 24
                    },
                    "adjuvant": "Add Non-Ionic Wetting Agent (Silicon Spreader) @ 0.5 ml/L for rain-fast leaf adherence."
                },
                "organic_bio_control": {
                    "bio_agent": "Trichoderma harzianum + Pseudomonas fluorescens (10 g/L foliar spray) or 2 kg/acre enriched in 100 kg FYM.",
                    "botanical": "Cold-Pressed Neem Oil (Azadirachtin 10,000 PPM) @ 4–5 ml/L + 1 ml bio-surfactant. Repeat every 5 days."
                },
                "nutritional_therapy": {
                    "fertigation": "Withhold Urea (Nitrogen) immediately; excess vegetative N creates thin cuticle layers susceptible to hyphal penetration.",
                    "immunity_boost": "Foliar Potassium Phosphite or SOP (0:0:50) @ 5 g/L to stimulate Systemic Acquired Resistance (SAR).",
                    "cell_wall": "Calcium Nitrate (2 g/L) + Boron (1 g/L) to strengthen pectin cell wall matrix against enzymatic degradation."
                },
                "frac_calendar": [
                    {"spray": "Spray 1 (Day 0 - Curative)", "chem": "Azoxystrobin + Difenoconazole", "frac": "FRAC 11 + 3"},
                    {"spray": "Spray 2 (Day 7 - Protectant)", "chem": "Mancozeb 75% WP", "frac": "FRAC M03"},
                    {"spray": "Spray 3 (Day 14 - Rotational)", "chem": "Chlorothalonil 75% WP", "frac": "FRAC M05"}
                ],
                "recovery_milestones": {
                    "day_0": "Complete bottom canopy pruning and apply primary systemic fungicide mist.",
                    "day_3": "Target spots turn dark, dry, and stop expanding; no new yellow halo margin formation.",
                    "day_7": "Upper canopy free of lesions; apply secondary protectant spray.",
                    "day_14": "Full foliar recovery; resume balanced N:P:K 19:19:19 fertigation."
                }
            },
            "recommendations": {
                "immediate": "Prune lower infected foliage and apply Azoxystrobin + Difenoconazole @ 1.0 ml/L within 24 hours.",
                "monitoring": "Scout field twice weekly for target concentric rings on mid-canopy leaves.",
                "prevention": "Install silver-black plastic mulch and shift from flood/overhead irrigation to drip lines.",
                "expert_help": "If lesions ascend to upper fruit clusters within 48h, escalate to local KVK Extension Agronomist."
            }
        },
        "Late Blight": {
            "pathogen": "Phytophthora infestans",
            "pathogen_class": "Oomycete / Water Mold",
            "severity": "Severe",
            "epiphytotic_triggers": {
                "temp_range": "15°C – 22°C (Cool & Damp)",
                "humidity": ">90% RH",
                "leaf_wetness": "Morning heavy dew or persistent cloud cover",
                "spread_vector": "Airborne sporangia travelling up to 10 km on wind currents"
            },
            "symptoms": [
                "Water-soaked irregular grayish-black lesions with pale light-green margin halos",
                "White frosty downy fungal sporulation on lower leaf surface during high humidity",
                "Rapid petiole and stem necrosis leading to sudden canopy collapse",
                "Greasy brown firm rot on green and ripe tomato fruits"
            ],
            "agronomic_prescription": {
                "field_sanitation": "Quarantine affected zone immediately. Remove and bag severely collapsed plants in sealed sacks. Destroy by burial (>1m depth).",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Ridomil Gold / Acrobat",
                        "active_ingredient": "Metalaxyl-M 4% + Mancozeb 64% WP or Dimethomorph 50% WP",
                        "dosage_per_liter": "2.5 g / L water",
                        "dosage_per_acre": "500 g in 200 Liters water per Acre",
                        "frac_code": "FRAC 4 + FRAC M03 (Systemic Oomycide)",
                        "phi_days": 7,
                        "rei_hours": 48,
                        "technique": "Full canopy drench with hollow cone nozzle; ensure complete coverage under foliage."
                    },
                    "alternative": {
                        "brand_name": "Tata Blitox 50 / Cupramar",
                        "active_ingredient": "Copper Oxychloride 50% WP",
                        "dosage_per_liter": "2.5 g – 3.0 g / L water",
                        "dosage_per_acre": "600 g in 200 Liters water per Acre",
                        "frac_code": "FRAC M01 (Contact Bactericide/Fungicide)",
                        "phi_days": 3,
                        "rei_hours": 24
                    },
                    "adjuvant": "Add Silicon non-ionic surfactant @ 0.5 ml/L for maximum rain persistence."
                },
                "organic_bio_control": {
                    "bio_agent": "Bacillus subtilis (QST 713 strain) @ 5 ml/L foliar spray + Copper Hydroxide biological grade.",
                    "botanical": "Bordeaux Mixture 1% (1 kg Copper Sulphate + 1 kg Quick Lime in 100L water) applied preventively."
                },
                "nutritional_therapy": {
                    "fertigation": "Zero Nitrogen feeding. Apply Potassium Silicate @ 2.5 g/L to deposit silica shields in leaf epidermis.",
                    "immunity_boost": "Foliar Potassium Phosphite @ 4 ml/L (directly triggers systemic plant phytoalexins).",
                    "cell_wall": "Chelated Calcium EDTA @ 1.5 g/L to stabilize pectate middle lamella."
                },
                "frac_calendar": [
                    {"spray": "Spray 1 (Immediate)", "chem": "Metalaxyl-M + Mancozeb", "frac": "FRAC 4 + M03"},
                    {"spray": "Spray 2 (Day 5)", "chem": "Dimethomorph 50% WP", "frac": "FRAC 40"},
                    {"spray": "Spray 3 (Day 10)", "chem": "Cymoxanil 8% + Mancozeb 64% WP", "frac": "FRAC 27 + M03"}
                ],
                "recovery_milestones": {
                    "day_0": "Execute emergency knockdown spray across infected block plus 10m buffer zone.",
                    "day_3": "Water-soaked margins turn brown and desiccate; white downy sporulation disappears.",
                    "day_7": "Inspect stem junctions for active cankers; apply follow-up FRAC 40 spray.",
                    "day_14": "Canopy stabilization; test newly formed fruit clusters for brown rot."
                }
            },
            "recommendations": {
                "immediate": "Apply Ridomil Gold (Metalaxyl + Mancozeb) @ 2.5g/L immediately across infected rows and buffer perimeter.",
                "monitoring": "Check early morning relative humidity; scout field daily at sunrise for white fungal fuzz.",
                "prevention": "Never irrigate late evening; switch completely to sub-surface drip irrigation.",
                "expert_help": "Late Blight is an epiphytotic threat; report to District Agriculture Officer immediately."
            }
        },
        "Healthy": {
            "pathogen": "None (Optimum Foliar Physiology)",
            "pathogen_class": "Healthy Biological State",
            "severity": "Healthy",
            "epiphytotic_triggers": {
                "temp_range": "20°C – 30°C",
                "humidity": "50% – 70% RH",
                "leaf_wetness": "Dry leaf surface",
                "spread_vector": "Zero pathogen pressure"
            },
            "symptoms": [
                "Lush dark emerald green foliage with high chlorophyll density",
                "Intact leaf lamina with sharp turgid margins",
                "Zero chlorosis, necrotic spotting, or pathogen sporulation"
            ],
            "agronomic_prescription": {
                "field_sanitation": "Maintain weed-free border bunds to eliminate Solanaceous weed hosts.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Preventive Maintenance (No Chemical Needed)",
                        "active_ingredient": "None required",
                        "dosage_per_liter": "0",
                        "dosage_per_acre": "0",
                        "frac_code": "N/A",
                        "phi_days": 0,
                        "rei_hours": 0,
                        "technique": "Maintain standard scouting."
                    }
                },
                "organic_bio_control": {
                    "bio_agent": "Preventive soil drench with Trichoderma viride @ 2 kg/acre with vermicompost.",
                    "botanical": "Prophylactic Seaweed Ascophyllum nodosum extract @ 2 ml/L every 14 days."
                },
                "nutritional_therapy": {
                    "fertigation": "Balanced N:P:K fertigation (19:19:19 @ 3 kg/acre weekly during vegetative; 13:0:45 during fruiting).",
                    "immunity_boost": "Chelated Micronutrient mixture (Zn, Fe, Mn, Cu, B, Mo) @ 1.5 g/L once monthly.",
                    "cell_wall": "Calcium Nitrate @ 2.5 kg/acre via drip."
                },
                "frac_calendar": [],
                "recovery_milestones": {
                    "day_0": "Maintain standard precision schedule.",
                    "day_7": "Routine weekly scouting.",
                    "day_14": "Targeting 38+ Quintals/Acre harvest yield."
                }
            },
            "recommendations": {
                "immediate": "No corrective chemical intervention needed.",
                "monitoring": "Continue weekly scouting for early signs of sucking pests or fungal spots.",
                "prevention": "Maintain scheduled NPK fertigation and drip moisture levels.",
                "expert_help": "Recheck if leaf color shifts or yellowing develops."
            }
        }
    },
    "Potato": {
        "Late Blight": {
            "pathogen": "Phytophthora infestans",
            "pathogen_class": "Oomycete",
            "severity": "Severe",
            "epiphytotic_triggers": {
                "temp_range": "12°C – 20°C",
                "humidity": ">90% RH",
                "leaf_wetness": "Dense fog / overcast weather",
                "spread_vector": "Airborne sporangia washed down to potato tubers via rainfall"
            },
            "symptoms": [
                "Water-soaked dark lesions spreading rapidly on foliage and stems",
                "White mildew on leaf undersides during cool damp mornings",
                "Brownish discoloration and dry rot in developing tubers"
            ],
            "agronomic_prescription": {
                "field_sanitation": "De-haulm (cut and destroy top vines) 10 days before harvesting to prevent tuber infection.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Curzate M8 (Corteva) / Ridomil Gold",
                        "active_ingredient": "Cymoxanil 8% + Mancozeb 64% WP",
                        "dosage_per_liter": "2.5 g / L water",
                        "dosage_per_acre": "500 g in 200L water / Acre",
                        "frac_code": "FRAC 27 + M03",
                        "phi_days": 14,
                        "rei_hours": 24,
                        "technique": "High pressure sprayer for dense canopy penetration."
                    }
                },
                "organic_bio_control": {
                    "bio_agent": "Pseudomonas fluorescens @ 10 g/L foliar spray.",
                    "botanical": "Garlic extract (5%) + Copper Hydroxide @ 2 g/L."
                },
                "nutritional_therapy": {
                    "fertigation": "Hill up soil around vines by 15 cm to physically shield tubers from spore wash-down.",
                    "immunity_boost": "Foliar Potassium Phosphite @ 3 ml/L.",
                    "cell_wall": "SOP (0-0-50) @ 5 g/L to harden tuber skin."
                },
                "frac_calendar": [
                    {"spray": "Spray 1", "chem": "Cymoxanil + Mancozeb", "frac": "FRAC 27 + M03"},
                    {"spray": "Spray 2", "chem": "Dimethomorph 50% WP", "frac": "FRAC 40"}
                ],
                "recovery_milestones": {
                    "day_0": "Apply systemic oomycide; hill up potato rows.",
                    "day_3": "Lesion arrest confirmed.",
                    "day_7": "Tuber sample inspection for dry rot."
                }
            },
            "recommendations": {
                "immediate": "Apply Cymoxanil + Mancozeb @ 2.5 g/L immediately.",
                "monitoring": "Monitor soil moisture and air dew point temperatures.",
                "prevention": "Ensure high ridge hilling to shield tubers from spore wash.",
                "expert_help": "Consult local Krishi Vigyan Kendra (KVK) for regional blight alert."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "18°C – 24°C", "humidity": "60% RH", "leaf_wetness": "Dry", "spread_vector": "None"},
            "symptoms": ["Vigorous green compound leaves", "Clean healthy stems"],
            "agronomic_prescription": {
                "field_sanitation": "Keep ridges free of weeds.",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Trichoderma soil application."},
                "nutritional_therapy": {"fertigation": "Apply MOP (Potash) @ 50 kg/acre for tuber bulking."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy status verified."}
            },
            "recommendations": {
                "immediate": "Maintain standard ridge irrigation and nutrition.",
                "monitoring": "Inspect undersides of leaves for aphid vectors.",
                "prevention": "Ensure deep soil hilling.",
                "expert_help": "Routine check."
            }
        }
    },
    "Cotton": {
        "Bacterial Blight": {
            "pathogen": "Xanthomonas citri pv. malvacearum",
            "pathogen_class": "Bacterial Pathogen",
            "severity": "Moderate",
            "epiphytotic_triggers": {
                "temp_range": "28°C – 34°C",
                "humidity": ">85% RH (Monsoon warm rains)",
                "leaf_wetness": "Rain storm splash",
                "spread_vector": "Bacterial streaming via rain splash and contaminated seeds"
            },
            "symptoms": [
                "Small angular translucent water-soaked spots delineated strictly by leaf veinlets",
                "Black arm lesion: elongated black sunken cankers girdling petioles and main stems",
                "Water-soaked oily dark spots on green bolls leading to internal boll rot"
            ],
            "agronomic_prescription": {
                "field_sanitation": "Rogue out and destroy black-arm infected branches; do not walk through wet field to prevent bacterial transfer.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Streptocycline + Blitox 50 WP",
                        "active_ingredient": "Streptomycin Sulphate 90% + Tetracycline 10% (6g) + Copper Oxychloride 50% WP (500g)",
                        "dosage_per_liter": "0.03 g Streptocycline + 2.5 g Copper Oxychloride per Liter",
                        "dosage_per_acre": "6 g Streptocycline + 500 g Blitox in 200 Liters water per Acre",
                        "frac_code": "FRAC 25 + FRAC M01 (Bactericide + Multi-site Copper)",
                        "phi_days": 14,
                        "rei_hours": 24,
                        "technique": "Foliar mist targeting both leaf surfaces during dry sunny intervals."
                    }
                },
                "organic_bio_control": {
                    "bio_agent": "Pseudomonas fluorescens foliar spray @ 10 g/L (produces 2,4-diacetylphloroglucinol antibiotic).",
                    "botanical": "Fermented Cow Dung & Butter-milk extract (10% foliar spray every 7 days)."
                },
                "nutritional_therapy": {
                    "fertigation": "Avoid excessive basal Nitrogen; apply Magnesium Sulphate (5 kg/acre) to prevent red leaf chlorosis.",
                    "immunity_boost": "Foliar Potassium Nitrate 13:0:45 @ 10 g/L + Boron 20% @ 1 g/L for boll wall strengthening.",
                    "cell_wall": "Zinc EDTA 12% @ 1 g/L."
                },
                "frac_calendar": [
                    {"spray": "Spray 1", "chem": "Streptocycline + Copper Oxychloride", "frac": "FRAC 25 + M01"},
                    {"spray": "Spray 2", "chem": "Copper Hydroxide 53.8% DF", "frac": "FRAC M01"}
                ],
                "recovery_milestones": {
                    "day_0": "Apply antibiotic-copper combination mist.",
                    "day_3": "Angular water-soaked lesions turn into dry reddish-brown necrotic spots with zero bacterial ooze.",
                    "day_7": "Stem black arm lesions heal; new top canopy flushes emerge clean."
                }
            },
            "recommendations": {
                "immediate": "Spray Streptocycline (6g) + Copper Oxychloride (500g) in 200L water per acre within 24h.",
                "monitoring": "Scout field after monsoon downpours for angular leaf spots.",
                "prevention": "Ensure acid-delinting of seeds for subsequent crop cycles.",
                "expert_help": "Consult cotton specialist if stem black arm lodging exceeds 10%."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "25°C – 35°C", "humidity": "60% RH", "leaf_wetness": "Dry", "spread_vector": "None"},
            "symptoms": ["Broad deep green palmate leaves", "Clean vigorous squares and bolls"],
            "agronomic_prescription": {
                "field_sanitation": "Maintain clean border bunds.",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Neem oil 1500 PPM preventive spray for whitefly."},
                "nutritional_therapy": {"fertigation": "Foliar DAP 2% + 13:0:45 @ 10 g/L at square formation."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy crop telemetry active."}
            },
            "recommendations": {
                "immediate": "No corrective chemical action required.",
                "monitoring": "Inspect squares and flower bracts for bollworm egg laying.",
                "prevention": "Maintain balanced micronutrient and potassium sprays.",
                "expert_help": "Routine check."
            }
        }
    },
    "Rice": {
        "Blast Disease": {
            "pathogen": "Magnaporthe oryzae (Pyricularia oryzae)",
            "pathogen_class": "Fungal Ascomycota",
            "severity": "Severe",
            "epiphytotic_triggers": {
                "temp_range": "20°C – 28°C",
                "humidity": ">90% RH",
                "leaf_wetness": ">10 hours dew persistence",
                "spread_vector": "High wind velocity dispersing airborne conidia"
            },
            "symptoms": [
                "Spindle-shaped / elliptical eye lesions with ash-gray center and dark reddish-brown margins",
                "Neck blast: blackish lesions girdling the panicle node causing complete grain chaffiness",
                "Nodes turning black, fragile, and snapping easily during tillering"
            ],
            "agronomic_prescription": {
                "field_sanitation": "Temporarily drain standing water for 48 hours to aerate the soil root zone and reduce atmospheric micro-humidity.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Beam (Dow) / Sivic / Baan",
                        "active_ingredient": "Tricyclazole 75% WP",
                        "dosage_per_liter": "0.6 g / L water",
                        "dosage_per_acre": "120 g in 200 Liters water per Acre",
                        "frac_code": "FRAC 16.1 (Melanin Biosynthesis Inhibitor)",
                        "phi_days": 21,
                        "rei_hours": 24,
                        "technique": "Uniform mist coverage across all tillers at early boot stage."
                    },
                    "alternative": {
                        "brand_name": "Nativo (Bayer)",
                        "active_ingredient": "Tebuconazole 50% + Trifloxystrobin 25% WG",
                        "dosage_per_liter": "0.4 g / L water",
                        "dosage_per_acre": "80 g in 200 Liters water per Acre",
                        "frac_code": "FRAC 3 + FRAC 11",
                        "phi_days": 15,
                        "rei_hours": 24
                    }
                },
                "organic_bio_control": {
                    "bio_agent": "Pseudomonas fluorescens @ 10 g/L (1 kg/acre foliar spray) + Trichoderma viride seed treatment.",
                    "botanical": "Cow urine extract (5%) + Fermented botanical concoction."
                },
                "nutritional_therapy": {
                    "fertigation": "Strictly withhold top-dress Urea; apply Muriate of Potash (MOP) @ 25 kg/acre to strengthen culms.",
                    "immunity_boost": "Foliar Potassium Silicate @ 2.5 g/L (silicon deposition hardens silica cell walls against appressorial penetration).",
                    "cell_wall": "Zinc Sulphate 21% @ 5 kg/acre basal."
                },
                "frac_calendar": [
                    {"spray": "Spray 1 (Tillering)", "chem": "Tricyclazole 75% WP", "frac": "FRAC 16.1"},
                    {"spray": "Spray 2 (Booting)", "chem": "Tebuconazole + Trifloxystrobin", "frac": "FRAC 3 + 11"}
                ],
                "recovery_milestones": {
                    "day_0": "Spray systemic melanin inhibitor; drain standing flood water for 2 days.",
                    "day_3": "Spindle lesion eye centers dry out and cease elongation.",
                    "day_7": "Panicle emergence clean with zero neck rot."
                }
            },
            "recommendations": {
                "immediate": "Apply Tricyclazole 75 WP @ 0.6g/L or Nativo @ 0.4g/L immediately.",
                "monitoring": "Scout panicle neck nodes during boot stage.",
                "prevention": "Split Nitrogen dose into 3 applications and avoid late heavy urea top-dressing.",
                "expert_help": "If neck blast exceeds 5%, alert district rice extension agronomist."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "24°C – 32°C", "humidity": "70% RH", "leaf_wetness": "Normal", "spread_vector": "None"},
            "symptoms": ["Erect dark green tillers", "Clean leaf sheaths with zero spindle spots"],
            "agronomic_prescription": {
                "field_sanitation": "Maintain optimal standing water depth (3-5 cm).",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Azospirillum & PSB bio-fertilizers."},
                "nutritional_therapy": {"fertigation": "Maintain balanced NPK with split nitrogen and potash."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy crop record."}
            },
            "recommendations": {
                "immediate": "Continue standard water and nutrient regime.",
                "monitoring": "Routine scouting for leaf folder and stem borer.",
                "prevention": "Ensure proper field drainage at physiological maturity.",
                "expert_help": "Routine check."
            }
        }
    },
    "Wheat": {
        "Yellow Rust": {
            "pathogen": "Puccinia striiformis f. sp. tritici",
            "pathogen_class": "Fungal Basidiomycota",
            "severity": "Severe",
            "epiphytotic_triggers": {
                "temp_range": "10°C – 15°C (Cool winter)",
                "humidity": ">85% RH (High humidity & dew)",
                "leaf_wetness": "Morning dew droplets",
                "spread_vector": "Urediniospores carried by high-altitude air currents over hundreds of km"
            },
            "symptoms": [
                "Bright lemon-yellow powdery pustules arranged in prominent parallel stripes along leaf veins",
                "Yellow dust rubbing off easily on fingertips upon touching leaf blades",
                "Premature drying and chlorosis of flag leaves drastically reducing grain filling"
            ],
            "agronomic_prescription": {
                "field_sanitation": "Quarantine field sector; avoid walking into adjacent plots without changing boots/clothes.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Tilt (Syngenta) / Result / Bumper",
                        "active_ingredient": "Propiconazole 25% EC",
                        "dosage_per_liter": "1.0 ml / L water",
                        "dosage_per_acre": "200 ml in 200 Liters water per Acre",
                        "frac_code": "FRAC 3 (DMI Triazole)",
                        "phi_days": 30,
                        "rei_hours": 24,
                        "technique": "Foliar spray targeting the flag leaf and top two leaves with flat fan nozzle."
                    },
                    "alternative": {
                        "brand_name": "Custodia / Opera",
                        "active_ingredient": "Azoxystrobin 11% + Tebuconazole 18.3% SC",
                        "dosage_per_liter": "1.0 ml / L water",
                        "dosage_per_acre": "200 ml in 200 Liters water per Acre",
                        "frac_code": "FRAC 11 + FRAC 3",
                        "phi_days": 21,
                        "rei_hours": 24
                    }
                },
                "organic_bio_control": {
                    "bio_agent": "Trichoderma harzianum @ 10 g/L foliar spray.",
                    "botanical": "Liquid Sulphur 80% WDG @ 3 g/L (acts as natural multi-site contact rust protectant)."
                },
                "nutritional_therapy": {
                    "fertigation": "Do not apply late urea; apply MOP (Potash) @ 20 kg/acre.",
                    "immunity_boost": "Foliar 0:52:34 (Monopotassium Phosphate) @ 10 g/L at flag leaf stage.",
                    "cell_wall": "Zinc Sulphate 21% @ 2 g/L + Boron 20% @ 1 g/L."
                },
                "frac_calendar": [
                    {"spray": "Spray 1 (Immediate)", "chem": "Propiconazole 25% EC", "frac": "FRAC 3"},
                    {"spray": "Spray 2 (Day 10 if needed)", "chem": "Tebuconazole 25.9% EC", "frac": "FRAC 3"}
                ],
                "recovery_milestones": {
                    "day_0": "Knockdown spray with Propiconazole targeting striped pustules.",
                    "day_3": "Yellow powdery pustules turn dull dark brown/black (teliospore transition) and stop sporulation.",
                    "day_7": "Flag leaves green and photosynthetic efficiency restored."
                }
            },
            "recommendations": {
                "immediate": "Spray Propiconazole 25 EC @ 1.0 ml/L (200ml/acre) immediately upon detecting yellow stripes.",
                "monitoring": "Scout flag leaves daily during cool morning hours.",
                "prevention": "Cultivate resistant wheat cultivars (e.g., HD-3086, DBW-187, PBW-725).",
                "expert_help": "Yellow Rust is a national food security priority; report immediately to local ICAR/SAU station."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "15°C – 25°C", "humidity": "50% RH", "leaf_wetness": "Dry", "spread_vector": "None"},
            "symptoms": ["Lush green erect wheat leaves", "Uniform healthy flag leaf without rust stripes"],
            "agronomic_prescription": {
                "field_sanitation": "Keep perimeter bunds clean.",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Bio-NPK consortia soil application."},
                "nutritional_therapy": {"fertigation": "Apply 13:0:45 @ 10 g/L at heading stage."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy wheat crop confirmed."}
            },
            "recommendations": {
                "immediate": "Maintain critical stage irrigation (CRI, Tillering, Heading, Milking).",
                "monitoring": "Routine scouting for aphids and rust.",
                "prevention": "Ensure balanced nutrition.",
                "expert_help": "Routine check."
            }
        }
    },
    "Maize": {
        "Common Rust": {
            "pathogen": "Puccinia sorghi",
            "pathogen_class": "Fungal Basidiomycota",
            "severity": "Moderate",
            "epiphytotic_triggers": {"temp_range": "16°C – 25°C", "humidity": ">85% RH", "leaf_wetness": "Morning dew", "spread_vector": "Windborne urediniospores"},
            "symptoms": ["Cinnamon-brown oval powdery pustules on both upper and lower leaf surfaces", "Chlorotic halos around bursting pustules", "Severe leaf browning and drying in high infestation"],
            "agronomic_prescription": {
                "field_sanitation": "Plow under crop stover post-harvest to bury fungal spores.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Dithane M-45 / Saaf",
                        "active_ingredient": "Mancozeb 75% WP or Carbendazim 12% + Mancozeb 63% WP",
                        "dosage_per_liter": "2.0 g / L water",
                        "dosage_per_acre": "400 g in 200L water / Acre",
                        "frac_code": "FRAC M03 + FRAC 1",
                        "phi_days": 15,
                        "rei_hours": 24,
                        "technique": "Foliar mist covering whorl and leaf canopy."
                    }
                },
                "organic_bio_control": {"bio_agent": "Liquid Sulphur 80% WDG @ 3 g/L.", "botanical": "Neem oil 10,000 PPM @ 4 ml/L."},
                "nutritional_therapy": {"fertigation": "Foliar Potassium Nitrate 13:0:45 @ 10 g/L.", "immunity_boost": "Zinc Sulphate 21% @ 2 g/L."},
                "frac_calendar": [{"spray": "Spray 1", "chem": "Mancozeb 75% WP", "frac": "FRAC M03"}],
                "recovery_milestones": {"day_0": "Apply protectant fungicide.", "day_3": "Pustules dry up and darken.", "day_7": "Cob leaf remains healthy."}
            },
            "recommendations": {
                "immediate": "Apply Mancozeb 75 WP @ 2.0 g/L across affected maize plants.",
                "monitoring": "Scout lower canopy leaves twice weekly.",
                "prevention": "Rotate with Legumes (Soybean/Gram).",
                "expert_help": "Consult agronomist if rust spreads to top ear leaf."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "20°C – 32°C", "humidity": "60% RH", "leaf_wetness": "Dry", "spread_vector": "None"},
            "symptoms": ["Vigorous wide green leaves", "Clean whorl with zero feeding holes"],
            "agronomic_prescription": {
                "field_sanitation": "Keep field free of weed hosts.",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Trichoderma seed treatment."},
                "nutritional_therapy": {"fertigation": "Zinc Sulphate 21% @ 10 kg/acre basal + Split Urea."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy maize telemetry."}
            },
            "recommendations": {
                "immediate": "Maintain knee-high and tasseling stage irrigation.",
                "monitoring": "Check whorls for Fall Armyworm larvae.",
                "prevention": "Balanced fertilizer management.",
                "expert_help": "Routine check."
            }
        }
    },
    "Onion": {
        "Purple Blotch": {
            "pathogen": "Alternaria porri",
            "pathogen_class": "Fungal Ascomycota",
            "severity": "Moderate",
            "epiphytotic_triggers": {"temp_range": "22°C – 30°C", "humidity": ">80% RH", "leaf_wetness": "Prolonged leaf surface moisture", "spread_vector": "Windblown conidia and rain splash"},
            "symptoms": ["Small water-soaked sunken lesions on leaves with characteristic purple-to-brown center", "Lesions girdling the leaf causing top collapse", "Dark powdery concentric rings of fungal sporulation"],
            "agronomic_prescription": {
                "field_sanitation": "Destroy crop residues; avoid overhead sprinkler watering in late evening.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Score (Syngenta) / Nativo",
                        "active_ingredient": "Difenoconazole 25% EC or Tebuconazole 50% + Trifloxystrobin 25% WG",
                        "dosage_per_liter": "1.0 ml / L water",
                        "dosage_per_acre": "200 ml in 200L water / Acre",
                        "frac_code": "FRAC 3 + FRAC 11",
                        "phi_days": 10,
                        "rei_hours": 24,
                        "technique": "Always mix with silicon sticker (0.5 ml/L) as onion leaves have a waxy cuticle."
                    }
                },
                "organic_bio_control": {"bio_agent": "Pseudomonas fluorescens @ 10 g/L.", "botanical": "Neem oil 10,000 PPM @ 5 ml/L."},
                "nutritional_therapy": {"fertigation": "Apply Sulphur 80% WDG @ 3 kg/acre via drip.", "immunity_boost": "0:52:34 @ 5 g/L."},
                "frac_calendar": [{"spray": "Spray 1", "chem": "Difenoconazole 25% EC", "frac": "FRAC 3"}],
                "recovery_milestones": {"day_0": "Apply systemic triazole spray with sticker.", "day_3": "Purple spots dry out.", "day_7": "New onion scapes emerge green."}
            },
            "recommendations": {
                "immediate": "Spray Difenoconazole 25 EC @ 1 ml/L + Silicon sticker (0.5 ml/L) immediately.",
                "monitoring": "Inspect tubular leaves for purplish sunken centers.",
                "prevention": "Ensure good field drainage and avoid high plant density.",
                "expert_help": "Consult agronomist if stalk breakage occurs before bulb maturity."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "15°C – 28°C", "humidity": "60% RH", "leaf_wetness": "Dry", "spread_vector": "None"},
            "symptoms": ["Erect tubular dark green leaves", "Clean bulb neck"],
            "agronomic_prescription": {
                "field_sanitation": "Keep beds weed-free.",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Trichoderma enriched FYM."},
                "nutritional_therapy": {"fertigation": "Sulphur and Potash application for bulb pungency."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy onion status."}
            },
            "recommendations": {
                "immediate": "Maintain light frequent irrigation.",
                "monitoring": "Check leaf axils for thrips.",
                "prevention": "Proper spacing.",
                "expert_help": "Routine check."
            }
        }
    },
    "Soybean": {
        "Rust": {
            "pathogen": "Phakopsora pachyrhizi",
            "pathogen_class": "Fungal Basidiomycota",
            "severity": "Severe",
            "epiphytotic_triggers": {"temp_range": "18°C – 26°C", "humidity": ">85% RH", "leaf_wetness": ">6 hours continuous moisture", "spread_vector": "Windblown airborne urediniospores"},
            "symptoms": ["Minute brown polygonal spots on lower leaves with volcano-shaped pustules on lower surface", "Rapid yellowing and canopy browning resembling early maturity", "Severe pod abortion and seed shrinkage"],
            "agronomic_prescription": {
                "field_sanitation": "Destroy self-sown volunteer soybean plants in off-season.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Hexaconazole 5% SC / Tilt",
                        "active_ingredient": "Hexaconazole 5% SC (2.0 ml/L) or Propiconazole 25% EC (1.0 ml/L)",
                        "dosage_per_liter": "2.0 ml / L water",
                        "dosage_per_acre": "400 ml in 200L water / Acre",
                        "frac_code": "FRAC 3 (Triazole)",
                        "phi_days": 21,
                        "rei_hours": 24,
                        "technique": "Thorough coverage of lower canopy before pod formation."
                    }
                },
                "organic_bio_control": {"bio_agent": "Trichoderma harzianum @ 10 g/L.", "botanical": "Liquid Sulphur 80% @ 3 g/L."},
                "nutritional_therapy": {"fertigation": "Foliar 0:52:34 @ 10 g/L at flowering.", "immunity_boost": "Boron 20% @ 1 g/L for pod set."},
                "frac_calendar": [{"spray": "Spray 1", "chem": "Hexaconazole 5% SC", "frac": "FRAC 3"}],
                "recovery_milestones": {"day_0": "Knockdown triazole spray applied.", "day_3": "Pustule eruption arrested.", "day_7": "Pods develop normally."}
            },
            "recommendations": {
                "immediate": "Apply Hexaconazole 5 SC @ 2.0 ml/L or Propiconazole @ 1.0 ml/L immediately.",
                "monitoring": "Inspect undersides of bottom leaves with 10x lens.",
                "prevention": "Sow early during recommended planting window.",
                "expert_help": "Alert local soybean breeder if rust appears before flowering."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "22°C – 32°C", "humidity": "65% RH", "leaf_wetness": "Dry", "spread_vector": "None"},
            "symptoms": ["Lush trifoliate green leaves", "Healthy nodules on root system"],
            "agronomic_prescription": {
                "field_sanitation": "Maintain clean inter-row spacing.",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Rhizobium & PSB seed inoculation."},
                "nutritional_therapy": {"fertigation": "Single Super Phosphate (SSP) for phosphorus & sulphur."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy soybean crop."}
            },
            "recommendations": {
                "immediate": "Maintain weed-free conditions up to 45 days.",
                "monitoring": "Scout for semilooper and girdle beetle.",
                "prevention": "Balanced fertilization.",
                "expert_help": "Routine check."
            }
        }
    },
    "Chilli": {
        "Anthracnose / Fruit Rot": {
            "pathogen": "Colletotrichum capsici",
            "pathogen_class": "Fungal Ascomycota",
            "severity": "Moderate",
            "epiphytotic_triggers": {"temp_range": "25°C – 32°C", "humidity": ">80% RH", "leaf_wetness": "Frequent rains", "spread_vector": "Rain splash and contaminated seeds"},
            "symptoms": ["Circular sunken spots on fruits with dark concentric rings and black acervuli", "Die-back of twigs from tip downwards with necrotic whitening", "Circular brown spots with dark margins on leaves"],
            "agronomic_prescription": {
                "field_sanitation": "Prune dry twigs 5 cm below infected zone; destroy mummified fruits.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Amistar (Syngenta) / Folicur",
                        "active_ingredient": "Azoxystrobin 23% SC (1.0 ml/L) or Tebuconazole 25.9% EC (1.0 ml/L)",
                        "dosage_per_liter": "1.0 ml / L water",
                        "dosage_per_acre": "200 ml in 200L water / Acre",
                        "frac_code": "FRAC 11 / FRAC 3",
                        "phi_days": 5,
                        "rei_hours": 24,
                        "technique": "Spray at flowering and fruit set stage."
                    }
                },
                "organic_bio_control": {"bio_agent": "Trichoderma viride foliar spray @ 10 g/L.", "botanical": "Neem oil 10,000 PPM @ 4 ml/L."},
                "nutritional_therapy": {"fertigation": "Calcium Nitrate (2 g/L) + Boron (1 g/L) to prevent blossom end rot.", "immunity_boost": "0:0:50 @ 5 g/L."},
                "frac_calendar": [{"spray": "Spray 1", "chem": "Azoxystrobin 23% SC", "frac": "FRAC 11"}],
                "recovery_milestones": {"day_0": "Prune dieback twigs and apply strobilurin spray.", "day_3": "Sunken fruit lesions desiccate.", "day_7": "New fruit sets free of rot."}
            },
            "recommendations": {
                "immediate": "Spray Azoxystrobin @ 1.0 ml/L or Tebuconazole @ 1.0 ml/L immediately.",
                "monitoring": "Inspect green and red chillies for circular sunken marks.",
                "prevention": "Treat seeds with Thiram or Trichoderma before nursery sowing.",
                "expert_help": "Consult agronomist if die-back spreads to main stem."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "20°C – 30°C", "humidity": "60% RH", "leaf_wetness": "Dry", "spread_vector": "None"},
            "symptoms": ["Lush green leaves with glossy texture", "Abundant healthy white flowers and shiny chillies"],
            "agronomic_prescription": {
                "field_sanitation": "Maintain clean mulched beds.",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Neem spray for thrips & mites."},
                "nutritional_therapy": {"fertigation": "19:19:19 fertigation + Micronutrients."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy chilli status."}
            },
            "recommendations": {
                "immediate": "Maintain drip fertigation.",
                "monitoring": "Scout for thrips (leaf upward curling) and mites (downward curling).",
                "prevention": "Blue and yellow sticky traps (15 traps/acre).",
                "expert_help": "Routine check."
            }
        }
    },
    "Grapes": {
        "Downy Mildew": {
            "pathogen": "Plasmopara viticola",
            "pathogen_class": "Oomycete",
            "severity": "Severe",
            "epiphytotic_triggers": {"temp_range": "20°C – 25°C", "humidity": ">90% RH (3-10 rule: 10cm shoot, 10mm rain, 10°C temp)", "leaf_wetness": ">4 hours", "spread_vector": "Windblown zoospores requiring free water film"},
            "symptoms": ["Translucent yellowish oily 'oil-spots' on upper leaf surface", "Dense white downy cottony growth on the underside directly under oil spots", "Berries turning brownish-leather and dropping (leather berry)"],
            "agronomic_prescription": {
                "field_sanitation": "Canopy thinning to allow maximum sunlight and air circulation inside the vine trellis.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Profilite (Bayer) / Revus",
                        "active_ingredient": "Fluopicolide 4.44% + Fosetyl-Al 66.67% WG or Mandipropamid 23.4% SC",
                        "dosage_per_liter": "2.5 g / L water",
                        "dosage_per_acre": "500 g in 200L water / Acre",
                        "frac_code": "FRAC 43 + FRAC P07",
                        "phi_days": 28,
                        "rei_hours": 48,
                        "technique": "Under-leaf mist with air-assisted canopy sprayer."
                    }
                },
                "organic_bio_control": {"bio_agent": "Trichoderma harzianum @ 5 g/L.", "botanical": "Bordeaux Mixture 1% (preventive before rain events)."},
                "nutritional_therapy": {"fertigation": "Potassium Phosphite @ 3 g/L.", "immunity_boost": "Calcium Chloride @ 2 g/L for berry skin firmness."},
                "frac_calendar": [{"spray": "Spray 1", "chem": "Fluopicolide + Fosetyl-Al", "frac": "FRAC 43 + P07"}],
                "recovery_milestones": {"day_0": "Apply systemic anti-oomycide.", "day_3": "Oil spots turn brown and crisp; white down ceases.", "day_7": "Cluster bunches protected."}
            },
            "recommendations": {
                "immediate": "Apply Fluopicolide + Fosetyl-Al @ 2.5 g/L or Mandipropamid @ 0.8 ml/L immediately.",
                "monitoring": "Check lower leaves for translucent oil-spots after rain events.",
                "prevention": "Ensure good shoot thinning and canopy aeration.",
                "expert_help": "Downy mildew in grapes can destroy an entire vineyard; alert local grape research center (NRCG)."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "20°C – 32°C", "humidity": "50% RH", "leaf_wetness": "Dry", "spread_vector": "None"},
            "symptoms": ["Lush green five-lobed leaves", "Clean vigorous vine shoots and uniform grape clusters"],
            "agronomic_prescription": {
                "field_sanitation": "Maintain vine trellis hygiene.",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Trichoderma vine drench."},
                "nutritional_therapy": {"fertigation": "Balanced fertigation according to pruning stage (Foundation vs Fruit)."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy vineyard status."}
            },
            "recommendations": {
                "immediate": "Maintain drip fertigation and canopy micro-climate monitoring.",
                "monitoring": "Routine scouting for thrips and powdery mildew.",
                "prevention": "Regular canopy management.",
                "expert_help": "Routine check."
            }
        }
    },
    "Default": {
        "Leaf Spot": {
            "pathogen": "Fungal / Bacterial Complex",
            "pathogen_class": "Foliar Pathogen Complex",
            "severity": "Moderate",
            "epiphytotic_triggers": {"temp_range": "22°C – 30°C", "humidity": ">80% RH", "leaf_wetness": ">4 hours", "spread_vector": "Rain splash and airborne conidia"},
            "symptoms": [
                "Scattered necrotic dark spots on foliage with chlorotic border halos",
                "Localized yellowing around lesion edges and leaf drop"
            ],
            "agronomic_prescription": {
                "field_sanitation": "Prune severely affected leaf blades and dispose away from field perimeter.",
                "chemical_control": {
                    "primary": {
                        "brand_name": "Saaf / Indofil M-45",
                        "active_ingredient": "Carbendazim 12% + Mancozeb 63% WP",
                        "dosage_per_liter": "2.0 g / L water",
                        "dosage_per_acre": "400 g in 200L water / Acre",
                        "frac_code": "FRAC 1 + FRAC M03",
                        "phi_days": 14,
                        "rei_hours": 24,
                        "technique": "Foliar spray with uniform canopy mist."
                    }
                },
                "organic_bio_control": {"bio_agent": "Trichoderma viride @ 10 g/L.", "botanical": "Neem Oil 10,000 PPM @ 4 ml/L."},
                "nutritional_therapy": {"fertigation": "Balanced NPK 19:19:19 @ 3 g/L.", "immunity_boost": "Zinc EDTA @ 1 g/L."},
                "frac_calendar": [{"spray": "Spray 1", "chem": "Carbendazim + Mancozeb", "frac": "FRAC 1 + M03"}],
                "recovery_milestones": {"day_0": "Apply broad-spectrum protectant.", "day_3": "Spot margins dry up.", "day_7": "New leaves healthy."}
            },
            "recommendations": {
                "immediate": "Apply Carbendazim + Mancozeb @ 2.0 g/L within 24h.",
                "monitoring": "Inspect new leaf flushes for spot recurrence.",
                "prevention": "Improve field drainage and plant spacing.",
                "expert_help": "Consult agricultural extension specialist if leaf drop increases."
            }
        },
        "Healthy": {
            "pathogen": "None",
            "pathogen_class": "Healthy",
            "severity": "Healthy",
            "epiphytotic_triggers": {"temp_range": "20°C – 30°C", "humidity": "60% RH", "leaf_wetness": "Dry", "spread_vector": "None"},
            "symptoms": ["Clean leaf surface", "Natural vibrant pigmentation with zero necrotic spots"],
            "agronomic_prescription": {
                "field_sanitation": "Maintain clean field perimeter.",
                "chemical_control": {"primary": {"brand_name": "None", "active_ingredient": "None", "dosage_per_liter": "0", "dosage_per_acre": "0", "frac_code": "N/A"}},
                "organic_bio_control": {"bio_agent": "Bio-fertilizers."},
                "nutritional_therapy": {"fertigation": "Balanced crop nutrition."},
                "frac_calendar": [],
                "recovery_milestones": {"day_0": "Healthy status."}
            },
            "recommendations": {
                "immediate": "Continue standard field management.",
                "monitoring": "Routine weekly canopy check.",
                "prevention": "Maintain proper moisture balance.",
                "expert_help": "Recheck if new symptoms develop."
            }
        }
    }
}
