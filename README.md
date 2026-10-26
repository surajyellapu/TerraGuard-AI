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

**Zetaris JDBC connector (opt-in):**

- Local sample JSON loader is unchanged and remains the flood-evidence path
- Optional JayDeBeApi JDBC client can test `SELECT 1` and preview `NY_TAXI.weather_data`
- New York taxi-zone weather is **not** flood evidence and is **not** used as Riverbend Village data
- Meterless, Nightshift, and NVIDIA are **not** implemented and are not claimed here

## What works today

- Load `sample_flood_evidence.json` (simulated sample flood evidence)
- Flag stale reports and conflicting water-level readings
- Show findings and an incident brief in the browser
- Keep the wording clear that sample data does **not** confirm a flood
- Optionally preview Zetaris `NY_TAXI.weather_data` when JDBC credentials and the local instance are available

## What is not built yet

- Live satellite imagery, maps, or official weather APIs
- Vulnerable-area mapping or official response recommendations
- Meterless, Nightshift, or NVIDIA integrations
- Using Zetaris weather rows as flood observations (intentionally not done)

## Repository Structure

- `src/analyzer.py` — evidence rules and findings
- `src/brief.py` — readable incident brief from analyzer output
- `src/zetaris_connector.py` — local sample loader plus optional Zetaris JDBC client
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

## Zetaris JDBC (optional)

Live Zetaris access is **opt-in**. Flood analysis always uses local simulated sample JSON. Weather rows from Zetaris are a **separate preview**.

### Simulated flood evidence vs live weather preview

| Source | What it is | What it is not |
|---|---|---|
| `sample_flood_evidence.json` | Simulated Riverbend Village flood-style observations | Not live Zetaris data |
| `NY_TAXI.weather_data` | New York taxi-zone weather table on local Zetaris | Not Riverbend Village, not flood confirmation, not verified rainfall in millimetres |

`precipitation` in `NY_TAXI.weather_data` is stored as a string. Its units and meaning are **not verified**. Do not treat those values as flood rainfall.

### Configure credentials securely

Set credentials in your **current PowerShell session** (they are not saved in the repo):

```powershell
$env:ZETARIS_USER = "your-username"
$env:ZETARIS_PASSWORD = "your-password"
```

Optional overrides (defaults match the verified local install):

```powershell
$env:ZETARIS_JDBC_URL = "jdbc:zetaris:lightning@localhost:10000"
$env:ZETARIS_JDBC_DRIVER_CLASS = "com.zetaris.lightning.jdbc.LightningDriver"
$env:ZETARIS_JDBC_JAR = "C:\zetaris-platform\zetaris-platform\jdbc\ndp-jdbc-driver-2.4.3.1-7eff043-driver.jar"
```

Do not commit passwords. `.env` is gitignored; do not add secret files to git.

### Test the JDBC connection

With Zetaris running at `http://localhost:3000` and credentials set:

```powershell
cd C:\Users\SAI\Desktop\TerraGuard-AI
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\zetaris_connector.py --test-connection
python src\zetaris_connector.py --fetch-weather --limit 5
```

If `ZETARIS_USER` / `ZETARIS_PASSWORD` are unset, the CLI prompts for them and does not print the password.

Without credentials or with Zetaris stopped, those commands fail with a clear error. The Streamlit app still runs the **local sample flood brief**.

### Troubleshooting

- **Missing ZETARIS_USER or ZETARIS_PASSWORD:** set them in the session, then retry the connector CLI. The Streamlit app currently uses local sample flood evidence only. Keep using sample flood data unless the live flood-evidence source has been verified.
- **JDBC driver JAR was not found:** confirm the JAR path and `ZETARIS_JDBC_JAR`.
- **Could not connect to Zetaris:** confirm the local instance is up, Java is installed, and DBeaver can still run `SELECT 1`.
- **JayDeBeApi / JPype import errors:** run `pip install -r requirements.txt` inside `.venv`. Java 25 + JPype can still fail even when DBeaver works; that is a live-integration issue, not a passing unit test.

## Safety

This prototype is for demonstration only. It must not replace official alerts, trained responders, or emergency services.
