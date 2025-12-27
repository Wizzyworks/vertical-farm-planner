import json
import os
from .models import FarmConfig, SimulationResult, CropData, InfraConfig
from .economics import calculate_economics

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

def load_data():
    with open(os.path.join(DATA_DIR, 'crops.json'), 'r') as f:
        crops = [CropData(**c) for c in json.load(f)]
    with open(os.path.join(DATA_DIR, 'infra_costs.json'), 'r') as f:
        infra_data = json.load(f)
        # Parse systems dict to list of models
        systems = []
        for k, v in infra_data['systems'].items():
            systems.append(InfraConfig(
                system_id=k, 
                system_name=v['name'], 
                capex_per_sqm=v['capex_per_sqm'],
                maintenance_annual_percent=v['maintenance_annual_percent']
            ))
    return crops, systems

def get_crop_by_id(crop_id: str, crops: list[CropData]) -> CropData:
    for c in crops:
        if c.id == crop_id:
            return c
    raise ValueError(f"Crop ID {crop_id} not found")

def get_system_by_id(system_id: str, systems: list[InfraConfig]) -> InfraConfig:
    for s in systems:
        if s.system_id == system_id:
            return s
    raise ValueError(f"System ID {system_id} not found")

def run_simulation(config: FarmConfig) -> SimulationResult:
    crops, systems = load_data()
    
    crop = get_crop_by_id(config.selected_crop_id, crops)
    infra = get_system_by_id(config.selected_system_id, systems)
    
    # 1. Yield Calculation
    # Cycles per year = 365 / (growth_cycle + cleaning_days)
    # Assuming 3 days cleaning
    cycle_days = crop.growth_cycle_days + 3
    cycles_per_year = 365 / cycle_days
    
    # Theoretical Yield
    yield_per_cycle = config.total_area_sqm * crop.yield_per_sqm_per_cycle
    # Apply modifier (user skill, tech efficiency)
    total_yield_annual = yield_per_cycle * cycles_per_year * config.custom_yield_modifier
    
    # 2. Economics
    financials = calculate_economics(config, crop, infra, total_yield_annual, cycles_per_year)
    
    # 3. Risks & Recs (Simple logic for now)
    risk_score = 20 # Low baseline
    recs = ["Ensure uniform airflow to prevent tipburn."]
    
    if financials.roi_percent < 0:
        risk_score += 50
        recs.append("Current configuration is not profitable. Consider increasing area or switching crops.")
    if config.location_city.lower() in ["dubai", "phoenix"]:
         recs.append("High cooling load expected. Ensure HVAC redundancy.")
         
    return SimulationResult(
        config=config,
        crop=crop,
        infra=infra,
        cycles_per_year=round(cycles_per_year, 1),
        total_yield_annual_kg=round(total_yield_annual, 1),
        financials=financials,
        risk_score=risk_score,
        recommendations=recs
    )
