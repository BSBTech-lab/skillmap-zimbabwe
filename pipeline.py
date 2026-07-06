import os
import requests
from bs4 import BeautifulSoup

# Define configuration constraints
MOCK_FILE_PATH = "mock_portal.html"
# Replace with the actual URL once the AI4I portal is unblocked
LIVE_PORTAL_URL = "https://example-ai4i-portal.gov.zw/data" 

def get_raw_html(source_type="local", url=None):
    """
    Fetches HTML content from either a local mock file or a live URL.
    Acts as a fail-safe toggle to keep backend development moving.
    """
    source_type = source_type.lower().strip()

    if source_type == "live":
        if not url:
            raise ValueError("Error: A valid URL must be provided for 'live' mode.")
        
        print(f"[INFO] Attempting to fetch live data from: {url}")
        try:
            # Emulate a standard browser header to avoid quick bot-blocking blocks
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            # 10-second timeout ensures the script doesn't hang indefinitely if the portal is slow
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() 
            print("[SUCCESS] Live data successfully retrieved.")
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Live fetch failed: {e}")
            print("[FALLBACK] Automatically switching to local mock file to prevent pipeline crash.")
            return get_raw_html(source_type="local")

    else:
        print(f"[INFO] Operating in LOCAL mode. Reading from: {MOCK_FILE_PATH}")
        
        # Guard rail: If the mock file doesn't exist, create a baseline structure automatically
        if not os.path.exists(MOCK_FILE_PATH):
            print(f"[WARNING] {MOCK_FILE_PATH} not found. Generating a baseline skeleton file...")
            skeleton_html = """
            <!DOCTYPE html>
            <html>
            <head><title>Mock AI4I Portal</title></head>
            <body>
                <div id="portal-data">
                    <div class="job-post" data-sector="ICT" data-region="Harare">
                        <h3 class="title">Cloud Security Architect</h3>
                        <p class="skills">Required: AWS, Kubernetes, Zero Trust Architecture</p>
                    </div>
                    <div class="job-post" data-sector="Mining" data-region="Manicaland">
                        <h3 class="title">Automation Systems Engineer</h3>
                        <p class="skills">Required: PLC Programming, Telemetry, SCADA</p>
                    </div>
                </div>
            </body>
            </html>
            """
            with open(MOCK_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(skeleton_html.strip())
        
        # Read and return the file content
        with open(MOCK_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()

if __name__ == "__main__":
    print("--- RUNNING BACKEND SCRIPT TEST ---")
    
    # 1. Test Local Execution (Your current daily driver)
    raw_html = get_raw_html(source_type="local")
    
    # 2. Parse the result with BeautifulSoup
    soup = BeautifulSoup(raw_html, "lxml") # 'lxml' is faster and more robust than html.parser
    
    # 3. Simple verification check to prove it works
    job_posts = soup.find_all(class_="job-post")
    print(f"[RESULT] Successfully parsed {len(job_posts)} entries from the HTML structure.")
    
    for idx, post in enumerate(job_posts, 1):
        title = post.find(class_="title").text if post.find(class_="title") else "N/A"
        skills = post.find(class_="skills").text if post.find(class_="skills") else "N/A"
        print(f"  -> Entry #{idx}: {title} | {skills.strip()}")
        
    print("\n--- TEST COMPLETE. READY FOR GEMINI API PIPELINE CONTEXT ---")