"""Safety-first advisory formatter for production diagnosis.

This module does not invent pesticide doses, disease severity, field measurements,
or live agronomic facts. It formats information already present in the static
knowledge record and the measured inference output. Chemical use remains a
reference for expert/label verification, not an automatically authorized
prescription.
"""

from typing import Any, Dict, List

_ADVISORY_CACHE: Dict[str, Dict[str, Any]] = {}
_MAX_CACHE_SIZE = 512


def _cache_key(crop: str, disease: str, severity_tier: str, conf_pct: int) -> str:
    bracket = "high" if conf_pct >= 80 else "medium" if conf_pct >= 60 else "low"
    return f"{crop.lower()}:{disease.lower()}:{severity_tier.lower()}:{bracket}"


def _reference_items(values: Any, limit: int = 3) -> List[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values[:limit] if str(item).strip()]


def _build_advisory(
    crop: str,
    disease: str,
    pathogen: str,
    severity_tier: str,
    necrotic_area_pct: float,
    confidence_pct: int,
    differential_diagnoses: List[Dict[str, Any]],
    base_info: Dict[str, Any],
) -> Dict[str, Any]:
    is_healthy = "healthy" in disease.lower() or severity_tier.lower() == "healthy"
    symptoms = _reference_items(base_info.get("symptoms_observed"))
    causes = str(base_info.get("likely_cause") or "")
    precautions = _reference_items(base_info.get("immediate_precautions"), limit=4)
    organic = _reference_items(base_info.get("treatment_organic"), limit=3)
    chemical = _reference_items(base_info.get("treatment_chemical"), limit=3)
    prevention = _reference_items(base_info.get("prevention_tips"), limit=4)

    if not symptoms:
        symptoms = ["No verified symptom description is available for this class."]
    if not precautions:
        precautions = [
            "Do not apply disease-specific chemicals from the AI result alone.",
            "Rescan with a clear image and verify the diagnosis with a local agriculture expert if symptoms persist.",
        ]

    # The measured necrotic percentage is only surfaced as model evidence; it is
    # never converted into a fabricated severity or treatment dose.
    evidence = [
        f"Production model confidence: {confidence_pct}%.",
        f"Estimated affected area: {max(0.0, min(float(necrotic_area_pct), 100.0)):.1f}%.",
    ]
    if pathogen:
        evidence.append(f"Reference pathogen: {pathogen}.")
    if differential_diagnoses:
        names = [str(item.get("name")) for item in differential_diagnoses[:2] if item.get("name")]
        if names:
            evidence.append("Differentials requiring visual confirmation: " + ", ".join(names) + ".")

    verification = (
        "Chemical and biological products are reference information only. Confirm the current "
        "label, crop registration, formulation, dose, PHI, compatibility, and local recommendation "
        "with a qualified agronomist/KVK before application."
    )

    return {
        "symptoms_observed": symptoms,
        "likely_cause": causes or "Cause is not established from the image alone.",
        "immediate_precautions": precautions,
        "evidence_features": evidence,
        "ipm": {
            "tier_1_biological": [
                {"reference": item, "dose": None, "application_timing": None}
                for item in organic
            ],
            "tier_2_chemical": [
                {
                    "reference": item,
                    "active_ingredient": None,
                    "dosage": None,
                    "dose_ml_per_15L": None,
                    "frac_code": None,
                    "phi_days": None,
                    "verification_required": True,
                }
                for item in chemical
            ],
            "tier_3_cultural": prevention,
        },
        "farmer_summary": (
            f"{crop}: {disease} was identified by the production model at {confidence_pct}% confidence. "
            f"Severity output: {severity_tier}. Estimated affected area: "
            f"{max(0.0, min(float(necrotic_area_pct), 100.0)):.1f}%. "
            "Use the evidence and reference information below for expert verification."
            if not is_healthy
            else f"{crop}: the production model classified this image as healthy at {confidence_pct}% confidence. Continue routine scouting."
        ),
        "verification_note": verification,
        "treatment_allowed": False,
        "reference_only": True,
    }


def generate_dynamic_advisory(
    crop: str,
    disease: str,
    pathogen: str,
    severity_tier: str,
    necrotic_area_pct: float,
    confidence_pct: int,
    differential_diagnoses: List[Dict[str, Any]],
    base_info: Dict[str, Any],
) -> Dict[str, Any]:
    key = _cache_key(crop, disease, severity_tier, confidence_pct)
    cached = _ADVISORY_CACHE.get(key)
    if cached is not None:
        return cached

    result = _build_advisory(
        crop,
        disease,
        pathogen,
        severity_tier,
        necrotic_area_pct,
        confidence_pct,
        differential_diagnoses,
        base_info,
    )
    if len(_ADVISORY_CACHE) >= _MAX_CACHE_SIZE:
        _ADVISORY_CACHE.pop(next(iter(_ADVISORY_CACHE)))
    _ADVISORY_CACHE[key] = result
    return result
