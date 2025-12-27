from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class CropData(BaseModel):
    id: str
    name: str
    type: str # e.g. "Leafy Green", "Herb"
    growth_cycle_days: int
    yield_per_sqm_per_cycle: float # kg
    optimal_temp_c: List[float] # [min, max]
    market_price_per_kg: float
    variable_cost_per_sqm_cycle: float # Seeds, nutrients specifically
    light_hours_per_day: int

class InfraConfig(BaseModel):
    system_id: str
    system_name: str
    capex_per_sqm: float
    maintenance_annual_percent: float

class FarmConfig(BaseModel):
    project_name: str = "My Vertical Farm"
    total_area_sqm: float = Field(..., gt=0)
    location_city: str = "New York"
    selected_crop_id: str
    selected_system_id: str
    electricity_cost_per_kwh: float = 0.15
    labor_cost_per_hour: float = 20.0
    # Advanced overrides
    custom_yield_modifier: float = 1.0

class FinancialResult(BaseModel):
    capex_total: float
    opex_annual: float
    revenue_annual: float
    gross_margin: float
    net_profit_annual: float
    roi_percent: float
    payback_period_years: float
    break_even_units: float # kg

class SimulationResult(BaseModel):
    config: FarmConfig
    crop: CropData
    infra: InfraConfig
    cycles_per_year: float
    total_yield_annual_kg: float
    financials: FinancialResult
    risk_score: int # 1-100
    recommendations: List[str]
