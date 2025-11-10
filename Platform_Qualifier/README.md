# Platform Qualification Tool (Streamlit)

A Streamlit UI to upload product documents (RFP/PRD/BRD), run RAG-backed LLM analysis against a checklist, compute weighted scores, classify the project, and export results to Excel.


## Prerequisites

- Python 3.9+
- pip
- Git (optional)
- Ollama running locally with a valid model (default: `llama2`)

The LLM interface in `modules/llm_interface.py` calls the local Ollama API at `http://localhost:11434/api/generate`.


## Quick Start (Local)

1. Create and activate a virtual environment
   
   - macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\\Scripts\\Activate.ps1
     ```

2. Install dependencies
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Start Ollama locally and pull the model (first time only)
   - Install: https://ollama.com/download
   - In a terminal:
     ```bash
     ollama serve
     # in another terminal
     ollama pull llama2
     ```
   - If you want to use a different model, update the `model` argument where `evaluate_checklist_with_rag` is called or adjust the default in `modules/llm_interface.py`.

4. Run the Streamlit app
   ```bash
   streamlit run app.py
   ```
   Streamlit will show a local URL (e.g., http://localhost:8501). Open it in your browser.


## Project Structure (key files)

- `app.py` — Streamlit UI entry point
- `modules/` — parsing, RAG, LLM, scoring, classification, excel export
- `config/prompts.yaml` — prompt templates
- `data/` — input checklist and sample outputs
- `requirements.txt` — Python deps


## Configuration Notes

- LLM endpoint: hardcoded in `modules/llm_interface.py` as `OLLAMA_URL = "http://localhost:11434/api/generate"`.
- Prompts: loaded from `config/prompts.yaml`.
- Uploads: The app accepts `.pdf`, `.docx`, `.txt`.


## Running on a Cloud VM (with local browser via SSH tunnel)

These steps assume a Linux VM (Ubuntu/Debian-like) with SSH access.

1. Connect to the VM via SSH
   ```bash
   ssh <vm-user>@<vm-ip>
   ```

2. Install system dependencies (Python and pip)
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3 python3-venv python3-pip git
   ```

3. Clone or upload the project
   ```bash
   git clone <your-repo-url> Platform_Qualifier
   cd Platform_Qualifier
   ```

4. Create venv and install requirements
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Install and run Ollama on the VM, pull the model
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama serve &
   ollama pull llama2
   ```

6. Run Streamlit on the VM and bind to all interfaces
   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```

7. From your local machine, create an SSH tunnel to the VM
   ```bash
   ssh -L 8501:localhost:8501 <vm-user>@<vm-ip>
   ```
   Then open http://localhost:8501 in your local browser.

   - If Ollama runs on the VM (recommended), no additional tunnel is required for the app since it talks to `localhost:11434` from within the VM.
   - If you need to access the VM’s Ollama API from your local machine (not typical for this app), you can add another tunnel:
     ```bash
     ssh -L 11434:localhost:11434 <vm-user>@<vm-ip>
     ```


## Using a Different Ollama Model

- Update the `model` parameter passed to `evaluate_checklist_with_rag` in `app.py` or change the default in `modules/llm_interface.py`.
- Make sure the model is pulled on the machine where Ollama is running:
  ```bash
  ollama pull <model-name>
  ```


## Troubleshooting

- Streamlit not loading remotely: confirm the tunnel command is active and the VM app is bound to `0.0.0.0` on port `8501`.
- Ollama errors: ensure `ollama serve` is running and the model is pulled. Check logs or run a quick test:
  ```bash
  curl http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"hello","stream":false}'
  ```
- PDF parsing errors: ensure files are valid PDFs. `PyMuPDF` is bundled as a Python wheel; no extra system packages are typically required.


## License

Proprietary/Internal use unless stated otherwise.
