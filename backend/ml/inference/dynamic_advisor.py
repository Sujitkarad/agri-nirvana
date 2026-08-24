"""
Dynamic AI Pathology Advisor — Generates tailored symptoms & IPM recommendations
grounded in real detection output (confidence score, severity tier, necrotic area %, differentials).

Replaces static lookup tables with dynamic, severity-scaled diagnostic text.
"""

import os
import json
import random
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger("DynamicPathologyAdvisor")

# In-Memory Dynamic Cache: (crop, disease, severity_tier, conf_bracket) -> generated_dict
_ADVISORY_CACHE: Dict[str, Dict[str, Any]] = {}


def _get_cache_key(crop: str, disease: str, severity_tier: str, conf_pct: int) -> str:
    # Bracket confidence into high (>=80), medium (60-79), low (<60)
    if conf_pct >= 80:
        conf_bracket = "high"
    elif conf_pct >= 60:
        conf_bracket = "med"
    else:
        conf_bracket = "low"
    return f"{crop.lower()}:{disease.lower()}:{severity_tier.lower()}:{conf_bracket}"


def _generate_rule_grounded_dynamic_advisory(
    crop: str,
    disease: str,
    pathogen: str,
    severity_tier: str,
    necrotic_area_pct: float,
    confidence_pct: int,
    differential_diagnoses: List[Dict[str, Any]],
    base_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    High-fidelity dynamic pathology natural language engine.
    Produces distinctly different symptoms, epidemiological causes, and IPM dosages
    scaled precisely to the measured severity tier and necrotic area %.
    """
    is_healthy = "healthy" in disease.lower() or severity_tier.lower() == "healthy"
    sev = severity_tier.lower()

    # 1. DYNAMIC SYMPTOMS (Scaled to Severity & Necrotic Area %)
    if is_healthy:
        symptoms_observed = [
            f"Foliage demonstrates uniform healthy chlorophyll density across all leaf margins.",
            f"No active foliar necrosis, chlorotic stippling, or mycelial mats detected (necrotic area: 0.0%).",
            f"Turgid lamina with intact cuticle barrier; optimal photosynthetically active radiation (PAR) absorption."
        ]
        likely_cause = f"Optimal balanced crop nutrition, adequate soil aeration, and absence of virulent {crop} fungal/bacterial inoculum."
        immediate_precautions = [
            "Maintain current bi-weekly preventive crop scouting protocol.",
            "Inspect lower canopy undersides after high humidity or heavy rainfall events."
        ]
    elif sev in ["low", "early"]:
        symptoms_observed = [
            f"Early-stage localized infection detected with approximately {necrotic_area_pct:.1f}% foliar necrotic involvement.",
            f"Isolated pinpoint chlorotic flecks and developing lesion margins localized primarily to lower canopy leaf lamina.",
            f"Vascular integrity remains largely preserved; early target rings/water-soaking visible under close inspection."
        ]
        likely_cause = f"Initial spore germination or bacterial entry via stomata/hydathodes triggered by recent leaf wetness and moderate ambient temperatures."
        immediate_precautions = [
            f"Isolate localized infected leaves immediately to halt primary spore dispersal across the field.",
            f"Avoid overhead irrigation during evening hours to minimize leaf wetness duration below 4 hours."
        ]
    elif sev == "moderate":
        symptoms_observed = [
            f"Active moderate infection covering approximately {necrotic_area_pct:.1f}% of the foliar surface area.",
            f"Expanding necrotic lesions with pronounced yellow chlorotic halos and characteristic concentric ring patterning.",
            f"Interveinal leaf tissue degradation beginning to impair photosynthetic capacity across middle canopy branches."
        ]
        likely_cause = f"Secondary cycle conidial/bacterial multiplication favored by relative humidity >75% and overcast canopy micro-climates."
        immediate_precautions = [
            f"Apply protective fungicide/bactericide spray within 24–48 hours to arrest lesion coalescence.",
            f"Prune lower infected foliage and dispose outside the field perimeter; do not compost."
        ]
    else:  # Severe
        symptoms_observed = [
            f"Critical severe infection with extensive necrotic destruction spanning {necrotic_area_pct:.1f}% of total foliar area.",
            f"Coalescing necrotic patches causing severe leaf blighting, curling, brittle leaf margins, and premature defoliation.",
            f"Lesions extending into petioles and stem nodes, threatening vascular wilt and severe yield penalty if unchecked."
        ]
        likely_cause = f"Uncontrolled exponential pathogen sporulation compounded by continuous leaf wetness and favorable thermal conditions."
        immediate_precautions = [
            f"Immediate emergency systemic chemical spray intervention required to protect apical growth and fruit/boll set.",
            f"Burn severely blighted plant debris; sanitize all pruning secateurs in 1% sodium hypochlorite solution."
        ]

    # If confidence is below 70%, append differential diagnosis note
    if confidence_pct < 70 and differential_diagnoses:
        diff_names = ", ".join([d.get("name", "similar pathogen") for d in differential_diagnoses[:2]])
        symptoms_observed.append(
            f"⚠️ Diagnostic Caution (Confidence {confidence_pct}%): Visual symptoms partially overlap with {diff_names}. Cross-verify lesion margins with local extension officer."
        )

    # 2. DYNAMIC 3-TIER IPM RECOMMENDATIONS (Scaled to Severity)
    structured_chem = base_info.get("structured_chemical", {})
    base_chem_name = structured_chem.get("active_ingredient", "Mancozeb 75% WP")
    frac_code = structured_chem.get("frac_code", "FRAC Group M03")
    rot_partner = structured_chem.get("rotation_partner", "Chlorothalonil 75% WP (FRAC M05)")
    phi_days = structured_chem.get("phi_days", 7)

    if is_healthy:
        tier_1_biological = [
            {"agent": "Trichoderma harzianum @ 5 g/L", "dosage": "75g in 15L tank", "application_timing": "Preventive foliar spray every 14 days"}
        ]
        tier_2_chemical = [
            {"active_ingredient": "No chemical intervention needed", "dose_ml_per_15L": 0.0, "frac_code": "N/A", "phi_days": 0}
        ]
        tier_3_cultural = [
            "Maintain 60cm row spacing for adequate canopy aeration",
            "Monitor twice weekly using delta pheromone/sticky traps"
        ]
    elif sev in ["low", "early"]:
        tier_1_biological = [
            {"agent": "Pseudomonas fluorescens 1% WP @ 5 g/L", "dosage": "75g per 15L tank", "application_timing": "Immediate morning spray to induce systemic resistance"},
            {"agent": "Neem Oil 10,000 PPM (Azadirachtin) @ 3 ml/L", "dosage": "45ml per 15L tank", "application_timing": "Evening spray as protective anti-feedant"}
        ]
        tier_2_chemical = [
            {"active_ingredient": f"Contact Protectant: {base_chem_name}", "dose_ml_per_15L": 30.0, "frac_code": frac_code, "phi_days": phi_days, "rotation_partner": rot_partner, "application_timing": "Apply if disease spots increase over next 48 hours"}
        ]
        tier_3_cultural = [
            "Strip lowest infected leaves showing initial chlorotic spots",
            "Avoid excessive split nitrogen top-dressing which softens foliar tissues",
            "Ensure surface drainage in furrow channels"
        ]
    elif sev == "moderate":
        tier_1_biological = [
            {"agent": "Bacillus subtilis @ 5 g/L + Trichoderma viride @ 5 g/L", "dosage": "75g + 75g per 15L tank", "application_timing": "Spray 3 days after chemical curative spray to recolonize phyllosphere"}
        ]
        tier_2_chemical = [
            {"active_ingredient": f"Curative + Protectant Tank Mix: {base_chem_name}", "dose_ml_per_15L": 37.5, "frac_code": frac_code, "phi_days": phi_days, "rotation_partner": rot_partner, "application_timing": "Morning spray (6:30–9:30 AM) on dry foliage with thorough canopy coverage"},
            {"active_ingredient": f"Rotational Partner (next cycle): {rot_partner}", "dose_ml_per_15L": 35.0, "frac_code": "Alternative FRAC Group", "phi_days": phi_days, "rotation_partner": base_chem_name, "application_timing": "Spray 7–10 days after first round to prevent resistance"}
        ]
        tier_3_cultural = [
            "Prune infected foliage and dispose away from field borders",
            "Switch to morning drip irrigation; avoid sprinkler/overhead methods",
            "Add silicon-based surfactant @ 0.5 ml/L to enhance leaf surface coverage"
        ]
    else:  # Severe
        tier_1_biological = [
            {"agent": "Bio-agent recovery consortium (Trichoderma + Pseudomonas)", "dosage": "100g per 15L tank", "application_timing": "Apply 7 days post chemical knockdown to suppress secondary soil-borne inocula"}
        ]
        tier_2_chemical = [
            {"active_ingredient": f"Emergency Curative Systemic: {base_chem_name}", "dose_ml_per_15L": 45.0, "frac_code": frac_code, "phi_days": phi_days, "rotation_partner": rot_partner, "application_timing": "Immediate high-pressure knapsack spray targeting both upper & lower leaf lamina"},
            {"active_ingredient": f"Follow-up Resistance Interrupter: {rot_partner}", "dose_ml_per_15L": 40.0, "frac_code": "Rotational Group", "phi_days": phi_days + 3, "rotation_partner": base_chem_name, "application_timing": "Mandatory follow-up spray at 5-day interval"}
        ]
        tier_3_cultural = [
            "Uproot severely wilted plants to prevent subterranean root-zone infection",
            "Implement mandatory 2-year non-host crop rotation for affected field block",
            "Deep summer plowing (chisel plowing) post-harvest to expose dormant sclerotia/spores to solar radiation"
        ]

    # 3. DYNAMIC MULTI-LINGUAL FARMER SUMMARY
    reg = base_info.get("regional_terms", {})
    marathi_dis = reg.get("disease_marathi", disease)
    hindi_dis = reg.get("disease_hindi", disease)

    if is_healthy:
        summary_en = f"Your {crop} crop is healthy with vibrant foliar development. Maintain scheduled organic scouting."
        summary_mr = f"तुमचे {crop} पीक पूर्णपणे निरोगी असून पानांची वाढ उत्तम आहे. नियमित सेंद्रिय देखरेख चालू ठेवा."
        summary_hi = f"आपकी {crop} की फसल पूरी तरह स्वस्थ है। नियमित जैविक निगरानी जारी रखें।"
    elif sev in ["low", "early"]:
        summary_en = f"Early-stage {disease} detected ({necrotic_area_pct:.1f}% leaf area). Bio-fungicide spray ({tier_1_biological[0]['agent']}) recommended to arrest early spread."
        summary_mr = f"{crop} पिकावर सुरुवातीच्या टप्प्यातील {marathi_dis} ({necrotic_area_pct:.1f}% भाग) आढळला आहे. जैविक फवारणीद्वारे तात्काळ नियंत्रण करा."
        summary_hi = f"{crop} की फसल में प्रारंभिक {hindi_dis} ({necrotic_area_pct:.1f}% क्षेत्र) देखा गया है। जैविक छिड़काव से तुरंत नियंत्रण करें।"
    elif sev == "moderate":
        summary_en = f"Active {disease} observed ({necrotic_area_pct:.1f}% necrotic area, {severity_tier} severity). Targeted spray of {tier_2_chemical[0]['active_ingredient']} (37.5g per 15L tank) advised within 48 hours."
        summary_mr = f"{crop} पिकावर {marathi_dis} चा प्रादुर्भाव मध्यम स्वरूपात ({necrotic_area_pct:.1f}%) आहे. १५ लिटर पंपाला ३७.५ ग्रॅम फवारणी २ दिवसांत करावी."
        summary_hi = f"{crop} फसल में {hindi_dis} मध्यम स्तर ({necrotic_area_pct:.1f}%) पर है। १५ लीटर पंप में ३७.५ ग्राम दवा मिलाकर अगले ४८ घंटों में छिड़काव करें।"
    else:  # Severe
        summary_en = f"Critical severe outbreak of {disease} ({necrotic_area_pct:.1f}% foliar destruction). Urgent curative spray required immediately to halt yield loss."
        summary_mr = f"⚠️ {crop} पिकावर {marathi_dis} चा तीव्र प्रादुर्भाव ({necrotic_area_pct:.1f}% नुकसान). नुकसान टाळण्यासाठी तात्काळ तातडीची फवारणी करा."
        summary_hi = f"⚠️ {crop} फसल में {hindi_dis} का गंभीर प्रकोप ({necrotic_area_pct:.1f}% पत्तियां प्रभावित). फसल बचाने के लिए तुरंत आपातकालीन छिड़काव करें।"

    return {
        "symptoms_observed": symptoms_observed,
        "likely_cause": likely_cause,
        "immediate_precautions": immediate_precautions,
        "ipm": {
            "tier_1_biological": tier_1_biological,
            "tier_2_chemical": tier_2_chemical,
            "tier_3_cultural": tier_3_cultural
        },
        "farmer_summary": {
            "english": summary_en,
            "marathi": summary_mr,
            "hindi": summary_hi
        }
    }


def generate_dynamic_advisory(
    crop: str,
    disease: str,
    pathogen: str,
    severity_tier: str,
    necrotic_area_pct: float,
    confidence_pct: int,
    differential_diagnoses: Optional[List[Dict[str, Any]]] = None,
    base_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main entry point for generating dynamic pathology advisory.
    Uses multi-level caching by (crop, disease, severity_tier, confidence_bracket).
    Attempts external LLM call if configured, falling back safely to the dynamic rule engine.
    """
    if differential_diagnoses is None:
        differential_diagnoses = []
    if base_info is None:
        base_info = {}

    cache_key = _get_cache_key(crop, disease, severity_tier, confidence_pct)
    if cache_key in _ADVISORY_CACHE:
        logger.info(f"[DynamicAdvisor] Cache hit for key: {cache_key}")
        return _ADVISORY_CACHE[cache_key]

    # Attempt External LLM Call if API Keys are configured
    llm_result = None
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if groq_key:
        try:
            prompt = (
                f"You are an agricultural pathologist for Maharashtra cash crops. An image was analyzed:\n"
                f"- Crop: {crop}\n- Diagnosis: {disease} ({pathogen})\n"
                f"- Confidence: {confidence_pct}%\n- Severity: {severity_tier} ({necrotic_area_pct:.1f}% necrotic area affected)\n"
                f"- Differentials: {[d.get('name') for d in differential_diagnoses[:2]]}\n\n"
                f"Generate JSON strictly with keys: 'symptoms_observed' (list of 3 strings tailored to this severity %), "
                f"'likely_cause' (1-2 sentences), 'immediate_precautions' (list of 2 strings), "
                f"'farmer_summary_en' (2 sentences summary with 15L knapsack tank dose)."
            )
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3,
                    "max_tokens": 400
                },
                timeout=3.5
            )
            if res.status_code == 200:
                parsed = res.json()["choices"][0]["message"]["content"]
                data = json.loads(parsed)
                # Merge into dynamic structure
                rule_fallback = _generate_rule_grounded_dynamic_advisory(
                    crop, disease, pathogen, severity_tier, necrotic_area_pct, confidence_pct, differential_diagnoses, base_info
                )
                rule_fallback["symptoms_observed"] = data.get("symptoms_observed", rule_fallback["symptoms_observed"])
                rule_fallback["likely_cause"] = data.get("likely_cause", rule_fallback["likely_cause"])
                rule_fallback["immediate_precautions"] = data.get("immediate_precautions", rule_fallback["immediate_precautions"])
                llm_result = rule_fallback
        except Exception as e:
            logger.warning(f"[DynamicAdvisor] Groq API call failed or timed out: {e}")

    # If LLM not available or timed out, use the dynamic natural language engine
    if not llm_result:
        llm_result = _generate_rule_grounded_dynamic_advisory(
            crop, disease, pathogen, severity_tier, necrotic_area_pct, confidence_pct, differential_diagnoses, base_info
        )

    # Store in Cache
    _ADVISORY_CACHE[cache_key] = llm_result
    return llm_result
