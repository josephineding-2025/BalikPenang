import sys
import os
import json
import pandas as pd
from typing import List, Dict, Union
from jamaibase import JamAI, types as t

# --- 1. SETUP AND PATH CONFIGURATION ---

# Adjust the path to import utilities from app/utils/
# Assuming this script is run from the project root (BalikPenang/)
UTILITY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'utils')
if UTILITY_PATH not in sys.path:
    sys.path.append(UTILITY_PATH)

try:
    # Import your utility functions
    from pdf_parser import extract_text_from_pdf
    from law_checker import split_text_into_clauses
except ImportError as e:
    print(f"FATAL ERROR: Could not import utilities. Check your file path configuration. Error: {e}")
    sys.exit(1)


# --- 2. CREDENTIALS AND CLIENT INITIALIZATION ---

# Read credentials from environment variables (BEST PRACTICE for local testing)
JAMAI_PROJECT_ID = os.environ.get("JAMAI_PROJECT_ID")
JAMAI_PAT = os.environ.get("JAMAI_PAT")
LAW_KB_NAME = "labour_law"

# Path to the PDF you want to test (MUST BE UPDATED)
TEST_PDF_PATH = r"C:\Users\jojoe\Downloads\Contract-of-Employment_0.pdf" 
# Use 'r"..."' (raw string) for Windows paths!

# Initialize JamAI Client (without using Streamlit's methods)
JAMAI_CLIENT = None
try:
    if JAMAI_PROJECT_ID and JAMAI_PAT:
        JAMAI_CLIENT = JamAI(
            project_id=JAMAI_PROJECT_ID,
            token=JAMAI_PAT
        )
        print("✅ JamAI Client Initialized (using Environment Variables).")
    else:
        print("❌ JamAI Client Initialization Skipped: JAMAI_PROJECT_ID or JAMAI_PAT env vars are missing.")
except Exception as e:
    print(f"❌ Error during JamAI client initialization: {e}")
    sys.exit(1)


# --- 3. CORE COMPLIANCE CHECK FUNCTION (Modified from law_checker) ---

def check_clause_compliance_core(
    clause_number: str, 
    clause_text: str
) -> Dict[str, Union[str, bool]]:
    """
    Checks a single clause compliance using JamAI RAG (Terminal-friendly version).
    """
    if JAMAI_CLIENT is None:
        return {"is_compliant": "Error", "reasoning": "JamAI Client not ready."}

    # System prompt remains the same
    system_prompt = (
        "You are an expert legal compliance officer checking a contract. "
        "Analyze the provided CONTRACT CLAUSE against the CONTEXT from the labour law. "
        "State clearly if the clause is Compliant, Non-Compliant, or Partially Compliant. "
        "If Non-Compliant, explain why and cite the relevant 'Title' or 'Text' from the CONTEXT. "
        "Keep the reasoning concise."
    )
    user_prompt = f"Contract Clause {clause_number}: {clause_text}"

    try:
        # NOTE: This API call connects to the knowledge base created by Teammate 2
        response = JAMAI_CLIENT.chat.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            tools=[{"name": LAW_KB_NAME}] 
        )
        
        reasoning = response.text
        
        if "non-compliant" in reasoning.lower() or "not compliant" in reasoning.lower():
            compliance_status = "Non-Compliant"
        elif "partially compliant" in reasoning.lower():
            compliance_status = "Partially Compliant"
        else:
            compliance_status = "Compliant"

        return {
            "is_compliant": compliance_status,
            "reasoning": reasoning
        }

    except Exception as e:
        return {
            "is_compliant": "API Error",
            "reasoning": f"JamAI API call failed: {str(e)}"
        }

# --- 4. MAIN EXECUTION PIPELINE ---

def run_test_pipeline():
    """Runs the full pipeline: PDF -> Split -> Compliance Check."""
    
    print("\n--- Starting Contract Processing Pipeline ---")
    
    # 4.1. Extract Text from PDF
    print(f"Step 1: Extracting text from {TEST_PDF_PATH}...")
    extracted_text = extract_text_from_pdf(TEST_PDF_PATH)
    
    if extracted_text is None or not extracted_text.strip():
        print("❌ Extraction failed or returned empty text. Exiting.")
        return
        
    print(f"✅ Extracted text successfully! (First 200 chars: {extracted_text[:200]}...)")
    
    # 4.2. Split Text into Clauses
    print("\nStep 2: Splitting text into clauses...")
    clauses = split_text_into_clauses(extracted_text)
    
    if not clauses:
        print("❌ Splitting failed. No clauses found.")
        return
        
    print(f"✅ Successfully split text into {len(clauses)} clauses.")

    # 4.3. Run Compliance Checks
    print("\nStep 3: Running Clause Compliance Checks (using JamAI RAG)...")
    
    if JAMAI_CLIENT is None:
        print("🛑 Cannot run compliance check: JamAI client not available.")
        return

    results = []
    
    for i, clause in enumerate(clauses):
        print(f"Checking clause {i+1}/{len(clauses)}: {clause['number']}...")
        
        compliance_check = check_clause_compliance_core(
            clause['number'], 
            clause['text']
        )
        
        results.append({
            "Clause": clause['number'],
            "Status": compliance_check['is_compliant'],
            "Reasoning": compliance_check['reasoning']
        })
        
    # 4.4. Display Results
    print("\n--- FINAL ANALYSIS RESULTS (Teammate 5 Output) ---")
    
    df = pd.DataFrame(results)
    print(df.to_markdown(index=False)) # Use markdown table format for clear output
    
    print("\n---------------------------------------------------")
    print("Full process complete. Check the output above.")
    

if __name__ == '__main__':
    # You MUST ensure `pdf_parser.py` and `law_checker.py` are saved in app/utils/
    # And you MUST update the TEST_PDF_PATH variable above.
    run_test_pipeline()