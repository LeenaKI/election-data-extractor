import google.genai as genai
from google.genai import types
import PIL.Image
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("LLM_MODEL", "gemini-2.5-flash")
INPUT_FOLDER = os.getenv("INPUT_FOLDER")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER")
TARGET_IMAGE_NAME = os.getenv("TARGET_IMAGE_NAME")

# Validate environment variables
if not all([API_KEY, INPUT_FOLDER, OUTPUT_FOLDER, TARGET_IMAGE_NAME]):
    raise ValueError("Missing required environment variables. Check your .env file.")

# 2. Setup File Paths
input_dir = Path(INPUT_FOLDER)
output_dir = Path(OUTPUT_FOLDER)

# Create output folder if it doesn't exist
output_dir.mkdir(parents=True, exist_ok=True)

# Combine folder path with the specific image name
img_file = input_dir / TARGET_IMAGE_NAME

if not img_file.exists() or not img_file.is_file():
    raise FileNotFoundError(f"Could not find the image at: {img_file}")

# 3. Initialize Client & Load Image
client = genai.Client(api_key=API_KEY)
image = PIL.Image.open(img_file)

# 4. Strict JSON Schema
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
                "total_used_ballot_papers ": {"type": "INTEGER"}
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
        "polling_agent_names": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
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

# 5. The Prompt
prompt = """
Extract all data from this Form EC 8A into the provided JSON schema. 

STRICT RULES:
1. METADATA CODES: Extract the numeric codes found in the boxes next to the State, Area Council, Ward, and Polling Unit. Keep them as strings to preserve any leading zeros.
2. POLLING AGENTS: Scan the entire 'NAME/SIGNATURE OF POLLING AGENT' column. 
   - If you see printed letters/text (a name), add it to the 'polling_agent_names' list.
   - If an entry is a signature (scribble), or empty, IGNORE IT.
   - This list is general and not tied to any specific party or row.
3. STATISTICS & RESULTS: Transcribe numbers exactly. Convert 'NIL' or empty boxes to 0. Ensure figures are integers.
4. SEAL: If the INEC official ink stamp is visible, set 'is_seal_present' to true, otherwise false.
5. INTEGRITY: Do not hallucinate. Do not guess illegible text.
"""

# 6. API Execution
print(f"Processing '{img_file.name}' using model '{MODEL_NAME}'...")

response = client.models.generate_content(
    model=MODEL_NAME,
    contents=[image, prompt],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=extraction_schema
    )
)

# 7. Save JSON to the Output Folder
# This takes 'election_form1.jpeg' and creates 'output_jsons/election_form1.json'
output_filename = output_dir / img_file.with_suffix('.json').name

data = json.loads(response.text)

with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print(f"Done. Data saved successfully to: {output_filename}")