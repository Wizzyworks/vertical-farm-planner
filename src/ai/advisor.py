import os
from dotenv import load_dotenv
from google import genai
from ..core.models import SimulationResult

# Load env immediately to ensure key is available
load_dotenv()

class VFAdvisor:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Gemini Client: {e}")
        
    def generate_advice(self, sim_result: SimulationResult, user_query: str = None) -> str:
        """
        Generates advice based on simulation results using Google Gemini.
        """
        if not self.client:
            return "⚠️ **Gemini API Key missing.** Please add `GEMINI_API_KEY` to your `.env` file to enable the AI Advisor."

        # Construct Context
        fin = sim_result.financials
        context = (
            f"You are an expert Vertical Farming consultant. Analyze this farm configuration:\n"
            f"- Project: {sim_result.config.project_name}\n"
            f"- Location: {sim_result.config.location_city}\n"
            f"- Crop: {sim_result.crop.name}\n"
            f"- System: {sim_result.infra.system_name}\n"
            f"- Annual Revenue: ${fin.revenue_annual:,.2f}\n"
            f"- Annual OpEx: ${fin.opex_annual:,.2f}\n"
            f"- Net Profit: ${fin.net_profit_annual:,.2f}\n"
            f"- ROI: {fin.roi_percent}%\n"
            f"- Break Even: {fin.payback_period_years} years\n\n"
            f"Risk Score: {sim_result.risk_score}/100\n"
        )
        
        prompt = context
        if user_query:
            prompt += f"\nUser Question: {user_query}\nProvide a specific, strategic answer based on the data above."
        else:
            prompt += "\nProvide a strategic executive summary of the viability of this farm. strict to 3-4 bullet points."

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"❌ **AI Error**: {str(e)}"

    def get_system_prompt(self):
        return "You are an expert Vertical Farming consultant."
