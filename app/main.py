import fitz  # PyMuPDF
import re
import tempfile
import os
from typing import Optional, Union

# Define the acceptable file type from Streamlit/Python's standard library
from io import BytesIO

# Change the function to accept either a path (for testing) or a file object (for Streamlit)
def extract_text_from_pdf(file_source: Union[str, BytesIO]) -> Optional[str]:
    """
    Extracts and cleans text from a PDF file. Accepts a file path or a BytesIO object (from Streamlit).
    """
    text = ""
    temp_file_path = None

    try:
        if isinstance(file_source, str):
            # Case 1: Local file path (for testing)
            pdf_path = file_source
        elif isinstance(file_source, BytesIO):
            # Case 2: Streamlit uploaded file object
            # Write the bytes content to a temporary file, as fitz often needs a physical path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_source.read())
                pdf_path = tmp.name
                temp_file_path = tmp.name
        else:
            print("Error: Invalid file source provided.")
            return None

        # 1. Open the document using the path (PyMuPDF core logic)
        doc = fitz.open(pdf_path)
        
        # 2. Iterate through pages and extract text
        for page in doc:
            text += page.get_text("text") 
            
        doc.close()
            
        # 3. Clean up the text (same as before)
        cleaned_text = re.sub(r'[ \t]+', ' ', text)
        cleaned_text = re.sub(r'([^\n])\n([^\n])', r'\1 \2', cleaned_text)
        cleaned_text = re.sub(r'\n{2,}', '\n\n', cleaned_text).strip()
        
        return cleaned_text
        
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    finally:
        # 4. CRITICAL: Clean up the temporary file if one was created
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# ... (remove or adjust the __main__ block for local testing only)