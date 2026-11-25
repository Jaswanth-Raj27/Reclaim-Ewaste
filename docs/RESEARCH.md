# Research and motivation

[Back to README](../README.md)

## Project purpose

Reclaim aims to help reduce unrecycled electronic waste and support efforts to identify and deter illegal dumping, including shipments to lower-income countries with limited capacity for safe e-waste handling.

The proposed approach is to make a device’s recorded journey easier to follow: who registered it, who accepted each handover, and whether collection, inspection, repair or recycling was recorded. An append-only blockchain history could support accountability and help investigators spot missing or disputed handovers when combined with verified participants, physical inspections and independent recycling evidence.

This is the project’s intended contribution, not a demonstrated reduction in dumping. The current prototype runs on a local blockchain and does not track physical location, verify shipment legality, authenticate recyclers or prove that recorded recycling actually occurred. Preventing illegal dumping also requires enforcement and reliable checks outside the blockchain.

## Research background and evidence

Sources reviewed **26 November 2026**. Publication dates and measurement years are stated separately below. These sources motivate the project; they do not validate its current training CSV or demonstrate its environmental impact.

### Scale of the recycling gap

The **ITU/UNITAR Global E-waste Monitor 2024** reports **62 million tonnes (Mt)** generated worldwide in **2022**, with **22.3%** documented as formally collected and recycled. It projects generation reaching **82 Mt in 2030**. These are report findings and projections, separate from Reclaim’s regression output. [Source: ITU, Global E-waste Monitor 2024](https://www.itu.int/en/ITU-D/Environment/Pages/Publications/The-Global-E-Waste-Monitor-2024.aspx)

The remaining share is **outside documented formal collection and recycling**; it should not all be labelled illegally dumped. Reclaim’s `Unrecycled_Mt` is an arithmetic scenario remainder, not a measured illegal-dumping quantity. The cited report is not established as the source of the repository’s annual dataset.

### Cross-border movements and environmental justice

The **Global Transboundary E-waste Flows Monitor 2022** estimates that **5.1 Mt crossed borders in 2019**, comprising **1.8 Mt of controlled movements** and **3.3 Mt of uncontrolled movements**. “Uncontrolled” is not proof that every shipment was illegal: the report discusses flows as used electrical/electronic equipment or e-waste that can facilitate illegal movements. The measurement year is 2019, not the report’s publication year. [Source: Global Transboundary E-waste Flows Monitor 2022](https://ewastemonitor.info/gtf-2022/)

WHO describes hazardous exposures from unsound e-waste handling, including lead release during informal activities such as open burning, and identifies children and pregnant women as particularly vulnerable. This supports the project’s focus on accountable handling and safer recovery, alongside the economic value of recovered materials. [Source: WHO, Electronic waste fact sheet, 1 October 2024](https://www.who.int/news-room/fact-sheets/detail/electronic-waste-(e-waste))

### Regulatory context

The Basel Convention’s e-waste amendments took effect on **1 January 2025** for Parties bound by them, extending its **prior informed consent (PIC)** controls to transboundary movements of hazardous and non-hazardous e-waste. The Secretariat notes exceptions for Parties that notified non-acceptance. Applicability also depends on equipment-versus-waste classification and relevant national rules; a blockchain entry is not a shipment permit or compliance certificate. [Source: Basel Convention Secretariat, E-waste Amendments FAQ](https://www.basel.int/Implementation/Ewaste/EwasteAmendments/EwasteAmendmentsFAQs/tabid/10107/Default.aspx)

### What blockchain contributes

NIST describes blockchains as shared ledgers with mechanisms that make alteration evident and resistant under their network assumptions. This supports a record-keeping rationale; it is not evidence that this project prevents dumping. [Source: NIST IR 8202, Blockchain Technology Overview, 2018](https://csrc.nist.gov/pubs/ir/8202/final)

**Reclaim’s design hypothesis:** recording accepted handovers and linking evidence fingerprints could make gaps and disputed claims easier to investigate. Proving that benefit requires real participants and independent observations. The current single-computer chain can be reset by its operator; a QR can be copied, and a valid file hash does not establish that the file’s contents are truthful.

### Research and evaluation next steps

These are proposed work, not implemented features or completed experiments:

- Replace the illustrative CSV with a documented, consistently defined dataset; evaluate forecasts on later held-out years using MAE/RMSE and compare with simple trend or last-value baselines.
- Pilot traceability with verified collectors and recyclers, independently checked device identifiers, and recycling receipts linked to recorded handovers.
- Compare the blockchain workflow with a conventional signed database: measure missing handovers, independently confirmed recycling, audit time, entry errors, cost and usability.
- Evaluate whether multiple independently operated nodes and wallet signing provide useful accountability for the actual participants. Keep sensitive identity and shipment documents off-chain.
- Measure any reduction in diversion or dumping through independently verified outcomes and a defined comparison period or group. Counts of blocks or registrations alone do not measure environmental benefit.
