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

- Local sample JSON loader is unchanged and remains the flood-evidence path.
- Optional JayDeBeApi JDBC client supports testing `SELECT 1` and previewing `NY_TAXI.weather_data` when correctly configured.
- New York taxi-zone weather is **not** flood evidence and is **not** used as Riverbend Village data.
- Meterless, Nightshift, and NVIDIA integrations are not claimed as implemented in this Phase 1 demo.

## What works today

- Load `sample_flood_evidence.json` (simulated sample flood evidence).
- Flag stale reports and conflicting water-level readings.
- Show findings and an incident brief in the browser.
- Make clear that sample data does **not** confirm a real flood.
- The connector includes an optional Zetaris weather-data preview, but live connectivity must be verified in the target environment before it is described as working.

## What is not built or verified yet

- Live satellite imagery, maps, or official weather APIs.
- Vulnerable-area mapping or official response recommendations.
- Meterless, Nightshift, or NVIDIA integrations in this Phase 1 demo.
- Using Zetaris weather rows as flood observations (intentionally not done).
- Confirmed live Zetaris JDBC connectivity in the current environment.
- H-MEM persistence across process or service restarts.
- Live Nightshift service connectivity.

## Repository Structure

- `src/analyzer.py` — evidence rules and findings.
- `src/brief.py` — readable incident brief from analyzer output.
- `src/zetaris_connector.py` — local sample loader plus optional Zetaris JDBC client.
- `app.py` — Streamlit demo UI.
- `tests/` — automated tests.
- `sample_flood_evidence.json` — simulated flood evidence.
- `evidence_rules.md` — demo assessment rules.
- `demo_script.md` — Phase 1 demo walkthrough.
- `requirements.txt` — Python dependencies for the UI and connector.

## Run the Phase 1 demo (Windows PowerShell)

Open PowerShell and navigate to your project folder. For example:

```powershell
cd C:\Users\KATIK\Desktop\TerraGuard-AI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

If PowerShell blocks script activation, follow your organization's approved PowerShell policy. Do not change system-wide execution policies unnecessarily.

## Run tests

From the project folder, run:

```powershell
py -m unittest discover -s tests -v
```

Alternatively, if `pytest` is installed:

```powershell
py -m pytest tests -v
```

## Zetaris JDBC (optional)

Live Zetaris access is **opt-in**. Flood analysis always uses the local simulated sample JSON. Weather rows from Zetaris are a separate preview.

### Simulated flood evidence vs live weather preview

| Source | What it is | What it is not |
|---|---|---|
| `sample_flood_evidence.json` | Simulated Riverbend Village flood-style observations | Not live Zetaris data |
| `NY_TAXI.weather_data` | New York taxi-zone weather table on a Zetaris environment | Not Riverbend Village, not flood confirmation, and not verified rainfall in millimetres |

The `precipitation` field in `NY_TAXI.weather_data` is stored as a string. Its units and meaning have not been verified. Do not treat those values as confirmed flood-rainfall measurements.

### Configure credentials securely

Only configure a connection after the project team or Zetaris administrator confirms the approved driver source, endpoint, and secure setup process.

Set credentials in your current PowerShell session using the approved values:

```powershell
$env:ZETARIS_USER = "your-username"
$env:ZETARIS_PASSWORD = "your-password"
```

Do not paste real credentials into chat, source code, screenshots, or GitHub. Do not commit credential files.

### JDBC configuration

The connector documents these optional configuration variables:

```powershell
$env:ZETARIS_JDBC_URL = "jdbc:zetaris:lightning@localhost:10000"
$env:ZETARIS_JDBC_DRIVER_CLASS = "com.zetaris.lightning.jdbc.LightningDriver"
$env:ZETARIS_JDBC_JAR = "C:\path\to\approved\zetaris-jdbc-driver.jar"
```

These are example settings, not confirmation that the endpoint or driver exists on your computer. Verify them with the approved Zetaris setup instructions. Do not download an unverified driver.

### Test the JDBC connection

After the approved driver is available, the connection settings are configured securely, and the authorized Zetaris test environment is running, open PowerShell in the project folder and run:

```powershell
py src\zetaris_connector.py --test-connection
```

If the connection test succeeds, and the team authorizes a small weather-data preview, run:

```powershell
py src\zetaris_connector.py --fetch-weather --limit 5
```

A successful `SELECT 1` confirms basic connectivity only. It does not prove that the weather data is suitable for flood analysis.

The live connection and weather-data fetch have **not been verified in the current environment**. The documented JDBC driver was not found at its default path or inside the project repository. The approved driver source and connection setup must be confirmed before testing.

The Streamlit demo should continue using the local simulated sample data unless a separate, authorized live flood-evidence source is verified.

### Troubleshooting

- **Missing username or password:** configure them using the approved secure process.
- **JDBC driver JAR not found:** obtain it from an approved Zetaris source and verify the path before setting `ZETARIS_JDBC_JAR`.
- **Could not connect:** confirm the authorized instance is running and that the JDBC endpoint and credentials are correct.
- **JayDeBeApi or JPype import errors:** install the project's Python requirements in the intended environment and check compatibility with the installed Java version.
- **Unit tests pass but live connection fails:** mocked or local tests do not establish live external connectivity.

## Integration Verification Status

The following checks remain pending in the current environment:

- **Zetaris JDBC:** Java 20.0.1 (64-bit) is installed, but the JDBC driver was not found at the documented default path or inside the project repository. A live `SELECT 1` and authorized weather-data fetch have not been verified.
- **H-MEM persistence:** persistence across a process or service restart has not yet been verified.
- **Nightshift:** live service connectivity has not yet been verified.

Update these statuses only after the corresponding checks pass. Record whether each result came from a live service, a mocked test, or simulated sample data.

## Safety

This prototype is for demonstration only. It must not replace official alerts, trained responders, or emergency services. Simulated evidence and unverified external data must not be presented as confirmed real-world disaster information.
