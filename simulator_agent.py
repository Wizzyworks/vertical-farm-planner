import os
import json
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()


class SimulatorAgent:
    def __init__(self):
        with open('infra.json', 'r') as f:
            self.infra = json.load(f)
        with open('rules.json', 'r') as f:
            self.rules = json.load(f)

        self.model_name = "gemini-2.5-flash"

    # -------------------- Utilities --------------------

    def _safe_get(self, section, key):
        try:
            return self.rules["rules"][section][key]
        except KeyError:
            raise ValueError(f"Invalid {section} key: {key}")

    # -------------------- External APIs --------------------

    def get_apis(self, location):
        lat, lon = self._get_coords(location)

        # Weather
        url_weather = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
            f"&daily=precipitation_sum&timezone=Asia/Kolkata"
        )
        try:
            resp = requests.get(url_weather)
            data = resp.json()
            weather = {
                "temp": data['current_weather']['temperature'],
                "rain": data['daily']['precipitation_sum'][0],
                "adj": 0.9 if data['daily']['precipitation_sum'][0] > 5 else 1.0
            }
        except Exception:
            weather = {"temp": 25, "rain": 0, "adj": 1.0}

        # Soil
        url_soil = f"https://api.ambeedata.com/soil/latest/by-lat-lng?lat={lat}&lng={lon}"
        headers = {"x-api-key": os.getenv("AMBEE_API_KEY")}
        try:
            resp = requests.get(url_soil, headers=headers)
            data = resp.json()
            soil = data['data'][0]
            soil_data = {
                "moisture": soil.get('soil_moisture', 30),
                "adj": 1.2 if soil.get('soil_moisture', 0) > 25 else 1.0
            }
        except Exception:
            soil_data = {"moisture": 30, "adj": 1.0}

        return {"weather": weather, "soil": soil_data}

    def _get_coords(self, city):
        coords = {
            "Kolkata": (22.57, 88.36),
            "Mumbai": (19.07, 72.88)
        }
        return coords.get(city, (22.57, 88.36))

    # -------------------- Rules Engine --------------------

    def apply_rules(self, inputs):
        # Canonical keys are assumed (already mapped in app.py)

        space_type = self._safe_get("space_type", inputs["space_type"])
        budget_rule = self._safe_get("budget_filters", inputs["budget_level"])
        energy_rule = self._safe_get("energy_adjust", inputs["energy_source"])
        crop_rule = self._safe_get("crop_phases", inputs["crop_phase"])

        area_key = (
            "small" if inputs["space_size"] < 1000
            else "medium" if inputs["space_size"] < 5000
            else "large"
        )
        area_rule = self._safe_get("area_thresholds", area_key)

        boosts = {
            "weather_adj": self.rules["rules"]["boosts"]["weather_rain_adj"][
                "high" if inputs["space_type"] == "greenhouse" else "low"
            ]
        }

        infra_selected = self._select_infra(inputs, area_rule, budget_rule)

        # -------------------- Calculations --------------------

        base_yield = crop_rule["base_yield_kg_per_500sqft"]
        space_factor = inputs["space_size"] / 500

        yield_val = (
            base_yield
            * space_factor
            * space_type["yield_mult"]
            * energy_rule["yield_mult"]
            * boosts["weather_adj"]
        )

        setup_cost = (
            self.infra["costs_india_2025"]["small_setup"]
            * space_factor
            * space_type["cost_mult"]
            * (budget_rule["max_setup"] / 200000)
        )

        monthly_op = self.infra["costs_india_2025"]["monthly_op"]

        if inputs["energy_source"] == "hybrid":
            base_op_cost = (monthly_op["solar"] + monthly_op["grid"]) / 2
        else:
            base_op_cost = monthly_op[inputs["energy_source"]]

        op_cost_month = base_op_cost * space_type["energy_mult"]

        profit_yr = (
            yield_val * self.infra["costs_india_2025"]["sale_price_per_kg"]
            - (op_cost_month * 12 + setup_cost / 5)
        )

        npv_5yr = profit_yr * 5 - setup_cost
        roi_pct = (profit_yr / setup_cost) * 100 if setup_cost > 0 else 0

        carbon_saved = yield_val * 0.5 * (1 - energy_rule["carbon"] / 5.6)

        return {
            "yield": yield_val,
            "profit": profit_yr,
            "roi": {"npv": npv_5yr, "pct": roi_pct},
            "carbon_saved": carbon_saved,
            "costs_breakdown": infra_selected,
            "area_rule": area_rule,
            "space_type": space_type
        }

    # -------------------- Infra Selection --------------------

    def _select_infra(self, inputs, area_rule, budget_rule):
        selected = []
        for cat, options in self.infra["equipment"].items():
            if isinstance(options, list):
                if inputs["budget_level"] == "low":
                    idx = 0
                elif inputs["budget_level"] == "high":
                    idx = len(options) - 1
                else:
                    idx = 1

                item = options[idx]
                qty = area_rule["tiers"]
                unit_cost = item.get("cost", item.get("cost_per_unit", 0))
                selected.append({
                    "category": cat,
                    "model": item.get("model") or item.get("name") or item.get("type", "Generic"),
                    "qty": qty,
                    "cost": unit_cost * qty
                })
        return selected

    # -------------------- Main Entry --------------------

    def simulate_plan(self, inputs):
        _ = self.get_apis(inputs["location"])
        static = self.apply_rules(inputs)

        prompt = self.rules["formulas"]["prompt_template"].format(
            inputs=inputs, static=static
        )

        config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=800,
            response_mime_type="application/json"
        )

        response = client.models.generate_content(
            model=self.model_name,
            contents=[prompt],
            config=config
        )

        try:
            gemini_result = json.loads(response.text.strip())
            for k, v in gemini_result.items():
                if k not in {"yield", "profit", "roi", "carbon_saved"}:
                 static[k] = v

        except Exception:
            static["plan_details"] = (
                "Sample plan: 3 tiers, Philips LEDs, Daikin HVAC. "
                "Timeline: Week 1 seed, Week 4 harvest."
            )

        return static

    def handle_qa(self, query):
        prompt = f"Answer VF doubt from knowledge: {query}. Keep short, accurate."
        config = types.GenerateContentConfig(temperature=0.5, max_output_tokens=200)
        response = client.models.generate_content(
            model=self.model_name,
            contents=[prompt],
            config=config
        )
        return response.text.strip()
