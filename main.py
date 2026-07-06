import json
import os
from pipeline import get_raw_html, BeautifulSoup
from processor import analyze_skills_data

def run_complete_pipeline(source_mode="local", target_url=None):
    print("==================================================")
    print("Starting SkillMap Zimbabwe Master Data Pipeline...")
    print("==================================================")
    
    # Step 1: Extract raw HTML from source (handles live or mock data automatically)
    raw_html = get_raw_html(source_type=source_mode, url=target_url)
    soup = BeautifulSoup(raw_html, "lxml")
    
    # Step 2: Grab the inner text of the portal to drop unnecessary HTML junk
    # Extract text content from your target wrapper div or body
    portal_body = soup.find(id="portal-data") or soup.body
    if not portal_body:
        print("[CRITICAL ERROR] Target container not found in extracted HTML.")
        return
        
    raw_text_payload = portal_body.get_text(separator="\n", strip=True)
    print(f"[INFO] Successfully prepared raw text segment ({len(raw_text_payload)} characters).")
    
    # Step 3: Run structured transformation via AI
    structured_json = analyze_skills_data(raw_text_payload)
    
    # Step 4: Final validation check and data handoff
    if structured_json:
        # Create output location if missing
        os.makedirs("data", exist_ok=True)
        output_filepath = os.path.join("data", "skills_matrix.json")
        
        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(structured_json, f, indent=4)
            
        print("==================================================")
        print(f"[PIPELINE COMPLETE] Live update pushed to: {output_filepath}")
        print("==================================================")
    else:
        print("[PIPELINE FAILURE] AI structural parsing phase failed.")

if __name__ == "__main__":
    # Keeping it local right now. When portal access drops, flip this to "live" and add the URL
    run_complete_pipeline(source_mode="local")