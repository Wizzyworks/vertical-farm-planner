import sys
import os

# Add the current directory to path so we can import src
sys.path.append(os.getcwd())

from src.core.models import FarmConfig
from src.core.engine import run_simulation, load_data

def test_engine():
    print("Loading data...")
    crops, systems = load_data()
    print(f"Loaded {len(crops)} crops and {len(systems)} systems.")
    
    print("Running Baseline Simulation...")
    config = FarmConfig(
        project_name="Test Farm",
        total_area_sqm=500,
        location_city="London",
        selected_crop_id="lettuce_iceberg",
        selected_system_id="hydroponic_nft",
        electricity_cost_per_kwh=0.20,
        labor_cost_per_hour=15.0
    )
    
    result = run_simulation(config)
    print("Simulation Successful!")
    print(f"ROI: {result.financials.roi_percent}%")
    print(f"Risk Score: {result.risk_score}")
    print(f"Recommendations: {result.recommendations}")
    
    if result.financials.roi_percent == 0 and result.financials.net_profit_annual != 0:
         print("WARNING: ROI is 0 but profit is not? Possible bug.")
         
    # Test Edge Case: Negative Profit
    print("\nRunning Stress Test (High Costs)...")
    config_stress = FarmConfig(
        project_name="Stress Test",
        total_area_sqm=100,
        location_city="Dubai",
        selected_crop_id="lettuce_iceberg",
        selected_system_id="hydroponic_nft",
        electricity_cost_per_kwh=1.0, # Very high
        labor_cost_per_hour=50.0
    )
    res_stress = run_simulation(config_stress)
    print(f"Stress ROI: {res_stress.financials.roi_percent}%")
    if res_stress.financials.net_profit_annual >= 0:
        print("FAIL: Expected negative profit for high costs.")
    else:
        print("PASS: Logic handled negative profit correctly.")

if __name__ == "__main__":
    test_engine()
