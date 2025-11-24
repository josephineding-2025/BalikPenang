import re
from typing import List, Dict, Union
import streamlit as st
from jamaibase import JamAI, types as t
import pandas as pd

# The ID of the Knowledge Base table created by Teammate 2
LAW_KB_NAME = "labour_law" 

# --- Configuration & Initialization ---

# Initialize JamAI Client using Streamlit Secrets
JAMAI_CLIENT = None
try:
    if "jamai" in st.secrets and "project_id" in st.secrets.jamai and "token" in st.secrets.jamai:
        JAMAI_CLIENT = JamAI(
            project_id=st.secrets.jamai.project_id,
            token=st.secrets.jamai.token
        )
    else:
        # st.error is called if we are running in a Streamlit environment
        st.error("JamAI Client failed to initialize: Missing credentials in Streamlit Secrets.")
except Exception as e:
    st.error(f"Error initializing JamAI client: {e}")


# --- Utility Function: Clause Splitting ---

def split_text_into_clauses(full_text: str) -> List[Dict[str, str]]:
    """
    Splits the full contract text into individual clauses based on common hierarchical 
    numbering patterns (e.g., 1., 2.1., 3.1.1.).
    """
    if not full_text:
        return []
        
    # Regex pattern targeting hierarchical numbering 
    CLAUSE_PATTERN = r"^(\s*(\d+\.?\d*\.?\d*\.)\s+)"
    
    parts = re.split(CLAUSE_PATTERN, full_text, flags=re.MULTILINE)
    
    clauses = []
    
    for i in range(3, len(parts), 3):
        clause_number = parts[i-1].strip()
        clause_text = parts[i].strip()
        
        if clause_number and clause_text:
            clauses.append({
                "number": clause_number,
                "text": clause_text
            })
            
    return clauses

# --- Core Function: Law Checking / RAG ---

def check_clause_compliance(
    clause_number: str, 
    clause_text: str,
) -> Dict[str, Union[str, bool]]:
    """
    Checks a single contract clause against the indexed law sections using JamAI's RAG capabilities.
    """
    if JAMAI_CLIENT is None:
        return {
            "is_compliant": "Error",
            "reasoning": "JamAI Client not initialized."
        }

    # 1. Define the RAG Query / System Prompt
    system_prompt = (
        "You are an expert legal compliance officer checking a contract. "
        "Analyze the provided CONTRACT CLAUSE against the CONTEXT provided by the legal knowledge base. "
        "Determine if the clause is compliant, partially compliant, or non-compliant. "
        "Always cite the relevant law section from the CONTEXT that supports your finding. "
        "If no relevant context is found, state that."
    )
    
    user_prompt = f"CONTRACT CLAUSE {clause_number}: {clause_text}"

    # 2. Call JamAI's completion/chat endpoint with RAG enabled
    try:
        response = JAMAI_CLIENT.chat.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            tools=[{"name": LAW_KB_NAME}] 
        )
        
        # 3. Process the LLM's Response
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
        st.error(f"JamAI API call failed for Clause {clause_number}.")
        return {
            "is_compliant": "API Error",
            "reasoning": f"JamAI API call failed: {str(e)}"
        }


# --- Main Orchestration Function ---

def check_full_contract(full_contract_text: str) -> List[Dict]:
    """
    Splits the contract and checks every clause for compliance.
    """
    st.subheader("1. Splitting Contract into Clauses")
    
    clauses = split_text_into_clauses(full_contract_text)
    
    if not clauses:
        st.warning("Could not automatically split text into numbered clauses.")
        return []

    st.success(f"Found {len(clauses)} potential clauses. Analyzing...")
    
    results = []
    
    # Use Streamlit's progress bar for a better UX
    progress_bar = st.progress(0, text="Analyzing Clause 1...")
    
    for i, clause in enumerate(clauses):
        # Update progress text for better user experience
        progress_text = f"Analyzing Clause {clause['number']}..."
        progress_bar.progress((i + 1) / len(clauses), text=progress_text)

        # Check the compliance of the clause
        compliance_check = check_clause_compliance(
            clause['number'], 
            clause['text']
        )
        
        results.append({
            "number": clause['number'],
            "text": clause['text'],
            "status": compliance_check['is_compliant'],
        })