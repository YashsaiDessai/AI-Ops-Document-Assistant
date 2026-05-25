# AI Ops Document Assistant

The **AI Ops Document Assistant** is a production-ready Python CLI pipeline designed to ingest unstructured internal documents (meeting logs, incident reports, research PDFs, etc.) and extract structured, actionable operations reports.

It uses an asynchronous Map-Reduce workflow powered by OpenAI's Structured Outputs API to synthesize page-by-page analyses and action item checklists.

---

## How to Run Locally

This tool runs as a CLI and requires Python 3.11+ and an OpenAI API key.

### Step 1: Clone the Repository
```bash
git clone https://github.com/YashsaiDessai/AI-Ops-Document-Assistant.git
cd AI-Ops-Document-Assistant
```

### Step 2: Set Up a Virtual Environment
Create and activate a Python virtual environment to manage dependencies:

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
Install the required dependencies listed in `requirements.txt`:
```bash
python -m pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
The application reads its configuration from environment variables or a local `.env` file. 

Create a `.env` file at the root of the project:
```ini
# .env
OPS_OPENAI_API_KEY=your-openai-api-key-here
OPS_MODEL_NAME=gpt-4-turbo
OPS_CHUNK_SIZE=1000
```
*Note: The environment variable prefix `OPS_` is required (e.g. `OPS_OPENAI_API_KEY`).*

### Step 5: Run the Tool
Run the pipeline directly on an input document (e.g. text or PDF):
```bash
python src/main.py Data/incident_report.txt
```

---

## Command Line Interface Options

You can customize the pipeline run using command line parameters:

```text
usage: main.py [-h] [-o OUTPUT_DIR] [-c CHUNK_SIZE] [--verbose] filepath

positional arguments:
  filepath              Path to the input document (supports .pdf and .txt)

options:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to save the generated report artifacts
                        (defaults to the directory of the input file)
  -c CHUNK_SIZE, --chunk-size CHUNK_SIZE
                        Character size threshold for document splitting
                        (overrides config setting)
  --verbose, -v         Enable detailed debug-level logging output
```

### Example Usage:

1. **Process a PDF report with custom chunk size and debug logging:**
   ```bash
   python src/main.py Data/monthly_audit.pdf -c 800 -v
   ```

2. **Save generated reports to a specific output folder:**
   ```bash
   python src/main.py Data/incident_report.txt -o Output/
   ```

---

## Generated Outputs

When running the pipeline, the CLI automatically generates two report formats and saves them in the output directory:

1. **Markdown Report (`*_report.md`)**: A human-readable Markdown file featuring:
   - A consolidated Executive Summary.
   - An **Action Items Table** sorted by priority (High, Medium, Low) with assigned owners.
2. **JSON Report (`*_report.json`)**: A machine-readable raw JSON export following strict schemas, ideal for downstream API integrations.
