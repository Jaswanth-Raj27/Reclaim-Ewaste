# Architecture and technical details

[Back to README](../README.md)

## Components

| Component | Responsibility |
| --- | --- |
| `App_Production.py` | Streamlit workspace, Outlook model and assessment interface |
| `traceability_ui.py` | Product registration, updates, handovers and QR display |
| `contracts/ProductPassport.sol` | On-chain permissions, custody and lifecycle history |
| `blockchain_client.py` | Loopback Ethereum connection and confirmed transactions |
| `chain_explorer.py` | Block visualisation and parent-link checks |
| `passport_server.py` | Separate read-only passport viewer for phone access |
| `assessment_engine.py` | Device profiles and explained triage rules |
| `device_scene_component/` | Three.js device previews and condition animation |

## Blockchain product traceability

- **Add a device:** choose its type, give it a name and press **Add to blockchain**. A unique device reference is generated automatically.
- **Update a device:** select it by name, choose what happened and press **Save to blockchain**. Notes and evidence files are optional for lifecycle updates; a note needs text.
- Look up a passport by reference or blockchain ID; download its QR code.
- Current custodian proposes a transfer; only the nominated recipient can accept it. Owners can cancel pending transfers.
- Track Registered → Collected → Inspected → Repaired or Recycled. Repaired products can re-enter collection/inspection. Recycling ends further custody/stage transitions.
- Owners can append notes/corrections without changing earlier history, including after recycling.
- Evidence files are SHA-256 hashed. Only the hash is recorded; file contents are neither stored nor published by the app.
- View on-chain history, confirmation transaction hashes and blocks; export passport JSON or verify evidence against recorded hashes.
- Explore existing EVM blocks as a linked diagram with block numbers, hashes, parent hashes, transaction counts and app events. Browse older block windows and inspect full transaction details.
- **Check the chain** checks every parent link from the first block to a fixed latest-block snapshot and reports broken links or a successful match. Check again after adding new blocks. This checks local link consistency, not independent consensus, physical authenticity or an externally trusted copy.
- Saving a registration, handover or lifecycle update automatically creates a transaction block. There is no separate block-creation step in the interface.
- Demo participant settings and technical identifiers are tucked away. A clearly labelled demo switch lets you act as a device’s current holder to try updates.

`contracts/ProductPassport.sol` enforces owner permissions, two-party handoffs, unique IDs and lifecycle transitions. This replaces the MySQL hash-chain demonstration. Existing MySQL records are not migrated or presented as blockchain history.

## Local state and phone QR setup

The node listens only on `127.0.0.1:8545`, chain ID 1337. Its generated development accounts are unlocked and funded with valueless local ETH. Selecting one simulates a participant; **this is not multi-user authentication or wallet signing**. Do not expose these services to a network or use real accounts/funds.

Chain data and deployment records live under ignored `.local/`. Restarting the node preserves its state. Back up this directory locally to retain demo history; it contains development account material and must never be committed. `deploy.py` reuses its matching deployment. Deleting `.local/` resets the development chain.

QR links include the product ID, chain ID and contract address. Without configuration they use localhost, which only opens on the computer. For phone scanning on the same Wi-Fi, start the separate read-only viewer (replace the example IP with your computer's Wi-Fi IPv4 address):

```powershell
python passport_server.py --host 192.168.1.10 --port 8502
```

Set `passport_base_url = "http://192.168.1.10:8502"` in ignored `.streamlit/secrets.toml`, or set `RECLAIM_PASSPORT_BASE_URL` before starting Streamlit. Generate a fresh QR after changing the destination. Keep the viewer and blockchain running; allow the viewer on your private network if Windows asks. The viewer exposes only passport reads; keep Streamlit and the Ethereum RPC on loopback. An IP change requires updating the setting and generating new QR codes. Public hosting, wallet authentication and public-chain deployment are not implemented.

## Device assessment

The assessment selector supports **23 named device types plus Other**, matching the blockchain registration categories:

| Group | Device types |
| --- | --- |
| Personal and computing | Smartphone, laptop, tablet, smartwatch, desktop computer, monitor, keyboard, mouse |
| Audio, imaging and entertainment | Television, headphones / earbuds, speaker, camera, gaming console |
| Office and networking | Printer, scanner, router / modem |
| Power | Lithium-ion battery, power bank, charger |
| Appliances | Refrigerator, washing machine, air conditioner, microwave oven |
| Other | General checks and an illustrative enclosure; registration also accepts a custom type name |

Each type has three functional checks and an illustrative 3D preview. Physical-condition changes show cracks and separated parts; functionality controls the screen appearance where a screen is present. Drag to rotate and scroll to zoom. Some related types share a stylised model, such as headphones and earbuds.

Battery health appears for smartphone, laptop, tablet, smartwatch, headphones / earbuds, camera, power bank and lithium-ion battery. The profiles assume rechargeable versions of these devices.

The result explains why a device is a reuse or refurbishment candidate, needs repair or battery service, needs further inspection, or requires specialist handling. Reported hazards and critical faults override the average condition score. Checks are prototype triage inputs; they are not instructions to open equipment or perform electrical testing.

## Outlook and interface

Outlook provides regression scenario forecasts, charts and CSV export. The workspace uses the ink-and-vermilion palette with client-side tabs for Outlook, Traceability and Device assessment.

### Machine learning in Outlook

Outlook uses **supervised learning with multiple linear regression**, implemented with scikit-learn’s `LinearRegression`, to estimate annual global e-waste generation.

| Model input | Unit |
| --- | --- |
| Global population | Billions of people |
| Global GDP | Trillions of USD |
| Global internet users | Billions of people |

The target is **e-waste generated in million tonnes (Mt)**. The model is trained on **14 annual records from 2010–2023**. The dataset contains 16 records through 2025; the 2024–2025 records are displayed but are not used for model fitting or a reported test score.

For **2026–2030**, predefined population, GDP and internet-user scenarios are passed to the fitted model. The dashboard then calculates:

- **Generated waste:** the model’s prediction.
- **Recycled waste:** predicted generation multiplied by an assumed recycling rate, rising from **23.5% in 2026 to 27.5% in 2030**.
- **Unrecycled waste:** predicted generation minus calculated recycled waste.
- **Cumulative unrecycled waste:** the dataset’s cumulative total through 2025 plus each projected year’s unrecycled waste. The total starts in 2010.

**Only generation is predicted by ML.** Recycling rates and future predictor values are predefined assumptions. The charts and CSV export expose these illustrative scenarios; they do not measure an effect caused by blockchain use.

This is a baseline forecasting prototype. The small dataset has no documented source, and no out-of-sample accuracy estimate, baseline comparison or prediction intervals have been established. The results should not be presented as validated real-world forecasts. Stronger evaluation would require sourced data, chronological holdout testing and comparison with simple forecasting baselines.

## Validation

```powershell
python -m unittest discover -s tests
# Requires running local node; deploys a separate integration-test contract:
python tests/blockchain_integration.py
```

The unit suite covers assessment rules, QR links, development mining and successful/broken chain links.

Integration checks cover duplicate registration, unauthorised actions, transfer acceptance/cancellation, lifecycle order, terminal recycling, append-only correction and evidence hashes. Test contracts do not populate the app contract.

## Limitations

The contract has not received a security audit. Ganache has reported transitive vulnerabilities; it is restricted to loopback and unsuitable as hosted production infrastructure. Its native websocket extension may fall back to JavaScript on newer Node versions.

A chain establishes which address recorded an event and preserves recorded history under its network assumptions. It does not prove physical identity, ownership in law, authentic manufacture or truthful inspection. This prototype does not verify organisations, prevent QR copying, or stop a local node administrator resetting the chain. Registration is self-asserted. Do not put personal information in labels or event details.

The CSV has 16 annual records (2010–2025) with no documented source in the original project. Treat them as illustrative. Training uses 2010–2023; future predictors and recycling rates are predefined scenarios, not validated forecasts. Device rules are prototype heuristics, not diagnostics or safety certifications. Models are stylised illustrations.

## Third-party software

Three.js 0.160.0 is bundled under its MIT license; see `device_scene_component/THREE-LICENSE.txt`. Compilation uses solc 0.8.30; the local chain uses Ganache 7.9.2. Other dependencies retain their respective licenses.
