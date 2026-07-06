import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# 1. Define the structural schema Bruce's frontend expects.
# Gemini will strictly adhere to this exact blueprint.
class RegionalImbalance(BaseModel):
    province: str = Field(description="The Zimbabwe province, e.g., Harare, Bulawayo, Manicaland")
    deficit_skills: List[str] = Field(description="Skills highly demanded by local employers but missing in candidates")
    surplus_skills: List[str] = Field(description="Skills commonly taught but low in current market demand")
    visibility_score: float = Field(description="Data alignment score from 0.0 (blind) to 1.0 (perfectly aligned)")

class SectorAnalysis(BaseModel):
    sector_name: str = Field(description="Economic sector, e.g., Mining, Agriculture, ICT")
    regional_breakdown: List[RegionalImbalance]

# 2. Check for the API Key safety rail
if not os.environ.get("GEMINI_API_KEY"):
    print("[ERROR] GEMINI_API_KEY environment variable not found!")
    print("Please run: $env:GEMINI_API_KEY='your_key' in your terminal before running this script.")
    exit(1)

# Initialize the Gemini Client
client = genai.Client()

def analyze_skills_data(raw_text_input: str):
    """Sends raw scraped text to Gemini and guarantees a strictly validated JSON response."""
    print("[INFO] Passing raw text payload to gemini-2.5-flash for structural mapping...")
    
    prompt = f"""
    You are the upstream data core for SkillMap Zimbabwe. Analyze the following raw scraped text 
    detailing industrial demand and educational pipeline output. Break it down into structured sectors 
    and regional imbalances, estimating an appropriate visibility alignment score.
    
    Raw Extracted Text:
    {raw_text_input}
    """
    
    try:
        # Use gemini-2.5-flash (optimized for fast, high-volume analytical structuring on the free tier)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SectorAnalysis, # Strict Pydantic enforcement
                temperature=0.1 # Low temperature eliminates conversational filler/hallucinations
            ),
        )
        
        # Parse text directly back into a clean python dictionary
        return json.loads(response.text)
        
    except Exception as e:
        print(f"[ERROR] Gemini processing failed: {e}")
        return None

if __name__ == "__main__":
    # Simulated input text combining our scraped data and local university mismatches
    SAMPLE_SCRAPED_DATA = """
    HARARE: Tech job board scraping shows 45 unfilled senior cloud infrastructure roles requiring AWS and Kubernetes. 
    Meanwhile, local IT certificate programs are graduating 300 students trained only in desktop support and local networking hardware.
    MUTARE: Mining operations reporting severe shortages in heavy machinery telemetry automation specialists. 
    Graduates applying hold general electrical diplomas but lack industrial automation frameworks.
    """
    
    print("--- RUNNING BACKEND PROCESSING TEST ---")
    structured_json = analyze_skills_data(SAMPLE_SCRAPED_DATA)
    
    if structured_json:
        print("[SUCCESS] Received clean, structured JSON from Gemini API:")
        print(json.dumps(structured_json, indent=4))
        
        # Save it directly as a physical asset for Bruce's frontend
        os.makedirs("data", exist_ok=True)
        with open("data/skills_matrix.json", "w", encoding="utf-8") as f:
            json.dump(structured_json, f, indent=4)
        print("[FILE SAVED] Written successfully to data/skills_matrix.json")