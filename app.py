import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from src.core.engine import run_simulation, load_data
from src.core.models import FarmConfig

# Load env vars
load_dotenv()
from src.ai.advisor import VFAdvisor
from src.utils.pdf_generator import generate_blueprint_pdf

# Page Config
st.set_page_config(page_title="VF Planner Pro", layout="wide")

st.title("🌿 Vertical Farming Planner Pro")
st.markdown("### Advanced Simulation & Economics Engine")

# --- Sidebar Inputs ---
st.sidebar.header("Farm Configuration")

# Load Data
crops, systems = load_data()
crop_options = {c.name: c.id for c in crops}
system_options = {s.system_name: s.system_id for s in systems}

selected_crop_name = st.sidebar.selectbox("Select Crop", list(crop_options.keys()))
selected_system_name = st.sidebar.selectbox("Select Infrastructure", list(system_options.keys()))

area = st.sidebar.number_input("Total Area (sqm)", min_value=10, value=500, step=10)
city = st.sidebar.text_input("Location", "Dubai")

st.sidebar.subheader("Economics")
elec_cost = st.sidebar.number_input("Electricity ($/kWh)", 0.01, 1.0, 0.12)
labor_cost = st.sidebar.number_input("Labor ($/hr)", 1.0, 100.0, 15.0)

# Build Config Object
config = FarmConfig(
    project_name="Sim 1",
    total_area_sqm=area,
    location_city=city,
    selected_crop_id=crop_options[selected_crop_name],
    selected_system_id=system_options[selected_system_name],
    electricity_cost_per_kwh=elec_cost,
    labor_cost_per_hour=labor_cost
)

# --- Run Simulation ---
result = run_simulation(config)
fin = result.financials

# --- PDF Generation ---
@st.cache_data(show_spinner=False)
def get_pdf_report(config_data, result_data):
    # Wrapper to generate and read PDF bytes
    # We pass dicts or Pydantic models. Streamlit caches based on these inputs.
    pdf_file = generate_blueprint_pdf(config_data, result_data)
    with open(pdf_file, "rb") as f:
        return f.read(), pdf_file

# Generate PDF only when inputs change (cached)
pdf_bytes, pdf_filename = get_pdf_report(config, result)

st.sidebar.download_button(
    label="📄 Download Farm Blueprint (PDF)",
    data=pdf_bytes,
    file_name=pdf_filename,
    mime="application/pdf"
)

# --- Dashboard Layout ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Annual Revenue", f"${fin.revenue_annual:,.0f}")
col2.metric("Annual OpEx", f"${fin.opex_annual:,.0f}", delta_color="inverse")
col3.metric("Net Profit", f"${fin.net_profit_annual:,.0f}")
col4.metric("ROI", f"{fin.roi_percent}%", delta=f"{fin.roi_percent}%")

# Main Tabs
tab1, tab2, tab3 = st.tabs(["📊 Financial Analysis", "⚙️ Operations", "🤖 AI Advisor"])

with tab1:
    st.subheader("Financial Breakdown")
    
    # Charts
    chart_data = pd.DataFrame({
        "Category": ["Revenue", "OpEx", "Net Profit"],
        "Amount": [fin.revenue_annual, fin.opex_annual, fin.net_profit_annual]
    })
    st.bar_chart(chart_data.set_index("Category"))
    
    with st.expander("Detailed Metrics"):
        st.json(fin.dict())

with tab2:
    st.subheader("Operational Metrics")
    st.write(f"**Crop Selected:** {result.crop.name}")
    st.write(f"**Cycles per Year:** {result.cycles_per_year}")
    st.write(f"**Total Annual Yield:** {result.total_yield_annual_kg:,.1f} kg")
    
    st.info(f"💡 Recommended Light Hours: {result.crop.light_hours_per_day} hours/day")

with tab3:
    st.subheader("AI Strategic Advisor")
    advisor = VFAdvisor()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": advisor.generate_advice(result)}
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask about customized risks, crop choices, or market insights..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = advisor.generate_advice(result, prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

