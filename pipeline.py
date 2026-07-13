import os
import requests
import time
from bs4 import BeautifulSoup

# Define configuration constraints
MOCK_FILE_PATH = "mock_portal.html"
LIVE_PORTAL_URL = "https://vacancymail.co.zw/" 

def get_raw_html(source_type="live", url=LIVE_PORTAL_URL, max_pages=5):
    """
    Fetches HTML content. If in live mode, loops through multiple paginated
    pages of the job board and aggregates them to gather hundreds of jobs.
    """
    source_type = source_type.lower().strip()

    if source_type == "live":
        combined_html_blocks = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Loop through the pages to pull deep job listings
        for page_num in range(1, max_pages + 1):
            # FIXED: Updated URL syntax to match how the site processes query parameters (?page=)
            target_url = url if page_num == 1 else f"{url}jobs/?page={page_num}"
            print(f"[INFO] Scraped Page {page_num}/{max_pages}: {target_url}")
            
            try:
                response = requests.get(target_url, headers=headers, timeout=15)
                response.raise_for_status()
                combined_html_blocks.append(response.text)
                
                # Polite scraping delay to avoid hitting server rate limits too fast
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Live scrape failed on page {page_num}: {e}")
                # If page 1 fails completely, fallback. If later pages fail, keep what we have.
                if page_num == 1:
                    print("[FALLBACK] Switching to local mock file to prevent pipeline crash.")
                    return get_raw_html(source_type="local")
                break
                
        print(f"[SUCCESS] {len(combined_html_blocks)} pages of live data successfully retrieved.")
        # Wrap everything in a dummy root tag so BeautifulSoup can parse it seamlessly
        return "<html><body>" + "\n".join(combined_html_blocks) + "</body></html>"

    else:
        print(f"[INFO] Operating in LOCAL mode. Reading from: {MOCK_FILE_PATH}")
        
        if not os.path.exists(MOCK_FILE_PATH):
            print(f"[WARNING] {MOCK_FILE_PATH} not found. Generating a baseline skeleton file...")
            skeleton_html = """
            <!DOCTYPE html>
            <html>
            <head><title>Mock POTRAZ/ITU AI4I Challenge Portal</title></head>
            <body>
                <div id="portal-data">
                    <div class="job-post" data-sector="ICT" data-region="Harare">
                        <h3 class="title">Senior Cloud Infrastructure Architect</h3>
                        <p class="skills">Required: AWS Cloud Practitioner, Kubernetes containerization, Terraform Infrastructure-as-Code</p>
                    </div>
                    <div class="job-post" data-sector="Mining" data-region="Midlands">
                        <h3 class="title">Automation & Telemetry Systems Engineer</h3>
                        <p class="skills">Required: PLC Programming (Siemens), SCADA systems monitoring, IIOT sensor networks</p>
                    </div>
                </div>
            </body>
            </html>
            """
            with open(MOCK_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(skeleton_html.strip())
        
        with open(MOCK_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()

def parse_extracted_html(raw_html, source_type="live"):
    """
    Extracts text-rich job fields depending on whether we are parsing
    our structural local mock or parsing a chaotic live public layout.
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    scraped_data_block = []

    if source_type.lower().strip() == "live":
        # Broader target selectors to look for job board elements
        job_listings = soup.find_all(['a', 'div', 'li', 'tr'])
        
        valid_count = 0
        for element in job_listings:
            classes = " ".join(element.get('class', [])).lower()
            
            # Check if the element looks like a job card or row element
            if any(kw in classes for kw in ['job', 'vacancy', 'post', 'listing', 'title']):
                text_content = element.get_text(separator=" ", strip=True)
                
                # Filter out small navigation elements or duplicate entries
                if len(text_content) > 25 and text_content not in scraped_data_block:
                    valid_count += 1
                    scraped_data_block.append(f"POSTING {valid_count}: {text_content}")
                    
        print(f"[INFO] Extracted {len(scraped_data_block)} raw visual text points from all collected pages.")
        
        if not scraped_data_block:
            print("[WARN] Specific selectors missed. Returning raw contextual layout slice.")
            return soup.get_text(separator=" ", strip=True)[:3500]
    else:
        job_posts = soup.find_all(class_="job-post")
        print(f"[RESULT] Successfully parsed {len(job_posts)} entries from the local mock structure.")
        for idx, post in enumerate(job_posts, 1):
            title = post.find(class_="title").text if post.find(class_="title") else "N/A"
            skills = post.find(class_="skills").text if post.find(class_="skills") else "N/A"
            scraped_data_block.append(f"ENTRY #{idx}: TITLE: {title} | SKILLS NEEDED: {skills.strip()}")

    return "\n".join(scraped_data_block)

if __name__ == "__main__":
    print("--- RUNNING BACKEND SCRIPT TEST ---")
    
    RUN_MODE = "live" 
    
    raw_html_content = get_raw_html(source_type=RUN_MODE, max_pages=5)
    final_text_payload = parse_extracted_html(raw_html_content, source_type=RUN_MODE)
    
    print("\n--- SAMPLE OF PROCESSED PAYLOAD TRANSMITTED TO GEMINI ---")
    print(final_text_payload[:1000] + "\n... [TRUNCATED] ...")