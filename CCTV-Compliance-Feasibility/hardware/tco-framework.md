# Hardware and Total Cost of Ownership Framework

## Purpose

A technically feasible model can still be a poor system choice if it costs too much to purchase, power, store, update or operate. This framework records the cost dimensions without inventing prices before hardware, region, workload and vendor quotes are known.

## Cost components

| Component | Edge-only | Hybrid | Cloud-only | Measurement or input required |
|---|---|---|---|---|
| Edge hardware purchase | camera gateway, storage, accelerator, enclosure | same, possibly smaller | none or capture gateway | device quote, useful life and replacement rate |
| Amortisation | purchase / months of useful life / supported cameras | same | n/a | purchase price, warranty, useful life, cameras per device |
| Power | watts at idle/steady/thermal state x tariff | edge plus cloud | cloud provider energy is indirect | wall-meter watts, tariff, duty cycle |
| Storage | ring buffer, evidence, local backups | local evidence plus cloud archive | cloud object/block storage | bytes per camera-hour, retention, replication |
| Bandwidth | LAN/maintenance only | approved metadata/frames/clips and retries | continuous video ingress/egress | encoded bitrate, export policy, retry volume |
| Cloud GPU/CPU | none or training | selective inference/training/review | continuous processing | provider SKU, region, runtime seconds, concurrency and minimum billing |
| Cloud egress | none | selected evidence and analytics | potentially continuous or report traffic | bytes exported, destination and rate |
| Maintenance | OS/security patches, model updates, device replacement | edge plus cloud service | cloud service and model/API changes | engineer hours, update frequency, support contract |
| Connectivity | site network and failover | WAN for optional features | WAN is critical path | network cost and outage budget |
| Privacy/security | local key, access and audit controls | gateway, redaction, cloud processor | broader data governance and vendor review | control implementation and review effort |
| Camera/site integration | local sensors/access control | gateway and event joins | cloud connectors | integration effort, protocol and support |

## Core formulas

```text
edge_amortisation_per_camera_month
  = (hardware_purchase + installation + commissioning) / useful_life_months
    / cameras_served_by_device

power_per_camera_month
  = average_watts * hours_per_month * tariff_per_kWh
    / cameras_served_by_device / 1000

storage_per_camera_month
  = bytes_per_camera_hour * retention_hours * replication_factor

cloud_inference_per_camera_month
  = billed_compute_seconds_per_camera_hour
    * camera_hours_per_month * price_per_compute_second

bandwidth_per_camera_month
  = exported_bytes_per_camera_hour * camera_hours_per_month
    * transfer_price_per_byte

cost_per_camera_hour
  = (amortisation + power + storage + cloud + bandwidth
     + maintenance allocation + support allocation)
    / camera_hours
```

Report both full cost and variable cost. State whether staff time, model licensing, cloud minimums, tax, currency conversion, installation and downtime are included.

## Capacity and cost experiment

For each exact hardware option, run 1..N cameras at the target resolution, source FPS, sampled FPS and rule mix until the first acceptance gate fails. Record:

- cameras per device at the approved p95 latency and quality gate;
- warm/cold startup and recovery;
- steady-state watts and thermal throttling;
- storage bytes per camera-hour and bytes per alert;
- cloud invocation rate per camera-hour for hybrid stages;
- VLM calls per alert and tokens/seconds per call;
- data egress bytes per camera-hour;
- monthly maintenance and operator hours estimate;
- price date, region, vendor SKU and quote/source.

Do not use TOPS or a vendor's single-model FPS as a cost or camera-count estimate.

## Decision rule

Prefer the option with the lowest total cost that passes the rule-level reliability, privacy, licensing, latency, storage, recovery and operator gates. A cheaper device that increases false alerts, misses, review labor or privacy exposure is not cheaper at system level.
