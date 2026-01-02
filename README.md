# 🌿 Vertical Farming Planner Pro

## 🌍 The Motivation: Why Vertical Farming?
As the global population surges towards 10 billion and urbanization accelerates, traditional agriculture faces unprecedented challenges. Arable land is shrinking, water scarcity is intensifying, and climate change is disrupting growing seasons.
![verticle farming diag-1](https://github.com/user-attachments/assets/44d2f1ca-c197-411c-993f-1cb927ca69c6)

**Vertical Farming** represents the inevitable evolution of agriculture. By moving farms into controlled indoor environments, we can:
- **Grow anywhere:** From urban centers to deserts.
- **Save water:** Uses up to 95% less water than traditional farming.
- **Ensure security:** Year-round production independent of weather.

However, the barrier to entry is high. Vertical farms are capital-intensive, technologically complex, and economically unforgiving. Many projects fail not because of biology, but because of bad math.

## 🚀 The Solution: VF Planner Pro
**VF Planner Pro** empowers entrepreneurs, investors, and researchers to **simulate the expenditure without spending a single penny.**

Our tool bridges the gap between agricultural potential and economic reality. It serves as a decision-support engine that helps you:
1.  **De-risk Investment:** Accurately simulate CapEx, OpEx, and ROI before laying a single brick.
2.  **Optimize Strategy:** Experiment with different crops (Leafy Greens vs. Herbs), infrastructure (Hydroponic vs. Aeroponic), and locations to find the profitable sweet spot.
3.  **AI-Driven Insights:** Leverage our integrated **AI Strategic Advisor** (powered by Google Gemini) to identify risks, analyze market viability, and get tailored recommendations.

## 🛠️ Installation & Usage Guide

Follow these steps to set up the project on your local machine.

### Prerequisites
- Python 3.9 or higher
- A Google Cloud API Key for Gemini (optional but recommended for AI features)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd vf_planner
```

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries using the generated requirements file.
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
To enable the AI Advisor functionalities, you need to set up your API key.

1.  Create a file named `.env` in the root directory.
2.  Add your Google Gemini API key:
    ```env
    GEMINI_API_KEY=your_actual_api_key_here
    ```

### 5. Run the Application
Launch the simulator using Streamlit.
```bash
streamlit run app.py
```

The application will open automatically in your default web browser (usually at `http://localhost:8501`).

## 📁 Project Structure
- `app.py`: Main application entry point.
- `src/`: Core logic and modules.
    - `core/`: Simulation engine and data models.
    - `ai/`: AI Advisor integration (Gemini).
    - `utils/`: Utilities like PDF generation.
- `data/`: Configuration data for crops and systems.

---
*Built for the future of food.*

