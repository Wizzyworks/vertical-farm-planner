from .models import FarmConfig, CropData, InfraConfig, FinancialResult

def calculate_economics(
    config: FarmConfig, 
    crop: CropData, 
    infra: InfraConfig,
    total_yield_kg: float,
    cycles_per_year: float
) -> FinancialResult:
    
    # 1. CapEx
    # Base system cost + environment control + fit-out
    # Simplifying for MVP: Infra cost includes lights/HVAC basic
    capex_total = config.total_area_sqm * infra.capex_per_sqm
    
    # 2. Revenue
    revenue_annual = total_yield_kg * crop.market_price_per_kg
    
    # 3. OpEx
    # Variable costs (seeds, nutes)
    variable_cost_annual = config.total_area_sqm * crop.variable_cost_per_sqm_cycle * cycles_per_year
    
    # Energy
    # Estimation: 16 hrs light * 0.04 kWh * area * 365
    daily_light_hours = crop.light_hours_per_day
    energy_kwh_annual = (daily_light_hours * 0.04 * config.total_area_sqm) * 365 # Very rough LED assumption
    # HVAC assumption: 0.5 kWh/sqm/day
    energy_kwh_annual += (0.5 * config.total_area_sqm * 365)
    
    energy_cost_annual = energy_kwh_annual * config.electricity_cost_per_kwh
    
    # Labor
    # Assumption: 1 FTE per 500 sqm ?? Or use hours/sqm logic
    # Using simple heuristic: 20 hours/sqm/year
    labor_hours_annual = 20 * config.total_area_sqm
    labor_cost_annual = labor_hours_annual * config.labor_cost_per_hour
    
    # Maintenance
    maintenance_cost_annual = capex_total * infra.maintenance_annual_percent
    
    opex_annual = variable_cost_annual + energy_cost_annual + labor_cost_annual + maintenance_cost_annual
    
    # 4. Profitability
    net_profit_annual = revenue_annual - opex_annual
    gross_margin = (revenue_annual - opex_annual) / revenue_annual if revenue_annual > 0 else 0
    
    roi_percent = (net_profit_annual / capex_total * 100) if capex_total > 0 else 0
    payback_period = capex_total / net_profit_annual if net_profit_annual > 0 else 999.0
    
    # Break even
    # Fixed costs = labor + maintenance ?? No, in long run all are variable? 
    # Let's say Contribution Margin per kg = Price - (Variable / Yield)
    # This is getting complex, keeping it simple: Total Cost / Price per kg
    break_even_units = opex_annual / crop.market_price_per_kg
    
    return FinancialResult(
        capex_total=round(capex_total, 2),
        opex_annual=round(opex_annual, 2),
        revenue_annual=round(revenue_annual, 2),
        gross_margin=round(gross_margin * 100, 2),
        net_profit_annual=round(net_profit_annual, 2),
        roi_percent=round(roi_percent, 2),
        payback_period_years=round(payback_period, 1),
        break_even_units=round(break_even_units, 2)
    )
