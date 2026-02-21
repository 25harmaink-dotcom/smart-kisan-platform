"""
Rule-based AI logic for Smart Kisan Platform
All decisions are made using expert agricultural knowledge encoded as rules.
No external APIs required.
"""

from i18n_utils import localize_free_text


# ---- IRRIGATION PLANNER ----

IRRIGATION_DATA = {
    "Wheat": {
        "Sandy": {"water": 3500, "freq": 5, "yield": 18},
        "Loamy": {"water": 2800, "freq": 7, "yield": 22},
        "Clay": {"water": 2200, "freq": 10, "yield": 20},
        "Clay Loam": {"water": 2500, "freq": 8, "yield": 21},
        "Sandy Loam": {"water": 3000, "freq": 6, "yield": 19},
        "Default": {"water": 2800, "freq": 7, "yield": 20},
    },
    "Rice": {
        "Clay": {"water": 6000, "freq": 3, "yield": 25},
        "Loamy": {"water": 5500, "freq": 4, "yield": 22},
        "Sandy": {"water": 7000, "freq": 2, "yield": 18},
        "Alluvial": {"water": 5000, "freq": 3, "yield": 28},
        "Default": {"water": 5500, "freq": 3, "yield": 22},
    },
    "Cotton": {
        "Black Cotton Soil": {"water": 4000, "freq": 10, "yield": 12},
        "Loamy": {"water": 3500, "freq": 8, "yield": 10},
        "Sandy Loam": {"water": 4500, "freq": 7, "yield": 9},
        "Default": {"water": 4000, "freq": 8, "yield": 10},
    },
    "Sugarcane": {
        "Loamy": {"water": 8000, "freq": 7, "yield": 300},
        "Alluvial": {"water": 7500, "freq": 7, "yield": 320},
        "Sandy": {"water": 10000, "freq": 5, "yield": 250},
        "Default": {"water": 8000, "freq": 7, "yield": 300},
    },
    "Maize": {
        "Sandy Loam": {"water": 3000, "freq": 6, "yield": 20},
        "Loamy": {"water": 2500, "freq": 7, "yield": 25},
        "Default": {"water": 2800, "freq": 6, "yield": 22},
    },
    "Soybean": {
        "Loamy": {"water": 2500, "freq": 8, "yield": 12},
        "Black Cotton Soil": {"water": 2200, "freq": 10, "yield": 14},
        "Default": {"water": 2500, "freq": 8, "yield": 12},
    },
    "Groundnut": {
        "Sandy": {"water": 2000, "freq": 8, "yield": 10},
        "Sandy Loam": {"water": 1800, "freq": 9, "yield": 12},
        "Default": {"water": 2000, "freq": 8, "yield": 11},
    },
    "Mustard": {
        "Sandy Loam": {"water": 1500, "freq": 12, "yield": 8},
        "Loamy": {"water": 1200, "freq": 15, "yield": 10},
        "Default": {"water": 1500, "freq": 12, "yield": 9},
    },
    "Pulses": {
        "Sandy": {"water": 1500, "freq": 10, "yield": 6},
        "Loamy": {"water": 1200, "freq": 12, "yield": 8},
        "Default": {"water": 1500, "freq": 10, "yield": 7},
    },
    "Potato": {
        "Sandy Loam": {"water": 3500, "freq": 5, "yield": 80},
        "Loamy": {"water": 3000, "freq": 6, "yield": 100},
        "Default": {"water": 3500, "freq": 5, "yield": 85},
    },
    "Vegetables": {
        "Loamy": {"water": 3000, "freq": 4, "yield": 60},
        "Sandy Loam": {"water": 3500, "freq": 3, "yield": 50},
        "Default": {"water": 3000, "freq": 4, "yield": 55},
    },
    "Default": {"Default": {"water": 2500, "freq": 7, "yield": 15}},
}


def get_irrigation_plan(crop, soil, water_source, area, lang="en"):
    crop_data = IRRIGATION_DATA.get(crop, IRRIGATION_DATA["Default"])
    soil_data = crop_data.get(soil, crop_data.get("Default", {"water": 2500, "freq": 7, "yield": 15}))

    water_per_acre = soil_data["water"]
    freq = soil_data["freq"]
    yield_per_acre = soil_data["yield"]

    total_water = int(water_per_acre * area)
    total_yield = yield_per_acre * area

    efficiency_tip = ""
    if water_source in ["Canal", "River", "Pond"]:
        efficiency_tip = "Consider drip/sprinkler to reduce water use by 30-40%"
    elif water_source in ["Drip Irrigation", "Sprinkler"]:
        total_water = int(total_water * 0.65)
        efficiency_tip = "Drip/Sprinkler detected - water requirement reduced by 35%"
    elif water_source == "Borewell":
        efficiency_tip = "Borewell usage - monitor groundwater levels. Consider scheduling at night."

    schedule = [localize_free_text(f"Day {i * freq}: Apply {int(water_per_acre * 0.2):,} L/acre", lang) for i in range(1, 6)]
    stages = [localize_free_text(s, lang) for s in _get_crop_stages(crop)]

    return {
        "water_per_acre": localize_free_text(f"{water_per_acre:,} L/acre", lang),
        "water_per_acre_num": water_per_acre,
        "total_water": localize_free_text(f"{total_water:,} L", lang),
        "frequency": localize_free_text(f"Every {freq} days", lang),
        "freq_days": freq,
        "next_irrigation": localize_free_text(f"In {freq} days", lang),
        "estimated_yield": localize_free_text(f"{total_yield:.1f} quintals", lang),
        "yield_per_acre": localize_free_text(f"{yield_per_acre} q/acre", lang),
        "efficiency_tip": localize_free_text(efficiency_tip, lang) if efficiency_tip else "",
        "schedule": schedule,
        "best_time": localize_free_text("Early morning (5-7 AM) or evening (6-8 PM)", lang),
        "stages": stages,
    }


def _get_crop_stages(crop):
    stages = {
        "Wheat": [
            "Sowing (Oct-Nov): 1 irrigation",
            "Tillering (Dec): 2nd irrigation",
            "Jointing (Jan): 3rd irrigation",
            "Heading (Feb): 4th irrigation",
            "Grain fill (Mar): 5th irrigation",
        ],
        "Rice": [
            "Transplanting: Keep 5cm standing water",
            "Tillering: 3-5cm water",
            "Panicle initiation: 5cm water",
            "Flowering: Critical - no stress",
            "Ripening: Drain 2 weeks before harvest",
        ],
        "Cotton": [
            "Germination: Light irrigation",
            "Vegetative: Every 10-12 days",
            "Flowering: Critical period, don't stress",
            "Boll development: Reduce frequency",
            "Maturity: Stop 4 weeks before harvest",
        ],
        "Sugarcane": [
            "Germination: Light frequent",
            "Tillering: Increase frequency",
            "Grand growth: Maximum water",
            "Maturity: Reduce gradually",
            "Pre-harvest: Stop 4 weeks before",
        ],
        "Default": [
            "Germination stage: Light irrigation",
            "Vegetative stage: Moderate irrigation",
            "Flowering stage: Critical period",
            "Grain/Fruit fill: Adequate water",
            "Maturity: Reduce water",
        ],
    }
    return stages.get(crop, stages["Default"])


# ---- CROP ROTATION ADVISOR ----

ROTATION_RULES = {
    "Wheat": {"next": "Soybean", "reason": "Soybeans fix nitrogen depleted by wheat, improving soil fertility", "soil_impact": "+15% Nitrogen, Improved organic matter"},
    "Rice": {"next": "Pulses", "reason": "Pulses restore nitrogen after rice's heavy nutrient demand", "soil_impact": "+20% Nitrogen fixation, Reduced waterlogging"},
    "Cotton": {"next": "Wheat", "reason": "Wheat breaks cotton pest cycles and improves soil structure", "soil_impact": "Reduced pest pressure, +10% organic matter"},
    "Sugarcane": {"next": "Groundnut", "reason": "Groundnut restores soil health after nutrient-intensive sugarcane", "soil_impact": "+18% Nitrogen, Improved aeration"},
    "Maize": {"next": "Mustard", "reason": "Mustard acts as natural pest deterrent and adds organic matter", "soil_impact": "Pest control, +12% organic matter"},
    "Soybean": {"next": "Wheat", "reason": "Wheat utilizes nitrogen fixed by soybean, maximizing benefits", "soil_impact": "Utilizes stored Nitrogen, Stable pH"},
    "Groundnut": {"next": "Cotton", "reason": "Cotton benefits from nitrogen-enriched soil left by groundnut", "soil_impact": "+15% soil nitrogen, Good for cotton fiber quality"},
    "Mustard": {"next": "Rice", "reason": "Rice paddy breaks mustard disease cycles effectively", "soil_impact": "Disease break, pH adjustment"},
    "Pulses": {"next": "Maize", "reason": "Maize uses the nitrogen fixed by pulses for high yields", "soil_impact": "+20% Nitrogen utilization, Good root depth"},
    "Vegetables": {"next": "Wheat", "reason": "Wheat rests the soil after intensive vegetable production", "soil_impact": "Soil rest, Reduced disease carryover"},
    "Potato": {"next": "Pulses", "reason": "Pulses break potato disease cycles and restore soil health", "soil_impact": "Disease break, +15% Nitrogen, Better structure"},
    "Default": {"next": "Pulses", "reason": "Pulses are universally beneficial for soil nitrogen restoration", "soil_impact": "+15% Nitrogen, Improved soil health"},
}

ADDITIONAL_TIPS = {
    "Sandy": "Add organic compost between rotations to improve water retention",
    "Clay": "Include deep-rooted crops like sunflower to improve drainage",
    "Loamy": "Ideal soil - maintain health with green manure crops",
    "Black Cotton Soil": "Avoid waterlogging-sensitive crops; include millets",
    "Red Soil": "Add lime to adjust pH; legumes help fix nitrogen",
    "Default": "Regular soil testing recommended every 2-3 seasons",
}


def get_crop_rotation(crop, soil, lang="en"):
    rule = ROTATION_RULES.get(crop, ROTATION_RULES["Default"])
    tip = ADDITIONAL_TIPS.get(soil, ADDITIONAL_TIPS["Default"])
    return {
        "next_crop": localize_free_text(rule["next"], lang),
        "reason": localize_free_text(rule["reason"], lang),
        "soil_impact": localize_free_text(rule["soil_impact"], lang),
        "soil_tip": localize_free_text(tip, lang),
        "fallow_option": localize_free_text("Consider 2-3 week fallow with green manure (Dhaincha/Sunhemp) between crops", lang),
    }


# ---- COMPLAINT PRIORITY DETECTION ----

HIGH_PRIORITY_KEYWORDS = [
    "flood",
    "drought",
    "dead",
    "disease",
    "pest",
    "locust",
    "no water",
    "crop failure",
    "loss",
    "damage",
    "emergency",
    "urgent",
    "dying",
    "contaminated",
    "poison",
    "toxic",
    "illegal",
    "bund broken",
    "canal broken",
    "बाढ़",
    "सूखा",
    "मर",
    "बीमारी",
    "कीट",
    "पानी नहीं",
    "फसल खराब",
    "नुकसान",
    "आपातकाल",
    "जरूरी",
    "जहर",
    "नाला टूटा",
]

MEDIUM_PRIORITY_KEYWORDS = [
    "delay",
    "not received",
    "pending",
    "subsidy",
    "payment",
    "application",
    "certificate",
    "repair",
    "maintenance",
    "request",
    "help",
    "issue",
    "problem",
    "विलंब",
    "नहीं मिला",
    "लंबित",
    "सब्सिडी",
    "भुगतान",
    "आवेदन",
    "मरम्मत",
]

DEPARTMENT_ROUTING = {
    "water": "Water Resources Department",
    "canal": "Water Resources Department",
    "bund": "Water Resources Department",
    "flood": "State Disaster Management",
    "drought": "Ministry of Jal Shakti",
    "subsidy": "Ministry of Agriculture",
    "scheme": "Ministry of Agriculture",
    "seed": "Ministry of Agriculture",
    "fertilizer": "Ministry of Agriculture",
    "pest": "State Agriculture Department",
    "disease": "State Agriculture Department",
    "loan": "NABARD",
    "credit": "NABARD",
    "road": "Rural Development",
    "electricity": "State Electricity Board",
    "pump": "State Agriculture Department",
    "default": "Ministry of Agriculture",
}


def detect_priority(title, description):
    text = (title + " " + description).lower()
    for kw in HIGH_PRIORITY_KEYWORDS:
        if kw.lower() in text:
            return "High"
    for kw in MEDIUM_PRIORITY_KEYWORDS:
        if kw.lower() in text:
            return "Medium"
    return "Low"


def route_department(title, description):
    text = (title + " " + description).lower()
    for keyword, dept in DEPARTMENT_ROUTING.items():
        if keyword in text:
            return dept
    return DEPARTMENT_ROUTING["default"]
