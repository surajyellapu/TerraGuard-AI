# TerraGuard AI

**Team:** DisasterX

TerraGuard AI is a disaster-evidence intelligence demo for the Open Agent Hackathon 2026 (“Solving Fragmented Intelligence” track).

Phase 1 turns fragmented **simulated** flood observations into clear analyzer findings and a human-readable incident brief. Sample data is for demonstration only and must not be treated as verified real-world disaster information.

## Project Status

**Phase 1 complete (local demo):**

- Rule-based evidence analyzer (`src/analyzer.py`)
- Human-readable incident brief (`src/brief.py`)
- Beginner-friendly Streamlit UI (`app.py`)
- Unit tests for the analyzer and brief

Later phases may add sponsor integrations. Those are **not implemented yet**, so this README does not claim they work.

## What works today

- Load `sample_flood_evidence.json` (simulated sample data)
- Flag stale reports and conflicting water-level readings
- Show findings and an incident brief in the browser
- Keep the wording clear that sample data does **not** confirm a flood

## What is not built yet

- Live satellite imagery, maps, or weather APIs
- Vulnerable-area mapping or official response recommendations
- Zetaris, Meterless, Nightshift, or NVIDIA integrations

## Repository Structure

- `src/analyzer.py` — evidence rules and findings
- `src/brief.py` — readable incident brief from analyzer output
- `app.py` — Streamlit demo UI
- `tests/` — automated tests
- `sample_flood_evidence.json` — simulated flood evidence
- `evidence_rules.md` — demo assessment rules
- `demo_script.md` — Phase 1 demo walkthrough
- `requirements.txt` — Python dependencies for the UI

## Run the Phase 1 demo (Windows PowerShell)

```powershell
cd C:\Users\SAI\Desktop\TerraGuard-AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks script activation once, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the virtual environment again and run `streamlit run app.py`.

## Run tests

```powershell
cd C:\Users\SAI\Desktop\TerraGuard-AI
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
```

## Safety

This prototype is for demonstration only. It must not replace official alerts, trained responders, or emergency services.
