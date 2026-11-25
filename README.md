# Reclaim

A Streamlit research prototype for exploring e-waste generation, recording device handoffs, and assessing possible recovery routes with an interactive 3D device scene.

## Features

- Outlook with historical dataset records, scenario forecasts, and CSV export.
- Local proof-of-work ledger with optional MySQL persistence and transaction search.
- Eight procedural 3D device types with intact, cracked and broken states, drag rotation, zoom, and animated condition changes.
- Device-specific functional checks and explained triage rules. Reported hazards and critical failures override the combined score.
- Ink and vermilion interface with client-side workspace tabs.

## Run locally

Requires Python 3.11+.

```sh
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run App_Production.py
```

Forecasting and device assessment work without MySQL. Without a database, ledger changes exist only in the current session.

### Optional MySQL database

Run `schema.sql` using a local MySQL/MariaDB client. Configure `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` in your environment before starting the app. Defaults are localhost, root, empty password, and `ewaste_blockchain`; use a dedicated account for any shared deployment. No database records are included.

```powershell
$env:DB_USER = 'reclaim_app'
$env:DB_PASSWORD = 'your-local-password'
python -m streamlit run App_Production.py
```

## Important limitations

The bundled CSV has 16 annual records, 2010–2025, with no documented source in the original project. Treat it as illustrative, not verified historical evidence. Linear regression trains on 2010–2023. Future population, GDP, internet users and recycling rates are predefined assumptions; forecasts have not been validated out of sample.

Assessment rules are transparent prototype heuristics, not manufacturer standards, automated diagnostics, or safety certifications. Models are stylised procedural illustrations. A low score does not prove disposal is required.

The ledger is a local educational demonstration, not a distributed blockchain. Its rehash feature can rewrite stored hashes and must not be presented as independent evidence of tamper resistance. The app is not production-hardened.

## Checks

```sh
python -m unittest discover -s tests
```

## Third-party software

Three.js 0.160.0 is bundled locally under its MIT license; see `device_scene_component/THREE-LICENSE.txt`. Other dependencies retain their respective licenses.
