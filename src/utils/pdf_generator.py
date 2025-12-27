from fpdf import FPDF
import datetime

def generate_blueprint_pdf(config, result):
    """
    Generates a PDF blueprint of the vertical farm simulation.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Colors & Fonts
    pdf.set_font('Arial', '', 12)
    primary_color = (46, 125, 50) # Dark Green
    
    # --- Title ---
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(*primary_color)
    pdf.cell(0, 15, 'Vertical Farming Strategic Blueprint', 0, 1, 'C')
    pdf.ln(5)
    
    # --- Executive Summary ---
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    pdf.cell(0, 10, f"Generated for {config.project_name} on {date_str}", 0, 1, 'C')
    pdf.ln(10)
    
    # --- Configuration Section ---
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, '1. Farm Configuration', 0, 1)
    
    pdf.set_font('Arial', '', 11)
    # Helper to add a row
    def add_row(label, value):
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(60, 8, label, 0, 0)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, str(value), 0, 1)

    add_row("Location:", config.location_city)
    add_row("Total Area:", f"{config.total_area_sqm} sqm")
    add_row("Selected Crop:", result.crop.name)
    add_row("Infrastructure:", result.infra.system_name)
    pdf.ln(5)
    
    # --- Financial Projections ---
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '2. Financial Projections (Annual)', 0, 1)
    
    fin = result.financials
    add_row("Total CapEx:", f"${fin.capex_total:,.2f}")
    add_row("Annual Revenue:", f"${fin.revenue_annual:,.2f}")
    add_row("Annual OpEx:", f"${fin.opex_annual:,.2f}")
    add_row("Net Profit:", f"${fin.net_profit_annual:,.2f}")
    
    pdf.set_text_color(*primary_color)
    add_row("ROI:", f"{fin.roi_percent}%")
    pdf.set_text_color(0, 0, 0)
    
    add_row("Payback Period:", f"{fin.payback_period_years} years")
    pdf.ln(5)
    
    # --- Operational Metrics ---
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '3. Operational Metrics', 0, 1)
    
    add_row("Annual Yield:", f"{result.total_yield_annual_kg:,.0f} kg")
    add_row("Grow Cycles per Year:", f"{result.cycles_per_year}")
    add_row("Daily Light Requirement:", f"{result.crop.light_hours_per_day} hours")
    
    # --- Recommendations ---
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '4. Strategic Recommendations', 0, 1)
    
    pdf.set_font('Arial', '', 11)
    for rec in result.recommendations:
        pdf.multi_cell(0, 8, f"- {rec}")
        
    if not result.recommendations:
        pdf.multi_cell(0, 8, "No specific warnings. The configuration looks solid.")

    # Output
    # Create a temporary filename
    filename = f"VF_Blueprint_{config.project_name.replace(' ', '_')}_{int(datetime.datetime.now().timestamp())}.pdf"
    pdf.output(filename)
    return filename
