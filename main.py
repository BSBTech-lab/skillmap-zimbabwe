import os
import json
# Import your web scraping tools
from pipeline import get_raw_html, parse_extracted_html
# Import your Gemini processor
from processor import analyze_skills_data

def run_master_pipeline():
    print("=" * 50)
    print("RUNNING FINAL COMBINED DEMAND + SUPPLY + EDUCATION PIPELINE (WEIGHTED ENGINE)")
    print("=" * 50)
    
    # 1. Fetch live HTML from Vacancy Mail (DEMAND SIDE)
    raw_html_content = get_raw_html(source_type="live")
    demand_text = parse_extracted_html(raw_html_content, source_type="live")
    
    # 2. Load structural labor supply text from ZIMSTAT text extraction
    supply_text = ""
    if os.path.exists("zimstat_report.txt"):
        with open("zimstat_report.txt", "r", encoding="utf-8") as f:
            supply_text = f.read()
    else:
        print("[WARNING] zimstat_report.txt not found. Run pdf_extractor.py first.")

    # 3. Load tertiary education graduate data from ZIMCHE text extraction
    education_text = ""
    if os.path.exists("zimche_report.txt"):
        with open("zimche_report.txt", "r", encoding="utf-8") as f:
            education_text = f.read()
    else:
        print("[WARNING] zimche_report.txt not found. Run pdf_extractor.py first.")
    
    if not demand_text and not supply_text and not education_text:
        print("[ABORT] No source data could be retrieved. Keeping old dataset safe.")
        return
        
    # 4. Combine all three sources into one master text layout prompt for Gemini
    master_ai_payload = f"""
    --- DEMAND SIDE SOURCE DATA (LIVE VACANCIES FROM VACANCY MAIL) ---
    {demand_text if demand_text else "No vacancy text retrieved."}
    
    --- SUPPLY SIDE SOURCE DATA (ZIMSTAT LABOUR DISPARITIES SURVEYS) ---
    {supply_text if supply_text else "No ZIMSTAT text retrieved."}

    --- ACADEMIC SUPPLY & CURRICULUM DATA (ZIMCHE GRADUATION STATISTICS) ---
    {education_text if education_text else "No ZIMCHE text retrieved."}
    
    --- ANALYSIS METHODOLOGY & INSTRUCTIONS ---
    You are an expert labor economist and backend data engineer specializing in Zimbabwe's workforce.
    Analyze the live job demands, ZIMSTAT labor gaps, and ZIMCHE university graduation trends together.
    
    CRITICAL INSTRUCTION:
    You MUST extract skills data and group them into the following 7 key sectors to match our dashboard layout:
    1. Agriculture & Food Systems
    2. Medical & Health Sciences
    3. Engineering & Technology
    4. Commerce, Business & Finance
    5. Applied Arts & Humanities
    6. ICT & Computer Science
    7. Tourism & Hospitality

    For each of these sectors, analyze the text to calculate a dynamic 'mismatch_index' (1 to 100) based on the ratio of demand to supply:
    
    1. CRITICAL LABOR GAPS (Index 75 - 100):
       Fields where live market vacancies or ZIMSTAT metrics show high active hiring demand, but ZIMCHE data indicates near-zero graduate output from matching tertiary courses.
       
    2. EDUCATIONAL OVERPRODUCTION / SURPLUS (Index 75 - 100):
       Fields where ZIMCHE statistics indicate thousands of annual graduates from specific academic courses, but live vacancy listings and ZIMSTAT records show near-zero active employment slots.
       
    3. MODERATE DISCONNECT (Index 40 - 74):
       Fields where graduate output is present but misaligned with industry specifications, or tracking mild supply/demand friction.
       
    4. BALANCED PIPELINES (Index 1 - 39):
       Stable career tracts where corporate vacancies tightly align with institutional graduate output volumes.
       
    Output the result strictly in valid JSON format matching the schema below. Do not default to 1 for everything; compute the true logical delta between the supply text and the demand text. Do not include markdown code block wrappers (```json) in your final response string.

    --- EXPECTED JSON SCHEMA STRUCTURE ---
    {{
        "skills_matrix": [
            {{
                "sector_name": "Agriculture & Food Systems",
                "regional_breakdown": [
                    {{
                        "location": "Harare",
                        "deficit_skills": [
                            {{
                                "skill": "Agronomy & Soil Chemistry",
                                "mismatch_index": 88
                            }}
                        ],
                        "surplus_skills": [
                            {{
                                "course": "General Agriculture Theory",
                                "mismatch_index": 70
                            }}
                        ]
                    }}
                ]
            }}
        ]
    }}
    """
    
    # === ADDED DEBUGGING SECTION: VIEW THE OUTBOUND API TEXT ===
    print("\n" + "#" * 30 + " OUTBOUND PAYLOAD PREVIEW FOR GEMINI " + "#" * 30)
    print(master_ai_payload[:2000]) 
    if len(master_ai_payload) > 2000:
        print(f"\n... [TRUNCATED - {len(master_ai_payload) - 2000} MORE CHARACTERS IN PAYLOAD] ...")
    print("#" * 97 + "\n")
    # ==========================================================
    
    print("[INFO] Sending multi-source combined payload to Gemini engine...")
    
    # 5. Pass the combined payload to Gemini to categorize and structure 
    structured_data = analyze_skills_data(master_ai_payload)
    
    if structured_data:
        # PATH FIXED: Saving directly to the frontend's data folder!
        output_path = os.path.join("data", "skills_matrix.json")
        
        # Ensure the data directory exists
        os.makedirs("data", exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(structured_data, f, indent=4)
            
        print("=" * 50)
        print(f"[PIPELINE SUCCESS] Multi-source weighted database asset rewritten: {output_path}")
        print("=" * 50)
    else:
        print("[ERROR] Engine failed to parse structural layout.")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("[ERROR] Set your GEMINI_API_KEY environment variable first!")
    else:
        run_master_pipeline()