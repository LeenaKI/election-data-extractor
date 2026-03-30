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
