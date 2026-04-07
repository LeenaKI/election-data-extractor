import streamlit as st
import google.genai as genai
from google.genai import types
import PIL.Image
import io
import json

# --- Page Configuration ---
st.set_page_config(page_title="Form EC 8A Extractor", layout="wide")

st.title("Form EC 8A Data Extractor")
st.markdown("Upload images of Form EC 8A to extract structured JSON data using Gemini.")

# --- Sidebar for API Key ---
with st.sidebar:
    st.header("Authentication")
    user_api_key = st.text_input("Enter your Gemini API Key", type="password")
    model_choice = st.selectbox("Select Model", ["gemini-3.1-pro-preview"], index=0)
    
    st.divider()
    st.info("The API key is used only for this session and is not stored.")

# --- Schema & Prompt (Original Logic) ---
extraction_schema = {
    "type": "OBJECT",
    "properties": {
        "metadata": {
            "type": "OBJECT",
            "properties": {
                "state": {"type": "STRING"},
                "state_code": {"type": "STRING"},
                "area_council": {"type": "STRING"},
                "area_council_code": {"type": "STRING"},
                "ward": {"type": "STRING"},
                "ward_code": {"type": "STRING"},
                "polling_unit": {"type": "STRING"},
                "polling_unit_code": {"type": "STRING"},
                "serial_number": {"type": "STRING"}
            },
            "required": ["state", "area_council", "ward", "polling_unit", "serial_number"]
        },
        "statistics": {
            "type": "OBJECT",
            "properties": {
                "registered_voters": {"type": "INTEGER"},
                "accredited_voters": {"type": "INTEGER"},
                "ballots_issued": {"type": "INTEGER"},
                "unused_ballots": {"type": "INTEGER"},
                "spoiled_ballots": {"type": "INTEGER"},
                "rejected_ballots": {"type": "INTEGER"},
                "total_valid_votes": {"type": "INTEGER"},
                "total_used_ballot_papers": {"type": "INTEGER"}
            }
        },
        "results": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "sn": {"type": "INTEGER"},
                    "party": {"type": "STRING"},
                    "votes_figures": {"type": "INTEGER"},
                    "votes_words": {"type": "STRING"}
                }
            }
        },
        "polling_agent_names": {"type": "ARRAY", "items": {"type": "STRING"}},
        "certification": {
            "type": "OBJECT",
            "properties": {
                "presiding_officer_name": {"type": "STRING"},
                "date": {"type": "STRING"}
            }
        },
        "is_seal_present": {"type": "BOOLEAN"}
    }
}

prompt = """
Extract all data from this Form EC 8A into the provided JSON schema. 

STRICT RULES:
1. METADATA CODES: Extract the numeric codes found in the boxes next to the State, Area Council, Ward, and Polling Unit. Keep them as strings.
2. POLLING AGENTS: Scan 'NAME/SIGNATURE OF POLLING AGENT' column. Add printed names to list, ignore scribbles/signatures.
3. STATISTICS & RESULTS: Transcribe numbers exactly. Convert 'NIL' or empty boxes to 0.
4. SEAL: Set 'is_seal_present' to true if the INEC official ink stamp is visible.
5. INTEGRITY: Do not hallucinate.
"""

# --- Main App Logic ---
uploaded_files = st.file_uploader("Choose Form EC 8A images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    if not user_api_key:
        st.error("Please provide a Gemini API Key in the sidebar.")
    else:
        try:
            # Initialize Client with User Key
            client = genai.Client(api_key=user_api_key)
            
            for uploaded_file in uploaded_files:
                with st.expander(f"📄 Processing: {uploaded_file.name}", expanded=True):
                    col1, col2 = st.columns([1, 1])
                    
                    # Read and Display Image
                    image_bytes = uploaded_file.read()
                    image = PIL.Image.open(io.BytesIO(image_bytes))
                    col1.image(image, caption="Uploaded Form", use_container_width=True)
                    
                    # Process with Gemini
                    with st.spinner("Analyzing with Gemini..."):
                        response = client.models.generate_content(
                            model=model_choice,
                            contents=[image, prompt],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=extraction_schema
                            )
                        )
                        
                        # Parse and Show Results
                        data = json.loads(response.text)
                        col2.success("Data Extracted!")
                        col2.json(data)
                        
                        # Download Button for individual file
                        json_str = json.dumps(data, indent=4)
                        col2.download_button(
                            label="Download JSON",
                            data=json_str,
                            file_name=f"{uploaded_file.name.split('.')[0]}.json",
                            mime="application/json"
                        )
                        
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.info("Awaiting file upload...")
