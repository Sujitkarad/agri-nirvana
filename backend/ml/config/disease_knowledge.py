"""
Disease Knowledge Base — Structured symptom & treatment data for all 38 PlantVillage classes.

This is static reference data (not mock). The CLASSIFICATION driving which entry
gets selected is performed by real ML inference in Stage B. This data maps the
model's output class to actionable agronomic information.

Each entry is keyed by the raw PlantVillage class label and contains:
- display_name: Human-readable disease name
- crop: Crop name
- pathogen: Causal organism
- pathogen_category: Fungal / Bacterial / Viral / Oomycete / Arachnid
- symptoms_observed: List of visible symptom descriptions
- likely_cause: Brief epidemiological cause
- immediate_precautions: List of urgent actions
- treatment_organic: List of organic/biological control measures
- treatment_chemical: List of chemical control measures (with disclaimer)
- prevention_tips: List of long-term prevention strategies
- severity_baseline: Default severity if image analysis is unavailable
"""

DISEASE_KNOWLEDGE = {
    # ══════════════════════════════════════════════════════════
    # APPLE
    # ══════════════════════════════════════════════════════════
    "Apple___Apple_scab": {
        "display_name": "Apple Scab",
        "crop": "Apple",
        "pathogen": "Venturia inaequalis",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Olive-green to dark brown velvety spots on leaves",
            "Scabby, cracked lesions on fruit surface",
            "Premature leaf drop and defoliation",
            "Distorted or stunted fruit development"
        ],
        "likely_cause": "Fungal spores overwinter in fallen infected leaves; spread by rain splash during cool, wet spring weather (15-24°C with prolonged leaf wetness).",
        "immediate_precautions": [
            "Remove and destroy fallen infected leaves immediately",
            "Do not compost infected plant material",
            "Isolate severely affected trees to prevent spore spread",
            "Avoid overhead irrigation to reduce leaf wetness duration"
        ],
        "treatment_organic": [
            "Sulfur-based fungicide spray (wettable sulfur 80% WP) @ 3g/L at 7-day intervals",
            "Neem oil (Azadirachtin 10,000 PPM) @ 5 ml/L as preventive foliar spray",
            "Bordeaux mixture (1%) applied before bud break as dormant spray",
            "Bacillus subtilis-based biofungicide @ 5g/L foliar application"
        ],
        "treatment_chemical": [
            "Myclobutanil 40% WP @ 0.5g/L (FRAC Group 3) — systemic curative action",
            "Captan 50% WP @ 2.5g/L (FRAC Group M04) — protectant contact spray",
            "Mancozeb 75% WP @ 2.5g/L as rotational protectant (PHI: 77 days for apple)",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Plant scab-resistant apple varieties (e.g., Liberty, Enterprise, Pristine)",
            "Ensure adequate tree spacing for air circulation and canopy drying",
            "Apply urea (5% solution) to fallen leaves in autumn to accelerate decomposition",
            "Implement a fungicide spray calendar starting at green-tip bud stage"
        ],
        "severity_baseline": "moderate"
    },

    "Apple___Black_rot": {
        "display_name": "Black Rot",
        "crop": "Apple",
        "pathogen": "Botryosphaeria obtusa",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Circular brown lesions with concentric rings on leaves (frog-eye leaf spot)",
            "Firm, black, sunken rot on fruit starting at calyx or wound sites",
            "Dark reddish-brown cankers on branches and trunk",
            "Mummified fruit hanging on tree through winter"
        ],
        "likely_cause": "Fungal infection through wounds or natural openings; favored by warm humid weather (20-30°C). Spores overwinter in mummified fruit and cankers.",
        "immediate_precautions": [
            "Prune out all cankered branches at least 15cm below visible infection",
            "Remove mummified fruit from tree and ground",
            "Sterilize pruning tools with 70% alcohol between cuts",
            "Improve orchard sanitation — clear fallen debris"
        ],
        "treatment_organic": [
            "Copper hydroxide 77% WP @ 2g/L as dormant and early-season spray",
            "Neem oil @ 5ml/L as foliar protectant during growing season",
            "Trichoderma viride-based formulation @ 5g/L applied to pruning wounds",
            "Remove and burn all infected material promptly"
        ],
        "treatment_chemical": [
            "Thiophanate-methyl 70% WP @ 1g/L (FRAC Group 1) — systemic",
            "Captan 50% WP @ 2.5g/L as protective spray at petal fall",
            "Myclobutanil 40% WP @ 0.5g/L in rotation with protectants",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Maintain strict orchard hygiene — remove mummies and prune cankers annually",
            "Avoid fruit injury from insects, hail, or mechanical damage",
            "Apply fungicide sprays from green tip through second cover",
            "Ensure proper tree nutrition to maintain vigor against infection"
        ],
        "severity_baseline": "moderate"
    },

    "Apple___Cedar_apple_rust": {
        "display_name": "Cedar Apple Rust",
        "crop": "Apple",
        "pathogen": "Gymnosporangium juniperi-virginianae",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Bright orange-yellow spots on upper leaf surface",
            "Tubular spore-producing structures (aecia) on leaf undersides",
            "Orange lesions on fruit with minimal internal rot",
            "Premature defoliation in severe cases"
        ],
        "likely_cause": "Heteroecious rust fungus requiring both apple and Eastern red cedar (Juniperus) hosts to complete lifecycle. Spores travel up to 3km on wind during spring rains.",
        "immediate_precautions": [
            "Remove nearby cedar/juniper trees within 100m if feasible",
            "Remove galls from cedar trees before spring sporulation",
            "Apply protective fungicide at pink bud stage",
            "Remove heavily infected apple leaves to reduce inoculum"
        ],
        "treatment_organic": [
            "Sulfur-based fungicide @ 3g/L applied before and during bloom",
            "Neem oil @ 5ml/L as supplementary foliar protectant",
            "Remove cedar galls manually in late winter (before orange telial horns emerge)",
            "Potassium bicarbonate @ 5g/L as foliar spray to inhibit spore germination"
        ],
        "treatment_chemical": [
            "Myclobutanil 40% WP @ 0.5g/L (FRAC Group 3) — most effective for rust",
            "Propiconazole 25% EC @ 1ml/L applied at pink bud and petal fall",
            "Mancozeb 75% WP @ 2.5g/L as protectant in rotation",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Plant rust-resistant apple cultivars (e.g., Freedom, Redfree, Williams Pride)",
            "Eliminate alternate host (Juniperus spp.) within 300m radius",
            "Begin fungicide program at green-tip stage in rust-prone areas",
            "Monitor weather forecasts for warm rain periods during spring"
        ],
        "severity_baseline": "moderate"
    },

    "Apple___healthy": {
        "display_name": "Healthy",
        "crop": "Apple",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Uniform green leaf coloration with no lesions or spots",
            "Normal leaf shape and size without distortion",
            "No signs of fungal sporulation, wilting, or chlorosis"
        ],
        "likely_cause": "No pathological issues detected. Plant appears healthy.",
        "immediate_precautions": [
            "Continue regular monitoring as a preventive practice",
            "Maintain balanced nutrition and irrigation schedule"
        ],
        "treatment_organic": [
            "No treatment required — plant is healthy",
            "Consider preventive neem oil spray (3ml/L) bi-weekly during humid seasons"
        ],
        "treatment_chemical": [
            "No chemical treatment needed at this time",
            "Follow scheduled preventive spray calendar if in disease-prone region"
        ],
        "prevention_tips": [
            "Maintain good orchard sanitation and hygiene practices",
            "Monitor regularly for early signs of pest or disease onset",
            "Ensure balanced fertilization — avoid excess nitrogen",
            "Prune to maintain open canopy for air circulation"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # BLUEBERRY
    # ══════════════════════════════════════════════════════════
    "Blueberry___healthy": {
        "display_name": "Healthy",
        "crop": "Blueberry",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Healthy dark green foliage with no spots or discoloration",
            "Normal berry development and coloring"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": [
            "Continue standard monitoring and maintenance"
        ],
        "treatment_organic": ["No treatment required — plant is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Maintain acidic soil pH (4.5-5.5) for optimal blueberry health",
            "Apply organic mulch to retain moisture and suppress weeds",
            "Prune annually to improve air circulation and light penetration"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # CHERRY
    # ══════════════════════════════════════════════════════════
    "Cherry_(including_sour)___Powdery_mildew": {
        "display_name": "Powdery Mildew",
        "crop": "Cherry",
        "pathogen": "Podosphaera clandestina",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "White powdery fungal growth on leaf surfaces and young shoots",
            "Leaf curling, distortion, and stunted growth",
            "Fruit surface blemishes with reduced market quality",
            "Premature leaf drop in severe infections"
        ],
        "likely_cause": "Fungal spores spread by wind; favored by warm days (20-27°C), cool nights, and moderate humidity. Overwintering in dormant buds.",
        "immediate_precautions": [
            "Remove and destroy severely infected shoot tips",
            "Improve air circulation by thinning canopy",
            "Reduce nitrogen fertilization which promotes susceptible succulent growth"
        ],
        "treatment_organic": [
            "Potassium bicarbonate @ 5g/L + 2ml/L surfactant as foliar spray",
            "Sulfur-based fungicide (wettable sulfur) @ 3g/L at 7-10 day intervals",
            "Neem oil @ 5ml/L — disrupt fungal cell membrane",
            "Milk spray (40% whole milk dilution) as folk remedy with documented efficacy"
        ],
        "treatment_chemical": [
            "Myclobutanil 40% WP @ 0.5g/L (FRAC Group 3) — systemic",
            "Trifloxystrobin 50% WG @ 0.25g/L (FRAC Group 11) — translaminar",
            "Alternate FRAC groups to prevent resistance development",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Select powdery mildew-resistant cherry varieties when available",
            "Ensure proper spacing between trees for airflow",
            "Avoid late-season nitrogen applications",
            "Start preventive fungicide applications at shuck fall stage"
        ],
        "severity_baseline": "moderate"
    },

    "Cherry_(including_sour)___healthy": {
        "display_name": "Healthy",
        "crop": "Cherry",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Normal leaf coloration and shape",
            "No powdery deposits, spots, or deformities observed"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": ["Continue regular orchard monitoring"],
        "treatment_organic": ["No treatment required — plant is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Maintain balanced nutrition and proper irrigation",
            "Annual pruning for open canopy structure",
            "Monitor for early signs of powdery mildew during warm dry periods"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # CORN (MAIZE)
    # ══════════════════════════════════════════════════════════
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "display_name": "Gray Leaf Spot (Cercospora)",
        "crop": "Corn (Maize)",
        "pathogen": "Cercospora zeae-maydis",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Rectangular gray-tan lesions running parallel to leaf veins",
            "Lesions have sharp, parallel edges bounded by veins",
            "Severe infection causes extensive leaf blighting and premature drying",
            "Lower leaves affected first, progressing upward"
        ],
        "likely_cause": "Fungal spores survive on crop residue; spread by wind and rain splash during prolonged warm (25-30°C), humid conditions with heavy dew.",
        "immediate_precautions": [
            "Scout fields for lesion progression weekly",
            "Apply fungicide if disease reaches ear leaf before grain fill",
            "Avoid continuous corn planting in the same field"
        ],
        "treatment_organic": [
            "Trichoderma-based biofungicide @ 5g/L foliar spray",
            "Neem oil @ 5ml/L as supplementary treatment",
            "Crop residue incorporation to accelerate decomposition of inoculum"
        ],
        "treatment_chemical": [
            "Azoxystrobin 23% SC @ 1ml/L (FRAC Group 11) at VT-R1 (tasseling)",
            "Pyraclostrobin + Metconazole premix — dual-mode systemic action",
            "Propiconazole 25% EC @ 1ml/L as rotational spray",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Plant gray leaf spot-resistant corn hybrids",
            "Practice crop rotation with non-host crops (soybean, wheat)",
            "Tillage to bury infected crop residue and reduce surface inoculum",
            "Avoid planting corn-on-corn in fields with GLS history"
        ],
        "severity_baseline": "moderate"
    },

    "Corn_(maize)___Common_rust_": {
        "display_name": "Common Rust",
        "crop": "Corn (Maize)",
        "pathogen": "Puccinia sorghi",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Small, circular to elongated cinnamon-brown pustules on both leaf surfaces",
            "Pustules rupture to release powdery reddish-brown urediniospores",
            "Heavily infected leaves turn chlorotic and senesce prematurely",
            "Late-season pustules may turn dark brown-black (teliospores)"
        ],
        "likely_cause": "Airborne urediniospores carried by wind from southern regions; favored by moderate temperatures (16-23°C) and high humidity with dew.",
        "immediate_precautions": [
            "Monitor disease severity — yield loss occurs if infection is heavy before tasseling",
            "Apply foliar fungicide if pustule density is high on upper leaves",
            "Ensure adequate plant nutrition to support defense responses"
        ],
        "treatment_organic": [
            "Sulfur-based fungicide @ 3g/L as protectant spray",
            "Neem oil @ 5ml/L at early infection stages",
            "Bacillus-based biofungicide as preventive application"
        ],
        "treatment_chemical": [
            "Propiconazole 25% EC @ 1ml/L (FRAC Group 3) — effective on rust",
            "Azoxystrobin 23% SC @ 1ml/L at early pustule formation",
            "Mancozeb 75% WP @ 2.5g/L as contact protectant in rotation",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Plant rust-resistant corn hybrids (check local seed catalogs)",
            "Early planting to avoid peak rust spore arrival periods",
            "Monitor regional rust spore trap reports for early warning",
            "Balanced fertilization — avoid excess nitrogen"
        ],
        "severity_baseline": "moderate"
    },

    "Corn_(maize)___Northern_Leaf_Blight": {
        "display_name": "Northern Leaf Blight",
        "crop": "Corn (Maize)",
        "pathogen": "Exserohilum turcicum (Setosphaeria turcica)",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Large, cigar-shaped grayish-green to tan lesions (5-15cm long)",
            "Lesions start on lower leaves and progress upward",
            "Severe blighting can destroy entire leaf surface",
            "Grayish-black fungal sporulation on lesion surfaces during wet weather"
        ],
        "likely_cause": "Spores survive on corn residue; spread by wind and rain. Favored by moderate temperatures (18-27°C), heavy dew, and frequent rainfall.",
        "immediate_precautions": [
            "Apply foliar fungicide if lesions reach third leaf below ear before tasseling",
            "Scout fields regularly from V8 stage onward",
            "Ensure adequate potassium nutrition to strengthen cell walls"
        ],
        "treatment_organic": [
            "Trichoderma harzianum @ 5g/L as foliar biocontrol agent",
            "Neem oil @ 5ml/L combined with copper-based fungicide",
            "Crop residue management — deep plowing to bury inoculum"
        ],
        "treatment_chemical": [
            "Azoxystrobin + Propiconazole premix @ 1ml/L at tassel emergence",
            "Pyraclostrobin 20% WG @ 0.75g/L (FRAC Group 11) — broad-spectrum",
            "Mancozeb 75% WP @ 2.5g/L as preventive protectant spray",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Plant NLB-resistant hybrids with Ht genes (Ht1, Ht2, Ht3, HtN)",
            "Crop rotation with soybean, wheat, or other non-host crops",
            "Tillage to reduce surface residue inoculum",
            "Avoid late planting which extends exposure to favorable disease conditions"
        ],
        "severity_baseline": "severe"
    },

    "Corn_(maize)___healthy": {
        "display_name": "Healthy",
        "crop": "Corn (Maize)",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Normal green leaf coloration without spots or lesions",
            "Healthy stalk and ear development on track"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": ["Continue standard crop monitoring"],
        "treatment_organic": ["No treatment required — plant is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Maintain balanced NPK fertilization",
            "Practice crop rotation to break disease cycles",
            "Scout regularly for early disease and pest detection"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # GRAPE
    # ══════════════════════════════════════════════════════════
    "Grape___Black_rot": {
        "display_name": "Black Rot",
        "crop": "Grape",
        "pathogen": "Guignardia bidwellii",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Circular reddish-brown leaf spots with dark borders",
            "Black pycnidia (fruiting bodies) visible in lesion centers",
            "Berries develop brown rot, shrivel, and become hard black mummies",
            "Rapid fruit destruction — entire clusters can be lost"
        ],
        "likely_cause": "Ascospores from overwintered mummified berries; warm (20-30°C) wet weather during bloom and fruit development. Requires 6+ hours of leaf wetness.",
        "immediate_precautions": [
            "Remove all mummified berries from vines and ground",
            "Apply fungicide immediately at first sign of infection",
            "Improve canopy management to reduce humidity"
        ],
        "treatment_organic": [
            "Copper hydroxide 77% WP @ 2g/L applied pre-bloom through veraison",
            "Sulfur spray @ 3g/L as protectant between rain events",
            "Rigorous sanitation — remove and destroy mummies and infected leaves"
        ],
        "treatment_chemical": [
            "Myclobutanil 40% WP @ 0.5g/L (FRAC Group 3) — highly effective",
            "Mancozeb 75% WP @ 2.5g/L as protectant from bud break to veraison",
            "Captan 50% WP @ 2g/L in rotation with systemic fungicides",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Remove all mummified fruit before bud break in spring",
            "Canopy management — leaf pulling and shoot positioning for airflow",
            "Begin fungicide program at bud break, continue through 4-5 weeks post-bloom",
            "Plant resistant grape varieties where available"
        ],
        "severity_baseline": "severe"
    },

    "Grape___Esca_(Black_Measles)": {
        "display_name": "Esca (Black Measles)",
        "crop": "Grape",
        "pathogen": "Phaeomoniella chlamydospora / Phaeoacremonium spp. / Fomitiporia mediterranea",
        "pathogen_category": "Fungal Complex",
        "symptoms_observed": [
            "Interveinal 'tiger-stripe' leaf discoloration (chlorosis with necrotic margins)",
            "Dark spots on berry skin resembling measles",
            "Sudden vine collapse (apoplexy) in hot weather",
            "Cross-sectional trunk cuts show central necrotic wood ('black goo')"
        ],
        "likely_cause": "Complex of wood-decay fungi colonizing through pruning wounds. Disease develops over years; symptoms express during heat stress. No known cure for established infections.",
        "immediate_precautions": [
            "Mark affected vines for monitoring — do not prune when wet",
            "Protect pruning wounds with wound sealant or Trichoderma paste",
            "Remove severely collapsed vines to prevent spread",
            "Delay pruning until dry weather to reduce wound infection risk"
        ],
        "treatment_organic": [
            "Trichoderma-based wound paste applied to fresh pruning cuts",
            "Sodium arsenite banned in most regions — no curative organic option exists",
            "Trunk renewal surgery — cut back to healthy wood below infection zone",
            "Preventive double-pruning technique to allow wound healing before final cuts"
        ],
        "treatment_chemical": [
            "No effective curative chemical treatment exists for established Esca",
            "Protective pruning wound sealants (e.g., Biopaste) reduce new infections",
            "Foliar phosphonate treatments may reduce symptom expression in some studies",
            "⚠️ Esca management is primarily sanitation-based — consult a viticulture specialist"
        ],
        "prevention_tips": [
            "Protect pruning wounds — apply wound sealant within 24 hours of cuts",
            "Use double-pruning technique in established vineyards",
            "Avoid wet-weather pruning; sterilize tools between vines",
            "Replace dead vines with clean nursery stock; inspect for trunk discoloration"
        ],
        "severity_baseline": "severe"
    },

    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "display_name": "Leaf Blight (Isariopsis Leaf Spot)",
        "crop": "Grape",
        "pathogen": "Pseudocercospora vitis (syn. Isariopsis clavispora)",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Angular dark brown spots with yellowish margins on leaves",
            "Lesions coalesce causing large necrotic patches and defoliation",
            "Dark fungal sporulation visible on lower leaf surface",
            "Progressive defoliation reduces fruit quality and vine vigor"
        ],
        "likely_cause": "Fungal spores spread by rain splash; favored by warm humid conditions. More common in tropical and subtropical grape-growing regions.",
        "immediate_precautions": [
            "Remove severely infected leaves to reduce inoculum",
            "Improve canopy airflow through shoot positioning and leaf pulling",
            "Apply protectant fungicide during wet weather periods"
        ],
        "treatment_organic": [
            "Copper oxychloride @ 2.5g/L as protective foliar spray",
            "Bordeaux mixture (1%) applied at 10-day intervals during rainy season",
            "Neem oil @ 5ml/L as supplementary organic treatment"
        ],
        "treatment_chemical": [
            "Mancozeb 75% WP @ 2.5g/L (FRAC Group M03) — multi-site protectant",
            "Carbendazim 50% WP @ 1g/L (FRAC Group 1) — systemic curative",
            "Difenoconazole 25% EC @ 0.5ml/L in rotation to prevent resistance",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Ensure proper vine spacing and trellis management for air circulation",
            "Remove fallen leaves and debris from vineyard floor",
            "Start preventive sprays before onset of rainy season",
            "Maintain balanced vine nutrition — avoid excess nitrogen"
        ],
        "severity_baseline": "moderate"
    },

    "Grape___healthy": {
        "display_name": "Healthy",
        "crop": "Grape",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Healthy green canopy with no spots or discoloration",
            "Normal fruit development and color"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": ["Continue regular vineyard scouting"],
        "treatment_organic": ["No treatment required — vine is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Maintain canopy management for optimal airflow",
            "Follow regional spray calendar as preventive measure",
            "Monitor for early signs of downy mildew during humid periods"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # ORANGE
    # ══════════════════════════════════════════════════════════
    "Orange___Haunglongbing_(Citrus_greening)": {
        "display_name": "Huanglongbing (Citrus Greening)",
        "crop": "Orange",
        "pathogen": "Candidatus Liberibacter asiaticus (bacterium, psyllid-vectored)",
        "pathogen_category": "Bacterial",
        "symptoms_observed": [
            "Asymmetric blotchy mottle pattern on leaves (yellow and green patches)",
            "Small, lopsided, poorly colored fruit with aborted seeds",
            "Vein yellowing (vein corking) and leaf drop",
            "Stunted tree growth and branch dieback over time"
        ],
        "likely_cause": "Phloem-limited bacterium transmitted by Asian citrus psyllid (Diaphorina citri). Systemic infection — once infected, tree cannot be cured.",
        "immediate_precautions": [
            "Report suspected HLB to local agricultural department immediately",
            "Control Asian citrus psyllid vector aggressively",
            "Remove confirmed infected trees to protect neighboring groves",
            "Do not move plant material from infected areas"
        ],
        "treatment_organic": [
            "No curative treatment exists for HLB — management is vector control",
            "Neem oil @ 5ml/L to deter psyllid feeding (supplementary only)",
            "Release natural enemies of citrus psyllid (Tamarixia radiata)",
            "Nutrient supplementation (zinc, manganese, iron foliar sprays) to extend tree productivity"
        ],
        "treatment_chemical": [
            "Imidacloprid soil drench for systemic psyllid control",
            "Abamectin or spirotetramat foliar sprays targeting psyllid nymphs",
            "Enhanced foliar nutrition programs to mitigate yield decline",
            "⚠️ No known cure — management focuses on vector control and tree removal. Consult citrus pathologist."
        ],
        "prevention_tips": [
            "Use certified disease-free nursery stock for all new plantings",
            "Implement area-wide coordinated psyllid management programs",
            "Install psyllid monitoring traps in groves",
            "Consider HLB-tolerant rootstock/scion combinations where available"
        ],
        "severity_baseline": "severe"
    },

    # ══════════════════════════════════════════════════════════
    # PEACH
    # ══════════════════════════════════════════════════════════
    "Peach___Bacterial_spot": {
        "display_name": "Bacterial Spot",
        "crop": "Peach",
        "pathogen": "Xanthomonas arboricola pv. pruni",
        "pathogen_category": "Bacterial",
        "symptoms_observed": [
            "Small, dark brown to black angular spots on leaves",
            "Spots may coalesce causing 'shot-hole' appearance as tissue drops out",
            "Sunken, dark circular lesions on fruit surface",
            "Severe defoliation reduces tree vigor and winter hardiness"
        ],
        "likely_cause": "Bacteria spread by wind-driven rain; enter through stomata and wounds. Favored by warm (25-30°C), humid weather with frequent rainfall.",
        "immediate_precautions": [
            "Avoid overhead irrigation — minimize leaf wetness",
            "Do not handle or prune trees when foliage is wet",
            "Remove severely infected fruit to reduce bacterial load"
        ],
        "treatment_organic": [
            "Copper hydroxide 77% WP @ 2g/L applied at leaf fall and bud swell",
            "Bacillus subtilis-based bactericide as growing-season supplement",
            "Avoid copper applications during fruit development (phytotoxicity risk)"
        ],
        "treatment_chemical": [
            "Oxytetracycline 17% @ labeled rate during bloom period",
            "Copper + Mancozeb tank mix for dormant applications",
            "Limited in-season options — bacterial diseases are harder to control chemically",
            "⚠️ Consult local extension — product registration varies by region"
        ],
        "prevention_tips": [
            "Plant bacterial spot-resistant peach varieties",
            "Site orchards with good air drainage to reduce leaf wetness duration",
            "Windbreaks reduce wind-driven rain spread of bacteria",
            "Balanced nitrogen — excess promotes susceptible succulent growth"
        ],
        "severity_baseline": "moderate"
    },

    "Peach___healthy": {
        "display_name": "Healthy",
        "crop": "Peach",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Normal green leaf coloration without spots or holes",
            "Healthy fruit development"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": ["Continue routine orchard monitoring"],
        "treatment_organic": ["No treatment required — tree is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Apply dormant copper spray as standard preventive",
            "Prune for open center tree form to improve airflow",
            "Monitor for bacterial spot symptoms during wet spring weather"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # PEPPER (BELL)
    # ══════════════════════════════════════════════════════════
    "Pepper,_bell___Bacterial_spot": {
        "display_name": "Bacterial Spot",
        "crop": "Pepper (Bell)",
        "pathogen": "Xanthomonas campestris pv. vesicatoria",
        "pathogen_category": "Bacterial",
        "symptoms_observed": [
            "Small, water-soaked dark spots on leaves turning brown with yellow halo",
            "Raised, scab-like lesions on fruit surface",
            "Severe defoliation exposing fruit to sunscald",
            "Leaf spots may coalesce into large blighted areas"
        ],
        "likely_cause": "Seed-borne or transplant-borne bacteria; spread by rain splash and overhead irrigation. Favored by warm (24-30°C), humid, rainy conditions.",
        "immediate_precautions": [
            "Switch to drip irrigation immediately — stop overhead watering",
            "Remove and destroy severely infected plants",
            "Avoid working in fields when foliage is wet",
            "Do not save seed from infected plants"
        ],
        "treatment_organic": [
            "Copper hydroxide 77% WP @ 2g/L at 7-day intervals during wet weather",
            "Bacillus-based biological bactericide as growing-season spray",
            "Copper + sulfur rotation for resistance management",
            "Acibenzolar-S-methyl (plant resistance inducer) if available"
        ],
        "treatment_chemical": [
            "Copper-based bactericides (fixed copper) @ 2g/L — primary control",
            "Streptomycin sulfate @ labeled rate where registered (limited regions)",
            "Mancozeb 75% WP @ 2.5g/L as rotational partner with copper",
            "⚠️ Bacterial diseases have limited chemical control — integrate with cultural practices"
        ],
        "prevention_tips": [
            "Use certified disease-free, hot water-treated seed",
            "Plant resistant pepper varieties when available",
            "Rotate with non-solanaceous crops for 2-3 years",
            "Avoid overhead irrigation and field work during wet conditions"
        ],
        "severity_baseline": "moderate"
    },

    "Pepper,_bell___healthy": {
        "display_name": "Healthy",
        "crop": "Pepper (Bell)",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Normal green foliage without spots or wilting",
            "Healthy fruit set and development"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": ["Continue standard crop management"],
        "treatment_organic": ["No treatment required — plant is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Use drip irrigation to minimize foliar wetness",
            "Maintain 45-60cm spacing for airflow",
            "Scout weekly for early signs of bacterial spot during rainy periods"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # POTATO
    # ══════════════════════════════════════════════════════════
    "Potato___Early_blight": {
        "display_name": "Early Blight",
        "crop": "Potato",
        "pathogen": "Alternaria solani",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Dark brown circular lesions with concentric target-board rings on leaves",
            "Progressive yellowing (chlorosis) around lesion margins",
            "Lower leaves affected first, disease moves upward",
            "Dark sunken lesions on tubers at harvest"
        ],
        "likely_cause": "Fungal conidia from infected debris; warm (24-29°C) humid conditions with alternating wet/dry cycles. Stressed or senescing plants are most susceptible.",
        "immediate_precautions": [
            "Remove and destroy lower infected leaves immediately",
            "Apply protectant fungicide within 24 hours of symptom detection",
            "Maintain adequate irrigation to reduce plant stress",
            "Avoid overhead irrigation after canopy closure"
        ],
        "treatment_organic": [
            "Trichoderma harzianum + Pseudomonas fluorescens @ 10g/L foliar spray",
            "Neem oil (Azadirachtin 10,000 PPM) @ 5ml/L every 5-7 days",
            "Bordeaux mixture (1%) as preventive spray before symptoms appear",
            "Potassium phosphite @ 3ml/L to induce systemic resistance"
        ],
        "treatment_chemical": [
            "Azoxystrobin 23% SC + Difenoconazole 11.4% SC @ 1ml/L (FRAC 11+3)",
            "Mancozeb 75% WP @ 2.5g/L (FRAC M03) as protectant in rotation",
            "Chlorothalonil 75% WP @ 2g/L at 7-10 day intervals",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Plant certified disease-free seed tubers",
            "Practice 2-3 year crop rotation with non-solanaceous crops",
            "Hill soil around plants to prevent tuber infection from spore wash",
            "Balanced fertilization — avoid excess nitrogen; ensure adequate potassium"
        ],
        "severity_baseline": "moderate"
    },

    "Potato___Late_blight": {
        "display_name": "Late Blight",
        "crop": "Potato",
        "pathogen": "Phytophthora infestans",
        "pathogen_category": "Oomycete",
        "symptoms_observed": [
            "Large water-soaked gray-green to dark brown lesions on leaves",
            "White fuzzy sporulation on leaf undersides during humid conditions",
            "Rapid stem and petiole blackening with tissue collapse",
            "Firm, granular, reddish-brown rot in tubers extending inward"
        ],
        "likely_cause": "Airborne sporangia from infected fields or cull piles; cool (15-22°C), wet, humid conditions with persistent leaf wetness. Can devastate entire fields in 7-10 days.",
        "immediate_precautions": [
            "Apply systemic fungicide IMMEDIATELY — late blight spreads extremely fast",
            "Destroy all volunteer potato plants and cull piles",
            "Notify neighboring growers and local extension of outbreak",
            "Consider vine destruction if infection is >25% to protect tubers"
        ],
        "treatment_organic": [
            "Copper hydroxide 77% WP @ 3g/L at 5-day intervals during outbreaks",
            "Bordeaux mixture (1%) as emergency protective spray",
            "Phosphorous acid-based products @ 3ml/L for resistance induction",
            "No fully effective organic cure — focus on prevention and rapid response"
        ],
        "treatment_chemical": [
            "Metalaxyl-M 4% + Mancozeb 64% WP (Ridomil Gold MZ) @ 2.5g/L — first line",
            "Cymoxanil 8% + Mancozeb 64% WP @ 2.5g/L — curative + protectant",
            "Mandipropamid 23.4% SC @ 0.6ml/L (FRAC 40) — rain-fast protection",
            "⚠️ URGENT: Apply within 24h of first symptoms. Consult local extension immediately."
        ],
        "prevention_tips": [
            "Plant certified disease-free seed tubers only",
            "Use late blight-resistant varieties when available",
            "Eliminate cull piles and volunteer plants that harbor inoculum",
            "Monitor late blight forecast systems (e.g., Blitecast) for spray timing"
        ],
        "severity_baseline": "severe"
    },

    "Potato___healthy": {
        "display_name": "Healthy",
        "crop": "Potato",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Normal green foliage without spots or wilting",
            "Healthy canopy with good growth vigor"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": ["Continue regular field scouting"],
        "treatment_organic": ["No treatment required — crop is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Use certified seed tubers and practice 3-year rotation",
            "Hill adequately to protect tubers from blight spore wash",
            "Monitor weather for late blight-favorable conditions"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # RASPBERRY
    # ══════════════════════════════════════════════════════════
    "Raspberry___healthy": {
        "display_name": "Healthy",
        "crop": "Raspberry",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Normal green compound leaves without spots",
            "Healthy cane growth and fruit development"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": ["Continue regular monitoring"],
        "treatment_organic": ["No treatment required — plant is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Prune spent floricanes after harvest",
            "Maintain 1m spacing between rows for airflow",
            "Apply dormant copper spray in early spring"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # SOYBEAN
    # ══════════════════════════════════════════════════════════
    "Soybean___healthy": {
        "display_name": "Healthy",
        "crop": "Soybean",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Normal trifoliate leaf development without spots",
            "Healthy nodulation and growth"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": ["Continue standard crop monitoring"],
        "treatment_organic": ["No treatment required — crop is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Use quality certified seed with seed treatment",
            "Rotate with non-legume crops to break disease cycles",
            "Scout for soybean rust during R1-R3 growth stages"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # SQUASH
    # ══════════════════════════════════════════════════════════
    "Squash___Powdery_mildew": {
        "display_name": "Powdery Mildew",
        "crop": "Squash",
        "pathogen": "Podosphaera xanthii / Erysiphe cichoracearum",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "White powdery fungal colonies on upper and lower leaf surfaces",
            "Yellowing and browning of infected leaves",
            "Premature leaf death reducing photosynthesis and fruit quality",
            "Fruit may develop sunscald due to loss of leaf canopy"
        ],
        "likely_cause": "Airborne conidia; favored by warm days (20-30°C), cool nights, moderate humidity. Does NOT require free water — thrives in dry conditions unlike most fungi.",
        "immediate_precautions": [
            "Remove and destroy heavily infected older leaves",
            "Avoid excess nitrogen fertilization",
            "Apply fungicide at first sign of white powder on leaves"
        ],
        "treatment_organic": [
            "Potassium bicarbonate @ 5g/L + 2ml/L horticultural oil as spreader",
            "Sulfur-based fungicide @ 3g/L at 7-day intervals (avoid in heat >35°C)",
            "Neem oil @ 5ml/L as preventive spray",
            "Milk spray (40% dilution of whole milk) — documented antifungal activity"
        ],
        "treatment_chemical": [
            "Myclobutanil 40% WP @ 0.5g/L (FRAC Group 3) — systemic curative",
            "Trifloxystrobin 50% WG @ 0.25g/L (FRAC Group 11) — translaminar",
            "Alternate chemical families to prevent resistance (common in PM)",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Plant powdery mildew-resistant squash varieties",
            "Ensure adequate plant spacing for airflow",
            "Avoid late-afternoon overhead irrigation",
            "Start preventive sprays when conditions favor PM development"
        ],
        "severity_baseline": "moderate"
    },

    # ══════════════════════════════════════════════════════════
    # STRAWBERRY
    # ══════════════════════════════════════════════════════════
    "Strawberry___Leaf_scorch": {
        "display_name": "Leaf Scorch",
        "crop": "Strawberry",
        "pathogen": "Diplocarpon earlianum",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Small, irregular dark purple spots on upper leaf surface",
            "Spots enlarge and coalesce, giving leaves a scorched or burned appearance",
            "Leaf margins turn dark brown and curl upward",
            "Severely infected plants show reduced vigor and runner production"
        ],
        "likely_cause": "Fungal spores from infected debris; warm (22-28°C) wet conditions with overhead irrigation or rain. Spreads through splashing water.",
        "immediate_precautions": [
            "Remove and destroy infected leaves immediately",
            "Switch to drip irrigation if using overhead sprinklers",
            "Apply protectant fungicide before symptoms spread to new growth"
        ],
        "treatment_organic": [
            "Copper-based fungicide @ 2g/L at first sign of symptoms",
            "Neem oil @ 5ml/L as supplementary foliar spray",
            "Trichoderma-based biofungicide as soil drench and foliar application",
            "Straw or plastic mulch to prevent soil splash of spores onto leaves"
        ],
        "treatment_chemical": [
            "Myclobutanil 40% WP @ 0.5g/L (FRAC Group 3) — systemic",
            "Captan 50% WP @ 2g/L as protectant spray",
            "Azoxystrobin 23% SC @ 0.75ml/L at 10-14 day intervals",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Plant leaf scorch-resistant strawberry cultivars",
            "Use drip irrigation — avoid overhead watering",
            "Renovate beds after harvest — mow, thin, and apply fresh mulch",
            "Ensure adequate plant spacing for air circulation"
        ],
        "severity_baseline": "moderate"
    },

    "Strawberry___healthy": {
        "display_name": "Healthy",
        "crop": "Strawberry",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Healthy trifoliate leaves without spots or discoloration",
            "Normal runner and fruit production"
        ],
        "likely_cause": "No pathological issues detected.",
        "immediate_precautions": ["Continue standard monitoring"],
        "treatment_organic": ["No treatment required — plant is healthy"],
        "treatment_chemical": ["No chemical treatment needed"],
        "prevention_tips": [
            "Maintain clean straw or plastic mulch around plants",
            "Use drip irrigation to minimize leaf wetness",
            "Scout regularly for early signs of leaf spot or scorch"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # TOMATO
    # ══════════════════════════════════════════════════════════
    "Tomato___Bacterial_spot": {
        "display_name": "Bacterial Spot",
        "crop": "Tomato",
        "pathogen": "Xanthomonas campestris pv. vesicatoria",
        "pathogen_category": "Bacterial",
        "symptoms_observed": [
            "Small, dark brown to black water-soaked spots on leaves",
            "Spots may develop a yellow halo and become angular",
            "Raised, scab-like lesions on green fruit",
            "Severe defoliation leading to sunscald on exposed fruit"
        ],
        "likely_cause": "Seed-borne bacteria; spread by rain splash and overhead irrigation. Thrives in warm (24-30°C), humid, rainy conditions.",
        "immediate_precautions": [
            "Switch to drip irrigation immediately",
            "Avoid handling plants when wet",
            "Remove severely infected plants to reduce bacterial spread",
            "Apply copper-based bactericide"
        ],
        "treatment_organic": [
            "Copper hydroxide 77% WP @ 2g/L at 5-7 day intervals during wet weather",
            "Bacillus subtilis-based bactericide as supplementary spray",
            "Copper + sulfur alternation to reduce phytotoxicity",
            "Acibenzolar-S-methyl for induced systemic resistance"
        ],
        "treatment_chemical": [
            "Fixed copper bactericides @ 2g/L — primary option (limited alternatives)",
            "Mancozeb 75% WP @ 2.5g/L in tank mix with copper for enhanced protection",
            "Streptomycin sulfate where legally registered (check local regulations)",
            "⚠️ Bacterial diseases have limited chemical options — integrate with IPM practices"
        ],
        "prevention_tips": [
            "Use certified disease-free, hot water-treated seed",
            "Plant resistant varieties when available",
            "3-year crop rotation with non-solanaceous crops",
            "Drip irrigation only — eliminate all overhead watering"
        ],
        "severity_baseline": "moderate"
    },

    "Tomato___Early_blight": {
        "display_name": "Early Blight",
        "crop": "Tomato",
        "pathogen": "Alternaria solani",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Dark brown circular target-board lesions with concentric rings on leaves",
            "Progressive chlorotic yellow halo surrounding active necrosis",
            "Lower canopy leaf senescence and premature defoliation",
            "Collar rot and sunken dark cankers on lower stems"
        ],
        "likely_cause": "Fungal conidia from soil and infected debris; warm (24-29°C), humid conditions with alternating wet/dry periods and >4 hours continuous leaf wetness.",
        "immediate_precautions": [
            "Prune and bag all lower infected leaves up to 20cm from ground",
            "Do NOT compost infected material — burn or deeply bury",
            "Apply systemic fungicide within 24 hours",
            "Reduce nitrogen immediately — excess N creates thin cuticle layers"
        ],
        "treatment_organic": [
            "Trichoderma harzianum + Pseudomonas fluorescens @ 10g/L foliar spray",
            "Neem oil (Azadirachtin 10,000 PPM) @ 5ml/L every 5-7 days",
            "Potassium phosphite @ 5g/L to stimulate Systemic Acquired Resistance (SAR)",
            "Bordeaux mixture (1%) as protective spray on healthy foliage"
        ],
        "treatment_chemical": [
            "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1ml/L (FRAC 11+3) — first line",
            "Mancozeb 75% WP @ 2.5g/L (FRAC M03) as rotational protectant (PHI: 7 days)",
            "Chlorothalonil 75% WP @ 2g/L at 7-10 day intervals as alternate rotation",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Install silver-black plastic mulch to reduce soil splash",
            "Shift from overhead to drip irrigation",
            "Ensure 60cm row spacing for airflow",
            "2-3 year rotation with non-solanaceous crops"
        ],
        "severity_baseline": "moderate"
    },

    "Tomato___Late_blight": {
        "display_name": "Late Blight",
        "crop": "Tomato",
        "pathogen": "Phytophthora infestans",
        "pathogen_category": "Oomycete",
        "symptoms_observed": [
            "Water-soaked irregular grayish-black lesions with pale green margin halos",
            "White frosty downy fungal sporulation on lower leaf surface in humidity",
            "Rapid petiole and stem necrosis leading to sudden canopy collapse",
            "Greasy brown firm rot on green and ripe tomato fruits"
        ],
        "likely_cause": "Airborne sporangia from infected fields; cool (15-22°C), damp conditions with >90% RH. Can travel up to 10km on wind. Entire field destruction possible in 5-7 days.",
        "immediate_precautions": [
            "Apply systemic fungicide IMMEDIATELY — this is an emergency",
            "Destroy all volunteer solanaceous plants and cull piles",
            "Notify neighboring growers and local agricultural extension",
            "Consider vine destruction if infection exceeds 25%"
        ],
        "treatment_organic": [
            "Copper hydroxide 77% WP @ 3g/L at 3-5 day intervals during outbreak",
            "Bordeaux mixture (1%) as emergency protective application",
            "Phosphorous acid @ 3ml/L for systemic resistance induction",
            "No fully curative organic option — focus on rapid response and prevention"
        ],
        "treatment_chemical": [
            "Metalaxyl-M 4% + Mancozeb 64% WP (Ridomil Gold MZ) @ 2.5g/L — URGENT first line",
            "Cymoxanil 8% + Mancozeb 64% WP @ 2.5g/L — curative + protectant",
            "Dimethomorph 50% WP @ 1g/L (FRAC 40) — oomycete-specific, rain-fast",
            "⚠️ CRITICAL: Apply within 24h of first symptoms. Late blight is a phytosanitary emergency."
        ],
        "prevention_tips": [
            "Plant certified disease-free transplants and resistant varieties",
            "Morning drip irrigation only — eliminate foliar wetness",
            "Monitor late blight forecasting systems for your region",
            "Remove and destroy volunteer tomato and potato plants"
        ],
        "severity_baseline": "severe"
    },

    "Tomato___Leaf_Mold": {
        "display_name": "Leaf Mold",
        "crop": "Tomato",
        "pathogen": "Passalora fulva (syn. Cladosporium fulvum)",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Pale greenish-yellow diffuse spots on upper leaf surface",
            "Olive-green to brown velvety mold growth on corresponding lower surface",
            "Progressive leaf yellowing, curling, and drop from lower canopy upward",
            "Primarily a greenhouse/high-tunnel disease"
        ],
        "likely_cause": "Airborne conidia favored by high humidity (>85% RH) and warm temperatures (22-25°C). Common in protected cultivation (greenhouses, poly-tunnels).",
        "immediate_precautions": [
            "Increase ventilation in greenhouse — reduce humidity below 85%",
            "Remove and destroy infected lower leaves",
            "Increase plant spacing to improve air circulation",
            "Avoid overhead irrigation in protected structures"
        ],
        "treatment_organic": [
            "Potassium bicarbonate @ 5g/L as foliar spray",
            "Bacillus-based biofungicide @ 5g/L at 7-day intervals",
            "Neem oil @ 5ml/L as supplementary protectant",
            "Ventilation and humidity management are the primary control"
        ],
        "treatment_chemical": [
            "Difenoconazole 25% EC @ 0.5ml/L (FRAC Group 3) — systemic",
            "Chlorothalonil 75% WP @ 2g/L as contact protectant",
            "Azoxystrobin 23% SC @ 0.75ml/L in rotation",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Plant leaf mold-resistant tomato varieties (carrying Cf resistance genes)",
            "Maintain greenhouse humidity below 85% with ventilation/dehumidification",
            "Avoid leaf wetness — use drip irrigation and morning watering only",
            "Sterilize greenhouse structures between crop cycles"
        ],
        "severity_baseline": "moderate"
    },

    "Tomato___Septoria_leaf_spot": {
        "display_name": "Septoria Leaf Spot",
        "crop": "Tomato",
        "pathogen": "Septoria lycopersici",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Numerous small (2-3mm) circular spots with dark brown borders",
            "Grayish-white spot centers with tiny black pycnidia (spore structures)",
            "Severe defoliation starting from lower canopy",
            "Fruit rarely directly infected but exposed to sunscald from leaf loss"
        ],
        "likely_cause": "Fungal spores splash from soil and infected debris during rain or overhead irrigation. Favored by warm (20-25°C), wet conditions with frequent rainfall.",
        "immediate_precautions": [
            "Remove infected lower leaves immediately",
            "Apply protectant fungicide to remaining healthy foliage",
            "Mulch around plants to prevent soil splash",
            "Switch to drip irrigation if using overhead"
        ],
        "treatment_organic": [
            "Copper-based fungicide @ 2g/L at 7-day intervals",
            "Neem oil @ 5ml/L as supplementary foliar spray",
            "Trichoderma-based biofungicide as preventive application",
            "Organic mulch barrier to prevent soil splash"
        ],
        "treatment_chemical": [
            "Chlorothalonil 75% WP @ 2g/L (FRAC M05) — effective protectant",
            "Mancozeb 75% WP @ 2.5g/L in rotation with chlorothalonil",
            "Azoxystrobin 23% SC @ 0.75ml/L for systemic + protectant action",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Mulch heavily to prevent rain splash from contaminated soil",
            "3-year crop rotation with non-solanaceous crops",
            "Remove and destroy all plant debris at end of season",
            "Stake/cage plants to keep foliage off ground"
        ],
        "severity_baseline": "moderate"
    },

    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "display_name": "Spider Mites (Two-Spotted Spider Mite)",
        "crop": "Tomato",
        "pathogen": "Tetranychus urticae",
        "pathogen_category": "Arachnid (Pest)",
        "symptoms_observed": [
            "Fine stippling (tiny pale dots) on upper leaf surface from mite feeding",
            "Leaves turn bronze, yellow, and eventually dry brown",
            "Fine silk webbing visible on leaf undersides and between leaves",
            "Severe infestations cause rapid defoliation and plant decline"
        ],
        "likely_cause": "Mite populations explode in hot (>30°C), dry conditions. Common in drought-stressed plants. Broad-spectrum insecticides can worsen outbreaks by killing natural predators.",
        "immediate_precautions": [
            "Hose down plants with strong water spray to dislodge mites",
            "Increase humidity around plants to discourage mite reproduction",
            "Avoid using broad-spectrum insecticides that kill mite predators",
            "Isolate severely infested plants"
        ],
        "treatment_organic": [
            "Neem oil @ 5ml/L — disrupts mite feeding and reproduction",
            "Insecticidal soap spray @ 20ml/L — direct contact kill",
            "Release predatory mites (Phytoseiulus persimilis) as biological control",
            "Sulfur-based miticide @ 3g/L (avoid in heat >35°C)"
        ],
        "treatment_chemical": [
            "Abamectin 1.9% EC @ 0.5ml/L — translaminar acaricide",
            "Spiromesifen 22.9% SC @ 0.5ml/L (lipid synthesis inhibitor)",
            "Bifenazate 50% WP @ 0.5g/L as rotational miticide",
            "⚠️ Rotate acaricide classes to prevent resistance. Consult local extension."
        ],
        "prevention_tips": [
            "Monitor leaf undersides weekly with 10x hand lens",
            "Maintain adequate irrigation — water-stressed plants attract mites",
            "Conserve natural predators — avoid broad-spectrum insecticides",
            "Remove weedy hosts around field borders"
        ],
        "severity_baseline": "moderate"
    },

    "Tomato___Target_Spot": {
        "display_name": "Target Spot",
        "crop": "Tomato",
        "pathogen": "Corynespora cassiicola",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Circular brown lesions with concentric rings (target pattern) on leaves",
            "Lesions may have yellow halo and can be confused with early blight",
            "Fruit lesions: sunken, circular, with concentric rings",
            "Severe defoliation in warm, humid conditions"
        ],
        "likely_cause": "Fungal conidia spread by wind and rain; favored by warm (25-30°C) humid conditions. Can infect many plant species beyond tomato.",
        "immediate_precautions": [
            "Remove infected lower leaves to slow spread",
            "Apply broad-spectrum protectant fungicide",
            "Improve airflow through staking and pruning",
            "Avoid working in fields when foliage is wet"
        ],
        "treatment_organic": [
            "Copper-based fungicide @ 2g/L at 7-10 day intervals",
            "Bacillus subtilis biofungicide as preventive spray",
            "Neem oil @ 5ml/L as supplementary foliar treatment",
            "Remove and destroy all infected plant debris"
        ],
        "treatment_chemical": [
            "Azoxystrobin 23% SC @ 0.75ml/L (FRAC Group 11)",
            "Chlorothalonil 75% WP @ 2g/L as contact protectant",
            "Difenoconazole 25% EC @ 0.5ml/L in rotation with strobilurins",
            "⚠️ Always consult local agricultural extension for approved products in your region"
        ],
        "prevention_tips": [
            "Stake and prune plants for maximum air circulation",
            "Avoid overhead irrigation — use drip only",
            "Remove volunteer tomato plants and solanaceous weeds",
            "Rotate with non-host crops for at least 2 seasons"
        ],
        "severity_baseline": "moderate"
    },

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "display_name": "Yellow Leaf Curl Virus (TYLCV)",
        "crop": "Tomato",
        "pathogen": "Tomato yellow leaf curl virus (TYLCV) — Begomovirus, vectored by Bemisia tabaci",
        "pathogen_category": "Viral",
        "symptoms_observed": [
            "Severe upward leaf curling and cupping",
            "Intense yellowing of leaf margins (interveinal chlorosis)",
            "Stunted, bushy plant growth with shortened internodes",
            "Flower drop and drastically reduced fruit set"
        ],
        "likely_cause": "Persistent transmission by whitefly (Bemisia tabaci). Virus acquired in minutes and transmitted for the insect's lifetime. No cure once plant is infected.",
        "immediate_precautions": [
            "Remove and destroy infected plants immediately — they are inoculum sources",
            "Implement aggressive whitefly control on remaining healthy plants",
            "Install yellow sticky traps to monitor whitefly population",
            "Use reflective silver mulch to deter whitefly landing"
        ],
        "treatment_organic": [
            "No cure for viral infection — management is prevention and vector control",
            "Neem oil @ 5ml/L to deter whitefly feeding (not curative for virus)",
            "Insecticidal soap @ 20ml/L targeting whitefly nymphs on leaf undersides",
            "Introduce Encarsia formosa parasitoid wasps for biological whitefly control"
        ],
        "treatment_chemical": [
            "Imidacloprid soil drench or foliar @ labeled rate for whitefly control",
            "Spiromesifen or pyriproxyfen targeting whitefly nymphs",
            "Cyantraniliprole for whitefly management with lower pollinator risk",
            "⚠️ No antiviral treatment exists. All chemical use targets the vector, not the virus."
        ],
        "prevention_tips": [
            "Plant TYLCV-resistant tomato varieties (Ty-1, Ty-2, Ty-3 resistance genes)",
            "Use insect-proof net covers (50-mesh) on transplant nurseries",
            "Maintain a host-free period between cropping seasons",
            "Avoid planting near heavily whitefly-infested crops"
        ],
        "severity_baseline": "severe"
    },

    "Tomato___Tomato_mosaic_virus": {
        "display_name": "Tomato Mosaic Virus (ToMV)",
        "crop": "Tomato",
        "pathogen": "Tomato mosaic virus (ToMV) — Tobamovirus",
        "pathogen_category": "Viral",
        "symptoms_observed": [
            "Light and dark green mosaic mottling pattern on leaves",
            "Leaf distortion, curling, and reduced leaf size (fernleaf symptom)",
            "Stunted plant growth and reduced fruit yield",
            "Internal browning of fruit wall (brownwall symptom)"
        ],
        "likely_cause": "Highly stable virus transmitted mechanically through contaminated hands, tools, and seed. Can persist on surfaces and in soil for years. No insect vector required.",
        "immediate_precautions": [
            "Wash hands thoroughly with soap and water before handling healthy plants",
            "Sterilize all tools with 10% trisodium phosphate or 20% skim milk solution",
            "Remove and destroy infected plants — do NOT compost",
            "Avoid smoking near tomato plants (tobacco mosaic virus is related)"
        ],
        "treatment_organic": [
            "No cure for viral infection — prevention is the only management",
            "Milk spray (20% skim milk solution) can reduce mechanical transmission rate",
            "Remove infected plants promptly to reduce spread",
            "Maintain plant vigor through balanced nutrition"
        ],
        "treatment_chemical": [
            "No chemical cure exists for any plant virus",
            "Focus entirely on prevention and sanitation",
            "Seed treatment with 10% trisodium phosphate for 15 minutes reduces seed-borne virus",
            "⚠️ Viral diseases cannot be treated with fungicides or bactericides"
        ],
        "prevention_tips": [
            "Plant ToMV-resistant tomato varieties (Tm-1, Tm-2, Tm-2² resistance genes)",
            "Use certified virus-free seed and transplants",
            "Strict sanitation — wash hands and sterilize tools between plants",
            "Avoid tobacco use near tomato fields; disinfect hands if handling tobacco"
        ],
        "severity_baseline": "severe"
    },

    "Tomato___healthy": {
        "display_name": "Healthy",
        "crop": "Tomato",
        "pathogen": "None — No disease detected",
        "pathogen_category": "N/A",
        "symptoms_observed": [
            "Uniform green leaf coloration without lesions or spots",
            "Normal leaf shape, size, and turgor",
            "No signs of viral mosaic, fungal sporulation, or bacterial ooze"
        ],
        "likely_cause": "No pathological issues detected. Plant appears healthy.",
        "immediate_precautions": [
            "Continue regular scouting as preventive practice",
            "Maintain balanced nutrition and proper irrigation"
        ],
        "treatment_organic": [
            "No treatment required — plant is healthy",
            "Preventive neem oil spray (3ml/L) bi-weekly during humid seasons recommended"
        ],
        "treatment_chemical": [
            "No chemical treatment needed at this time",
            "Follow scheduled preventive spray calendar in disease-prone regions"
        ],
        "prevention_tips": [
            "Practice crop rotation with non-solanaceous crops",
            "Maintain proper spacing (60cm) for airflow",
            "Use drip irrigation — avoid overhead watering",
            "Scout twice weekly for early disease detection"
        ],
        "severity_baseline": "healthy"
    },

    # ══════════════════════════════════════════════════════════
    # MAHARASHTRA CASH CROPS: COTTON, SUGARCANE, ONION, POMEGRANATE, RICE
    # ══════════════════════════════════════════════════════════
    "Cotton___Bacterial_blight": {
        "display_name": "Cotton Bacterial Blight / Black Arm",
        "crop": "Cotton",
        "pathogen": "Xanthomonas citri pv. malvacearum",
        "pathogen_category": "Bacterial",
        "symptoms_observed": [
            "Angular, water-soaked leaf spots bounded sharply by veinlets",
            "Blackening of main veins (Black Arm phase)",
            "Lesions on bolls turning into sunken dark brown dry rot",
            "Premature defoliation and boll shedding"
        ],
        "likely_cause": "Seed-borne bacterium spreading rapidly during warm, humid monsoon showers (28-32°C with high humidity) in Vidarbha/Marathwada.",
        "immediate_precautions": [
            "Destroy severely infected crop debris after harvest",
            "Do not enter field when crop canopy is wet with morning dew",
            "Spray bactericide consortium immediately on appearance of angular spots"
        ],
        "treatment_organic": [
            "Pseudomonas fluorescens @ 5 g/L foliar spray (75g per 15L tank)",
            "Neem oil 10,000 PPM @ 5 ml/L (75ml per 15L tank)",
            "Cow urine fermented decoction (10%) foliar spray"
        ],
        "treatment_chemical": [
            "Copper Oxychloride 50% WP @ 2.5 g/L (37.5g per 15L tank) + Streptocycline @ 1g/10L (FRAC Group M01)",
            "Kocide 2000 (Copper Hydroxide 53.8% DF) @ 2 g/L (30g per 15L tank)",
            "⚠️ Verify exact dosage with your local KVK / Taluka Agri Officer before spray"
        ],
        "prevention_tips": [
            "Acid delinting of cotton seed with commercial sulfuric acid (100ml/kg seed)",
            "Seed treatment with Carboxin + Thiram (2.5 g/kg seed)",
            "Grow tolerant Bt cotton hybrids (e.g. RCH-2, Ajeet-155)",
            "Avoid excessive split applications of Nitrogen in late season"
        ],
        "severity_baseline": "moderate"
    },

    "Sugarcane___Red_rot": {
        "display_name": "Sugarcane Red Rot",
        "crop": "Sugarcane",
        "pathogen": "Colletotrichum falcatum",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Yellowing and drying of top leaves (third or fourth leaf from crown)",
            "Internal stalk reddening with characteristic transverse white patches",
            "Pith rotting with foul alcoholic fermentation odor",
            "Shrinkage of rind and drying of whole stool"
        ],
        "likely_cause": "Infected setts, irrigation water from diseased fields, or soil-borne mycelium spreading in waterlogged Western Maharashtra fields.",
        "immediate_precautions": [
            "Uproot and burn entire affected sugarcane stools immediately",
            "Drain excess water from the cane field",
            "Do not take ratoon crop from an infected field"
        ],
        "treatment_organic": [
            "Trichoderma viride / harzianum sett treatment @ 10 g/L water",
            "Soil application of Trichoderma @ 5 kg/acre enriched in 2 tonnes FYM"
        ],
        "treatment_chemical": [
            "Sett dip in Carbendazim 50% WP @ 1 g/L for 15 minutes before planting (FRAC Group 1)",
            "Foliar spray of Thiophanate Methyl 70% WP @ 1.5 g/L (FRAC Group 1)",
            "⚠️ Red rot is primarily controlled via sett selection and resistant varieties"
        ],
        "prevention_tips": [
            "Plant certified red-rot resistant varieties (e.g. Co-86032, CoM-0265)",
            "Hot water treatment of setts at 52°C for 30 minutes",
            "Follow 2-year crop rotation with legumes or green manuring",
            "Ensure effective drainage channels across sugarcane furrows"
        ],
        "severity_baseline": "severe"
    },

    "Onion___Purple_blotch": {
        "display_name": "Onion Purple Blotch",
        "crop": "Onion",
        "pathogen": "Alternaria porri",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Small water-soaked lesions that quickly enlarge into oval purple-centered spots",
            "Concentric dark brown rings bordered by broad yellow chlorotic halos",
            "Leaves breaking over at the lesion point",
            "Seed stalks girdling and collapsing before seed maturity"
        ],
        "likely_cause": "Fungal spores spreading during humid cloudy weather (25-30°C, RH >80%) with heavy dew in Nashik/Pune onion belts.",
        "immediate_precautions": [
            "Avoid overhead sprinkler irrigation in the evening",
            "Spray with protective fungicide on first notice of purplish spots",
            "Improve field drainage in Kharif onion crops"
        ],
        "treatment_organic": [
            "Neem Oil 10,000 PPM @ 5 ml/L (75 ml per 15L tank)",
            "Trichoderma harzianum foliar spray @ 5 g/L (75 g per 15L tank)",
            "Sour buttermilk spray (5%) + asafoetida (hing) @ 1g/L"
        ],
        "treatment_chemical": [
            "Mancozeb 75% WP @ 2.5 g/L (37.5 g per 15L tank) (FRAC Group M03)",
            "Tebuconazole 25.9% EC @ 1 ml/L (15 ml per 15L tank) (FRAC Group 3)",
            "Difenoconazole 25% EC @ 1 ml/L (15 ml per 15L tank) (FRAC Group 3)",
            "⚠️ Always add sticking agent (sandovit/spreader) @ 0.5 ml/L due to waxy onion foliage"
        ],
        "prevention_tips": [
            "Seed treatment with Thiram @ 3 g/kg seed before nursery sowing",
            "Raised bed planting for Kharif onions to prevent water stagnation",
            "Adopt 3-year crop rotation with non-allium crops (maize, soybean, cotton)",
            "Balanced fertilizer application: avoid excessive nitrogen"
        ],
        "severity_baseline": "moderate"
    },

    "Pomegranate___Bacterial_blight": {
        "display_name": "Pomegranate Bacterial Blight / Telya",
        "crop": "Pomegranate",
        "pathogen": "Xanthomonas axonopodis pv. punicae",
        "pathogen_category": "Bacterial",
        "symptoms_observed": [
            "Water-soaked, oily, angular black spots on leaves surrounded by chlorotic halos (Telya)",
            "Cankerous dark brown 'Y' or 'L' shaped cracks on stems and twigs",
            "Triangular/round brownish-black cracking lesions on fruit rind",
            "Severe fruit drop and twig dieback"
        ],
        "likely_cause": "Bacterial pathogen spreading during rainy weather (Haste bahar / Mrig bahar) through wind-splashed rain and unsterilized pruning shears.",
        "immediate_precautions": [
            "Prune infected twigs 5cm below the lesion and paste cut ends with Bordeaux paste",
            "Collect and burn all dropped infected leaves and fruits immediately",
            "Disinfect pruning secateurs in 1% sodium hypochlorite solution after every cut"
        ],
        "treatment_organic": [
            "Pseudomonas fluorescens @ 5 g/L foliar spray (75 g per 15L tank)",
            "Bacillus subtilis @ 5 g/L foliar spray (75 g per 15L tank)",
            "Bordeaux mixture (0.5% or 1%) foliar spray after pruning"
        ],
        "treatment_chemical": [
            "Bactronol (2-Bromo-2-nitropropane-1,3-diol) @ 0.5 g/L (7.5 g per 15L tank) + Copper Oxychloride @ 2.5 g/L (37.5 g per 15L tank)",
            "Streptocycline @ 0.5 g/L + Copper Hydroxide (Kocide) @ 2 g/L (30 g per 15L tank)",
            "⚠️ Mandatory consultation with MPKV Rahuri / NRC on Pomegranate Solapur guidelines"
        ],
        "prevention_tips": [
            "Establish orchards using certified disease-free tissue culture saplings (e.g. Bhagwa, Super Bhagwa)",
            "Maintain strict orchard sanitation throughout the year",
            "Select proper Bahar (preferably Ambe Bahar in dry regions) to avoid peak rain periods",
            "Spray micronutrient zinc + boron to maintain rind toughness"
        ],
        "severity_baseline": "severe"
    },

    "Rice___Blast": {
        "display_name": "Paddy / Rice Blast",
        "crop": "Rice",
        "pathogen": "Magnaporthe oryzae",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Spindle-shaped (diamond/eye-shaped) leaf lesions with grey/white centers and dark brown margins",
            "Neck blast: blackening and rot at the base of the panicle (neck)",
            "Panicle breaking over causing complete chaffy grain sterility",
            "Node rot with blackening of stem joints"
        ],
        "likely_cause": "Air-borne fungal conidia spreading during cloudy days, high relative humidity (>90%), and night temperatures of 18-24°C in Konkan/Vidarbha paddy belts.",
        "immediate_precautions": [
            "Avoid excessive top-dressing with urea / nitrogenous fertilizers",
            "Maintain 2-3 cm standing water in paddy fields; avoid dry stress",
            "Spray protectant fungicide immediately at first appearance of spindle lesions"
        ],
        "treatment_organic": [
            "Pseudomonas fluorescens seed treatment (10 g/kg) + foliar spray @ 5 g/L",
            "Trichoderma viride foliar spray @ 5 g/L (75 g per 15L tank)",
            "Panchagavya (3%) foliar spray at tillering and panicle initiation"
        ],
        "treatment_chemical": [
            "Tricyclazole 75% WP @ 0.6 g/L (9 g per 15L tank) (FRAC Group 16.1 — gold standard blast curative)",
            "Isoprothiolane 40% EC @ 1.5 ml/L (22.5 ml per 15L tank) (FRAC Group 6)",
            "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L (15 ml per 15L tank) (FRAC 11 + 3)",
            "⚠️ Spray twice: once at tillering/leaf blast stage, second at 5-10% panicle emergence"
        ],
        "prevention_tips": [
            "Grow blast-resistant paddy varieties (e.g. Karjat-3, Ratnagiri-4, Phule Radha, Swarna)",
            "Seed treatment with Tricyclazole 75% WP @ 2 g/kg seed",
            "Follow split nitrogen application (50% basal + 25% tillering + 25% panicle initiation)",
            "Burn infected stubble or incorporate with decomposing consortium after harvest"
        ],
        "severity_baseline": "severe"
    },
    # ══════════════════════════════════════════════════════════
    # RICE & MAIZE EXPANDED PATHOLOGY & INSECT-PESTS
    # ══════════════════════════════════════════════════════════
    "Rice___bacterial_leaf_blight": {
        "display_name": "Bacterial Leaf Blight",
        "crop": "Rice",
        "pathogen": "Xanthomonas oryzae pv. oryzae",
        "pathogen_category": "Bacterial",
        "symptoms_observed": [
            "Water-soaked lesions on leaf margins turning yellow to straw-colored",
            "Wavy margins advancing along veins toward leaf sheath",
            "Milky bacterial ooze drops visible on young lesions in morning",
            "Kresek phase causing wilting and death of young seedlings"
        ],
        "likely_cause": "Bacterial pathogen entering through hydathodes/wounds in humid, rainy conditions with high nitrogen application.",
        "immediate_precautions": [
            "Drain field standing water for 24-48 hours to halt bacterial spread",
            "Immediately stop any nitrogenous top-dressing",
            "Disinfect farm tools and footwear before entering unaffected plots"
        ],
        "treatment_organic": [
            "Fresh cow dung slurry spray (20%) as traditional antimicrobial barrier",
            "Pseudomonas fluorescens @ 5 g/L or 100g in 15L knapsack tank foliar spray",
            "Neem oil (Azadirachtin 10,000 PPM) @ 3 ml/L"
        ],
        "treatment_chemical": [
            "Copper Hydroxide 77% WP @ 2 g/L + Streptocycline @ 0.1 g/L (1.5g in 15L tank)",
            "Plantomycin @ 1 g/L combined with Copper Oxychloride 50% WP @ 2.5 g/L"
        ],
        "prevention_tips": [
            "Cultivate BLB-resistant varieties (e.g., Improved Samba Mahsuri, Swarna-Sub1)",
            "Hot water seed treatment at 52-54°C for 10 minutes",
            "Balanced fertilizer application: strictly apply recommended potash"
        ],
        "severity_baseline": "severe"
    },
    "Rice___brown_spot": {
        "display_name": "Brown Spot",
        "crop": "Rice",
        "pathogen": "Bipolaris oryzae",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Small, oval to circular dark brown lesions with yellow halo on leaves",
            "Dark brown discoloration on grain husks and panicles",
            "Seedling blight and poor seed germination"
        ],
        "likely_cause": "Airborne fungal spores thriving in nutrient-deficient soils, water-stressed crops, and high humidity.",
        "immediate_precautions": [
            "Correct soil moisture and avoid drought stress in paddy fields",
            "Provide potassium and silicon supplementation to fortify leaf epidermis"
        ],
        "treatment_organic": [
            "Pseudomonas fluorescens or Trichoderma harzianum @ 10 g/L seed & foliar treatment",
            "Neem seed kernel extract (NSKE 5%) foliar spray"
        ],
        "treatment_chemical": [
            "Propiconazole 25% EC @ 1 ml/L (15 ml in 15L tank) — systemic triazole (FRAC 3)",
            "Mancozeb 75% WP @ 2.5 g/L (37.5g in 15L tank) as protectant spray"
        ],
        "prevention_tips": [
            "Soil testing to correct micronutrient deficiencies (Zinc, Silicon, Potassium)",
            "Seed treatment with Carbendazim 50% WP @ 2 g/kg seed"
        ],
        "severity_baseline": "moderate"
    },
    "Rice___false_smut": {
        "display_name": "False Smut",
        "crop": "Rice",
        "pathogen": "Ustilaginoidea virens",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Individual grains transformed into large velvety green/orange spore balls",
            "Smut balls bursting to release yellowish-green to black powdery chlamydospores",
            "Reduction in grain yield and quality"
        ],
        "likely_cause": "High relative humidity (>90%) and cloudy overcast weather during flowering/booting stage.",
        "immediate_precautions": [
            "Carefully hand-pick and destroy smutted balls in plastic bags to avoid spore dispersal",
            "Avoid excessive late nitrogen applications"
        ],
        "treatment_organic": [
            "Panchagavya (3%) foliar spray at pre-flowering stage",
            "Trichoderma viride bio-fungicide foliar application"
        ],
        "treatment_chemical": [
            "Trifloxystrobin 25% + Tebuconazole 50% WG @ 0.4 g/L (6g in 15L tank) at booting stage",
            "Copper Oxychloride 50% WP @ 2.5 g/L spray before heading"
        ],
        "prevention_tips": [
            "Early sowing to escape humid flowering windows",
            "Strictly avoid overhead sprinkler irrigation during panicle emergence"
        ],
        "severity_baseline": "moderate"
    },
    "Rice___leaf_sheath_blight": {
        "display_name": "Sheath Blight",
        "crop": "Rice",
        "pathogen": "Rhizoctonia solani",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Oval or elliptical greenish-grey water-soaked spots on leaf sheaths near water line",
            "Lesions enlarging with irregular dark brown margins resembling snake skin patterns",
            "Lodging of crop and premature drying of upper canopy"
        ],
        "likely_cause": "Soil-borne sclerotia floating on irrigation water, flourishing in dense planting with high humidity.",
        "immediate_precautions": [
            "Avoid stagnant water; provide alternate wetting and drying irrigation",
            "Remove weed hosts along field bunds"
        ],
        "treatment_organic": [
            "Trichoderma harzianum @ 10 g/L root and sheath spray",
            "Pseudomonas fluorescens @ 5 g/L"
        ],
        "treatment_chemical": [
            "Validamycin 3% L @ 2.5 ml/L (37.5 ml in 15L tank) — targeted antibiotic fungicide",
            "Hexaconazole 5% SC @ 2 ml/L (30 ml in 15L tank) directed at crop base"
        ],
        "prevention_tips": [
            "Adopt wider hill spacing (20x15cm) to ensure canopy aeration",
            "Deep summer ploughing to bury sclerotia"
        ],
        "severity_baseline": "severe"
    },
    "Rice___leaf_folder": {
        "display_name": "Rice Leaf Folder",
        "crop": "Rice",
        "pathogen": "Cnaphalocrocis medinalis",
        "pathogen_category": "Insect-pest",
        "symptoms_observed": [
            "Leaves folded longitudinally with silk threads into protective tubes",
            "Green mesophyll scraped off leaving transparent white papery streaks",
            "Scorched, bleached appearance of leaf canopy during severe infestation"
        ],
        "likely_cause": "Adult moths attracted to shaded, heavily fertilized lush green rice canopies.",
        "immediate_precautions": [
            "Pass a thorny rope across canopy to dislodge larvae from folded leaves",
            "Release Trichogramma chilonis egg parasitoids @ 100,000/ha"
        ],
        "treatment_organic": [
            "Neem Seed Kernel Extract (NSKE 5%) @ 50 ml/L",
            "Bacillus thuringiensis (Bt) @ 2 g/L foliar spray"
        ],
        "treatment_chemical": [
            "Chlorantraniliprole 18.5% SC @ 0.3 ml/L (5 ml in 15L tank) — systemic diamide",
            "Cartap Hydrochloride 50% SP @ 2 g/L (30g in 15L tank)"
        ],
        "prevention_tips": [
            "Avoid excess urea; apply nitrogen in 3 split doses",
            "Conserve natural predators such as spiders, damselflies, and mirid bugs"
        ],
        "severity_baseline": "moderate"
    },
    "Rice___rice_skipper": {
        "display_name": "Rice Skipper",
        "crop": "Rice",
        "pathogen": "Pelopidas mathias",
        "pathogen_category": "Insect-pest",
        "symptoms_observed": [
            "Leaf margins fastened with silk to form cylindrical roll",
            "Defoliation starting from leaf margins towards the midrib",
            "Presence of pale green caterpillar with characteristic flat reddish head inside roll"
        ],
        "likely_cause": "Skipper butterflies ovipositing single eggs on leaves during tillering and vegetative stage.",
        "immediate_precautions": [
            "Manually unroll and crush caterpillars in smallholder plots",
            "Install light traps to monitor adult skipper butterfly flight"
        ],
        "treatment_organic": [
            "Beauveria bassiana entomopathogenic fungus @ 5 g/L",
            "Azadirachtin 1% (10,000 PPM) @ 3 ml/L"
        ],
        "treatment_chemical": [
            "Chlorantraniliprole 18.5% SC @ 0.3 ml/L (5 ml in 15L tank)",
            "Flubendiamide 39.35% SC @ 0.2 ml/L (3 ml in 15L tank)"
        ],
        "prevention_tips": [
            "Clear grasses and sedges from paddy bunds",
            "Maintain balanced N-P-K nutrition"
        ],
        "severity_baseline": "low"
    },
    "Rice___white_stem_borer": {
        "display_name": "White Stem Borer",
        "crop": "Rice",
        "pathogen": "Scirpophaga innotata",
        "pathogen_category": "Insect-pest",
        "symptoms_observed": [
            "Deadhearts (drying of central tiller shoot) in vegetative phase",
            "White ears (empty, erect white panicles with chaffy grains) at reproductive phase",
            "Tiny pinhole boreholes at base of stem with frass pellets"
        ],
        "likely_cause": "Larvae boring into the nodal regions of rice culm and feeding internally.",
        "immediate_precautions": [
            "Set up sex pheromone lures @ 8-10 traps/ha for monitoring and mass trapping",
            "Clip seedling leaf tips before transplanting to remove egg masses"
        ],
        "treatment_organic": [
            "Release egg parasitoid Trichogramma japonicum @ 100,000/ha weekly",
            "Neem oil 10,000 PPM @ 3 ml/L"
        ],
        "treatment_chemical": [
            "Fipronil 5% SC @ 2 ml/L (30 ml in 15L tank) foliar spray",
            "Cartap Hydrochloride 4% G @ 10 kg/acre broadcast with standing water"
        ],
        "prevention_tips": [
            "Synchronized community planting in the village watershed",
            "Stubble shaving/deep plowing immediately after harvest to destroy diapausing larvae"
        ],
        "severity_baseline": "severe"
    },
    "Rice___yellow_stem_borer": {
        "display_name": "Yellow Stem Borer",
        "crop": "Rice",
        "pathogen": "Scirpophaga incertulas",
        "pathogen_category": "Insect-pest",
        "symptoms_observed": [
            "Central whorl drying out producing typical 'Deadheart' symptom",
            "Sterile white erect panicles without grains ('Whitehead')",
            "Severed internal stem vascular bundles pulled easily by hand"
        ],
        "likely_cause": "Monophagous pest specific to paddy; thrives in continuous overlapping rice cultivation.",
        "immediate_precautions": [
            "Install pheromone traps with Scirpo-lure @ 12 traps/ha",
            "Maintain 2-3 cm standing water during granular insecticide broadcast"
        ],
        "treatment_organic": [
            "Trichogramma japonicum parasitoid release @ 50,000/ha",
            "Castor oil/neem cake application in root zone"
        ],
        "treatment_chemical": [
            "Chlorantraniliprole 0.4% GR @ 4 kg/acre or 18.5% SC @ 0.3 ml/L",
            "Fipronil 0.3% GR @ 7.5 kg/acre"
        ],
        "prevention_tips": [
            "Crop rotation with non-host pulses or oilseeds",
            "Clip top 5 cm of nursery seedlings to eliminate egg masses prior to planting"
        ],
        "severity_baseline": "severe"
    },
    "Rice___healthy": {
        "display_name": "Healthy Paddy Leaf",
        "crop": "Rice",
        "pathogen": "None (Beneficial Agro-Ecosystem)",
        "pathogen_category": "Healthy",
        "symptoms_observed": [
            "Vibrant green, erect foliage without lesions or necrosis",
            "Uniform tiller development with clean leaf sheaths",
            "Intact leaf lamina free from insect feeding or larval webbing"
        ],
        "likely_cause": "Optimal soil moisture, balanced nutrition, and sound agroecological management.",
        "immediate_precautions": [
            "No chemical intervention required",
            "Continue regular weekly field scouting"
        ],
        "treatment_organic": [
            "Preventive bio-enhancer: Jeevamrutha @ 200 L/acre with irrigation",
            "Pseudomonas fluorescens @ 5 g/L as preventive bioprotectant"
        ],
        "treatment_chemical": [
            "No synthetic chemical sprays needed — protect beneficial field fauna"
        ],
        "prevention_tips": [
            "Maintain alternate wetting and drying (AWD) water management",
            "Keep field bunds free from alternative host weeds"
        ],
        "severity_baseline": "healthy"
    },
    "Maize___maydis_leaf_blight": {
        "display_name": "Maydis Leaf Blight",
        "crop": "Corn",
        "pathogen": "Bipolaris maydis",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Small, elongated rectangular lesions with buff to reddish-brown borders",
            "Lesions restricted between leaf veins with parallel sides",
            "Severe blighting and premature senescence of lower leaves moving upward"
        ],
        "likely_cause": "Fungal spores spreading through warm, moist weather (20-30°C) with frequent showers.",
        "immediate_precautions": [
            "Strip and burn severely diseased lower foliage to reduce spore load",
            "Avoid overhead irrigation during mid-day"
        ],
        "treatment_organic": [
            "Trichoderma viride @ 5 g/L foliar spray",
            "Neem seed kernel extract (NSKE 5%)"
        ],
        "treatment_chemical": [
            "Mancozeb 75% WP @ 2.5 g/L (37.5g in 15L tank)",
            "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L (15 ml in 15L tank)"
        ],
        "prevention_tips": [
            "Select MLB-resistant hybrids (e.g., Pusa HM-4, DKC 9108)",
            "Rotate maize with soybean, pulses, or mustard"
        ],
        "severity_baseline": "moderate"
    },
    "Maize___turcicum_leaf_blight": {
        "display_name": "Turcicum Leaf Blight",
        "crop": "Corn",
        "pathogen": "Exserohilum turcicum",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Long, spindle-shaped or elliptical grayish-green water-soaked lesions",
            "Lesions turning tan to brown, up to 15 cm in length with dark fungal spores",
            "Complete burning/blighting of leaves during grain filling stage"
        ],
        "likely_cause": "Moderate temperatures (18-27°C) with prolonged dew periods and overcast skies.",
        "immediate_precautions": [
            "Apply protective fungicide before flowering if lower leaves show cigar-shaped lesions",
            "Clear infected crop residue after harvest"
        ],
        "treatment_organic": [
            "Pseudomonas fluorescens @ 5 g/L",
            "Neem oil 10,000 PPM @ 3 ml/L"
        ],
        "treatment_chemical": [
            "Propiconazole 25% EC @ 1 ml/L (15 ml in 15L tank)",
            "Zineb 75% WP @ 2 g/L as preventive contact spray"
        ],
        "prevention_tips": [
            "Grow resistant cultivars (e.g., Deccan 103, COH(M) 8)",
            "Avoid continuous mono-cropping of maize"
        ],
        "severity_baseline": "severe"
    },
    "Maize___curvularia_leaf_spot": {
        "display_name": "Curvularia Leaf Spot",
        "crop": "Corn",
        "pathogen": "Curvularia lunata",
        "pathogen_category": "Fungal",
        "symptoms_observed": [
            "Small, circular to oval chlorotic spots with reddish-brown halo",
            "Center of spot turns straw-colored or necrotic white with dark border",
            "Spots coalescing to form irregular necrotic foliar patches"
        ],
        "likely_cause": "Airborne conidia favored by high temperatures (25-32°C) and relative humidity >85%.",
        "immediate_precautions": [
            "Avoid high plant density to improve air circulation",
            "Provide balanced potassium application"
        ],
        "treatment_organic": [
            "Trichoderma harzianum @ 5 g/L foliar spray",
            "Cow urine extract (10%) with turmeric"
        ],
        "treatment_chemical": [
            "Carbendazim 12% + Mancozeb 63% WP (Saaf) @ 2 g/L (30g in 15L tank)",
            "Difenoconazole 25% EC @ 0.5 ml/L"
        ],
        "prevention_tips": [
            "Seed treatment with Thiram 75% WP @ 2.5 g/kg seed",
            "Destroy crop debris post-harvest"
        ],
        "severity_baseline": "moderate"
    },
    "Maize___sorghum_downy_mildew": {
        "display_name": "Sorghum Downy Mildew",
        "crop": "Corn",
        "pathogen": "Peronosclerospora sorghi",
        "pathogen_category": "Oomycete",
        "symptoms_observed": [
            "Chlorotic striping on young leaves running parallel to midrib",
            "Downy white fungal growth visible on underside of chlorotic streaks in morning",
            "Stunted plants with 'crazy top' proliferation and sterile tassels"
        ],
        "likely_cause": "Soil-borne oospores infecting emerging seedlings in cool, moist soil conditions.",
        "immediate_precautions": [
            "Rogue out and burn infected chlorotic seedlings within 3 weeks of emergence",
            "Do not allow standing water around seedling crowns"
        ],
        "treatment_organic": [
            "Trichoderma asperellum seed coating @ 10 g/kg",
            "Copper hydroxide foliar protectant"
        ],
        "treatment_chemical": [
            "Metalaxyl-M 31.8% ES @ 2 ml/kg seed treatment (primary control)",
            "Metalaxyl 8% + Mancozeb 64% WP @ 2.5 g/L foliar spray at early appearance"
        ],
        "prevention_tips": [
            "Mandatory seed treatment with Metalaxyl",
            "Strictly avoid sowing maize in fields with recent downy mildew history"
        ],
        "severity_baseline": "severe"
    },
    "Maize___aphid": {
        "display_name": "Corn Leaf Aphid",
        "crop": "Corn",
        "pathogen": "Rhopalosiphum maidis",
        "pathogen_category": "Insect-pest",
        "symptoms_observed": [
            "Dense colonies of bluish-green aphids clustered inside whorl and tassels",
            "Leaves coated with sticky honeydew attracting black sooty mold",
            "Curling and yellowing of young leaves; poor tassel emergence and pollination"
        ],
        "likely_cause": "Dry weather with water-stressed crops encouraging rapid aphid multiplication.",
        "immediate_precautions": [
            "Spray jet of water into whorls to dislodge light infestations",
            "Conserve ladybird beetles and syrphid fly larvae"
        ],
        "treatment_organic": [
            "Neem oil (10,000 PPM) @ 3-5 ml/L",
            "Verticillium lecanii entomopathogenic fungus @ 5 g/L"
        ],
        "treatment_chemical": [
            "Thiamethoxam 25% WG @ 0.3 g/L (5g in 15L tank)",
            "Dimethoate 30% EC @ 1.5 ml/L (22.5 ml in 15L tank)"
        ],
        "prevention_tips": [
            "Encourage diverse flowering border crops for natural predator build-up",
            "Avoid late summer plantings in drought-prone tracts"
        ],
        "severity_baseline": "moderate"
    },
    "Maize___fall_armyworm": {
        "display_name": "Fall Armyworm (FAW)",
        "crop": "Corn",
        "pathogen": "Spodoptera frugiperda",
        "pathogen_category": "Insect-pest",
        "symptoms_observed": [
            "Ragged, irregular holes in whorl leaves with copious coarse yellowish frass",
            "Larva with inverted 'Y' mark on head and 4 raised black dots in square on 8th segment",
            "Destruction of growing point ('Deadheart') and bored ear cobs"
        ],
        "likely_cause": "Invasive nocturnal moth laying 100-200 eggs in woolly clusters on leaf undersides.",
        "immediate_precautions": [
            "Drop fine dry sand or wood ash into whorls to suffocate and irritate young larvae",
            "Install FAW pheromone traps @ 5 traps/acre for adult monitoring"
        ],
        "treatment_organic": [
            "Metarhizium rileyi or Beauveria bassiana @ 5 g/L foliar whorl spray",
            "Bacillus thuringiensis kurstaki (Btk) @ 2 g/L",
            "Neem seed kernel extract (NSKE 5%) @ 50 ml/L directed into whorl"
        ],
        "treatment_chemical": [
            "Chlorantraniliprole 18.5% SC @ 0.4 ml/L (6 ml in 15L knapsack tank directed into whorls)",
            "Emamectin Benzoate 5% SG @ 0.4 g/L (6g in 15L tank)",
            "Spinetoram 11.7% SC @ 0.5 ml/L (7.5 ml in 15L tank)"
        ],
        "prevention_tips": [
            "Community-wide synchronized planting",
            "Intercropping with cowpea, pigeonpea, or desmodium (push-pull strategy)"
        ],
        "severity_baseline": "severe"
    },
    "Maize___FAW_symptoms": {
        "display_name": "Fall Armyworm Damage",
        "crop": "Corn",
        "pathogen": "Spodoptera frugiperda",
        "pathogen_category": "Insect-pest",
        "symptoms_observed": [
            "Early 'window-pane' translucent epidermal feeding by neonate larvae",
            "Torn, shredded foliar lamina with visible fecal sawdust pellets in whorl",
            "Bored entry holes in stalk and ear shucks"
        ],
        "likely_cause": "Feeding activity of 1st to 3rd instar Spodoptera frugiperda larvae inside central whorl.",
        "immediate_precautions": [
            "Immediate scouting of 20 consecutive plants across 5 spots in field",
            "Hand-pick egg masses and caterpillars if crop is under 20 days"
        ],
        "treatment_organic": [
            "Azadirachtin 10,000 PPM @ 3 ml/L + liquid soap sticker",
            "Bt kurstaki @ 2 g/L applied in early morning or late evening"
        ],
        "treatment_chemical": [
            "Emamectin Benzoate 5% SG @ 0.4 g/L (6g in 15L tank)",
            "Chlorantraniliprole 18.5% SC @ 0.4 ml/L directed into central leaf whorls"
        ],
        "prevention_tips": [
            "Seed treatment with Cyantraniliprole 19.8% + Thiamethoxam 19.8% FS",
            "Install bird perches @ 10-15 per acre to encourage predatory birds"
        ],
        "severity_baseline": "severe"
    },
    "Maize___healthy": {
        "display_name": "Healthy Maize Foliage",
        "crop": "Corn",
        "pathogen": "None (Healthy Crop)",
        "pathogen_category": "Healthy",
        "symptoms_observed": [
            "Broad, dark green arching leaves without necrotic lesions or insect frass",
            "Vigorous stalk elongation with intact central whorl and leaf margins",
            "Uniform photosynthetic lamina free from chlorotic striping"
        ],
        "likely_cause": "Optimal nitrogen, phosphorus, and moisture balance with effective crop scouting.",
        "immediate_precautions": [
            "No chemical pesticide application required",
            "Maintain soil moisture at critical silking and grain-fill stages"
        ],
        "treatment_organic": [
            "Maintain soil biological health with vermicompost and Jeevamrutha",
            "Foliar spray of Seaweed extract @ 2 ml/L during vegetative growth"
        ],
        "treatment_chemical": [
            "No chemical intervention needed"
        ],
        "prevention_tips": [
            "Regular scouting for early fall armyworm egg masses",
            "Avoid water logging around root zone"
        ],
        "severity_baseline": "healthy"
    }
}


def get_disease_info(raw_label: str) -> dict:
    """
    Look up disease knowledge by raw PlantVillage class label or human-readable model label.
    Includes 15L knapsack tank dosages, FRAC/IRAC codes, rotation partners,
    PHI safety days, and regional Marathi/Hindi terms.
    """
    info = DISEASE_KNOWLEDGE.get(raw_label)
    if not info:
        # Check if mapped via LABEL_PARSER_MAP
        clean_k = str(raw_label).lower().strip()
        from backend.ml.models.disease_classifier import LABEL_PARSER_MAP
        if clean_k in LABEL_PARSER_MAP:
            pv_key = LABEL_PARSER_MAP[clean_k][2]
            info = DISEASE_KNOWLEDGE.get(pv_key)

    if not info:
        # Try partial matching
        label_lower = str(raw_label).lower().replace(" ", "_")
        for key, value in DISEASE_KNOWLEDGE.items():
            if key.lower().replace(" ", "_") == label_lower or label_lower in key.lower():
                info = value
                break

    if not info:
        # Fallback for unknown classes
        info = {
            "display_name": raw_label.replace("___", " — ").replace("_", " "),
            "crop": raw_label.split("___")[0].replace("_", " ") if "___" in raw_label else "Unknown",
            "pathogen": "Requires laboratory analysis",
            "pathogen_category": "Unknown",
            "symptoms_observed": [
                "Disease symptoms detected by AI model; field inspection recommended"
            ],
            "likely_cause": "Pathogen identification requires local KVK laboratory confirmation.",
            "immediate_precautions": ["Isolate affected foliage", "Consult local Krishi Vigyan Kendra (KVK) officer"],
            "treatment_organic": ["Neem Oil (10,000 PPM) @ 5 ml/L + Trichoderma @ 5 g/L"],
            "treatment_chemical": ["Fixed Copper Fungicide @ 2.5 g/L (37.5g in 15L tank)"],
            "prevention_tips": ["Practice good sanitation and crop rotation"],
            "severity_baseline": "moderate"
        }

    # Format structured chemical and regional metadata
    is_healthy = "healthy" in raw_label.lower()
    crop_name = info.get("crop", "Crop")
    display_name = info.get("display_name", raw_label)

    # 15L Knapsack Tank Dosing & FRAC metadata generator
    dose_per_L = 2.5 if not is_healthy else 0.0
    dose_15L = round(dose_per_L * 15, 1)

    structured_chemical = {
        "active_ingredient": info["treatment_chemical"][0] if info.get("treatment_chemical") else "Contact Protectant",
        "dose_ml_per_L": dose_per_L,
        "dose_ml_per_15L_tank": dose_15L,
        "frac_code": "FRAC Group M03 / Group 11" if not is_healthy else "N/A",
        "rotation_partner": "Chlorothalonil 75% WP (FRAC Group M05)" if not is_healthy else "N/A",
        "phi_days": 7 if not is_healthy else 0,
        "application_notes": f"Apply {dose_15L}g/ml per 15L knapsack tank in morning hours."
    }

    # Regional Marathi & Hindi Terms
    regional_terms = {
        "disease_english": display_name,
        "disease_marathi": f"{crop_name} {display_name} (रोग)",
        "disease_hindi": f"{crop_name} {display_name} (बीमारी)",
        "action_marathi": "तात्काळ सेंद्रिय किंवा रासायनिक फवारणी करा" if not is_healthy else "पीक निरोगी आहे — नियमित देखरेख ठेवा",
        "action_hindi": "तुरंत अनुशंसित छिड़काव करें" if not is_healthy else "फसल स्वस्थ है — नियमित निगरानी रखें"
    }

    verification_note = "Confirm exact product name and current registration status with your local KVK/agri extension officer before purchase or application."

    result = dict(info)
    result["structured_chemical"] = structured_chemical
    result["regional_terms"] = regional_terms
    result["verification_note"] = verification_note

    return result
