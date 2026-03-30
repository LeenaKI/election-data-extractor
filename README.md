# Election Form Data Extractor

An AI-powered batch processing tool designed to digitize and extract data from Nigerian Election Forms (Form EC 8A). 

By utilizing the **Google Gemini 3.1 Pro Multimodal API**, this tool bypasses the limitations of traditional OCR by accurately transcribing messy handwriting, parsing complex tables, extracting metadata, and verifying official INEC seals—outputting everything into a strict, database-ready JSON format.

##  Features

* **Batch Processing:** Automatically processes folders containing hundreds of ballot images (`.jpg`, `.jpeg`, `.png`).
* **Smart Handwriting OCR:** Reason-based extraction easily handles handwritten numbers, corrections, and names.
* **Strict JSON Schema:** Guarantees consistent key names and data types (integers, strings, booleans) to prevent database errors.
* **Zero-Hallucination Prompting:** Strictly ignores illegible scribbles (like agent signatures) and prevents the AI from guessing data.
* **Official Seal Detection:** Automatically verifies the presence of the INEC Presiding Officer ink stamp.

##  Quick Start

### 1. Prerequisites
Ensure you have Python 3.9+ installed. Install the required dependencies:

```bash
pip install google-genai pillow python-dotenv
```
###  2. Environment Setup
Create a .env file in the root directory and add your Google AI Studio API key and folder paths:
```
GEMINI_API_KEY=your_api_key_here
LLM_MODEL=gemini-2.5-flash
INPUT_FOLDER=input_images
OUTPUT_FOLDER=output_jsons
TARGET_IMAGE_NAME=election_form2.jpeg
```

### 3. Usage
Place your scanned Form EC 8A images into the input_images folder, then run the script:
```
python img_app.py        #for single file processing
python folder_app.py     #for batch processing
```

###  Example JSON Output
The tool outputs a highly structured schema, including:

* metadata: State, Area Council, Ward, Polling Unit, and their respective codes.

* statistics: Registered voters, accredited voters, valid/rejected ballots.

* results: A clean array of political parties and their tallied votes.

* polling_agent_names: A consolidated list of clearly printed agent names (ignoring signatures).

* is_seal_present: Boolean verification of the official stamp.
