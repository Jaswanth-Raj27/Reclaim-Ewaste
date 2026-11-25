# Reclaim Ewaste

A research prototype combining blockchain product traceability, interactive 3D device assessment and machine-learning e-waste scenarios.

Reclaim aims to support accountable e-waste handling and help identify gaps that could enable illegal dumping, including shipments to lower-income countries. Its environmental impact has not yet been measured.

## Features

- **Traceability:** add a named device, record lifecycle updates, accept handovers and view its blockchain history.
- **Chain checks:** verify block links with one button; explore blocks and transaction details.
- **Device assessment:** 23 device types plus Other, functional checks and 3D previews that respond to condition.
- **Phone passports:** downloadable QR codes and a read-only viewer on the same Wi-Fi.
- **Outlook:** e-waste generation scenarios for 2026–2030, interactive charts and CSV export.

Built with Python, Streamlit, scikit-learn, Plotly, Solidity, Web3.py, Ganache and Three.js.

## Quick start

Requires Python 3.11+ and Node.js/npm. Run from the repository folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm ci
npm run compile
npm run chain
```

Keep the node running. In a second terminal:

```powershell
.venv\Scripts\Activate.ps1
python scripts/deploy.py
python -m streamlit run App_Production.py --server.address 127.0.0.1
```

Open [Reclaim locally](http://127.0.0.1:8501). This demo uses unlocked local accounts and no real funds. Keep the app and Ethereum RPC restricted to your computer. See [phone QR setup and local state](docs/ARCHITECTURE.md#local-state-and-phone-qr-setup) for Wi-Fi passport access.

## Machine learning

Outlook uses multiple linear regression to estimate e-waste generation from population, GDP and internet users. It trains on 14 annual records from 2010–2023 and applies predefined inputs for 2026–2030. Recycling and unrecycled quantities are calculated using assumed recycling rates.

The dataset has no documented source and out-of-sample accuracy has not been established. Treat the outputs as illustrative scenarios. [Model details](docs/ARCHITECTURE.md#machine-learning-in-outlook)

## Scope and limitations

This is a local research prototype. Blockchain records do not prove physical identity, truthful inspections or actual recycling, and do not prevent illegal dumping by themselves. Device assessments are triage heuristics; the contract has not been security-audited.

## Documentation

- [Research, evidence and sources](docs/RESEARCH.md)
- [Architecture, device profiles, setup details and limitations](docs/ARCHITECTURE.md)
- [Tests and validation](docs/ARCHITECTURE.md#validation)

Three.js is bundled under its [MIT license](device_scene_component/THREE-LICENSE.txt).
