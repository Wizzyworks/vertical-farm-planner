# AI Vertical Farm Planner

## Problem
Urban Kolkata: Limited space, water scarcity, high fresh produce costs. Traditional farming fails in monsoons.

## Solution
ADK Agent uses Gemini (via Gen AI SDK) to analyze photos → Suggest stacked crops, plans, yields. Saves 90% water, boosts urban yields 30%.

## Tech Stack
- Google Gen AI SDK (latest, non-deprecated)
- ADK for agentic workflows (autonomous analysis)
- Streamlit for UI
- W&B for experiment tracking

## Run Locally
1. `pip install -r requirements.txt`
2. Set .env with GOOGLE_API_KEY
3. `streamlit run app.py`

## Demo Flow
- Upload photo → Agent runs Gemini vision/text → JSON plan → Dashboard metrics.

## Impact
- Market: $3B CEA by 2034
- Scalable to Vertex AI for prod.

*First outside-college hackathon entry – Let's crush it! 🚀*