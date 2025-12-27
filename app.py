import streamlit as st
import os
from dotenv import load_dotenv
from agents.simulator_agent import SimulatorAgent
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import pandas as pd

load_dotenv()

# Title
st.set_page_config(page_title="VF Planner MVP", layout="wide")
st.title("🌱 Vertical Farm Planner – Pre-Process Simulator")
st.write("Enter details below for personalized plan, yield/profit prediction, and cost estimate. (Powered by Gemini + Static Rules)")

# ---------- Canonical Value Maps ----------
SPACE_TYPE_MAP = {
    "Greenhouse": "greenhouse",
    "Warehouse": "warehouse"
}

BUDGET_MAP = {
    "Low (₹1-2L)": "low",
    "Medium (₹3-5L)": "medium",
    "High (₹5L+)": "high"
}

ENERGY_MAP = {
    "Solar": "solar",
    "Grid": "grid",
    "Hybrid": "hybrid"
}

CROP_PHASE_MAP = {
    "Phase 1: Leafy Greens": "phase1_leafy",
    "Phase 2: Strawberries/Dwarf Tomatoes": "phase2_strawberry"
}


# Main Screen Inputs (Columns for Clean Layout)
col1, col2 = st.columns(2)
with col1:
    location = st.text_input("Location (City/Zip, e.g., Kolkata)", "Kolkata")
    space_type = st.selectbox("Space Type", ["Greenhouse", "Warehouse"])
    space_size = st.number_input("Space Size (sq ft)", min_value=100, max_value=10000, value=500)
    crop_phase = st.selectbox("Crop Phase", ["Phase 1: Leafy Greens", "Phase 2: Strawberries/Dwarf Tomatoes"])
    budget_level = st.selectbox("Budget Level", ["Low (₹1-2L)", "Medium (₹3-5L)", "High (₹5L+)"])

with col2:
    energy_source = st.selectbox("Energy Source", ["Solar", "Grid", "Hybrid"])
    advanced_toggle = st.checkbox("Advanced Options")
    if advanced_toggle:
        medium_type = st.selectbox("Growing Medium", ["Hydro Trays NFT", "Aero Mist", "Soil + Biochar"])
        co2_target = st.selectbox("CO₂ Target (ppm)", ["None", "700", "1000"])

# Simulate Button
if st.button("Simulate Plan & Predictions"):
    inputs = {
        "location": location,
        "space_type": SPACE_TYPE_MAP[space_type],
        "space_size": space_size,
        "crop_phase": CROP_PHASE_MAP[crop_phase],
        "budget_level": BUDGET_MAP[budget_level],
        "energy_source": ENERGY_MAP[energy_source],
        "medium_type": medium_type if advanced_toggle else "Hydro Trays NFT",
        "co2_target": co2_target if advanced_toggle else "None"
    }

    
    with st.spinner("Simulating... (Rules + Gemini Magic)"):
        agent = SimulatorAgent()
        result = agent.simulate_plan(inputs)
    
    # Outputs on Main Screen
    st.header("Key Metrics")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Est. Yield (kg/year)", f"{result['yield']:.1f}")
    with col_b:
        st.metric("Est. Profit (₹/year)", f"{result['profit']:.0f}")
    with col_c:
        st.metric("Carbon Saved (kg CO₂eq)", f"{result['carbon_saved']:.1f}")
    
    st.header("Cost Breakdown")
    df_costs = pd.DataFrame(result['costs_breakdown'])
    st.table(df_costs)
    
    st.header("Personalized Plan")
    st.write(result['plan_details'])  # Bullets from Gemini
    
    st.header("ROI & What-If")
    st.write(f"5-Year NPV: ₹{result['roi']['npv']:.0f} | ROI: {result['roi']['pct']:.1f}%")
    st.write("What-If: Add PVT Solar → Yield +10%, Cost -20% (Recalc? Adjust inputs)")
    
    # Chart: 5-Year Profit Projection (Simple Line)
    years = list(range(1, 6))
    profits = [result['profit'] * y * 1.05 for y in years]  # 5% annual growth
    chart_data = pd.DataFrame({'Year': years, 'Profit (₹)': profits})
    st.line_chart(chart_data.set_index('Year'))
    
    # PDF Export
    if st.button("Export Plan PDF"):
        pdf_filename = "vf_plan.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        c.drawString(100, 750, "VF Plan Summary")
        y_pos = 700
        for key, val in result.items():
            c.drawString(100, y_pos, f"{key}: {val}")
            y_pos -= 20
        c.save()
        with open(pdf_filename, "rb") as f:
            st.download_button("Download PDF", f.read(), file_name=pdf_filename)

# Sidebar for Q&A (Doubts Clearing – Gemini from Box)
with st.sidebar:
    st.header("Ask Doubts?")
    qa_query = st.text_input("E.g., 'How to handle monsoon risks?'")
    if qa_query:
        agent = SimulatorAgent()
        qa_response = agent.handle_qa(qa_query)
        st.write(qa_response)