# TerraGuard AI — Phase 1 Demo Script

**Audience:** hackathon mentors / teammates  
**Length:** about 2–3 minutes  
**Data:** simulated sample only — not a real flood confirmation

## Before you start

1. Open PowerShell and start the app (see README).
2. Confirm the browser shows the red **SIMULATED SAMPLE DATA** banner.

## What to say and click

1. **Introduce the problem (20 seconds)**  
   “TerraGuard AI helps a reviewer combine fragmented disaster reports. Phase 1 uses local simulated flood evidence only.”

2. **Show the safety label (10 seconds)**  
   Point to the banner: “Everything here is sample data. We do not claim a real flood.”

3. **Run the analysis (30 seconds)**  
   Click **Load sample evidence and run analysis**.  
   Show the evidence table: five Riverbend Village observations, all marked sample data.

4. **Explain the findings (45 seconds)**  
   - One older report is flagged as stale.  
   - Two water-level readings disagree (4.2 m vs 4.0 m).  
   - The assessment still says sample data does not confirm a flood.

5. **Show the incident brief (30 seconds)**  
   Scroll to **Incident brief**.  
   “A human can read this, download it, and decide what to verify next.”

6. **Close honestly (20 seconds)**  
   “Phase 1 is local rules plus a brief UI. Sponsor data and model integrations are planned for later phases and are not claimed here.”

## Optional CLI check

If the UI is not available, you can still show the analyzer:

```powershell
python src\analyzer.py
```
