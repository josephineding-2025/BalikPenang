import sys
import os
import json

# Ensure the app/utils directory is in the path so imports work
# This is often needed when running from the root directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'utils'))

# 1. Import the necessary functions from your utilities
from pdf_parser import extract_text_from_pdf
from law_checker import split_text_into_clauses


# --- Configuration ---
# ⚠️ IMPORTANT: REPLACE WITH THE ACTUAL PATH TO YOUR TEST PDF
TEST_PDF_PATH = r"C:\Users\jojoe\Downloads\Contract-of-Employment_0.pdf" 
# Ensure you use 'r""' for a raw string to avoid SyntaxError on Windows paths.


def run_test_pipeline():
    print("--- Starting Contract Processing Pipeline ---")
    
    # 2. Extract Text from PDF
    print(f"Step 1: Extracting text from {TEST_PDF_PATH}...")
    
    extracted_text = extract_text_from_pdf(TEST_PDF_PATH)
    
    if extracted_text is None:
        print("❌ Extraction failed. Check PDF path and file access.")
        return
        
    print(f"✅ Extracted text successfully! (Length: {len(extracted_text)})")
    
    # 3. Split Text into Clauses
    print("\nStep 2: Splitting text into clauses...")
    
    clauses = split_text_into_clauses(extracted_text)
    
    if not clauses:
        print("❌ Splitting failed. No clauses found. Check contract format or regex pattern.")
        return
        
    print(f"✅ Successfully split text into {len(clauses)} clauses.")

    # 4. Display Results
    print("\n--- Clause Splitting Results (First 5 Clauses) ---")
    
    for i, clause in enumerate(clauses[:5]):
        # Display the clause number and the first 100 characters of the text
        print(f"[{i+1}] Clause {clause['number']}: {clause['text'][:100]}...")
        
    print("\n--- Full Structured Output Example (Clause 1) ---")
    print(json.dumps(clauses[0], indent=4))
    
    # Optional: You can then test the placeholder compliance check if needed
    # print("\nTesting Placeholder Compliance Check on Clause 1...")
    # from law_checker import check_clause_compliance
    # compliance = check_clause_compliance(clauses[0]['number'], clauses[0]['text'])
    # print(json.dumps(compliance, indent=4))


if __name__ == '__main__':
    run_test_pipeline()