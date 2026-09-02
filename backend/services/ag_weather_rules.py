"""Agri Nirvana - Agricultural Weather Rules Engine.

Deterministic, agronomy-grounded interpretation of physical weather variables.
Translates raw meteorological variables (temperature, humidity, rain probability,
wind speed, solar radiation, ET0 evapotranspiration) into actionable, non-prescriptive
signals for farmers and agronomists.

IMPORTANT AGRONOMIC CONSTRAINTS:
- Never diagnoses disease from weather alone (weather creates potential risk conditions;
  actual infection requires presence of inoculum, host susceptibility, and physical symptoms).
- Never generates chemical dosages or ungrounded pesticide prescriptions.
- Always provides transparent, explainable reasoning.
"""

from typing import Any, Dict, List, Optional


def evaluate_agricultural_weather(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates raw weather forecast data into structured agricultural signals.

    Parameters:
    - weather_data: formatted dictionary containing 'current', 'hourly', and 'daily' structures.

    Returns:
    - Dictionary with agricultural signals and explanations.
    """
    current = weather_data.get("current", {})
    daily = weather_data.get("daily", [])
    hourly = weather_data.get("hourly", [])

    temp_c = current.get("temperature_c", 25.0) or 25.0
    rh_pct = current.get("relative_humidity_pct", 50.0) or 50.0
    wind_kmh = current.get("wind_speed_kmh", 10.0) or 10.0
    gust_kmh = current.get("wind_gusts_kmh", 15.0) or 15.0
    precip_mm = current.get("precipitation_mm", 0.0) or 0.0

    today_daily = daily[0] if daily else {}
    next_24h_pop_max = today_daily.get("precipitation_probability_max_pct", 0) or 0
    next_24h_rain_sum = today_daily.get("rain_sum_mm", 0.0) or 0.0
    et0_mm = today_daily.get("et0_fao_evapotranspiration_mm", 4.0) or 4.0

    # 1. RAIN OUTLOOK SIGNAL
    if next_24h_rain_sum >= 15.0 or next_24h_pop_max >= 75:
        rain_status = "High Chance of Rainfall"
        rain_summary = f"Substantial rainfall (~{next_24h_rain_sum:.1f} mm expected, {next_24h_pop_max}% probability). Prepare field drainage."
        rain_level = "high"
    elif next_24h_rain_sum >= 3.0 or next_24h_pop_max >= 40:
        rain_status = "Moderate Chance of Rain"
        rain_summary = f"Scattered showers possible ({next_24h_pop_max}% probability, ~{next_24h_rain_sum:.1f} mm). Monitor local cloud build-up."
        rain_level = "moderate"
    elif next_24h_pop_max >= 20:
        rain_status = "Low Rain Probability"
        rain_summary = f"Predominantly dry with slight shower chance ({next_24h_pop_max}%). Good for general field work."
        rain_level = "low"
    else:
        rain_status = "Dry Conditions"
        rain_summary = "Very low rain probability (<20%). Clear conditions favorable for drying and harvesting."
        rain_level = "dry"

    # 2. FIELD MOISTURE OUTLOOK
    if next_24h_rain_sum >= 10.0:
        moisture_status = "Increasing / Wet Soil Profile"
        moisture_summary = "Significant rainfall expected to recharge upper root zones. Heavy tractor movement may cause soil compaction."
    elif next_24h_rain_sum >= 2.0:
        moisture_status = "Stable / Light Moisture Addition"
        moisture_summary = "Light surface moisture addition expected. Soil trafficability remains generally manageable."
    elif et0_mm >= 5.5 and temp_c >= 32.0:
        moisture_status = "Depleting Rapidly (High ET₀)"
        moisture_summary = f"High evaporative demand (ET₀ {et0_mm:.1f} mm/day). Soil moisture will deplete steadily."
    else:
        moisture_status = "Steady Depletion"
        moisture_summary = f"Normal crop water consumption (ET₀ {et0_mm:.1f} mm/day). Standard irrigation intervals apply."

    # 3. IRRIGATION MANAGEMENT CHECK
    if next_24h_rain_sum >= 12.0 or next_24h_pop_max >= 70:
        irrigation_status = "Delay Scheduled Irrigation"
        irrigation_summary = "Meaningful rainfall expected. Hold planned furrow/drip irrigation to avoid root zone waterlogging and nutrient leaching."
        irrigation_badge = "Hold"
    elif next_24h_rain_sum >= 4.0:
        irrigation_status = "Review / Reduce Irrigation Volume"
        irrigation_summary = "Moderate showers possible. Adjust drip timings downward and check soil probe/tensiometer readings."
        irrigation_badge = "Review"
    elif temp_c >= 35.0 and et0_mm >= 6.0:
        irrigation_status = "Ensure Adequate Drip Timing"
        irrigation_summary = "High temperatures and evapotranspiration elevate plant water stress. Run irrigation during cooler morning/evening hours."
        irrigation_badge = "Increase"
    else:
        irrigation_status = "Normal Irrigation Cycle"
        irrigation_summary = "Atmospheric evaporative demand is within normal seasonal bounds. Maintain standard crop water schedule."
        irrigation_badge = "Normal"

    # 4. WIND & DRIFT CONDITIONS
    if wind_kmh >= 22.0 or gust_kmh >= 30.0:
        wind_status = "High Wind / Strong Gusts"
        wind_summary = f"Sustained wind {wind_kmh:.1f} km/h (gusts to {gust_kmh:.1f} km/h). Severe droplet drift risk. Secure greenhouse netting."
        wind_level = "high"
    elif wind_kmh >= 14.0 or gust_kmh >= 20.0:
        wind_status = "Moderate Breeze"
        wind_summary = f"Breeze at {wind_kmh:.1f} km/h. Fine foliar misting may drift off-target. Use low-drift nozzles if spraying."
        wind_level = "moderate"
    else:
        wind_status = "Calm to Gentle Air"
        wind_summary = f"Gentle wind at {wind_kmh:.1f} km/h. Favorable conditions for foliar nutrient applications and drone operations."
        wind_level = "calm"

    # 5. BEST FIELD ACTIVITY & SPRAY WINDOW
    # Rule evaluation:
    # Poor if: active rain or high rain risk (>50%) or strong wind (>=18 km/h or gusts >=25 km/h)
    # Caution if: rain risk 25-50% or wind 12-18 km/h
    # Good if: dry (<25% rain), wind < 12 km/h
    if precip_mm > 0.5 or next_24h_pop_max >= 60 or wind_kmh >= 18.0 or gust_kmh >= 25.0:
        activity_window = "Poor"
        activity_color = "red"
        reasons = []
        if precip_mm > 0.5 or next_24h_pop_max >= 60:
            reasons.append("Rain risk may wash off foliar treatments before absorption")
        if wind_kmh >= 18.0 or gust_kmh >= 25.0:
            reasons.append(f"Wind speed ({wind_kmh:.1f} km/h) causes unacceptable drift")
        activity_rationale = "; ".join(reasons) + ". Defer outdoor spray applications."
    elif next_24h_pop_max >= 30 or wind_kmh >= 12.0:
        activity_window = "Caution"
        activity_color = "amber"
        activity_rationale = f"Variable conditions: wind ({wind_kmh:.1f} km/h) or shower risk ({next_24h_pop_max}%). Target calm early morning windows with coarse droplets."
    else:
        activity_window = "Good"
        activity_color = "emerald"
        activity_rationale = f"Calm wind ({wind_kmh:.1f} km/h) and low rain risk ({next_24h_pop_max}%). Favorable for spraying, dusting, and tractor operations."

    # 6. HEAT & SOLAR STRESS WATCH
    if temp_c >= 38.0:
        heat_status = "Severe Heat Stress Alert"
        heat_summary = f"Extreme temperature ({temp_c:.1f}°C). Pollen viability and blossom drop risk in flowering crops. Increase shade/mulching."
    elif temp_c >= 33.0:
        heat_status = "Moderate Thermal Load"
        heat_summary = f"Warm temperature ({temp_c:.1f}°C). Midday stomatal closure likely. Schedule foliar sprays before 9:30 AM or after 4:30 PM."
    elif temp_c <= 10.0:
        heat_status = "Cool Temperature"
        heat_summary = f"Cool conditions ({temp_c:.1f}°C). Slower nutrient uptake and delayed seed germination."
    else:
        heat_status = "Optimal Thermal Range"
        heat_summary = f"Comfortable temperature ({temp_c:.1f}°C) within active photosynthesis threshold for most field crops."

    # 7. DISEASE-FAVORABLE WEATHER NOTICE (Non-prescriptive, purely micro-climatic)
    # Fungal sporulation is strongly favored by prolonged high humidity (RH > 75-80%)
    # coupled with moderate temperatures (18°C - 28°C) and precipitation.
    if rh_pct >= 80.0 and 18.0 <= temp_c <= 28.0 and (precip_mm > 0.0 or next_24h_pop_max >= 45):
        disease_weather_status = "Favorable for Fungal Sporulation"
        disease_weather_level = "elevated"
        disease_weather_notice = (
            "Sustained high humidity (80%+) and moderate temperatures (18–28°C) create micro-climatic "
            "conditions favorable for fungal pathogen spread (e.g. blights, mildews). "
            "Scout crop leaves and use AI Crop Diagnostics to verify physical symptoms before taking action."
        )
    elif rh_pct >= 70.0 and 16.0 <= temp_c <= 30.0:
        disease_weather_status = "Moderate Micro-Climatic Moisture"
        disease_weather_level = "moderate"
        disease_weather_notice = (
            "Dew formation and elevated relative humidity present. Monitor canopy air circulation. "
            "Confirm any visual leaf spotting with the diagnostic camera."
        )
    else:
        disease_weather_status = "Low Disease-Favorable Weather Pressure"
        disease_weather_level = "low"
        disease_weather_notice = (
            "Current ambient humidity and temperature do not indicate high fungal pressure. "
            "Continue standard preventative agronomic practices."
        )

    return {
        "rain_outlook": {
            "status": rain_status,
            "level": rain_level,
            "summary": rain_summary,
            "probability_pct": next_24h_pop_max,
            "rain_sum_mm": next_24h_rain_sum,
        },
        "field_moisture": {
            "status": moisture_status,
            "summary": moisture_summary,
        },
        "irrigation_check": {
            "status": irrigation_status,
            "badge": irrigation_badge,
            "summary": irrigation_summary,
            "et0_mm": et0_mm,
        },
        "wind_conditions": {
            "status": wind_status,
            "level": wind_level,
            "summary": wind_summary,
            "speed_kmh": wind_kmh,
            "gusts_kmh": gust_kmh,
        },
        "field_activity_window": {
            "status": activity_window,
            "level": activity_color,
            "rationale": activity_rationale,
        },
        "heat_stress": {
            "status": heat_status,
            "summary": heat_summary,
        },
        "disease_favorable_weather": {
            "status": disease_weather_status,
            "level": disease_weather_level,
            "notice": disease_weather_notice,
            "disclaimer": "Weather conditions describe environmental suitability only. This is not a disease diagnosis.",
        },
    }
