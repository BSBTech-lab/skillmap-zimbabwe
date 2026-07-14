import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# 1. Define sub-schema to handle the weighted skill object
class DeficitSkill(BaseModel):
    skill: str = Field(description="The specific high-demand skill or career profile experiencing a gap")
    mismatch_index: int = Field(description="Calculated severity score from 1 to 100. If explicit metrics aren't present, scale this dynamically based on the frequency and urgency of the job postings in the text.")

# 2. Define structural schema
class RegionalImbalance(BaseModel):
    province: str = Field(description="The Zimbabwe province, e.g., Harare, Bulawayo, Manicaland, Midlands")
    deficit_skills: List[DeficitSkill] = Field(description="List of skills highly demanded by local employers but missing in candidates, with mismatch indices")
    surplus_skills: List[str] = Field(description="Skills commonly taught but low in current market demand")
    visibility_score: float = Field(description="Data alignment score from 0.0 (blind) to 1.0 (perfectly aligned)")

class SectorAnalysis(BaseModel):
    sector_name: str = Field(description="Economic sector, e.g., Mining, Agriculture, ICT, Renewable Energy")
    regional_breakdown: List[RegionalImbalance]

class NationalSkillsResponse(BaseModel):
    skills_matrix: List[SectorAnalysis] = Field(description="List of all analyzed economic sectors across Zimbabwe")

if not os.environ.get("GEMINI_API_KEY"):
    print("[ERROR] GEMINI_API_KEY environment variable not found!")
    exit(1)

client = genai.Client()

def analyze_skills_data(raw_text_input: str):
    print("[INFO] Passing raw text payload to gemini-2.5-flash for structural mapping...")
    
    # Updated prompt with explicit scaling instructions for raw listings
    prompt = f"""
    You are the upstream data core for SkillMap Zimbabwe. Analyze the following raw scraped text 
    detailing industrial demand and job listings. 
    
    CRITICAL INSTRUCTION FOR MISMATCH_INDEX:
    Count how frequently specific roles or fields appear in the listings. Roles that appear repeatedly 
    represent a wider, more severe market deficit. Assign a dynamic 'mismatch_index' scaled from 1 to 100 
    proportionate to this frequency and market urgency (e.g., highly repeated roles or specialized roles 
    like CyberSecurity or Cisco Network Engineering should be scored significantly higher, between 60-95, 
    while rare or entry-level positions should scale lower). Do not assign a uniform score across skills.
    
    Raw Extracted Text:
    {raw_text_input}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=NationalSkillsResponse, 
                temperature=0.2 # Small bump to allow comparative numeric assignment
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"[ERROR] Gemini processing failed: {e}")
        return None