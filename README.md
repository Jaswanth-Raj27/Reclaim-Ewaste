# Reclaim Ewaste

A Streamlit research prototype for electronic-product passports, Ethereum custody transfers, interactive 3D condition assessment and illustrative e-waste forecasting.

## Blockchain product traceability

- Register an opaque product reference, public label and device category.
- Look up a passport by reference or blockchain ID; download its QR code.
- Current custodian proposes a transfer; only the nominated recipient can accept it. Owners can cancel pending transfers.
- Track Registered → Collected → Inspected → Repaired or Recycled. Repaired products can re-enter collection/inspection. Recycling ends further custody/stage transitions.
- Owners can append notes/corrections without changing earlier history, including after recycling.
- Evidence files are SHA-256 hashed. Only the hash is recorded; file contents are neither stored nor published by the app.
- View on-chain history, confirmation transaction hashes and blocks; export passport JSON or verify evidence against recorded hashes.
- Explore existing EVM blocks as a linked diagram with block numbers, hashes, parent hashes, transaction counts and app events. Browse older block windows and inspect full transaction details.
- The **Add block to chain** button mines a real empty block on the local development chain. It does not create a passport event; registrations, custody changes and lifecycle events create their own transaction blocks.

`contracts/ProductPassport.sol` enforces owner permissions, two-party handoffs, unique IDs and lifecycle transitions. This replaces the MySQL hash-chain demonstration. Existing MySQL records are not migrated or presented as blockchain history.

## Local setup

Requires Python 3.11+ and Node.js/npm. No real cryptocurrency is needed.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm ci
npm run compile
npm run chain
```

Keep the node running. In a second terminal in the same repository:

```powershell
.venv\Scripts\Activate.ps1
python scripts/deploy.py
python -m streamlit run App_Production.py --server.address 127.0.0.1
```

The node listens only on `127.0.0.1:8545`, chain ID 1337. Its generated development accounts are unlocked and funded with valueless local ETH. Selecting one simulates a participant; **this is not multi-user authentication or wallet signing**. Do not expose these services to a network or use real accounts/funds.

Chain data and deployment records live under ignored `.local/`. Restarting the node preserves its state. Back up this directory locally to retain demo history; it contains development account material and must never be committed. `deploy.py` reuses its matching deployment. Deleting `.local/` resets the development chain.

QR links include the product ID, chain ID and contract address. Without configuration they use localhost, which only opens on the computer. For phone scanning on the same Wi-Fi, start the separate read-only viewer (replace the example IP with your computer's Wi-Fi IPv4 address):

```powershell
python passport_server.py --host 192.168.1.10 --port 8502
```

Set `passport_base_url = "http://192.168.1.10:8502"` in ignored `.streamlit/secrets.toml`, or set `RECLAIM_PASSPORT_BASE_URL` before starting Streamlit. Generate a fresh QR after changing the destination. Keep the viewer and blockchain running; allow the viewer on your private network if Windows asks. The viewer exposes only passport reads; keep Streamlit and the Ethereum RPC on loopback. An IP change requires updating the setting and generating new QR codes. Public hosting, wallet authentication and public-chain deployment are not implemented.

## Other screens

- Outlook: regression scenario forecasts, charts and CSV export.
- Device assessment: eight procedural 3D device types, animated damage, rotation/zoom, device-specific checks and explained triage. Critical faults override average scores.
- Ink and vermilion interface with client-side tabs.

## Validation

```powershell
python -m unittest discover -s tests
# Requires running local node; deploys a separate integration-test contract:
python tests/blockchain_integration.py
```

Integration checks cover duplicate registration, unauthorised actions, transfer acceptance/cancellation, lifecycle order, terminal recycling, append-only correction and evidence hashes. Test contracts do not populate the app contract.

## Limitations

The contract has not received a security audit. Ganache has reported transitive vulnerabilities; it is restricted to loopback and unsuitable as hosted production infrastructure. Its native websocket extension may fall back to JavaScript on newer Node versions.

A chain establishes which address recorded an event and preserves recorded history under its network assumptions. It does not prove physical identity, ownership in law, authentic manufacture or truthful inspection. This prototype does not verify organisations, prevent QR copying, or stop a local node administrator resetting the chain. Registration is self-asserted. Do not put personal information in labels or event details.

The CSV has 16 annual records (2010–2025) with no documented source in the original project. Treat them as illustrative. Training uses 2010–2023; future predictors and recycling rates are predefined scenarios, not validated forecasts. Device rules are prototype heuristics, not diagnostics or safety certifications. Models are stylised illustrations.

## Third-party software

Three.js 0.160.0 is bundled under its MIT license; see `device_scene_component/THREE-LICENSE.txt`. Compilation uses solc 0.8.30; the local chain uses Ganache 7.9.2. Other dependencies retain their respective licenses.
