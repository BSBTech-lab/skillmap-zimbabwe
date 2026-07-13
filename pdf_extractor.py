import sys
import fitz # PyMuPDF

def extract_pdf_text(pdf_path, output_txt_path, keywords):
    """Extracts targeted text from a PDF report based on relevant keywords."""
    print(f"[PDF EXTRACTOR] Ingesting report from: {pdf_path}")
    extracted_context = []
    
    try:
        with fitz.open(pdf_path) as doc:
            print(f"[PDF EXTRACTOR] Total document pages: {len(doc)}")
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text("text")
                
                # Filter pages to optimize context window space
                if any(kw in page_text.lower() for kw in keywords):
                    extracted_context.append(f"\n--- Report Page {page_num+1} ---\n{page_text}")
            
            full_text = "\n".join(extracted_context)
            
            # Save the extracted text to a text file for main.py to read later
            with open(output_txt_path, "w", encoding="utf-8") as out_file:
                out_file.write(full_text)
            print(f"[SUCCESS] Extracted text saved to: {output_txt_path}")
            
            return full_text[:4000] # Return preview cap
            
    except Exception as e:
        print(f"[ERROR] PDF Extraction failed for {pdf_path}: {e}")
        return ""

if __name__ == "__main__":
    print("--- RUNNING PDF EXTRACTION ---")
    
    # Check if a filename was typed in the terminal command line
    if len(sys.argv) > 1:
        target_pdf = sys.argv[1]
        
        # Branch based on which file you are running
        if "zimche" in target_pdf.lower():
            # ZIMCHE Target Keywords
            zimche_keywords = ["graduation", "graduate", "university", "enrolment", "degree", "diploma", "courses"]
            preview = extract_pdf_text(target_pdf, "zimche_report.txt", zimche_keywords)
        else:
            # Fallback/ZIMSTAT Keywords
            zimstat_keywords = ["unemployment", "labour force", "informal sector", "education", "skills"]
            preview = extract_pdf_text(target_pdf, "zimstat_report.txt", zimstat_keywords)
            
        print("\n--- TEXT PREVIEW (FIRST 1000 CHARACTERS) ---")
        print(preview[:1000] + "\n... [TRUNCATED] ...")
    else:
        print("[USAGE ERROR] Please provide a PDF filename. Example:")
        print("python pdf_extractor.py zimche_report.pdf")