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

## How traceability works

Each device receives an automatically generated ID and a product passport. Its holder can record collection, inspection, repair or recycling. A handover requires the named recipient to accept it, while corrections become new notes rather than edits to earlier entries. Recycling closes further lifecycle transitions.

The Solidity contract enforces these rules on a local Ethereum development chain. Optional evidence files are represented by SHA-256 fingerprints; their contents are not stored on-chain. The chain checker compares every block’s parent reference with the preceding block. This demonstrates local consistency, rather than independent proof of a device’s physical journey.

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

## Machine learning in Outlook

Outlook uses **supervised learning with multiple linear regression**, implemented through scikit-learn’s `LinearRegression`, to estimate annual global e-waste generation in **million tonnes (Mt)**. Its three input features are global population in billions, GDP in trillions of USD, and internet users in billions.

Training uses **14 annual records from 2010–2023**. The complete dataset contains 16 records through 2025; the final two years are displayed but are not used to fit the model or calculate a reported test score. For **2026–2030**, the fitted model receives predefined population, GDP and internet-use scenarios.

Only the generated-waste quantity comes from ML. The other outputs follow explicit calculations:

- **Recycled waste:** predicted generation multiplied by an assumed recycling rate, increasing from 23.5% in 2026 to 27.5% in 2030.
- **Unrecycled waste:** generation minus calculated recycling.
- **Cumulative unrecycled waste:** the dataset’s running total through 2025 plus subsequent projected unrecycled quantities.

Interactive charts compare dataset records with scenario projections, and users can export the combined data as CSV. These forecasts describe possible outcomes under the supplied assumptions; they do not estimate how much waste blockchain adoption would prevent.

This is a baseline ML workflow, not a validated forecasting system. The dataset’s source is undocumented, its sample is small, and no out-of-sample accuracy, baseline comparison or prediction intervals have been established. Future evaluation should use sourced observations, chronological holdout testing, and MAE/RMSE comparisons against simple forecasts. [Full model details](docs/ARCHITECTURE.md#machine-learning-in-outlook)

## Device assessment

The assessment combines physical condition, functionality, applicable battery health and three device-specific checks. Reported hazards or failed functions override a favourable average score. Results explain whether further inspection, repair, battery service, refurbishment or potential reuse is appropriate.

Procedural Three.js models change with the condition inputs, showing surface damage or separated parts. These are stylised illustrations, not scans or diagnostics of the actual device.

## Scope and limitations

This is a local research prototype. Blockchain records do not prove physical identity, truthful inspections or actual recycling, and do not prevent illegal dumping by themselves. Device assessments are triage heuristics; the contract has not been security-audited.

Tests cover assessment rules, QR generation, chain links and contract behaviour.

## Documentation

- [Research, evidence and sources](docs/RESEARCH.md)
- [Architecture, device profiles, setup details and limitations](docs/ARCHITECTURE.md)
- [Tests and validation](docs/ARCHITECTURE.md#validation)

Three.js is bundled under its [MIT license](device_scene_component/THREE-LICENSE.txt).
