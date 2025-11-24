import streamlit as st
import io 
import pandas as pd

# CRITICAL: Import functions from your utility files (Teammate 5's responsibilities)
try:
    from app.utils.pdf_parser import extract_text_from_pdf
    from app.utils.law_checker import check_full_contract
except ImportError as e:
    st.error(f"Failed to import utilities. Check your file structure and Python path. Error: {e}")
    st.stop()


# --- STREAMLIT UI CONFIGURATION ---

st.set_page_config(
    page_title="Legal Compliance Analyzer",
    layout="wide"
)

st.title("⚖️ Contract Compliance Analyzer")
st.markdown(
    "Upload an employment contract PDF to check clause-by-clause compliance against the **Labour Law Knowledge Base** (Akta Kerja 1955, etc.)."
)

# --- FILE UPLOADER (Teammate 3 UI) ---

uploaded_file = st.file_uploader(
    "Choose a Contract PDF", 
    type=['pdf'], 
    help="Upload the contract text to check for compliance."
)

# --- PROCESSING LOGIC ---

if uploaded_file is not None:
    # 1. Read the uploaded file bytes
    file_bytes = io.BytesIO(uploaded_file.read())
    
    # 2. Extract Text (Calls pdf_parser.py)
    with st.spinner('1/3: Extracting and cleaning text from PDF...'):
        extracted_text = extract_text_from_pdf(file_bytes)
    
    if extracted_text and st.button("Start Compliance Check", type="primary"):
        
        st.subheader("2/3: Extracted Contract Text (for QA)")
        with st.expander("Click to view full extracted text"):
            # Display text to allow the user (and Teammate 4) to verify source data
            st.text_area(
                "Full Text", 
                extracted_text, 
                height=300,
                key="extracted_text_area"
            )
        
        # 3. Start Compliance Analysis (Calls law_checker.py)
        st.subheader("3/3: Compliance Analysis Results")
        
        # This function handles splitting the text into clauses and running JamAI RAG checks
        analysis_results = check_full_contract(extracted_text)
        
        if analysis_results:
            # 4. Display results in a styled DataFrame
            df = pd.DataFrame(analysis_results)
            
            # Function to apply color based on compliance status
            def color_status(val):
                if 'non-compliant' in str(val).lower():
                    return 'background-color: #ffcccc' # Light Red
                elif 'compliant' in str(val).lower():
                    return 'background-color: #ccffcc' # Light Green
                else:
                    return 'background-color: #ffffcc' # Light Yellow

            # Apply styling to the status column and configure table view
            styled_df = df[['number', 'status', 'reasoning']].style.applymap(color_status, subset=['status'])
            
            st.dataframe(
                styled_df, 
                use_container_width=True,
                column_config={
                    "number": st.column_config.TextColumn("Clause", width="small"),
                    "status": st.column_config.TextColumn("Status", width="small"),
                    "reasoning": st.column_config.Column("AI Reasoning & Citation", width="large"),
                }
            )

        # Teammate 3 - Download Functionality Placeholder
        # NOTE: Contract generation is handled by Teammate 4, but the button goes here.
        st.divider()
        st.info("Download/Correction functionality (Teammate 4) goes here.")
        
    elif extracted_text is None:
        st.error("Error: Failed to extract text from the PDF. The file may be corrupt or scanned (requiring OCR).")