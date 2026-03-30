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

# Validate environment variables
if not all([API_KEY, INPUT_FOLDER, OUTPUT_FOLDER]):
    raise ValueError("Missing required environment variables. Check your .env file.")

# 2. Setup Directories
input_path = Path(INPUT_FOLDER)
output_path = Path(OUTPUT_FOLDER)

# Ensure the output folder exists (creates it if it doesn't)
output_path.mkdir(parents=True, exist_ok=True)

if not input_path.exists() or not input_path.is_dir():
    raise NotADirectoryError(f"The input folder '{INPUT_FOLDER}' does not exist.")

# 3. Initialize Client
client = genai.Client(api_key=API_KEY)

# 4. Strict JSON Schema (Unchanged)
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

# 5. Prompt (Unchanged)
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

# 6. Batch Processing Loop
# We only want to process actual images, ignoring hidden files like .DS_Store
valid_extensions = {".jpg", ".jpeg", ".png"}

print(f"Starting batch process on folder: {input_path}")
print(f"Saving results to: {output_path}\n" + "-"*30)

success_count = 0
error_count = 0

for img_file in input_path.iterdir():
    # Skip directories or non-image files
    if not img_file.is_file() or img_file.suffix.lower() not in valid_extensions:
        continue
        
    print(f"Processing: {img_file.name}...")
    
    # Use a try/except block so one bad image doesn't stop the whole script
    try:
        image = PIL.Image.open(img_file)
        
        # API Call
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=extraction_schema
            )
        )
        
        # Determine output filename (e.g., input_images/form1.jpg -> output_jsons/form1.json)
        output_filename = output_path / img_file.with_suffix('.json').name
        
        # Parse and save
        data = json.loads(response.text)
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        print(f"  [SUCCESS] Saved to {output_filename.name}")
        success_count += 1
        
    except Exception as e:
        print(f"  [ERROR] Failed to process {img_file.name}: {e}")
        error_count += 1

print("-" * 30)
print(f"Batch processing complete! Successfully processed {success_count} files. Errors: {error_count}.")